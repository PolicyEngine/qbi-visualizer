"""Modal deployment wrapper for the QBI Visualizer FastAPI backend.

Deploy with:

    cd backend
    pip install modal
    modal token new            # first-time auth
    modal deploy modal_app.py

Modal prints a URL like
    https://<workspace>--qbi-visualizer-backend-web.modal.run
that the `/api` proxy rewrite in `frontend/next.config.ts` should point at.
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
        "slowapi>=0.1.9",
        # Pinned exactly: policyengine-us releases change tax parameters and
        # logic, so a floating floor would let deployed results drift between
        # image rebuilds. Bump deliberately (keep in sync with pyproject.toml).
        "policyengine-us==1.669.0",
    )
    .add_local_dir(ROOT / "app", remote_path="/root/app")
)

app = modal.App("qbi-visualizer-backend", image=image)


@app.function(
    timeout=120,
    # Keep warm containers around for 5 minutes after the last request —
    # PolicyEngine imports take ~5-10s, which dominates first-request latency.
    # Bump to min_containers=1 if cold starts become annoying.
    scaledown_window=300,
    # Cost cap: each container pays the full policyengine-us import and each
    # request burns real CPU-seconds, so bound how far a burst can scale out.
    max_containers=5,
)
@modal.asgi_app()
def web():
    from app.main import app as fastapi_app

    return fastapi_app
