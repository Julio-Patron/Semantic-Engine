# jas_vector_core

High-performance vector cosine similarity search and Top-K re-ranking engine written in Rust with zero-copy PyO3/NumPy bindings. Powers the **SES (Semantic Engine)** platform and operates as a standalone Rust crate.

[![Crates.io](https://img.shields.io/crates/v/jas_vector_core.svg)](https://crates.io/crates/jas_vector_core)
[![PyPI](https://img.shields.io/pypi/v/ses-core.svg)](https://pypi.org/project/ses-core/)
[![License](https://img.shields.io/badge/License-Dual%20(GPLv3%20%7C%20Commercial)-blue.svg)](https://github.com/elbuilder77/Semantic-Engine/blob/main/COMMERCIAL_LICENSE.md)

---

## Highlights

- **30x–36x Faster than Pure Python:** Delivers sub-millisecond cosine similarity scoring over 384-dimensional embedding batches (`0.52 ms` for 1,000 vectors; `2.43 ms` for 5,000 vectors).
- **Zero-Copy NumPy Integration:** Reads C-contiguous 1D and 2D `float32` NumPy arrays directly in memory without allocation overhead.
- **Standalone Rust API:** Clean, dependency-light slice API (`&[f32]`) with configurable score thresholds and partial Top-K sorting.

---

## Rust Usage

```toml
[dependencies]
jas_vector_core = "0.1"
```

```rust
use jas_vector_core::cosine_similarity_scores;

fn main() {
    let query = vec![1.0_f32, 0.0, 0.0];
    let docs = vec![
        vec![1.0_f32, 0.0, 0.0],
        vec![0.0_f32, 1.0, 0.0],
        vec![0.7_f32, 0.7, 0.0],
    ];

    let top_k = cosine_similarity_scores(&query, &docs, 2, Some(0.5)).unwrap();
    for (idx, score) in top_k {
        println!("Document #{idx} -> score: {score:.4}");
    }
}
```

---

## Python Usage (via `ses-core`)

```python
import numpy as np
import jas_vector_core

query = np.array([1.0, 0.0, 0.0], dtype=np.float32)
docs = np.array([[0.0, 1.0, 0.0], [1.0, 0.0, 0.0]], dtype=np.float32)

# Returns list of (doc_index, similarity_score) tuples
results = jas_vector_core.cosine_similarity_search_numpy(query, docs, top_k=5)
```

---

## Dual Licensing (GPL-3.0-only & Commercial Exemption)

`jas_vector_core` is distributed under a **Dual-License** model:

1. **Open Source (`GPL-3.0-only` — Free):** Free for open-source software complying with GPLv3 copyleft terms.
2. **Commercial Dual-License Exemption ($149 USD One-Time):** [Purchase via Stripe](https://buy.stripe.com/3cI14odkL9TS1Zy91ke3e00) — Perpetual license for 1 organization to link or embed `jas_vector_core` and `ses-core` in closed-source proprietary software without GPLv3 source disclosure obligations.
3. **Enterprise White-Label Suite ($299 USD One-Time):** [Purchase via Stripe](https://buy.stripe.com/cNi8wQ3KbaXW7jSb9se3e01) — Unlimited client deployments for agencies and consultancies + full SES Enterprise Gateway, Next.js 16 Portal, and White-Label PDF Audit Engine.

See [COMMERCIAL_LICENSE.md](https://github.com/elbuilder77/Semantic-Engine/blob/main/COMMERCIAL_LICENSE.md) for complete legal terms.
