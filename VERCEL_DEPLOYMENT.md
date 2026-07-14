# Deploying AI Behavioral Guardian on Vercel

Everything — the React frontend **and** the FastAPI backend — runs on a single
Vercel project. No second hosting provider needed.

---

## Prerequisites

- A **GitHub account** (Vercel deploys from Git).
- A **Vercel account** — free, sign up at [vercel.com](https://vercel.com)
  (use "Continue with GitHub" for one-click setup).

---

## Step 1 — Push to GitHub

If your repo isn't on GitHub yet:

```powershell
# From the project root
git add .
git commit -m "Configure Vercel deployment"
```

Then create a repo on **github.com → New Repository** (name it whatever you
want, public or private both work), and push:

```powershell
git remote add origin https://github.com/YOUR_USERNAME/ai-behavioral-guardian.git
git branch -M main
git push -u origin main
```

---

## Step 2 — Import into Vercel

1. Go to [vercel.com/new](https://vercel.com/new).
2. Click **"Import Git Repository"** and select your GitHub repo.
3. Vercel auto-detects the `vercel.json` in the project root — **you don't
   need to change any build settings**. Everything is pre-configured:
   - **Build Command**: `cd frontend && npm install && npm run build`
   - **Output Directory**: `frontend/dist`
   - **Python Serverless Function**: `api/index.py`

4. **Add these Environment Variables** before clicking Deploy:

   | Key                              | Value                              | Notes                              |
   |----------------------------------|------------------------------------|------------------------------------|
   | `VITE_API_BASE_URL`              | `/api/v1`                          | Relative — same Vercel domain      |
   | `BEHAVIORAL_GUARDIAN_JWT_SECRET`  | *(any random 32+ char string)*     | e.g. `openssl rand -hex 32`        |

   > **Tip**: For the JWT secret, open a terminal and run:
   > ```bash
   > python -c "import secrets; print(secrets.token_hex(32))"
   > ```
   > Paste the output as the value.

5. Click **Deploy**. Wait ~2-3 minutes.

---

## Step 3 — Verify

Once deployed, Vercel gives you a URL like `https://ai-behavioral-guardian.vercel.app`.

- **Frontend**: Open the URL — you should see the login/register page.
- **API Health Check**: Visit `https://YOUR_APP.vercel.app/health`
  — should return `{"status":"ok"}`.
- **Swagger Docs**: Visit `https://YOUR_APP.vercel.app/docs`
  — full interactive API documentation.

**That's it. You're deployed.** 🎉

---

## How It Works Under the Hood

```
vercel.json routes:

  /api/v1/*       →  api/index.py  (Python serverless function = FastAPI)
  /health         →  api/index.py
  /docs           →  api/index.py
  /openapi.json   →  api/index.py
  /*              →  index.html    (React SPA with client-side routing)
```

The `api/index.py` file imports the existing FastAPI app from
`behavioral_guardian/backend/main.py` — zero duplication.

---

## ⚠️ Known Limitation: Ephemeral Database

Vercel serverless functions have a **read-only filesystem** — SQLite writes go
to `/tmp`, which is cleared between function invocations. This means:

- **Users you register will eventually disappear** (when the function cold-starts).
- This is **perfectly fine for a demo / college project**.
- For persistence, set `BEHAVIORAL_GUARDIAN_DATABASE_URL` to an external
  Postgres URL (e.g., [Neon](https://neon.tech) free tier) and add
  `psycopg2-binary` to `requirements.txt`. No code changes needed.

---

## Redeploying After Changes

Just push to GitHub — Vercel auto-deploys on every `git push`:

```powershell
git add .
git commit -m "Your change description"
git push
```

Vercel picks it up within seconds and deploys automatically.
