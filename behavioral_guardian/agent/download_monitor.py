"""Download activity monitoring."""

from pathlib import Path
from typing import Any, Dict

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from behavioral_guardian.utils.logging_config import setup_logging

logger = setup_logging(__name__)


class DownloadEventHandler(FileSystemEventHandler):
    """Track file creation size in watched directories."""

    def __init__(self) -> None:
        self.download_bytes = 0
        self.zip_creation = False

    def on_created(self, event) -> None:
        """Increment download bytes on new files."""
        if event.is_directory:
            return
        path = Path(event.src_path)
        try:
            size = path.stat().st_size
        except OSError:
            size = 0
        self.download_bytes += size
        if path.suffix.lower() in {".zip", ".7z", ".rar"}:
            self.zip_creation = True


class DownloadMonitor:
    """Watch download directories for spikes."""

    def __init__(self, watch_paths: list[Path] | None = None) -> None:
        self._handler = DownloadEventHandler()
        self._observer = Observer()
        self._started = False
        paths = watch_paths or [Path.home() / "Downloads"]
        for path in paths:
            if path.exists():
                self._observer.schedule(self._handler, str(path), recursive=False)

    def start(self) -> None:
        """Start filesystem observer."""
        if not self._started:
            self._observer.start()
            self._started = True
            logger.info("Download monitor started")

    def stop(self) -> None:
        """Stop filesystem observer."""
        if self._started:
            self._observer.stop()
            self._observer.join(timeout=2)
            self._started = False

    def snapshot(self) -> Dict[str, Any]:
        """Return download activity and reset counters."""
        data = {
            "download_bytes": float(self._handler.download_bytes),
            "zip_creation": self._handler.zip_creation,
        }
        self._handler.download_bytes = 0
        self._handler.zip_creation = False
        return data
