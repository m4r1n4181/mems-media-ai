# ml — brand–creator recommender

Training and evaluation code for recommending creators (influencers) to brands,
built on the research *Influencer and Brand Dataset* (Instagram, 2017–2019).

The dataset is **not** included in this repository (research-only license).
Personal data (names, bios, emails, phones, URLs) is dropped during extraction,
and creators are shown under pseudonyms.

## Notebooks

| notebook | what it shows |
|---|---|
| [01_data_exploration](notebooks/01_data_exploration.ipynb) | what the data contains, why likes must be normalised, why the sponsored label is circular, the brand–creator graph, niches learned from hashtags |
| [02_baselines](notebooks/02_baselines.ipynb) | the recommendation task, temporal split, metrics, and four baselines |

Notebooks only present results; the logic lives in `src/mlrec/` so it can be tested and served.

## Setup

```bash
cd ml
python -m venv .venv
source .venv/Scripts/activate      # Git Bash on Windows
pip install -r requirements.txt
```

Point the code at the extracted tables (output of `extract.py`):

```bash
export INFLUENCER_DATA_DIR="$HOME/Desktop/influencer-data/_derived"
```

Reproduce the baseline numbers: `python scripts/run_baselines.py val`
