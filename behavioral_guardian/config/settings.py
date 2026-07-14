"""Application configuration — single source of truth for constants."""

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"
MODELS_DIR = DATA_DIR / "models"

# Tests override this via the BEHAVIORAL_GUARDIAN_DATABASE_URL env var so they
# never read/write the real demo database. Unset in normal/dev use, so this
# is fully backward compatible.
DATABASE_URL = os.environ.get(
    "BEHAVIORAL_GUARDIAN_DATABASE_URL",
    f"sqlite:///{DATA_DIR / 'behavioral_guardian.db'}",
)

API_PREFIX = "/api/v1"
API_HOST = os.environ.get("BEHAVIORAL_GUARDIAN_API_HOST", "127.0.0.1")
API_PORT = int(os.environ.get("BEHAVIORAL_GUARDIAN_API_PORT", "8080"))
# Full override for hosted deployments (e.g. "https://your-app.onrender.com")
# — takes priority over API_HOST/API_PORT when set, and skips assuming http://.
API_BASE_URL_OVERRIDE = os.environ.get("BEHAVIORAL_GUARDIAN_API_BASE_URL", "")

# JWT auth. Override JWT_SECRET_KEY via env var in production — this default
# is only safe for local development.
JWT_SECRET_KEY = os.environ.get(
    "BEHAVIORAL_GUARDIAN_JWT_SECRET", "dev-only-secret-change-me-in-production-32bytes+"
)
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = 24

# Long-lived token for background services (the agent) — exchanged once for
# a normal 24h login token, then cached locally so the agent never has to
# ask for a password again until this expires.
JWT_DEVICE_TOKEN_EXPIRE_DAYS = 30

FEATURE_VECTOR_INTERVAL_SECONDS = 30
TRAINING_PERIOD_DAYS_MIN = 7
TRAINING_PERIOD_DAYS_MAX = 10

ANOMALY_SCORE_MIN = 0.0
ANOMALY_SCORE_MAX = 1.0
TRUST_SCORE_MIN = 0
TRUST_SCORE_MAX = 100
RISK_SCORE_MIN = 0
RISK_SCORE_MAX = 100

# Trust status thresholds (identity_trust)
TRUST_THRESHOLD_NORMAL = 80
TRUST_THRESHOLD_ELEVATED = 60
TRUST_THRESHOLD_SUSPICIOUS = 40
TRUST_THRESHOLD_HIGH_RISK = 20

# Response level thresholds (combined trust + risk)
RESPONSE_LEVEL_1_MAX_RISK = 25
RESPONSE_LEVEL_2_MAX_RISK = 50
RESPONSE_LEVEL_3_MAX_RISK = 70
RESPONSE_LEVEL_4_MAX_RISK = 85

# Trust engine tuning
TRUST_DECAY_RATE = 0.05
TRUST_RECOVERY_RATE = 0.02
TRUST_ANOMALY_WEIGHT = 0.7
TRUST_HISTORY_WEIGHT = 0.3

# Risk rule weights (frozen)
RISK_WEIGHT_UNKNOWN_PROCESS = 35
RISK_WEIGHT_POWERSHELL = 20
RISK_WEIGHT_CMD = 15
RISK_WEIGHT_USB_INSERTION = 30
RISK_WEIGHT_DOWNLOAD_SPIKE = 25
RISK_WEIGHT_ZIP_CREATION = 20
RISK_WEIGHT_NETWORK_UPLOAD_SPIKE = 30
RISK_WEIGHT_CHILD_PROCESS_EXPLOSION = 20
RISK_WEIGHT_CREDENTIAL_TOOLS = 50
RISK_WEIGHT_REGISTRY_PERSISTENCE = 40

DOWNLOAD_SPIKE_THRESHOLD_BYTES = 50_000_000
NETWORK_UPLOAD_SPIKE_THRESHOLD_BYTES = 25_000_000
CHILD_PROCESS_EXPLOSION_THRESHOLD = 15

FROZEN_FEATURE_NAMES = (
    "ks_dwell_mean",
    "ks_dwell_std",
    "ks_flight_mean",
    "ks_flight_std",
    "ks_wpm",
    "ks_error_rate",
    "ms_speed_mean",
    "ms_speed_std",
    "ms_click_rate",
    "ms_idle_ratio",
    "ap_unique_count",
    "ap_unknown_flag",
)

TRUST_STATUS_NORMAL = "NORMAL"
TRUST_STATUS_ELEVATED = "ELEVATED"
TRUST_STATUS_SUSPICIOUS = "SUSPICIOUS"
TRUST_STATUS_HIGH_RISK = "HIGH_RISK"
TRUST_STATUS_CRITICAL = "CRITICAL"

RESPONSE_ACTION_MONITOR = "monitor"
RESPONSE_ACTION_WARN = "warn"
RESPONSE_ACTION_REAUTH = "reauth"
RESPONSE_ACTION_KILL_PROCESS = "kill_process"
RESPONSE_ACTION_LOCK_WORKSTATION = "lock_workstation"

MODEL_FILENAME_ISOLATION_FOREST = "isolation_forest.pkl"
MODEL_FILENAME_SCALER = "scaler.pkl"
MODEL_FILENAME_BASELINE = "baseline.json"

LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
