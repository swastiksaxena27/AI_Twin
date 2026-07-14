# Team Playbook

## Roles and Boundaries

| Role | Scope | Must Not |
|------|-------|----------|
| Database Engineer | `database/` | Modify other modules |
| Agent Engineer | `agent/` | Store typed text |
| ML Engineer | `ml/` | Online learning |
| Trust Engineer | `engines/trust_engine/` | Execute actions |
| Risk Engineer | `engines/risk_engine/` | Perform ML |
| Response Engineer | `engines/response_engine/` | Compute trust or risk |
| Backend Engineer | `backend/` | Business logic in routes |
| Dashboard Engineer | `dashboard/` | Scoring inside UI |
| Test Engineer | `tests/` | Skip new module tests |
| Integration Engineer | Wiring only | Rewrite module internals |

## Workflow

1. Read the engineering constitution before any change
2. Preserve contracts (API, schema, feature names)
3. Write tests alongside new modules
4. Run the full test suite before merge
5. Code review against constitution checklist

## Code Review Checklist

- Architecture violations
- Naming violations
- Contract violations
- Missing type hints, docstrings, logging
- Hardcoded values
- Monolithic files
- Missing tests
- `print()` statements
- Direct database access from UI

## Integration Order

Database → Backend → Agent → ML → Trust → Risk → Response → Dashboard

Preserve contracts. No breaking changes.
