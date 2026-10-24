# SES Enterprise Admin Portal

The **SES Enterprise Admin Portal** (`portal/`) is a modern Next.js 16 web application for managing the **SES Enterprise Gateway**, monitoring service health, executing RAG queries, managing multi-tenant API keys, and exporting corporate PDF audit reports.

---

## Key Features & Routes

- **`/dashboard`** — Real-time cluster health status (Gateway, Qdrant, Redis, Ollama) and request metrics.
- **`/search`** — Interactive RAG search console with Rust acceleration indicators and 1-click Evidence PDF export.
- **`/documents`** — Drag-and-drop document upload (`PDF`, `DOCX`, `XLSX`, `CSV`, `TXT`, `MD`), namespace inspection, and deletion.
- **`/keys`** — Multi-tenant API key provisioning, namespace assignment, rate-limit configuration, and instant revocation.
- **`/analytics`** — Request volume, error rate, latency telemetry, and per-key usage breakdown.
- **`/reports`** — Instant generation and download of Corporate Usage and System Health PDF dossiers.
- **`/settings`** — Browser-side Gateway URL and API key connection management (`localStorage`).

---

## Zero-Code White-Label Configuration

Customize the Portal's brand identity via environment variables without modifying React components:

```ini
NEXT_PUBLIC_BRAND_NAME=ACME AI Portal
NEXT_PUBLIC_BRAND_EDITION=Enterprise Suite
NEXT_PUBLIC_PORTAL_TITLE=ACME AI | Document Intelligence Console
NEXT_PUBLIC_SES_API_URL=http://localhost:8000
```

---

## Development & Production Build

```bash
# Install dependencies
npm ci --prefix portal

# Run development server on http://127.0.0.1:3000
npm --prefix portal run dev -- --hostname 127.0.0.1 --port 3000

# Run test suite and production build
npm --prefix portal run test
npm --prefix portal run build
```
