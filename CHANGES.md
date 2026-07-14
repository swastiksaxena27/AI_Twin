# Changes in this fork

This is the AI-twin project (the more sophisticated engine of the two you shared: MITRE-tagged
risk rules, trust decay/recovery modeling, 7-module agent, 35-test suite, Tailwind frontend, full
`docs/` folder) with the things guardian-fullstack was doing better now ported in.

## 1. Real authentication (the big one)

Previously: `/auth/login` just returned `{success, user}` — no token, and every other route
(`/trust/{user_id}`, `/risk/{user_id}`, `/alerts/{user_id}`, etc.) was **completely open**. Anyone
could query anyone else's behavioral data with no credentials at all.

Now:
- `POST /auth/register` and `POST /auth/login` issue a signed JWT (`access_token`, HS256, 24h
  expiry) — see `behavioral_guardian/utils/security.py` (`create_access_token` /
  `decode_access_token`) and `config/settings.py` (`JWT_SECRET_KEY`, override via
  `BEHAVIORAL_GUARDIAN_JWT_SECRET` in production).
- Every other route now requires `Authorization: Bearer <token>` — enforced by
  `get_current_user` in `backend/dependencies.py`.
- Path-based user routes (`/trust/{user_id}`, `/risk/{user_id}`, `/alerts/{user_id}`,
  `/history/{user_id}`, `/session/{user_id}`, `/settings/{user_id}`, `/users/{user_id}`,
  `/analytics/{user_id}`) additionally require the token to belong to that `user_id`, or to an
  org admin — enforced by `require_self_or_org_admin`.
- Body-based routes (`POST /analyze`, `POST /reauth`) check the token holder against
  `payload.user_id` inside the handler, since there's no path param to hook a dependency to.
- `GET /users` (roster) just requires *a* valid token; non-admins are silently scoped to their own
  organization regardless of what `organization` query param they pass.
- Frontend: `frontend/src/api/client.js` now stores the token (`getToken`/`setToken`/
  `clearToken`), attaches it to every request, and clears it on a 401. `AppContext.jsx` and
  `Login.jsx` pass the token through on login/register. `App.jsx` gained a `RequireAuth` guard on
  the `/app/*` routes so a stale "authed" flag without a real token bounces back to `/login`.

## 2. Doc/code consistency

The README described a `dashboard/` folder (Streamlit + Plotly) that was never actually built —
the real UI is the React frontend under `frontend/`. That reference, and the unused
`streamlit`/`plotly` entries in `requirements.txt` and `pyproject.toml`, have been removed.
`README.md` now documents the actual auth requirements for every endpoint.

## 3. Test suite

- `tests/conftest.py`: `register_user` fixture now also returns `access_token`; added an
  `auth_headers()` helper.
- `tests/test_api.py`, `tests/test_analytics.py`, `tests/test_users.py`, `tests/test_settings.py`:
  updated to register a real user, grab their token, and send it — since these routes are no
  longer open. Also added ownership-rejection assertions (a token for user A can't read user B's
  data).
- New `tests/test_auth_protection.py`: sweeps every protected GET route to confirm it 403s with no
  token, 403s with someone else's token, and that an org admin can read a teammate's data.
- New dependency: `pyjwt>=2.7.0` (added to `requirements.txt` and `pyproject.toml`).

## 4. Agent no longer needs a password every run

The agent originally required `BEHAVIORAL_GUARDIAN_AGENT_USERNAME` /
`BEHAVIORAL_GUARDIAN_AGENT_PASSWORD` on every single start — fine for a quick test,
bad for a real (especially non-technical) user. Fixed with a proper device-token flow:

- New endpoint `POST /auth/device-token` (protected — needs a normal login token):
  exchanges it for a long-lived (30 day) token, via `create_device_token()` in
  `utils/security.py` (`JWT_DEVICE_TOKEN_EXPIRE_DAYS` in `config/settings.py`).
- `agent_runner.py` now, on first run only, prompts interactively for username +
  a hidden password (via `getpass`, never in shell history), logs in, exchanges for a
  device token, and saves *only that token* — never the password — to
  `behavioral_guardian/data/.agent_session.json` (gitignored).
- Every run after that reads the saved token silently — zero prompts, zero env vars.
- If the saved token is ever rejected (30-day expiry, or the file's gone), it
  transparently re-triggers the one-time login instead of crashing.
- `BEHAVIORAL_GUARDIAN_AGENT_USERNAME`/`PASSWORD` env vars still work too, for
  unattended/service-account setups that can't prompt interactively.

## 5. Hosting (Phase 1) and .exe packaging (Phase 3)

See `DEPLOYMENT.md` for the full walkthrough. Summary of what changed to make these possible:

- `config/settings.py`: `API_HOST`/`API_PORT` are now env-overridable, and a new
  `API_BASE_URL_OVERRIDE` lets both the agent and (via `render.yaml`) the hosted setup point at a
  real backend URL instead of assuming `localhost`.
- `render.yaml`: one-click Render Blueprint — a free web service for the backend, a free static
  site for the frontend. Known limitation documented in `DEPLOYMENT.md`: Render's free tier has no
  persistent disk, so the SQLite file resets on redeploy — fine for a demo, not for production
  without migrating to Postgres (the DB layer is already URL-configurable, so that's a config
  change, not a code rewrite).
- `agent_runner.py`: fixed a real bug *before* it could bite — the cached-token file used to be
  stored next to the script itself via `__file__`, which works fine as a normal Python script but
  would silently break once packaged, since a PyInstaller `.exe` extracts to a temp folder that gets
  wiped after every run. It now detects `sys.frozen` and uses a proper per-user app-data folder
  instead when running as a packaged `.exe`.
- `packaging/agent.spec` + `packaging/build_agent.bat`: builds `GuardianAgent.exe` from
  `agent_runner.py`, with the pynput/pywin32 hidden-imports it needs on Windows. Must be run on
  Windows — PyInstaller doesn't cross-compile.

## What was intentionally left alone

Everything guardian-fullstack was *behind* on stays as-is here: the MITRE-tagged risk engine
(`engines/risk_engine/`), the decay/recovery trust model (`engines/trust_engine/`), the 7-module
agent (`agent/`), and the docs folder. Those were already the stronger implementation and didn't
need porting from the other project.

## Caveat

I don't have network access in this environment, so I could not `pip install` and boot-test this
live. Every change was verified by static review — reading the FastAPI dependency-injection
pattern used, cross-checking every schema field, and re-deriving the expected HTTP status code for
each new test (note: FastAPI's `HTTPBearer` returns **403** for a missing Authorization header and
**401** only for a present-but-invalid token — the test suite reflects that split). Please run:

```bash
pip install -r requirements.txt
python -m behavioral_guardian.database.connection
pytest behavioral_guardian/tests -v
```

and send me the traceback if anything fails — happy to fix it from there.
