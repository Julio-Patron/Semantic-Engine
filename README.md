<div align="center">
  <h1>SES — Semantic Engine</h1>
  <p><strong>Enterprise Offline-First RAG Engine, Read-Only Document Indexer &amp; Rust-Accelerated Vector Search Platform</strong></p>

  [![PyPI](https://img.shields.io/pypi/v/ses-core.svg)](https://pypi.org/project/ses-core/)
  [![Crates.io](https://img.shields.io/crates/v/jas_vector_core.svg)](https://crates.io/crates/jas_vector_core)
  [![Python](https://img.shields.io/badge/Python-3.9--3.12-blue.svg)](https://www.python.org)
  [![CI](https://github.com/elbuilder77/Semantic-Engine/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/elbuilder77/Semantic-Engine/actions/workflows/ci.yml)
  [![License](https://img.shields.io/badge/License-Dual%20(GPLv3%20%7C%20Commercial)-blue.svg)](COMMERCIAL_LICENSE.md)

  <p>
    <a href="https://elbuilder77.github.io/Semantic-Engine/">Official Website</a> •
    <a href="#quickstart">Quickstart</a> •
    <a href="#enterprise-deployment">Enterprise Stack</a> •
    <a href="#official-sdks">SDKs</a> •
    <a href="#commercial-licensing--white-label-editions">Commercial Licensing</a>
  </p>
</div>

---

## Overview

**SES (Semantic Engine)** is a self-hosted, air-gapped document intelligence and Retrieval-Augmented Generation (RAG) platform built for organizations that require strict data sovereignty. It indexes local folders and network shares in **read-only Mount Mode**, accelerates high-density vector re-ranking with a native **Rust/PyO3 core (`jas_vector_core`)**, and serves multi-tenant applications through a **FastAPI Gateway**, **Next.js 16 Admin Portal**, and **Audit-Ready PDF Evidence Engine**.

### Key Capabilities

- **Non-Intrusive Read-Only Mount Mode:** Connects directly to existing local directories and SMB/NAS shares (`PDF`, `DOCX`, `XLSX`, `CSV`, `TXT`, `MD`) with SHA-256 delta detection and full `source_path` provenance—without moving or altering source files.
- **36x Rust Vector Acceleration (`jas_vector_core`):** Zero-copy NumPy memory views over C-contiguous float32 buffers deliver sub-millisecond cosine similarity search and Top-K re-ranking.
- **Fail-Closed Multi-Tenant Gateway:** FastAPI service with SHA-256 hashed API keys, namespace isolation, Redis rate limiting, and dual SQLite / PostgreSQL (`asyncpg`) persistence.
- **White-Label Corporate PDF Audit Reports:** Generates verifiable Evidence, Usage, and Health PDF dossiers with relevance score bars, SHA-256 chunk hashes, watermarks, and zero-code `.env` branding.
- **Next.js 16 Admin Portal & Official SDKs:** Ready-to-deploy web console plus zero-dependency client SDKs for **TypeScript/JavaScript** and **Go**.

---

## Architecture

```text
Read-Only Document Stores (Local / NAS / SMB)
        │
        ▼
Mount Mode Scanner (SHA-256 Delta) ──► Document Parser & Semantic Chunker
                                                        │
                                                        ▼
Next.js 16 Admin Portal ──► FastAPI Enterprise Gateway ──► Qdrant / Redis / Ollama
                                        │
                                        ├── PyO3 Rust Vector Core (jas_vector_core)
                                        ├── Corporate PDF Evidence & Audit Engine
                                        └── Multi-Tenant API Keys & Telemetry
```

---

## Quickstart

### 1. Install from PyPI

```bash
pip install ses-core
```

### 2. Command-Line Interface (`ses`)

```bash
# Index a directory in read-only Mount Mode
ses mount ./contracts --namespace legal

# Run a semantic query with local LLM synthesis
ses search "termination notice requirements" --namespace legal --generate-answer

# Verify service connectivity (Qdrant, Redis, Ollama, Rust Core)
ses doctor
```

### 3. Python SDK

```python
import asyncio
import ses

async def main():
    await ses.mount("./contracts", namespace="legal")
    response = await ses.search(
        query="What are the confidentiality obligations?",
        namespace="legal",
        top_k=5,
        generate_answer=True,
    )
    print(response["answer"])

asyncio.run(main())
```

---

## Enterprise Deployment

Deploy the full production stack (**FastAPI Gateway**, **Next.js 16 Admin Portal**, **Qdrant**, **Redis**, and **Ollama**) with cryptographically generated secrets:

```bash
# 1. Generate production environment configuration (.env.prod)
python scripts/deploy_production.py

# 2. Launch the isolated container stack
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d --build
```

- **Admin Portal:** `http://127.0.0.1:3000`
- **Enterprise Gateway & OpenAPI Docs:** `http://127.0.0.1:8000/docs`

---

## Official SDKs

### TypeScript / JavaScript (`@ses-ai/client`)

```typescript
import { SemanticEngineClient } from "@ses-ai/client";

const client = new SemanticEngineClient({
  baseUrl: "http://localhost:8000",
  apiKey: process.env.SES_API_KEY!,
});

const result = await client.search({
  namespace: "legal",
  query: "termination clause",
  generateAnswer: true,
});
```

### Go (`ses-go`)

```go
import ses "github.com/elbuilder77/Semantic-Engine/sdk/go"

client, _ := ses.NewClient(ses.ClientConfig{
    BaseURL: "http://localhost:8000",
    APIKey:  os.Getenv("SES_API_KEY"),
})

resp, _ := client.Search(ctx, ses.SearchRequest{
    Namespace:      "legal",
    Query:          "termination clause",
    GenerateAnswer: true,
})
```

---

## Module Documentation

| Component | Description | Documentation |
| :--- | :--- | :--- |
| **Rust Vector Core** | Standalone Rust crate & PyO3 zero-copy vector engine | [core_rs/README.md](core_rs/README.md) |
| **Enterprise Gateway** | Multi-tenant FastAPI server, auth, and PDF report endpoints | [gateway/README.md](gateway/README.md) |
| **Admin Portal** | Next.js 16 management console & white-label configuration | [portal/README.md](portal/README.md) |
| **Mount Mode** | Non-intrusive read-only indexing & delta sync specification | [docs/MOUNT_MODE.md](docs/MOUNT_MODE.md) |
| **TypeScript SDK** | Client library for Node.js, Next.js, and web apps | [sdk/typescript/README.md](sdk/typescript/README.md) |
| **Go SDK** | Standard-library Go client for backend microservices | [sdk/go/README.md](sdk/go/README.md) |

---

## Commercial Licensing & White-Label Editions

SES is distributed under a **Dual-License** model. Choose the license that matches your deployment:

| Feature / Right | Community Edition (`$0`) | Commercial License (`$149 USD`) | Enterprise White-Label Kit (`$299 USD`) |
| :--- | :---: | :---: | :---: |
| **License Terms** | **GPL-3.0-only** (Open-Source Copyleft) | **Perpetual Commercial Exemption** (1 Org) | **Perpetual Agency / Multi-Client License** |
| **Closed-Source / Proprietary Use** | ❌ Requires disclosing source under GPLv3 | ✅ **Permitted (No GPLv3 obligations)** | ✅ **Permitted across unlimited clients** |
| **White-Label Branding (`.env`)** | ❌ | Internal use | ✅ **Rebrand PDF Reports & Next.js Portal** |
| **Turnkey Enterprise Stack** | Core + CLI | Core + Gateway + SDKs | **Full Stack + White-Label Quickstart Kit** |
| **Payment & Support Model** | Free / Community | **One-Time Payment** (*Provided As-Is*) | **One-Time Payment** (*Provided As-Is*) |

- **Option 1 — Commercial Dual-License ($149 USD):** [Purchase via Stripe Checkout](https://buy.stripe.com/3cI14odkL9TS1Zy91ke3e00)
- **Option 2 — Enterprise White-Label Boilerplate & Agency Kit ($299 USD):** [Purchase via Stripe Checkout](https://buy.stripe.com/cNi8wQ3KbaXW7jSb9se3e01)

See [COMMERCIAL_LICENSE.md](COMMERCIAL_LICENSE.md) for complete legal terms.
