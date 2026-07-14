# Integration Checklist

## Module Connections

- [ ] Database initialized and tables created
- [ ] Backend connects to database via SQLAlchemy session
- [ ] Agent posts feature vectors to `POST /api/v1/analyze`
- [ ] Backend invokes ML inference on analyze
- [ ] ML anomaly score feeds Trust Engine
- [ ] Agent activity signals feed Risk Engine
- [ ] Trust + Risk scores feed Response Engine
- [ ] Explainability Engine generates human-readable output
- [ ] All events persisted to SQLite
- [ ] Dashboard reads from API (never direct DB)

## Integration Tests

| Flow | Status |
|------|--------|
| Agent → Backend | Pending runtime |
| Backend → ML | Covered in unit tests |
| ML → Trust | Covered in unit tests |
| Risk → Response | Covered in unit tests |
| Dashboard → API | Pending runtime |

## Contract Preservation

- [ ] Feature names unchanged
- [ ] API endpoints unchanged
- [ ] Column names unchanged
- [ ] Status levels unchanged (NORMAL, ELEVATED, SUSPICIOUS, HIGH_RISK, CRITICAL)
- [ ] Risk rule weights unchanged

## Run Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Initialize database
python -m behavioral_guardian.database.connection init_db

# Start backend
uvicorn behavioral_guardian.backend.main:app --reload

# Start agent (separate terminal)
python -m behavioral_guardian.agent.agent_runner

# Start dashboard (separate terminal)
streamlit run behavioral_guardian/dashboard/app.py
```
