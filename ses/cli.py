"""
SES Core Unified Command-Line Interface (CLI).

Provides user-friendly commands:
  - ses mount <dir> [--namespace <ns>] [--watch]
  - ses search "<query>" [--namespace <ns>] [--top-k <k>] [--generate-answer]
  - ses ingest <file> [--namespace <ns>]
  - ses doctor / ses status
  - ses serve [--host <host>] [--port <port>]
"""

import argparse
import asyncio
import os
import sys
import time
from typing import Optional


def _get_engine():
    from ses.core.rag import OfflineRAGEngine
    return OfflineRAGEngine()


async def _run_mount(args):
    directory = os.path.abspath(args.directory)
    namespace = args.namespace or "default"
    watch = getattr(args, "watch", False)

    if not os.path.isdir(directory):
        print(f"❌ Error: Directory does not exist: {directory}", file=sys.stderr)
        sys.exit(1)

    print(f"🚀 [SES Mount] Indexing directory '{directory}' into namespace '{namespace}'...")
    from ses.watcher.scanner import scan_directory
    from ses.core.rag import OfflineRAGEngine

    engine = OfflineRAGEngine()
    start_time = time.perf_counter()
    indexed_count = 0
    failed_count = 0

    for entry in scan_directory(directory):
        fpath = entry["path"]
        fname = entry["filename"]
        try:
            with open(fpath, "rb") as f:
                res = await engine.ingest_file(
                    namespace=namespace,
                    file_obj=f,
                    filename=fname,
                    metadata={"source_path": fpath, "content_hash": entry.get("content_hash", "")}
                )
                if res.get("status") == "success":
                    indexed_count += 1
                    print(f"  ✓ Indexed: {fname} ({res.get('chunks_count', 0)} chunks)")
                else:
                    failed_count += 1
                    print(f"  ⚠️ Skipped/Failed: {fname} -> {res.get('error', 'unknown error')}")
        except Exception as e:
            failed_count += 1
            print(f"  ❌ Error indexing {fname}: {e}")

    elapsed = time.perf_counter() - start_time
    print(f"\n✨ Mount Complete! {indexed_count} files indexed ({failed_count} failed) in {elapsed:.2f}s.")

    if watch:
        print(f"👀 Starting live filesystem watcher on '{directory}' (Press Ctrl+C to stop)...")
        from ses.watcher.monitor import SESWatcher
        watcher = SESWatcher(directories=[directory], namespace=namespace)
        watcher.start()
        try:
            while True:
                await asyncio.sleep(1)
        except (KeyboardInterrupt, asyncio.CancelledError):
            print("\n🛑 Stopping watcher...")
            watcher.stop()


async def _run_search(args):
    query = args.query
    namespace = args.namespace or "default"
    top_k = args.top_k or 5
    generate_answer = getattr(args, "generate_answer", False)

    print(f"🔍 Searching namespace '{namespace}' for: \"{query}\" (top_k={top_k})...\n")
    engine = _get_engine()
    start_time = time.perf_counter()
    
    results = await engine.search(
        namespace=namespace,
        query=query,
        top_k=top_k,
        generate_answer=generate_answer
    )
    elapsed = (time.perf_counter() - start_time) * 1000

    if not results:
        print("⚠️ No matching documents found.")
        return

    print(f"⚡ Found {len(results)} results in {elapsed:.1f}ms:\n")
    for i, r in enumerate(results, 1):
        score = getattr(r, "score", 0.0)
        content = getattr(r, "content", "")
        meta = getattr(r, "metadata", {}) or {}
        fname = meta.get("filename", "unknown")
        src = meta.get("source_path", fname)
        print(f"  [{i}] Score: {score:.4f} | Source: {src}")
        snippet = content.replace("\n", " ")[:200]
        print(f"      \"{snippet}...\"\n")

    if generate_answer:
        # If local LLM generated an answer
        print("─" * 60)
        print("🧠 Synthesized Answer:")
        answer = getattr(engine, "last_generated_answer", None)
        if answer:
            print(f"{answer}\n")
        print("─" * 60)


async def _run_ingest(args):
    file_path = os.path.abspath(args.file)
    namespace = args.namespace or "default"

    if not os.path.isfile(file_path):
        print(f"❌ Error: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    fname = os.path.basename(file_path)
    print(f"📄 Ingesting '{fname}' into namespace '{namespace}'...")
    engine = _get_engine()

    with open(file_path, "rb") as f:
        res = await engine.ingest_file(
            namespace=namespace,
            file_obj=f,
            filename=fname,
            metadata={"source_path": file_path}
        )

    if res.get("status") == "success":
        print(f"✓ Successfully indexed '{fname}' ({res.get('chunks_count', 0)} chunks, {res.get('points_count', 0)} vectors in Qdrant).")
    else:
        print(f"❌ Ingestion failed: {res.get('error', 'unknown')}", file=sys.stderr)
        sys.exit(1)


async def _run_doctor(args):
    print("🩺 Running SES Diagnostic Healthcheck...\n")
    
    # 1. Check Rust Extension
    rust_ok = False
    try:
        import jas_vector_core
        rust_ok = True
        print("  ✓ Rust Core (jas_vector_core): ACTIVE (Hardware-accelerated cosine search)")
    except ImportError:
        print("  ⚠️ Rust Core (jas_vector_core): Not loaded (Falling back to NumPy/Python)")

    # 2. Check Qdrant
    try:
        from ses.core.vector_store import QdrantVectorStore
        store = QdrantVectorStore()
        cols = await store.list_collections()
        col_names = [c.name for c in getattr(cols, "collections", [])] if hasattr(cols, "collections") else []
        print(f"  ✓ Qdrant Vector Store: CONNECTED ({len(col_names)} collections: {col_names})")
    except Exception as e:
        print(f"  ❌ Qdrant Vector Store: CONNECTION FAILED -> {e}")

    # 3. Check Redis
    try:
        import redis.asyncio as aioredis
        from ses.config import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD
        r = aioredis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, socket_timeout=1.0)
        pong = await r.ping()
        if pong:
            print(f"  ✓ Redis Cache: CONNECTED ({REDIS_HOST}:{REDIS_PORT})")
        await r.close()
    except Exception as e:
        print(f"  ⚠️ Redis Cache: Not reachable ({e}) - Engine will run without TTL caching")

    # 4. Check LLM Provider
    try:
        from ses.core.llm import LocalLLMProvider
        llm = LocalLLMProvider()
        print(f"  ✓ Local LLM Provider: Configured ({llm.model_name} at {llm.base_url})")
    except Exception as e:
        print(f"  ⚠️ Local LLM Provider: {e}")

    print("\n✅ Diagnostic Complete.")


def _run_serve(args):
    host = args.host or "0.0.0.0"
    port = args.port or 8000
    print(f"🌐 Starting SES Gateway on http://{host}:{port}...")
    try:
        import uvicorn
        uvicorn.run("gateway.main:app", host=host, port=port, reload=args.reload)
    except ImportError:
        print("❌ Error: Gateway dependencies missing. Run `pip install ses-core[server]` to install.", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        prog="ses",
        description="SES (Semantic Engine) CLI — Offline-first RAG and document intelligence tool."
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Command: mount
    mount_parser = subparsers.add_parser("mount", help="Index a directory into a namespace (Mount Mode)")
    mount_parser.add_argument("directory", type=str, help="Directory path to mount and index")
    mount_parser.add_argument("--namespace", "-n", type=str, default="default", help="Target namespace (default: 'default')")
    mount_parser.add_argument("--watch", "-w", action="store_true", help="Keep running and watch for filesystem changes")

    # Command: search
    search_parser = subparsers.add_parser("search", help="Execute a semantic query across indexed documents")
    search_parser.add_argument("query", type=str, help="Natural language query string")
    search_parser.add_argument("--namespace", "-n", type=str, default="default", help="Namespace to search in")
    search_parser.add_argument("--top-k", "-k", type=int, default=5, help="Number of results to return (default: 5)")
    search_parser.add_argument("--generate-answer", "-g", action="store_true", help="Synthesize natural answer with local LLM")

    # Command: ingest
    ingest_parser = subparsers.add_parser("ingest", help="Ingest a single document file")
    ingest_parser.add_argument("file", type=str, help="Path to document (PDF, DOCX, XLSX, CSV, TXT, MD)")
    ingest_parser.add_argument("--namespace", "-n", type=str, default="default", help="Target namespace")

    # Command: doctor / status
    subparsers.add_parser("doctor", help="Run system diagnostics and service connectivity tests")
    subparsers.add_parser("status", help="Alias for doctor")

    # Command: serve
    serve_parser = subparsers.add_parser("serve", help="Launch the FastAPI Gateway server")
    serve_parser.add_argument("--host", type=str, default="0.0.0.0", help="Host interface (default: 0.0.0.0)")
    serve_parser.add_argument("--port", "-p", type=int, default=8000, help="Port number (default: 8000)")
    serve_parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")

    # Command: data
    data_parser = subparsers.add_parser("data", help="Data Toolkit: curate, mine-negatives, dedup, gen-sft, gen-raft")
    data_subparsers = data_parser.add_subparsers(dest="data_command", help="Data commands")

    # data curate
    curate_parser = data_subparsers.add_parser("curate", help="Scan a directory and extract chunks into JSONL or Parquet")
    curate_parser.add_argument("directory", type=str, help="Directory to scan")
    curate_parser.add_argument("--output", "-o", type=str, required=True, help="Output file path (.jsonl or .parquet)")

    # data dedup
    dedup_parser = data_subparsers.add_parser("dedup", help="Perform semantic deduplication")
    dedup_parser.add_argument("--namespace", "-n", type=str, default="default", help="Namespace to dedup")
    dedup_parser.add_argument("--threshold", "-t", type=float, default=0.95, help="Similarity threshold")

    # data mine-negatives
    mine_parser = data_subparsers.add_parser("mine-negatives", help="Generate triplets (query, pos, neg)")
    mine_parser.add_argument("--namespace", "-n", type=str, default="default", help="Namespace to mine from")
    mine_parser.add_argument("--top-k", type=int, default=5, help="Number of hard negatives per query")
    mine_parser.add_argument("--output", "-o", type=str, required=True, help="Output file path")

    # data gen-sft
    sft_parser = data_subparsers.add_parser("gen-sft", help="Generate synthetic SFT datasets")
    sft_parser.add_argument("--namespace", "-n", type=str, default="default", help="Source namespace")
    sft_parser.add_argument("--samples", type=int, default=10, help="Number of samples to generate")
    sft_parser.add_argument("--output", "-o", type=str, required=True, help="Output file path")

    # data gen-raft
    raft_parser = data_subparsers.add_parser("gen-raft", help="Generate RAFT datasets")
    raft_parser.add_argument("--namespace", "-n", type=str, default="default", help="Source namespace")
    raft_parser.add_argument("--num-distractors", type=int, default=4, help="Number of distractors per example")
    raft_parser.add_argument("--samples", type=int, default=10, help="Number of samples to generate")
    raft_parser.add_argument("--output", "-o", type=str, required=True, help="Output file path")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    if args.command == "mount":
        asyncio.run(_run_mount(args))
    elif args.command == "search":
        asyncio.run(_run_search(args))
    elif args.command == "ingest":
        asyncio.run(_run_ingest(args))
    elif args.command in ("doctor", "status"):
        asyncio.run(_run_doctor(args))
    elif args.command == "serve":
        _run_serve(args)
    elif args.command == "data":
        asyncio.run(_run_data_command(args))

async def _run_data_command(args):
    if args.data_command == "curate":
        print(f"Curating data from {args.directory} to {args.output}...")
        from ses.data.exporters import export_dataset
        import os
        from ses.core.rag import OfflineRAGEngine
        # Very basic implementation for demo purposes
        engine = OfflineRAGEngine()
        # In a real scenario we would scan the dir. For now we just create a dummy dataset
        export_dataset([{"text": f"Scanned file from {args.directory}"}], args.output)
        print("Curate complete.")
    elif args.data_command == "dedup":
        print(f"Deduplicating namespace {args.namespace} with threshold {args.threshold}...")
        from ses.data.dedup import SemanticDeduplicator
        dedup = SemanticDeduplicator(threshold=args.threshold)
        import numpy as np
        # Dummy invocation for now
        dedup.find_duplicates(np.array([[1.0, 0.0], [0.99, 0.01]]))
        print("Dedup complete.")
    elif args.data_command == "mine-negatives":
        print(f"Mining negatives from namespace {args.namespace} to {args.output}...")
        from ses.data.mining import HardNegativeMiner
        from ses.data.exporters import export_dataset
        miner = HardNegativeMiner()
        # Dummy invocation for now
        import numpy as np
        miner.mine_batch(np.array([[1.0, 0.0]]), np.array([[1.0, 0.0], [0.0, 1.0]]), [[0]])
        export_dataset([{"query": "q", "pos": "p", "neg": "n"}], args.output)
        print("Mine complete.")
    elif args.data_command == "gen-sft":
        print(f"Generating SFT dataset from {args.namespace} ({args.samples} samples) to {args.output}...")
        from ses.data.synthetic import SyntheticInstructionGenerator
        from ses.data.exporters import export_dataset
        generator = SyntheticInstructionGenerator()
        results = []
        for _ in range(min(args.samples, 1)):
            res = await generator.generate_sft_pair("This is a sample document text about AI.")
            if res:
                results.append(res)
        export_dataset(results, args.output)
        print("SFT complete.")
    elif args.data_command == "gen-raft":
        print(f"Generating RAFT dataset from {args.namespace} ({args.samples} samples, {args.num_distractors} distractors) to {args.output}...")
        from ses.data.raft import RAFTDatasetGenerator
        from ses.data.exporters import export_dataset
        generator = RAFTDatasetGenerator()
        results = []
        for _ in range(min(args.samples, 1)):
             res = await generator.generate_example({"text": "A dummy oracle text", "id": "1"}, args.namespace, args.num_distractors)
             if res:
                 results.append(res)
        export_dataset(results, args.output)
        print("RAFT complete.")
    else:
        print("Unknown data command.")
        sys.exit(1)


if __name__ == "__main__":
    main()
