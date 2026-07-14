# AI Behavioral Guardian Architecture

## Core Thesis

Authentication should not be a one-time event. Trust should be continuously evaluated.

## Data Flow

```
User
  ↓
Agent Layer
  ↓
Feature Extraction
  ↓
Local SQLite
  ↓
FastAPI Backend
  ↓
Digital Twin
  ↓
Identity Trust Engine + Activity Risk Engine
  ↓
Response Engine
  ↓
Explainability Engine
  ↓
Dashboard
```

## Components

### Agent Layer

**Purpose:** Collect behavioral data.

**Modules:** Keyboard, Mouse, Process, USB, Download, Network

**Output:** Feature Vector (every 30 seconds)

### Digital Twin

**Purpose:** Learn normal behavior.

**Model:** Isolation Forest (one model per user, static, 7–10 day training)

**Output:** Anomaly Score (0–1)

### Trust Engine

**Purpose:** Generate identity trust.

**Output:** `identity_trust` (0–100), status level

### Risk Engine

**Purpose:** Generate activity risk from rule-based signals.

**Output:** `activity_risk` (0–100), triggered rules, explanations

### Response Engine

**Purpose:** Take actions based on trust and risk levels.

**Outputs:** monitor, warn, reauth, kill_process, lock_workstation

### Explainability Engine

**Purpose:** Convert decisions into human-readable explanations.

### Dashboard

**Purpose:** Visualize trust and risk (Streamlit + Plotly).

## Integration Order

1. Database
2. Backend
3. Agent
4. ML
5. Trust Engine
6. Risk Engine
7. Response Engine
8. Dashboard
