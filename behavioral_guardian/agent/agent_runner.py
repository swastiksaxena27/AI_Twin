"""Agent runner — collects data and posts to backend every 30 seconds.

Auth model (three ways to link a device, checked in this order):

1. A pairing file: from the web dashboard, Settings → "Connect this
   device" downloads `guardian-pairing.json` to your Downloads folder.
   The agent finds it automatically on startup, adopts the token inside,
   and renames the file so it can't be reused. No terminal input at all.
2. A previously-saved token: after step 1 (or step 3) runs once, the
   token is cached locally — every run after that just reads it silently.
3. Interactive fallback: if neither of the above exists, the agent asks
   ONCE for a username, then a hidden password prompt (nothing echoed to
   the screen or left in shell history), logs in, and immediately
   exchanges that for a long-lived device token — which then becomes the
   cached token from step 2 for all future runs.

For unattended/automated setups (e.g. a service account, CI), you can
still skip the prompt entirely by setting
BEHAVIORAL_GUARDIAN_AGENT_USERNAME / BEHAVIORAL_GUARDIAN_AGENT_PASSWORD as
environment variables before starting the agent — those are checked first
in step 3.
"""

import getpass
import json
import os
import sys
import time
from pathlib import Path

import requests
from pynput import keyboard, mouse

from behavioral_guardian.agent.download_monitor import DownloadMonitor
from behavioral_guardian.agent.feature_extractor import FeatureExtractor
from behavioral_guardian.agent.keyboard_collector import KeyboardCollector
from behavioral_guardian.agent.mouse_collector import MouseCollector
from behavioral_guardian.agent.network_monitor import NetworkMonitor
from behavioral_guardian.agent.process_monitor import ProcessMonitor
from behavioral_guardian.agent.usb_monitor import USBMonitor
from behavioral_guardian.backend.schemas.models import FeatureVector
from behavioral_guardian.config.settings import (
    API_BASE_URL_OVERRIDE,
    API_HOST,
    API_PORT,
    API_PREFIX,
    FEATURE_VECTOR_INTERVAL_SECONDS,
)
from behavioral_guardian.utils.logging_config import setup_logging

logger = setup_logging(__name__)

# Local cache for the long-lived device token. Lives next to the SQLite DB,
# outside version control (see .gitignore), and holds no password — only a
# token that's revocable and expires on its own.
def _persistent_data_dir() -> Path:
    """Where to store the cached device token / pairing state.

    When running as a normal Python script (dev machine), this stays right
    next to the project's own data/ folder, same as before.

    When running as a PyInstaller-frozen .exe, `__file__` points inside a
    temporary extraction folder that PyInstaller deletes after every run —
    so storing anything there would silently defeat the whole point of
    caching the token (you'd be asked to log in again every single launch).
    In that case, use a real per-user app-data folder instead, so it
    survives between runs like any normal installed application.
    """
    if getattr(sys, "frozen", False):
        base = Path(os.environ.get("LOCALAPPDATA") or Path.home())
        return base / "BehavioralGuardianAgent"
    return Path(__file__).resolve().parent.parent / "data"


TOKEN_FILE = _persistent_data_dir() / ".agent_session.json"

# Where the browser saves the file when someone clicks "Download pairing
# file" in Settings. Checked automatically on every start — if present, it's
# consumed once (copied into TOKEN_FILE, then renamed so it can't be reused
# or accidentally left lying around readable).
PAIRING_FILE_LOCATIONS = [
    Path.home() / "Downloads" / "guardian-pairing.json",
    Path.cwd() / "guardian-pairing.json",
]


class AgentAuthError(RuntimeError):
    """Raised when the agent can't obtain a bearer token to talk to the API."""


class AgentRunner:
    """Orchestrate collectors and send feature vectors to API."""

    def __init__(
        self,
        user_id: int = 1,
        device_id: int | None = None,
        access_token: str | None = None,
    ) -> None:
        self.user_id = user_id
        self.display_name = "Unknown"  # replaced with the real name once linked
        self.device_id = device_id
        self.base_url = API_BASE_URL_OVERRIDE.rstrip("/") or f"http://{API_HOST}:{API_PORT}{API_PREFIX}"
        self.api_url = f"{self.base_url}/analyze"
        self.access_token = access_token
        self.keyboard_collector = KeyboardCollector()
        self.mouse_collector = MouseCollector()
        self.process_monitor = ProcessMonitor()
        self.usb_monitor = USBMonitor()
        self.download_monitor = DownloadMonitor()
        self.network_monitor = NetworkMonitor()
        self.feature_extractor = FeatureExtractor()
        self._running = False

    # ── Local token cache ────────────────────────────────────────────

    def _load_cached_token(self) -> bool:
        """Try to load a previously-saved device token. Returns True if found."""
        if not TOKEN_FILE.exists():
            return False
        try:
            data = json.loads(TOKEN_FILE.read_text())
            self.user_id = data["user_id"]
            self.access_token = data["access_token"]
            self.display_name = data.get("display_name", "Unknown")
            logger.info("Loaded saved device token for %s (no login needed)", self.display_name)
            return True
        except (json.JSONDecodeError, KeyError, OSError):
            logger.warning("Saved token file was unreadable, ignoring it")
            return False

    def _consume_pairing_file(self) -> bool:
        """Look for a `guardian-pairing.json` downloaded from Settings →
        'Connect this device'. If found: adopt its token as the permanent
        cached token, then rename the original so it can't be silently
        reused (e.g. if it were left in a shared Downloads folder) or
        mistaken for still-pending on the next run. Returns True if a
        pairing file was found and adopted."""
        for path in PAIRING_FILE_LOCATIONS:
            if not path.exists():
                continue
            try:
                data = json.loads(path.read_text())
                user_id, token = data["user_id"], data["access_token"]
            except (json.JSONDecodeError, KeyError, OSError):
                logger.warning("Found %s but couldn't read it as a pairing file, ignoring", path)
                continue

            display_name = data.get("full_name") or data.get("username") or "Unknown"
            self.user_id = user_id
            self.access_token = token
            self.display_name = display_name
            self._save_cached_token(user_id, token, display_name)

            try:
                path.rename(path.with_suffix(".used.json"))
            except OSError:
                path.unlink(missing_ok=True)  # rename failed (e.g. cross-device) — delete instead

            logger.info("Linked this device to %s (user_id=%s) from %s", display_name, user_id, path)
            return True
        return False

    def _save_cached_token(self, user_id: int, device_token: str, display_name: str = "Unknown") -> None:
        TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
        TOKEN_FILE.write_text(
            json.dumps({"user_id": user_id, "access_token": device_token, "display_name": display_name})
        )
        try:
            os.chmod(TOKEN_FILE, 0o600)  # owner read/write only; no-op on Windows
        except OSError:
            pass
        logger.info("Saved device token for %s — future runs won't need a password", display_name)

    def _clear_cached_token(self) -> None:
        self.access_token = None
        TOKEN_FILE.unlink(missing_ok=True)

    # ── Auth ──────────────────────────────────────────────────────────

    def _get_credentials(self) -> tuple[str, str]:
        """Env vars first (for unattended setups); otherwise prompt once,
        interactively, with the password hidden."""
        username = os.environ.get("BEHAVIORAL_GUARDIAN_AGENT_USERNAME")
        password = os.environ.get("BEHAVIORAL_GUARDIAN_AGENT_PASSWORD")
        if username and password:
            return username, password

        if not sys.stdin.isatty():
            raise AgentAuthError(
                "No saved device token, and no env vars set, and this isn't an "
                "interactive terminal to prompt in. Set "
                "BEHAVIORAL_GUARDIAN_AGENT_USERNAME / BEHAVIORAL_GUARDIAN_AGENT_PASSWORD "
                "or run this once interactively first."
            )

        print("\nFirst-time agent setup — log in once to link this device.")
        print("(Your password is not stored; only a revocable device token is saved.)")
        username = input("Username or email: ").strip()
        password = getpass.getpass("Password: ")
        return username, password

    def _login_and_exchange(self, username: str, password: str) -> tuple[int, str, str]:
        """Log in, then immediately trade that short-lived token for a
        long-lived device token. Returns (user_id, display_name, device_token)."""
        res = requests.post(
            f"{self.base_url}/auth/login",
            json={"identifier": username, "password": password},
            timeout=10,
        )
        res.raise_for_status()
        body = res.json()
        if not body.get("success") or not body.get("access_token"):
            raise AgentAuthError(f"Login failed for '{username}': {body.get('message')}")

        user_id = body["user"]["id"]
        display_name = body["user"].get("full_name") or body["user"].get("username") or username
        login_token = body["access_token"]

        res2 = requests.post(
            f"{self.base_url}/auth/device-token",
            headers={"Authorization": f"Bearer {login_token}"},
            timeout=10,
        )
        res2.raise_for_status()
        device_token = res2.json()["access_token"]
        logger.info("Agent linked to %s (user_id=%s)", display_name, user_id)
        return user_id, display_name, device_token

    def _ensure_token(self) -> str:
        if self.access_token:
            return self.access_token
        if self._load_cached_token():
            return self.access_token
        if self._consume_pairing_file():
            return self.access_token

        username, password = self._get_credentials()
        user_id, display_name, device_token = self._login_and_exchange(username, password)
        self.user_id = user_id
        self.display_name = display_name
        self.access_token = device_token
        self._save_cached_token(user_id, device_token, display_name)
        return self.access_token

    def _start_input_listeners(self) -> tuple[keyboard.Listener, mouse.Listener]:
        """Start pynput listeners for keyboard and mouse."""
        kb_listener = keyboard.Listener(
            on_press=self.keyboard_collector.on_press,
            on_release=self.keyboard_collector.on_release,
        )
        ms_listener = mouse.Listener(
            on_move=self.mouse_collector.on_move,
            on_click=self.mouse_collector.on_click,
        )
        kb_listener.start()
        ms_listener.start()
        return kb_listener, ms_listener

    def _collect_and_send(self) -> None:
        """Build feature vector and POST to backend."""
        keyboard_data = self.keyboard_collector.snapshot()
        mouse_data = self.mouse_collector.snapshot()
        process_data = self.process_monitor.snapshot()
        usb_data = self.usb_monitor.snapshot()
        download_data = self.download_monitor.snapshot()
        network_data = self.network_monitor.snapshot()

        features = self.feature_extractor.build_vector(keyboard_data, mouse_data, process_data)
        activity_signals = self.feature_extractor.build_activity_signals(
            process_data, usb_data, download_data, network_data
        )

        payload = FeatureVector(
            user_id=self.user_id,
            device_id=self.device_id,
            activity_signals=activity_signals,
            **features,
        )

        token = self._ensure_token()
        headers = {"Authorization": f"Bearer {token}"}

        try:
            response = requests.post(self.api_url, json=payload.model_dump(), headers=headers, timeout=10)
            if response.status_code == 401:
                # Saved token expired or was revoked — clear it and log in
                # fresh once (prompts again only if it's really been 30 days).
                logger.info("Saved token rejected, re-authenticating")
                self._clear_cached_token()
                token = self._ensure_token()
                headers = {"Authorization": f"Bearer {token}"}
                payload.user_id = self.user_id
                response = requests.post(self.api_url, json=payload.model_dump(), headers=headers, timeout=10)
            response.raise_for_status()
            logger.info("[%s] Feature vector sent: %s", self.display_name, response.json())
        except requests.RequestException as exc:
            logger.exception("Failed to send feature vector: %s", exc)

    def run(self) -> None:
        """Main collection loop."""
        self._ensure_token()  # do auth up front, before touching input listeners
        self._running = True
        self.download_monitor.start()
        kb_listener, ms_listener = self._start_input_listeners()
        logger.info("Agent started for %s (user_id=%d)", self.display_name, self.user_id)

        try:
            while self._running:
                self._collect_and_send()
                time.sleep(FEATURE_VECTOR_INTERVAL_SECONDS)
        finally:
            self._running = False
            kb_listener.stop()
            ms_listener.stop()
            self.download_monitor.stop()
            logger.info("Agent stopped")


def main() -> None:
    """Entry point for agent process. See module docstring for the auth flow."""
    runner = AgentRunner(device_id=1)
    try:
        runner.run()
    except AgentAuthError as exc:
        logger.error(str(exc))


if __name__ == "__main__":
    main()
