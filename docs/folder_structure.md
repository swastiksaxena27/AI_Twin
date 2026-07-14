# Folder Structure

```
behavioral_guardian/
├── config/              # Application settings (single source of truth)
├── agent/               # Behavioral data collection
├── ml/                  # Digital Twin (Isolation Forest)
├── engines/
│   ├── trust_engine/    # Identity trust scoring
│   ├── risk_engine/     # Activity risk scoring
│   ├── response_engine/ # Action execution
│   └── explainability_engine/
├── backend/             # FastAPI application
│   ├── routers/
│   ├── services/
│   └── schemas/
├── database/            # SQLAlchemy models and repositories
├── dashboard/           # Streamlit UI
├── utils/               # Shared utilities (logging, etc.)
├── logs/                # Runtime logs
├── tests/               # Unit and integration tests
├── docs/                # Architecture and contracts
├── data/                # SQLite DB and ML artifacts
└── requirements.txt
```

## Principles

- One file = one responsibility
- No monolithic files
- Maximum file size preferred: 300 lines
- No business logic in routes or dashboard
