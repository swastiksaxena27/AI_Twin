# Engineering Constitution

## Principles

1. **Privacy First** — Never store typed text; only timings and metadata
2. **Explainability Over Complexity**
3. **Reliability Over Intelligence**
4. **Engineering Before AI**
5. **Response Before Restriction**
6. **Graceful Degradation**
7. **Static Digital Twin** — No online learning
8. **No Magic Constants** — All values in config
9. **Single Source Of Truth** — Config and contracts govern behavior

## Naming

| Element | Convention |
|---------|------------|
| Variables, functions, modules | `snake_case` |
| Classes | `PascalCase` |
| Constants | `UPPER_CASE` |

## Never

- `print()` — use logging
- Global variables
- Hardcoded paths
- Duplicate code
- Monolithic files
- Breaking API contracts
- Renaming frozen feature names or columns

## Always

- Type hints
- Docstrings
- Logging
- Error handling
- Pydantic (API layer)
- SQLAlchemy (database layer)
- Tests for new modules

## Technology Stack

- **Backend:** FastAPI
- **Database:** SQLite (SQLAlchemy ORM)
- **ML:** scikit-learn Isolation Forest, joblib persistence
- **Dashboard:** Streamlit, Plotly
- **Agent:** psutil, pynput, watchdog
