# SES Enterprise White-Label Boilerplate — Quickstart Guide

Thank you for purchasing the **SES Enterprise White-Label Boilerplate & Agency Kit**.
This guide shows you how to rebrand the entire platform (**PDF Audit Reports**, **Enterprise Gateway**, and **Next.js 16 Admin Portal**) and deploy it on-premise for your clients in under 5 minutes without modifying core engine code.

---

## 1. Zero-Code Full-Stack Branding (`.env` / `.env.prod`)

Both the corporate PDF generator (`ses/core/reports.py`) and the Next.js 16 Admin Portal (`portal/`) support environment-driven white-labeling out of the box. Add the following variables to your `.env` or `.env.prod` file:

```ini
# --- PDF Audit Reports Branding ---
# Short 3-5 letter monogram rendered in the top-left badge of every PDF page
SES_BRAND_SHORT=ACME

# Footer organization name printed on every page of Evidence, Usage, and Compliance PDFs
SES_BRAND_FOOTER=ACME Legal Intelligence Platform

# --- Next.js 16 Admin Portal Branding ---
NEXT_PUBLIC_BRAND_NAME=ACME AI Portal
NEXT_PUBLIC_BRAND_EDITION=LegalTech Enterprise Suite
NEXT_PUBLIC_PORTAL_TITLE=ACME AI | Enterprise Document Intelligence
```

When your client opens the Portal, calls `POST /api/v1/reports/evidence`, or downloads Usage/Compliance bundles, both the UI and all generated PDFs will display your client's brand.

---

## 2. Advanced Portal Styling (`portal/`)

1. **Logo & Sidebar Layout:**
   - Open `portal/components/Sidebar.tsx` and `portal/app/layout.tsx` if you wish to replace the geometric vector mark with a custom SVG logo.
2. **Color Palette:**
   - Open `portal/app/globals.css` to adjust primary accent colors.

---

## 3. Turnkey 1-Click Production Deployment

All service images in `docker-compose.prod.yml` are pinned to immutable versions (`qdrant/qdrant:v1.18.3`, `redis:7.4.10-alpine`, `ollama/ollama:0.32.5`) to guarantee long-term stability without maintenance.

```powershell
# 1. Generate unique cryptographic secrets (.env.prod)
python scripts/deploy_production.py

# 2. (Optional) Add your white-label variables to .env.prod
Add-Content .env.prod "`nSES_BRAND_SHORT=YOURBRAND`nSES_BRAND_FOOTER=Your Company Name`nNEXT_PUBLIC_BRAND_NAME=Your Portal"

# 3. Launch the complete stack
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d --build
```

---

## 4. Enabling Multi-Tenant PostgreSQL (Optional)

By default, the Gateway uses an embedded SQLite database (`/data/gateway_state.db`). For high-concurrency multi-tenant deployments, enable the built-in `asyncpg` PostgreSQL adapter in `.env.prod`:

```ini
POSTGRES_ENABLED=true
POSTGRES_HOST=your-postgres-host
POSTGRES_PORT=5432
POSTGRES_DB=ses_gateway
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-secure-password
```

---

## 5. Commercial License Certificate

Your purchase includes perpetual **Tier 2 Commercial & Agency White-Label Rights** as detailed in `COMMERCIAL_LICENSE.md` and `SES_COMMERCIAL_LICENSE.pdf`. Retain your Stripe or Gumroad receipt as official proof of license for your organization and client deployments.
