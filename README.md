# AI Behavioral Guardian

Continuous behavioral authentication system. Trust is evaluated continuously — not just at login.

**Core question:** WHO are you? WHAT are you doing? WHAT should happen next? WHY was this decision made?

## Project Structure

```
behavioral_guardian/
├── agent/          # Keyboard, mouse, process, USB, download, network collectors
├── ml/             # Isolation Forest Digital Twin
├── engines/        # Trust, Risk, Response, Explainability
├── backend/        # FastAPI (/api/v1)
├── database/       # SQLAlchemy + SQLite
├── config/         # Single source of truth for constants
├── tests/
└── docs/           # Architecture, contracts, constitution
frontend/           # React + Vite + Tailwind UI
```

> Note: an earlier version of this README listed a `dashboard/` (Streamlit + Plotly) folder.
> That folder was never actually built — the React frontend under `frontend/` is the real UI —
> so the reference (and the unused `streamlit`/`plotly` dependencies) has been removed.

## Auth

All endpoints except `POST /api/v1/auth/register` and `POST /api/v1/auth/login` require a bearer
token. Register or log in to get one:

```bash
curl -X POST http://localhost:8080/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"hunter2222"}'
# → { "success": true, "access_token": "eyJ...", "user": {...} }
```

Send it back on every other request:

```bash
curl http://localhost:8080/api/v1/trust/1 \
  -H "Authorization: Bearer eyJ..."
```

- A token only works for its own `user_id` in path-based endpoints (`/trust/{user_id}`,
  `/risk/{user_id}`, `/alerts/{user_id}`, `/history/{user_id}`, `/session/{user_id}`,
  `/settings/{user_id}`, `/users/{user_id}`, `/analytics/{user_id}`) — unless the caller is an
  **org admin** (`is_org_admin=true`), who can view anyone in the same request.
- `POST /analyze` and `POST /reauth` take `user_id` in the request body; the token holder must
  match that `user_id` (or be an org admin).
- `GET /users` (the roster) requires any valid token; non-admins are silently scoped to their own
  `organization` regardless of the `organization` query param they pass.
- Tokens are JWTs (HS256), valid for 24 hours. Set `BEHAVIORAL_GUARDIAN_JWT_SECRET` in production —
  the default in `config/settings.py` is for local development only.

## Quick Start

### Backend

```bash
cd .   # project root (AI-twin)
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Initialize database
python -m behavioral_guardian.database.connection

# Start API
uvicorn behavioral_guardian.backend.main:app --reload --port 8080
```

Verify at http://localhost:8080/docs

```bash
# Start agent (separate terminal, optional — real keyboard/mouse capture)
python -m behavioral_guardian.agent.agent_runner
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

## API Endpoints

| Method | Path | Auth |
|--------|------|------|
| POST | `/api/v1/auth/register` | none |
| POST | `/api/v1/auth/login` | none |
| POST | `/api/v1/analyze` | bearer token, body `user_id` must match |
| GET | `/api/v1/trust/{user_id}` | bearer token, self or org admin |
| GET | `/api/v1/risk/{user_id}` | bearer token, self or org admin |
| GET | `/api/v1/alerts/{user_id}` | bearer token, self or org admin |
| GET | `/api/v1/history/{user_id}` | bearer token, self or org admin |
| GET | `/api/v1/session/{user_id}` | bearer token, self or org admin |
| GET/PUT | `/api/v1/settings/{user_id}` | bearer token, self or org admin |
| GET | `/api/v1/users` | bearer token (any) |
| GET/PATCH | `/api/v1/users/{user_id}` | bearer token, self or org admin |
| GET | `/api/v1/analytics/{user_id}` | bearer token, self or org admin |
| POST | `/api/v1/reauth` | bearer token, body `user_id` must match |

## Run Tests

```bash
pytest behavioral_guardian/tests -v
```

## Documentation

See `docs/` for architecture, database schema, API contract, engineering constitution, and
role-specific Cline prompts. (`docs/api_contract.md` predates the auth layer added here — the
table above is the current source of truth for what each route requires.)
