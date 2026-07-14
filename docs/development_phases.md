# Development Phases

## Phase 1 — Foundation

- [x] Project structure and documentation
- [x] Config and logging utilities
- [x] Database models and migrations bootstrap
- [x] Pydantic schemas and API contracts

## Phase 2 — Core Engines

- [x] Trust Engine (weighted averaging, decay, recovery)
- [x] Risk Engine (rule-based scoring)
- [x] Response Engine (5-level actions)
- [x] Explainability Engine

## Phase 3 — Backend & ML

- [x] FastAPI routes and services
- [x] Isolation Forest enrollment, training, inference
- [x] Model persistence (isolation_forest.pkl, scaler.pkl, baseline.json)

## Phase 4 — Agent Layer

- [x] Keyboard, mouse, process collectors
- [x] USB, download, network monitors
- [x] Feature extraction (30-second interval)

## Phase 5 — Dashboard & Integration

- [x] Streamlit user and owner views
- [x] Integration tests (Agent → Backend → ML → Engines → Dashboard)

## Phase 6 — Hardening (Future)

- [ ] PostgreSQL migration
- [ ] MITRE ATT&CK rule expansion
- [ ] Production deployment and monitoring
- [ ] Extended enrollment UX (7–10 day baseline)
