# jas_vector_core

High-performance vector cosine similarity search and Top-K re-ranking engine written in Rust with zero-copy PyO3/NumPy bindings. Powers the **SES (Semantic Engine)** platform and operates as a standalone Rust crate.

[![Crates.io](https://img.shields.io/crates/v/jas_vector_core.svg)](https://crates.io/crates/jas_vector_core)
[![PyPI](https://img.shields.io/pypi/v/ses-core.svg)](https://pypi.org/project/ses-core/)
[![License](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://github.com/elbuilder77/Semantic-Engine/blob/main/LICENSE)

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

## License

GPL-3.0-only
