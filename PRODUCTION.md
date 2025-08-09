## Production Readiness Checklist (MVP)

This checklist captures the gaps identified for launching the MVP to production without any local storage.

### High-priority blockers (fix before launch)
- Secrets in repo [DONE]
  - ✅ `api/.env` is not in git (verified - properly gitignored)
  - Configure all secrets via deployment environment variables.
- Vector DB uses local disk [DONE]
  - ✅ Switch to managed Qdrant: set `QDRANT_MODE=cloud`, provide `QDRANT_URL` and `QDRANT_API_KEY`.
  - ✅ Remove tracked local data at `api/qdrant_storage/` and ignore it going forward.
- PDFs written to filesystem
  - Stop writing to `project/data/` and any local paths.
  - Store PDFs in object storage (e.g., S3/R2/Supabase) and keep URLs.
  - Vectorize from bytes or remote URL, not a local file path.
- Hardcoded localhost URLs in frontend
  - Replace direct `fetch('http://localhost:8000/...')` with centralized endpoints from `frontend/src/config/api.ts`.
  - Honor `NEXT_PUBLIC_API_URL` for production.
- CORS for Vercel previews
  - Replace wildcard string with regex: `allow_origin_regex=r"https://.*\\.vercel\\.app"`, and include your prod domain explicitly.
- Route path double-prefix risk
  - Avoid `/api/api/...` mismatches. Use empty `root_path` in production and keep router prefixes as `"/api"`, aligned with platform routing.

### Medium-priority (strongly recommended)
- Enforce upload size (e.g., 10MB) server-side; validate content-type.
- Serverless/runtime limits
  - Long FDA calls and vectorization may exceed serverless timeouts. Prefer Fly.io (already referenced) or configure Vercel function limits appropriately.
  - If using Fly.io for API, remove redundant Vercel Python build to avoid confusion.
- Observability and resilience
  - Add Sentry (backend + frontend), structured logs, retries with backoff on external calls.
- Rate limiting for heavy endpoints to prevent abuse.
- Deployment consistency and CI
  - Choose one API host; pin deps; add CI for lint/tests.

### Concrete changes to implement
- Backend storage config
  - `api/config/settings.py`: ensure `QDRANT_MODE` sourced from env; document required envs.
  - Remove and ignore local data: `api/qdrant_storage/`.
- PDF persistence refactor (no local disk)
  - `api/services/predicate_discovery_service.py`:
    - Remove `self.data_dir` and all disk writes.
    - On download, upload bytes to object storage; persist returned URL.
    - Add/route flows that vectorize from bytes or fetched remote URL.
  - `api/core/vector_store.py`:
    - Add helper to load PDFs from bytes (use temporary in-memory or ephemeral temp files only during request lifecycle).
- Frontend API calls
  - Replace all `http://localhost:8000/...` occurrences with `API_ENDPOINTS` from `frontend/src/config/api.ts` in:
    - `frontend/src/app/page.tsx`
    - `frontend/src/app/predicate-search/page.tsx`
    - `frontend/src/components/FileUpload.tsx`
- CORS
  - In `api/main.py`, use `allow_origin_regex` for Vercel previews and explicitly allow your production domain.
- Root path
  - In `api/main.py`, set `root_path=""` for production; keep router prefixes as `"/api"`. Ensure platform routing (e.g., `vercel.json` or Fly.io) maps to those paths.
- Secrets hygiene
  - Remove `api/.env` from repo, rotate keys, and configure **only** via env vars in your deployment platform.

### Environment variables to set (production)
- Backend
  - `OPENAI_API_KEY`
  - `QDRANT_MODE=cloud`
  - `QDRANT_URL`
  - `QDRANT_API_KEY`
  - `LANGCHAIN_TRACING_V2` ("true"/"false"), `LANGCHAIN_PROJECT`, `LANGSMITH_API_KEY` (optional)
  - `ENVIRONMENT=production`, `DEBUG=false`
- Frontend
  - `NEXT_PUBLIC_API_URL` (points to deployed API, e.g., Fly.io URL)
- Optional
  - `SENTRY_DSN` (frontend and backend)

### Post-change validation
- Secrets are not in git; keys rotated and set in env.
- API connects to Qdrant Cloud and initializes collections successfully.
- CORS allows production domain and Vercel previews (via regex).
- Frontend calls use `API_BASE_URL` and succeed in production.
- End-to-end flows work:
  - Upload PDF → summary → intended use → analysis
  - Predicate search → IFU extraction → equivalence check

### Items to remove from repository
- `api/.env` (and any other committed secrets)
- `api/qdrant_storage/` (local vector store files)
