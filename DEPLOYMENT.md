# Deploying AI Behavioral Guardian so other people can actually use it

This covers the two remaining pieces from our earlier plan:
**Phase 1** — host the backend + frontend somewhere reachable (not just your laptop).
**Phase 3** — package the agent into a `.exe` so someone else doesn't need Python or a terminal.

(Phase 2 — the "Connect this device" pairing flow — is already built; see CHANGES.md.)

---

## Phase 1: Hosting on Render (free tier)

Render was chosen because, as of 2026, it's the only major platform with a genuinely free tier —
Railway and Fly.io both dropped theirs. The tradeoff: the free backend "sleeps" after 15 minutes of
no traffic, and the first request after that takes 30–50 seconds to wake up. Fine for a demo/college
project; upgrade the plan later if this becomes a real always-on product.

### Steps

1. **Push this project to GitHub** (a public or private repo — Render deploys from git).
   ```powershell
   git init
   git add .
   git commit -m "Initial commit"
   # create a repo on github.com, then:
   git remote add origin https://github.com/<you>/ai-behavioral-guardian.git
   git push -u origin main
   ```

2. **Create a Render account** at render.com (free, GitHub sign-in works).

3. **New → Blueprint** → connect your GitHub repo → Render will find `render.yaml` in this
   project automatically and set up both services (backend web service + frontend static site) in
   one go. Click **Apply**.

4. Wait for the backend to finish deploying. Copy its URL from the Render dashboard — it'll look
   like `https://ai-behavioral-guardian-backend.onrender.com`.

5. Go to the **frontend** service → Environment → set:
   ```
   VITE_API_BASE_URL = https://ai-behavioral-guardian-backend.onrender.com/api/v1
   ```
   (`render.yaml` left this one blank on purpose — `sync: false` — because you don't know the
   backend's URL until step 4.) Save, then **Manual Deploy → Deploy latest commit** to rebuild the
   frontend with that URL baked in.

6. Open the frontend's Render URL — that's your live app. Register an account, confirm login/
   dashboard work end-to-end against the hosted backend.

### Known limitation: the database will reset periodically

Render's **free** web services don't include a persistent disk — every redeploy (and sometimes
every restart) wipes the SQLite file, along with all registered users and trust history. This is fine
for a demo where you re-register test accounts occasionally; it is **not** fine for a real product.

If you outgrow this: the database URL is already fully configurable
(`BEHAVIORAL_GUARDIAN_DATABASE_URL` env var — see `config/settings.py`), so swapping to Render's
free PostgreSQL is mostly just: create the Postgres instance in Render, set that env var to its
connection string, add `psycopg2-binary` to `requirements.txt`. No application code changes needed
beyond that, since the ORM layer doesn't hardcode SQLite anywhere.

---

## Phase 3: Packaging the agent as a `.exe`

This lets someone run the agent by double-clicking a file — no Python, no terminal, no `pip install`.

**Important constraint:** PyInstaller does not cross-compile. Building on Linux produces a Linux
binary; you must run the build itself on a Windows machine to get a Windows `.exe`. If you've been
developing this whole project on your own Windows laptop (per our terminal screenshots), you're
already set up to do this.

### One-time fix before building

The `.exe` needs to know your backend's real URL — but it can't read an environment variable off
the machine it's later run on (that machine won't have one set, and a non-technical user won't know
to add it). So the URL has to be baked in at build time instead:

1. Finish Phase 1 above so you have a real backend URL.
2. Open `behavioral_guardian/config/settings.py` and change:
   ```python
   API_BASE_URL_OVERRIDE = os.environ.get("BEHAVIORAL_GUARDIAN_API_BASE_URL", "")
   ```
   to:
   ```python
   API_BASE_URL_OVERRIDE = os.environ.get(
       "BEHAVIORAL_GUARDIAN_API_BASE_URL", "https://your-actual-backend.onrender.com/api/v1"
   )
   ```

### Build it

```powershell
cd "C:\Users\Shamaya\Documents\AI Behavioral\AI-Twin"
venv\Scripts\activate
cd packaging
build_agent.bat
```

This installs PyInstaller + pywin32, then builds. Find the result at
`packaging\dist\GuardianAgent.exe`.

### Giving it to someone else

1. They open your hosted frontend URL (from Phase 1) in their browser and register an account.
2. They go to Settings → "Connect this device" → download `guardian-pairing.json` to their
   Downloads folder.
3. You send them `GuardianAgent.exe` (email, USB drive, shared drive — however).
4. They double-click it. It finds the pairing file automatically, links itself, and starts running —
   no terminal, no typing, no Python installed.

If you skip step 2, `GuardianAgent.exe` still works — it just opens a console window asking for a
username and password once (see CHANGES.md for the full auth flow), then remembers it after that.

### Making it start automatically (optional, further polish)

Right now, someone has to double-click the `.exe` each time they want monitoring active. To make it
start automatically on login (closer to how real endpoint agents behave): drop a shortcut to
`GuardianAgent.exe` into their Windows Startup folder
(`shell:startup` in the Run dialog). This is a per-machine manual step for now — a proper installer
(e.g. built with Inno Setup) that does this automatically is a reasonable next step if you want to
polish this further, but is beyond today's scope.
