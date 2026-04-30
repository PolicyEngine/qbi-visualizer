# Deployment

Frontend on Vercel, backend on Modal.

## Backend (Modal)

1. Install the Modal CLI and authenticate (one-time):

   ```bash
   pip install modal
   modal token new
   ```

2. Deploy:

   ```bash
   cd backend
   modal deploy modal_app.py
   ```

   Modal prints a URL like
   `https://<workspace>--qbi-visualizer-backend-web.modal.run`. Copy it.

3. Lock down CORS to your Vercel domain (optional but recommended):

   ```bash
   modal secret create qbi-visualizer-cors \
     CORS_ORIGINS=https://<your-vercel-domain>.vercel.app
   ```

   Then add `secrets=[modal.Secret.from_name("qbi-visualizer-cors")]` to
   the `@app.function(...)` decorator in `modal_app.py` and re-deploy.

## Frontend (Vercel)

1. Update `vercel.json` at the repo root: replace
   `REPLACE-WITH-MODAL-URL.modal.run` with the Modal URL from above.

2. Commit and push.

3. Connect the repo to Vercel (one-time): from the Vercel dashboard,
   "Add New… → Project", import this repo. Leave the Vercel build
   settings on defaults — `vercel.json` overrides them.

   Or via CLI:

   ```bash
   npm i -g vercel
   vercel link
   vercel --prod
   ```

## Updating

- Backend changes: `cd backend && modal deploy modal_app.py`. The Modal
  URL is stable across deploys, so the Vercel rewrite keeps working.
- Frontend changes: just `git push` — Vercel rebuilds automatically.
