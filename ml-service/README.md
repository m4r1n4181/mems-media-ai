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

## New brands (cold start)

The model ranks creators for the 300 brands it knows (the 39 clients the app starts with plus the most active
other brands). A new client that is one of them uses its own ranking. For a brand the model has never seen, the
manager names up to five similar known brands: their ranked lists, plus the most active creators of the brand's
niche, are merged with **reciprocal rank fusion** (each creator gets 1 / (60 + rank) from every list it is in).
Only positions are used, so lists with differently scaled scores combine fairly.

How good is that? `ml/scripts/cold_start_simulation.py` pretends every validation brand is new and measures
Recall@50 against its real new partners: the brand's own model ranking 0.255; look-alikes chosen by shared
creators 0.049 (0.054 with the niche list fused in); look-alikes chosen by niche and size 0.021, raised to
0.030 by fusing the niche list; random look-alikes 0.007. Suggestions for a new brand are a starting point, about
a fifth as good as for a known brand, and the app says so. Once the brand runs campaigns it becomes a normal brand
at the next model export.

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
| POST | `/lookalike/recommendations` | cold start: a new brand's suggestions fused from similar brands (+ its niche) |
| POST | `/outreach/draft` | AI e-mail draft with faithfulness checks (`similar_brands` for a brand the model does not know) |

## Tests

```bash
python -m pytest -q
```

Tests use a tiny synthetic dataset and a fake LLM, so they need neither the real data nor a model.
