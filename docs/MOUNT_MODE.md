# SES Mount Mode — Non-Intrusive Document Indexing

**Mount Mode** is the core ingestion architecture of **SES (Semantic Engine)**. It connects directly to existing document repositories (local directories, NAS volumes, or SMB network shares) and builds a derived semantic index in Qdrant **without moving, duplicating, or modifying source files**.

---

## Core Design Principles

1. **Strict Read-Only Access:** Source files remain untouched in their original directory structure. SES opens files strictly in read-only stream mode.
2. **Full Physical Provenance (`source_path`):** Every indexed chunk preserves the absolute file path, filename, and SHA-256 content hash of its source document for audit-ready retrieval and PDF evidence generation.
3. **SHA-256 Delta Synchronization:** During initial scans and real-time file monitoring, SES computes cryptographic SHA-256 signatures and skips unchanged documents automatically.
4. **Atomic Manifest & Safe Re-Indexing:** When a document is updated, SES ingests the new version before removing superseded vectors and persists state atomically in `mount_manifest.json`.

---

## Processing Pipeline

```text
Read-Only Source Directory / SMB Share
  └──► Recursive Discovery (PDF, DOCX, XLSX, CSV, TXT, MD)
        └──► SHA-256 Delta Check (Skip Unchanged Files)
              └──► Text Extraction & Semantic Chunking
                    └──► Local Embedding Generation (384d)
                          └──► Qdrant Vector Index + Provenance Metadata
```

---

## Supported Formats

| Format | Extension | Extraction Engine |
| :--- | :--- | :--- |
| **PDF Documents** | `.pdf` | `pypdf` page-aware text extraction |
| **Word Documents** | `.docx` | `python-docx` paragraph & structural parser |
| **Excel Spreadsheets** | `.xlsx` | `openpyxl` multi-sheet tabular extractor |
| **Delimited Data** | `.csv` | Native streaming row parser |
| **Plain Text & Markdown** | `.txt`, `.md` | UTF-8 normalized text reader |

---

## CLI & Programmatic Usage

### Command Line

```bash
# Index a directory into a dedicated namespace
ses mount /data/corporate_contracts --namespace legal

# Index and keep watching for real-time file changes
ses mount /data/corporate_contracts --namespace legal --watch
```

### Python API

```python
import asyncio
import ses

async def main():
    results = await ses.mount("/data/corporate_contracts", namespace="legal")
    print(f"Processed {len(results)} files.")

asyncio.run(main())
```
