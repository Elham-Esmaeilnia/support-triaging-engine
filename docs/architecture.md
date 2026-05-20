## System Processing Flow

The diagram below illustrates the end‑to‑end ticket processing pipeline.
```text
┌──────────────────┐
│    Raw Ticket    │
└────────┬─────────┘
         │
         ▼
┌──────────────────────────────────────┐
│          Context Optimization        │
│  • Rule-based cleanup                │
│  • Noise removal / trimming          │
│  • Optional LLM-assisted compression │
└────────┬─────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────┐
│         Semantic Cache Lookup        │
│  • Generate embedding                │
│  • Cosine similarity search          │
│  • Threshold check (0.85)            │
└────────┬─────────────────────────────┘
         │
   ┌─────┴───────────────┐
   │                     │
   ▼                     ▼
┌───────────────┐   ┌────────────────────────────────┐
│   Cache Hit   │   │       LLM Orchestration        │
│               │   │  • Prompt construction         │
│ Return cached │   │  • Model inference             │
│ analysis      │   │  • Structured output parsing   │
└───────┬───────┘   │  • Output validation + retry   │
        │           └───────────────┬────────────────┘
        │                           │
        └───────────────┬───────────┘
                        ▼
┌────────────────────────────┐
│     Cache Insert + Reply   │
│  • Store embedding         │
│  • Store analysis result   │
│  • Return final response   │
└────────────────────────────┘
```
## Flow Description

1. Raw Ticket Intake

The system receives the incoming support ticket via the API layer.

2. Context Optimization

The ticket is cleaned and optionally compressed to reduce noise while preserving intent.

3. Semantic Cache Lookup

The ticket embedding is generated and compared against cached embeddings using cosine similarity.

- If similarity ≥ 0.85 → cache hit
- Otherwise → cache miss
4. LLM Orchestration (on Miss)

The orchestrator builds the prompt, calls the LLM, validates structured output, and applies retry logic if necessary.

5. Cache Insert and Response

The result is stored in the semantic cache and returned to the caller.