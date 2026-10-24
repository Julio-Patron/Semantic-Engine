# @ses-ai/client — Official TypeScript / JavaScript SDK

Official TypeScript and JavaScript client library for **SES (Semantic Engine)**. Built with native `fetch` and zero external runtime dependencies for Node.js, Next.js, and browser environments.

---

## Installation

```bash
npm install @ses-ai/client
```

---

## Quickstart

### 1. Initialize Client

```typescript
import { SemanticEngineClient } from "@ses-ai/client";

const client = new SemanticEngineClient({
  baseUrl: process.env.SES_API_URL || "http://localhost:8000",
  apiKey: process.env.SES_API_KEY!,
});
```

### 2. Semantic Search & Local RAG Synthesis

```typescript
const response = await client.search({
  namespace: "legal_docs",
  query: "What is the termination notice period?",
  topK: 5,
  generateAnswer: true,
});

console.log("Synthesized Answer:", response.answer);
console.log("Evidence Sources:", response.results);
```

### 3. Ingest Text & Files

```typescript
import fs from "node:fs";

await client.ingestText({
  namespace: "legal_docs",
  text: "Agreements require 30 days written notice prior to termination.",
  metadata: { category: "MSA", year: 2026 },
});

await client.ingestFile({
  namespace: "legal_docs",
  file: fs.readFileSync("./contract.pdf"),
  filename: "contract.pdf",
});
```

### 4. Administrative & Telemetry Operations

```typescript
const newKey = await client.createApiKey("service_worker_01", "client");
const stats = await client.getAnalytics();
const health = await client.getHealth();
```

---

## Licensing

Distributed under the `GPL-3.0-only` license. See [LICENSE](../../LICENSE).
