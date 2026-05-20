## Project Structure

The repository is organized to separate API logic, core configuration, services, and documentation. This structure keeps the system modular and easier to maintain or extend.

```
engine-triaging-support/
│
├── src/
│   ├── api/
│   │   └── main.py              # FastAPI entrypoint
│   │
│   ├── core/
│   │   ├── config.py            # Env & settings
│   │   ├── logging.py
│   │   └── exceptions.py
│   │
│   ├── models/
│   │   └── ticket_schema.py     # Pydantic schema
│   │
│   ├── services/
│   │   ├── context_optimizer.py # Part 1
│   │   ├── llm_client.py        # LLM abstraction
│   │   ├── orchestrator.py      # Part 2 (LLM + retry)
│   │   └── semantic_cache.py    # Part 3
│   │
│   ├── prompts/
│   │   └── ticket_analysis.txt
│   │
│   ├── utils/
│   │   └── text.py
│   └─ logs/
│        └─ engine_triage.log
│
├── data/
│   └── cache/                   # FAISS storage
│
├── config/
│   └── settings.yaml
│
├── docs/
│   ├── architecture.md
│   ├── installation.md
│   ├── caching_strategy.md
│   └── vllm_deployment.md
│
├── scripts/
│   └── run_local.sh
│
├── README.md
├── requirements.txt
└── .env.example
```