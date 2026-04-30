"""Modal deployment wrapper for the QBI Visualizer FastAPI backend.

Deploy with:

    cd backend
    pip install modal
    modal token new            # first-time auth
    modal deploy modal_app.py

Modal prints a URL like
    https://<workspace>--qbi-visualizer-backend-web.modal.run
that the Vercel rewrite in `/vercel.json` should point at.
"""

from pathlib import Path

import modal

ROOT = Path(__file__).parent

# policyengine-us pulls in numpy / pandas / numba / a fair amount of US
# tax / benefit data. The image is large, so we let Modal cache it.
image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0",
        "pydantic>=2.0.0",
        "pydantic-settings>=2.0.0",
        "python-dotenv>=1.0.0",
        "policyengine-us>=1.653.3",
    )
    .add_local_dir(ROOT / "app", remote_path="/root/app")
)

app = modal.App("qbi-visualizer-backend", image=image)


@app.function(
    timeout=120,
    # Bump to min_containers=1 if cold starts become annoying. PolicyEngine
    # imports take ~5-10s, which dominates first-request latency.
)
@modal.asgi_app()
def web():
    from app.main import app as fastapi_app

    return fastapi_app
