# API Contract

## Base URL

`/api/v1`

## Endpoints

### POST /analyze

**Input:** `FeatureVector`

**Output:** `AnalyzeResponse`

Runs ML inference, trust scoring, risk scoring, response evaluation, and persistence.

---

### GET /trust/{user_id}

**Output:**

- `identity_trust` (0–100)
- `status_level` (NORMAL | ELEVATED | SUSPICIOUS | HIGH_RISK | CRITICAL)

---

### GET /risk/{user_id}

**Output:**

- `activity_risk` (0–100)

---

### GET /alerts/{user_id}

**Output:** `AlertResponse[]`

---

### GET /history/{user_id}

**Output:** Historical trust and risk scores

---

### POST /reauth

**Input:** Reauthentication payload

**Output:**

- `success` (bool)
- `message` (string)

---

### GET /session/{user_id}

**Output:** Current session information

## Rules

- Never break existing endpoints
- Use Pydantic for all request/response models
- Structured JSON only
- Business logic in services, not routes
