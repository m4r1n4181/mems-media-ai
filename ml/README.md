# ml — brand–creator recommender

Recommends Instagram creators (influencers) to brands for **new paid collaborations**.
Built on the research *Influencer and Brand Dataset*: 1.6M posts, 38K creators, 25K brands (2017–2019).

## Result

On a held-out future period (Jan–Apr 2019, evaluated once), the model finds **29% more of a brand's new partners
in its top 50** than the strongest heuristic, and it is better for every kind of brand:

| model | Recall@10 | Recall@50 | Recall@100 | NDCG@50 |
|---|---|---|---|---|
| item kNN | 0.075 | 0.145 | 0.188 | 0.070 |
| heuristic: organic mentions, kNN breaks ties | 0.124 | 0.214 | 0.261 | 0.113 |
| **two-stage ranker (final)** | **0.150** | **0.276** | **0.344** | **0.142** |

The gain is consistent across walk-forward folds (+21% and +23% Recall@50) — see [EXPERIMENTS.md](EXPERIMENTS.md).

## How it works

```
brand ─► candidate generation (~1,100 per brand)          ─► LightGBM LambdaRank ─► ranked creators
           organic mentions · brand kNN · niche pool          26 features: recency of mentions, graph scores,
           SVD embeddings · LightGCN graph embeddings          niche fit, creator size & experience, brand profile
```

* **Temporal evaluation:** models only see data before a cutoff and are scored on collaborations that start after it.
* **Niches** (fashion, beauty, fitness, food, …) are learned from hashtags with NMF and transferred to brands.
* **LightGCN** (graph neural network, PyTorch) gave the largest single gain, especially for brands with little history.
* Every experiment, including rejected ones, is in [EXPERIMENTS.md](EXPERIMENTS.md) and tracked with MLflow.

## Notebooks

| notebook | what it shows |
|---|---|
| [01_data_exploration](notebooks/01_data_exploration.ipynb) | what the data contains, why likes must be normalised, why the sponsored label is circular, the brand–creator graph, niches learned from hashtags |
| [02_baselines](notebooks/02_baselines.ipynb) | the recommendation task, temporal split, metrics, four baselines |
| [03_ranker](notebooks/03_ranker.ipynb) | candidate ceiling, experiment path, walk-forward and final test, popularity bias, limitations |

Notebooks only present results; the logic lives in `src/mlrec/` so it can be tested and served.

## Data and privacy

The dataset is **not** included (research-only licence). Extraction (`extract.py`, run next to the data) drops names,
bios, e-mails, phones and URLs. Creators are pseudonymized with a salted hash; the salt stays next to the data.
`results/` holds only aggregate metrics.

## Reproduce

```bash
cd ml
python -m venv .venv && source .venv/Scripts/activate      # Git Bash on Windows
pip install -r requirements.txt
export INFLUENCER_DATA_DIR="$HOME/Desktop/influencer-data/_derived"

python scripts/run_baselines.py val            # baselines on validation (~2 min)
python scripts/walk_forward.py                 # walk-forward folds (~45 min)
python scripts/train_ranker.py test            # final test, once (~25 min)
python scripts/export_service.py               # final model -> ../ml-service/data (~30 min)
mlflow ui --backend-store-uri sqlite:///mlflow.db
```

## Limitations

Implicit feedback only (no rejected candidates), about half of new partners are never retrieved, offline evaluation
only, data from 2017–2019. Details in [notebook 03](notebooks/03_ranker.ipynb).
