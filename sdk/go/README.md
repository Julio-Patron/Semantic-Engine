# ses-go — Official Go SDK for Semantic Engine

Official zero-dependency Go client library (standard library only) for **SES (Semantic Engine)**. Designed for high-throughput backend microservices and enterprise pipelines.

---

## Installation

```bash
go get github.com/elbuilder77/Semantic-Engine/sdk/go
```

---

## Quickstart

### 1. Semantic Search & RAG Answer Generation

```go
package main

import (
	"context"
	"fmt"
	"log"
	"os"

	ses "github.com/elbuilder77/Semantic-Engine/sdk/go"
)

func main() {
	client, err := ses.NewClient(ses.ClientConfig{
		BaseURL: "http://localhost:8000",
		APIKey:  os.Getenv("SES_API_KEY"),
	})
	if err != nil {
		log.Fatal(err)
	}

	ctx := context.Background()
	resp, err := client.Search(ctx, ses.SearchRequest{
		Namespace:      "contracts",
		Query:          "What are the confidentiality obligations?",
		TopK:           5,
		GenerateAnswer: true,
	})
	if err != nil {
		log.Fatal(err)
	}

	if resp.Answer != nil {
		fmt.Printf("Answer: %s\n", *resp.Answer)
	}
	for _, hit := range resp.Results {
		fmt.Printf("[%.2f] %s\n", hit.Score, hit.Text)
	}
}
```

### 2. Ingest Text & Document Streams

```go
file, err := os.Open("agreement.pdf")
if err != nil {
	log.Fatal(err)
}
defer file.Close()

res, err := client.IngestFile(ctx, "contracts", "agreement.pdf", file, map[string]interface{}{
	"department": "legal",
})
```

---

## Licensing

Distributed under the `GPL-3.0-only` license. See [LICENSE](../../LICENSE).
