"""Vercel serverless function entry point with import error diagnostics.

If the import of the main backend app fails, this diagnostic wrapper catches
the traceback and returns it as a plain-text HTTP 500 response, making it
easy to debug import/startup issues in the serverless environment.
"""

import sys
from pathlib import Path
import traceback

# Add the project root (one level up from api/) to the Python import path.
_project_root = str(Path(__file__).resolve().parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

app = None
import_error = None

try:
    from behavioral_guardian.backend.main import app as real_app
    app = real_app
except Exception as e:
    import_error = traceback.format_exc()

if import_error:
    async def app(scope, receive, send):
        if scope['type'] == 'http':
            response_body = f"Vercel Startup/Import Error Traceback:\n\n{import_error}".encode('utf-8')
            await send({
                'type': 'http.response.start',
                'status': 500,
                'headers': [
                    (b'content-type', b'text/plain; charset=utf-8'),
                ]
            })
            await send({
                'type': 'http.response.body',
                'body': response_body,
            })
