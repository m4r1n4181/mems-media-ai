# ml-service

FastAPI service that serves the brand–creator recommender to the MEMS marketing app and drafts outreach e-mails
with an LLM.

* **Recommendations are computed offline** (batch) by `ml/scripts/export_service.py`: the final two-stage model
  (candidates from organic mentions, item-kNN, niche pool, SVD and LightGCN embeddings; LightGBM LambdaRank ranker)
  ranks the top 300 creators for each client brand. The service only filters and pages them, so every request is fast.
* **Outreach e-mails** are written by an LLM *only from facts we hold* (brand, campaign brief, the creator's niche,
  size and past collaborations, and why the recommender picked them). Every draft is checked automatically:
  no invented numbers, money, @handles or placeholders, and it must name the brand and the campaign.
  A failing draft gets one retry with the list of problems; after that, or when no LLM is reachable, a template
  e-mail is used and the response says so.

## Run

```bash
cd ml-service
python -m venv .venv
source .venv/Scripts/activate          # Git Bash on Windows (Linux/macOS: .venv/bin/activate)
pip install -r requirements.txt
uvicorn app.main:app --port 8000       # API docs: http://localhost:8000/docs
```

The model data must be in `ml-service/data/` (not in git). Create it with
`python ml/scripts/export_service.py` (needs the dataset, ~30 min), or copy the four files from someone who has them.

## LLM for e-mails

| `LLM_PROVIDER` | what it uses | settings |
|---|---|---|
| `ollama` (default) | a local model through [Ollama](https://ollama.com) | `OLLAMA_URL` (default `http://localhost:11434`), `OLLAMA_MODEL` (default: first installed chat model, preferring qwen/llama/mistral/gemma) |
| `openai` | any OpenAI-compatible API (OpenAI, LM Studio, vLLM…) | `OPENAI_MODEL`, `OPENAI_API_KEY`, `OPENAI_BASE_URL` |
| `anthropic` | Claude | `ANTHROPIC_API_KEY`, `ANTHROPIC_MODEL` (default `claude-haiku-5-5`) |
| `template` | no model, deterministic template | — |

Recommended local model: `ollama pull qwen2.5:7b`. `GET /health` shows which provider and model are active.

Settings can be put in `ml-service/.env` (git-ignored; real environment variables win). `.env.example` shows a
cloud setup with Qwen through its OpenAI-compatible endpoint. `OPENAI_EXTRA_BODY` is a JSON object merged into
every request, for provider-specific switches such as `{"enable_thinking": false}`.

## Endpoints

| method | path | |
|---|---|---|
| GET | `/health` | data and LLM status |
| GET | `/model-info` | model version, as-of date, test metrics |
| GET | `/brands`, `/brands/{brand}` | client brands |
| GET | `/brands/{brand}/recommendations?k&min_followers&max_followers&niche&exclude` | ranked creators with reasons |
| GET | `/creators/{creator_id}` | creator profile (pseudonymized) |
| POST | `/outreach/draft` | AI e-mail draft with faithfulness checks |

## Tests

```bash
python -m pytest -q
```

Tests use a tiny synthetic dataset and a fake LLM, so they need neither the real data nor a model.
