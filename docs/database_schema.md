# Database Schema

## Engine

- **Current:** SQLite
- **Future:** PostgreSQL compatible

## Tables

| Table | Purpose |
|-------|---------|
| `user` | Registered users |
| `device` | Devices linked to users |
| `feature_vector` | Behavioral feature snapshots |
| `trust_event` | Identity trust score history |
| `risk_event` | Activity risk score history |
| `triggered_rule` | Rules fired during risk evaluation |
| `response_event` | Actions taken by response engine |
| `alert` | User and owner alerts |
| `session` | Active and historical sessions |
| `explanation` | Human-readable decision explanations |
| `reauth_event` | Reauthentication attempts |
| `model_metadata` | ML model training metadata |

## Relationships

```
user
├── device
├── feature_vector
├── trust_event
├── risk_event
│   └── triggered_rule
├── response_event
├── session
├── alert
└── reauth_event
```

## Feature Names (Frozen)

- `ks_dwell_mean`, `ks_dwell_std`, `ks_flight_mean`, `ks_flight_std`
- `ks_wpm`, `ks_error_rate`
- `ms_speed_mean`, `ms_speed_std`, `ms_click_rate`, `ms_idle_ratio`
- `ap_unique_count`, `ap_unknown_flag`

## Conventions

- SQLAlchemy ORM
- Explicit relationships
- UTC timestamps
- Indexes on foreign keys and query columns
- No raw SQL unless necessary
