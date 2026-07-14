"""Vercel serverless function entry point.

Vercel's @vercel/python runtime looks for an `app` variable that is an
ASGI application.  We just re-export the FastAPI instance that is already
fully configured in the main backend module.

Because this file lives at  api/index.py  relative to the project root,
we need the project root on sys.path so that `behavioral_guardian.*`
imports resolve correctly.
"""

import sys
from pathlib import Path

# Add the project root (one level up from api/) to the Python import path.
_project_root = str(Path(__file__).resolve().parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from behavioral_guardian.backend.main import app  # noqa: E402  (import after path fix)

# Vercel picks up the `app` variable automatically as an ASGI application.
