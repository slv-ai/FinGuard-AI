# FinGuard AI 🛡

**Agentic RAG system for AML fraud detection and regulatory compliance**

A production-grade AI system that automates the compliance officer workflow: takes a flagged suspicious transaction, investigates it using multi-step reasoning, retrieves applicable regulations, checks OFAC sanctions, and drafts a SAR — in under 10 seconds. Built with LangGraph, AWS Bedrock, and Qdrant.

---

## What it does

Financial institutions are legally required to investigate suspicious transactions and file Suspicious Activity Reports (SARs) within 30 days. This process is currently manual — a compliance officer spends 2–3 hours per case cross-referencing regulations, checking sanctions lists, and writing narratives.

FinGuard AI automates the entire investigation workflow with a 4-node agentic pipeline:

1. **Triage** — scores risk (0–1), classifies fraud type, routes high/low/escalate
2. **Investigator** — retrieves similar historical cases (RAG), screens OFAC SDN list (MCP), flags counterparty risk patterns
3. **Compliance** — hybrid RAG search over FinCEN/FFIEC/OCC regulations, identifies specific violations, determines SAR/CTR requirements
4. **Reporter** — drafts full SAR narrative with Five W's format and regulation citations

Human-in-the-loop: graph pauses before final disposition. Analyst reviews, edits, and approves/rejects via Streamlit dashboard.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Streamlit UI                          │
│     Pick flagged tx → Run agent → Review → Approve      │
└───────────────────────┬─────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────┐
│              LangGraph Agent (FinGuardState)             │
│                                                          │
│  triage → investigator → compliance → reporter           │
│     ↓           ↓              ↓           ↓            │
│  auto_close  [RAG+OFAC]   [RAG+rules]  [SAR draft]      │
│  escalate    [patterns]   [violations] [confidence]      │
│                                                          │
│  Human-in-the-loop interrupt before final_disposition    │
└─────────────┬─────────────────────────┬─────────────────┘
              │                         │
┌─────────────▼──────┐    ┌─────────────▼──────────────────┐
│   Qdrant (vector)   │    │   AWS Bedrock                  │
│                     │    │   Claude 3 Sonnet (LLM)        │
│  regulations        │    │   Titan Embeddings v2          │
│  transactions       │    │                                │
│  OFAC SDN           │    └────────────────────────────────┘
│  hybrid BM25+kNN    │
└────────────────────┘
              │
┌─────────────▼──────────────────────────────────────────────┐
│  Data sources                                               │
│  IEEE-CIS fraud dataset · PaySim · FinCEN/FFIEC PDFs        │
│  OFAC SDN list (Treasury.gov) · Synthetic cases             │
└────────────────────────────────────────────────────────────┘
```

---

## Tech stack

| Layer | Technology |
|---|---|
| Agent orchestration | LangGraph `StateGraph` with conditional edges |
| LLM | AWS Bedrock — Claude 3 Sonnet |
| Embeddings | AWS Bedrock — Titan Embeddings v2 (1024-dim) |
| Vector store | Qdrant — hybrid dense + sparse (BM25) search |
| RAG retrieval | Reciprocal Rank Fusion (RRF) over dense + sparse |
| MCP tools | Custom OFAC SDN screening server |
| API | FastAPI + Pydantic v2 |
| UI | Streamlit |
| Evaluation | RAGAS (faithfulness, answer recall, context precision) |
| Tracing | LangSmith |
| Monitoring | AWS CloudWatch custom metrics |
| CI/CD | GitHub Actions → pytest → RAGAS gate → EC2 deploy |
| Deploy | EC2 t3.medium + Docker Compose |
| Package manager | uv |

---

## Evaluation results

| Metric | Score | Threshold | Status |
|---|---|---|---|
| Faithfulness | 0.87 | ≥ 0.75 | ✅ Pass |
| Answer recall | 0.82 | ≥ 0.70 | ✅ Pass |
| Context precision | 0.79 | ≥ 0.65 | ✅ Pass |

RAGAS eval runs automatically in CI. Deploy is blocked if any metric falls below threshold.

---

## Performance

| Metric | Value |
|---|---|
| Avg processing time | ~4–8 seconds per case |
| Avg Bedrock tokens | ~1,800 per case |
| Avg cost per case | ~$0.04 |
| Fraud type coverage | structuring, wire fraud, money laundering, card fraud, account takeover |
| Regulation knowledge base | 6 FinCEN/FFIEC/OCC documents + synthetic corpus |
| OFAC SDN entries | 200+ real + 10 synthetic demo entries |

---

## Quickstart

### Prerequisites
- AWS account with Bedrock enabled (Claude 3 Sonnet + Titan Embeddings v2)
- Docker
- Python 3.11+
- uv (`curl -LsSf https://astral.sh/uv/install.sh | sh`)

### 1. Clone and install

```bash
git clone https://github.com/YOUR_USERNAME/finguard-ai.git
cd finguard-ai
uv sync
cp .env.example .env
# Fill in: AWS_REGION, LANGCHAIN_API_KEY, API_SECRET_KEY
```

### 2. Start Qdrant

```bash
docker run -d --name qdrant -p 6333:6333 qdrant/qdrant
```

### 3. Bootstrap data (embed + index everything)

```bash
python ingestion/qdrant_indexer.py --bootstrap
# Downloads regulations, generates transactions, embeds with Bedrock Titan,
# indexes into Qdrant. Takes ~5 min on first run.

# Test hybrid search is working:
python ingestion/qdrant_indexer.py --test
```

### 4. Run the UI

```bash
streamlit run ui/app.py
# Open http://localhost:8501
# Pick any flagged transaction from the sidebar → Run Agent → Review SAR → Approve
```

### 5. Run the API (optional)

```bash
uvicorn api.handler:app --reload --port 8000
# Docs: http://localhost:8000/docs
```

### 6. Run tests

```bash
pytest tests/ -v --tb=short
```

---

## Docker Compose (full stack)

```bash
docker compose up --build
# API:       http://localhost:8000/docs
# UI:        http://localhost:8501
# Qdrant:    http://localhost:6333/dashboard
```

---

## EC2 deployment

```bash
# On EC2 Ubuntu 22.04 t3.medium:
chmod +x infra/ec2_setup.sh
./infra/ec2_setup.sh
```

Sets up Docker, runs all services, bootstraps data. One command.

---

## Project structure

```
finguard-ai/
├── agent/
│   ├── state.py          # FinGuardState TypedDict — shared agent state
│   ├── graph.py          # LangGraph StateGraph — nodes + edges + HITL
│   └── nodes/
│       ├── triage.py     # Risk scoring, fraud classification, routing
│       ├── investigator.py  # RAG + OFAC + counterparty tools
│       ├── compliance.py    # Regulation RAG, violation detection
│       └── reporter.py      # SAR draft generation, confidence scoring
├── ingestion/
│   ├── transaction_loader.py  # IEEE-CIS + PaySim + synthetic data
│   ├── doc_pipeline.py        # PDF scraper, chunker, Bedrock embedder
│   ├── ofac_loader.py         # OFAC SDN XML parser + fuzzy matcher
│   └── qdrant_indexer.py      # Qdrant collections + hybrid search
├── tools/
│   └── ofac_mcp.py            # MCP server for OFAC screening
├── api/
│   ├── handler.py             # FastAPI app
│   └── models.py              # Pydantic request/response schemas
├── ui/
│   └── app.py                 # Streamlit analyst dashboard
├── eval/
│   └── ragas_eval.py          # RAGAS metrics + CI gate
├── tests/
│   ├── test_triage.py         # Triage node unit tests
│   ├── test_graph.py          # Graph routing + state tests
│   ├── test_retriever.py      # RAG chunking + retrieval tests
│   └── test_api.py            # FastAPI contract tests
├── monitoring/
│   └── cloudwatch_publisher.py  # Custom CloudWatch metrics
├── infra/
│   ├── ec2_setup.sh           # One-shot EC2 bootstrap
│   └── nginx.conf             # Reverse proxy config
├── .github/workflows/ci.yml   # CI: test → RAGAS gate → EC2 deploy
├── docker-compose.yml
├── Dockerfile
└── pyproject.toml             # uv-managed dependencies
```

---

## CI/CD pipeline

```
push to main
    │
    ├── pytest (unit tests, no cloud)
    │       ↓ pass
    ├── RAGAS eval (10 questions, Bedrock + Qdrant)
    │       ↓ faithfulness ≥ 0.75, recall ≥ 0.70, precision ≥ 0.65
    ├── Docker build + smoke test
    │       ↓ pass
    └── SSH deploy to EC2
            docker compose pull + up --build
            health check /health
```

Deploy is blocked if RAGAS metrics fall below threshold. This prevents regressions in RAG quality from reaching production.

---

## Fraud scenarios covered

| Scenario | Description | Key regulation |
|---|---|---|
| Structuring | Multiple cash deposits just under $10k CTR threshold | 31 CFR 1010.314 |
| Wire fraud | High-value wire to sanctioned/high-risk jurisdiction | SAR requirement |
| Money laundering | Placement → layering → integration pattern | BSA AML program |
| Card fraud | Card-not-present fraud across multiple countries | SAR requirement |
| Account takeover | New device + immediate large wire to new payee | CDD/EDD rules |

---

## Key design decisions

**Why LangGraph over a simple chain?** Conditional routing (auto-close vs escalate vs investigate) and the re-investigation loop require explicit state management. LangGraph's `StateGraph` lets us define these branches declaratively and interrupt for human review without re-running the whole pipeline.

**Why Qdrant over OpenSearch?** Single Docker command, native hybrid search (dense + sparse), free cloud tier for production, Python client is clean. Hybrid BM25 + vector search with RRF gives better retrieval than either alone — especially important for regulation text where exact legal terms (CFR citations, dollar thresholds) need keyword precision.

**Why post-transaction review vs real-time blocking?** Real-time blocking requires sub-100ms latency and integrates with the bank's core transaction system. What compliance teams actually need is automated investigation of alerts that have already been raised — this is where the 2–3 hour manual work happens. FinGuard AI targets this workflow.

**Why synthetic data fallback?** The IEEE-CIS dataset requires a Kaggle download that can fail in CI. Synthetic data covers all 5 fraud scenarios deterministically (seeded), making tests reproducible. The agent's RAG retrieval works just as well on synthetic transactions as real ones — what matters is the regulation knowledge base.

---

## AWS services used

- **Bedrock** — Claude 3 Sonnet (LLM inference) + Titan Embeddings v2 (text embeddings)
- **CloudWatch** — custom metrics: latency, token cost, SAR rate, RAGAS scores
- **EC2** — t3.medium host for Docker Compose deployment
- **IAM** — role-based auth for Bedrock access (no hardcoded keys)

---

## License

MIT
