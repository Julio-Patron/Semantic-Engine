# SES Enterprise Gateway

The **SES Enterprise Gateway** (`gateway/`) is a multi-tenant FastAPI server that exposes semantic search, document ingestion, API key lifecycle management, usage analytics, and corporate PDF audit report generation over HTTP.

---

## Architecture & Security Controls

- **Fail-Closed Authentication:** All protected routes require `X-API-Key`. Administrator operations require a high-entropy `GATEWAY_ADMIN_KEY` (minimum 32 characters).
- **One-Time Key Issuance & SHA-256 Storage:** Client API keys are displayed once upon creation and persisted exclusively as SHA-256 cryptographic hashes.
- **Namespace Isolation:** Every API key is bound to a dedicated vector namespace, isolating tenant queries and document collections.
- **Dual Database Persistence:** Supports embedded **SQLite** out of the box and **PostgreSQL (`asyncpg`)** for high-concurrency multi-tenant deployments (`POSTGRES_ENABLED=true`).
- **Distributed Rate Limiting:** Enforces per-key request quotas via Redis (`503 Service Unavailable` fail-closed behavior when `DEBUG=false`).

---

## Quickstart

```bash
# 1. Generate unique local secrets in .env
cp .env.example .env
python scripts/rotate_local_secrets.py

# 2. Start Qdrant, Redis, and Ollama
cp .env.compose.example .env.compose
docker compose --env-file .env.compose up -d

# 3. Launch the Gateway on http://127.0.0.1:8000
python gateway/run.py
```

Interactive OpenAPI documentation is available at `http://127.0.0.1:8000/docs`.

---

## Core API Endpoints

### Retrieval & Document Management (`X-API-Key` Required)
- `POST /api/v1/search` — Semantic vector search with automatic Rust re-ranking (`jas_vector_core`) and optional local LLM answer synthesis.
- `POST /api/v1/ingest/file` — Multipart file upload and indexing (`PDF`, `DOCX`, `XLSX`, `CSV`, `TXT`, `MD`).
- `POST /api/v1/ingest/text` — Direct raw text indexing with custom metadata.
- `GET /api/v1/documents` — List indexed documents in the active namespace.
- `DELETE /api/v1/documents/{doc_id}` — Remove a document and its vectors.
- `POST /api/v1/reports/evidence` — Generate a signed Corporate Evidence Audit PDF for a query and its retrieved sources.

### Health & Readiness Probes
- `GET /healthz` — Lightweight process liveness check.
- `GET /readyz` — Dependency readiness check across Qdrant, Redis, and Ollama.
- `GET /api/v1/health` — Detailed component status report.

### Administration (`Admin` Role Required)
- `GET /api/v1/admin/keys` — List registered tenant API keys.
- `POST /api/v1/admin/keys` — Provision a new API key with custom rate limit and namespace.
- `DELETE /api/v1/admin/keys/{key_id}` — Revoke an API key immediately.
- `GET /api/v1/admin/analytics` — Retrieve aggregated latency, volume, and per-key telemetry.
- `GET /api/v1/admin/reports/usage` — Download a tenant Usage & Billing Analytics PDF report.
- `GET /api/v1/admin/reports/health` — Download a System Health & Infrastructure PDF snapshot.
