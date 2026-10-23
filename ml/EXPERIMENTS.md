# Experiment log

Validation window: new paid collaborations 2018-10-01 → 2018-12-31, ~6.5k brands, ~35k candidate creators.
All rankers are trained on earlier windows only. Metrics are means over brands.
The test window (2019-01-01 → 2019-04-30) has **not** been used yet.

| # | change | candidate recall | Recall@10 | Recall@50 | Recall@100 | NDCG@50 | kept? |
|---|---|---|---|---|---|---|---|
| B1 | popularity (all time) | — | 0.004 | 0.011 | 0.020 | 0.005 | baseline |
| B2 | organic mentions | — | 0.118 | 0.163 | 0.182 | 0.099 | baseline |
| B3 | brand kNN | — | 0.071 | 0.138 | 0.183 | 0.069 | baseline |
| B4 | hard co-clusters (k-means 50×100 on SVD vectors) | — | 0.017 | 0.049 | 0.068 | 0.022 | no — too coarse |
| B5 | SVD embeddings alone (128 dims) | — | 0.034 | 0.093 | 0.137 | 0.041 | as candidate source |
| B6 | LightGCN alone (128 dims, 2 layers, BPR, 30 epochs) | — | 0.081 | 0.179 | 0.244 | 0.080 | as candidate source + features |
| B7 | LightGCN alone with time-decayed edges (half-life 90 days) | — | 0.102 | 0.203 | 0.271 | 0.100 | not in ranker (see R8) |
| H | heuristic: organic mentions, kNN breaks ties (same candidates as R5) | — | 0.128 | 0.207 | 0.247 | 0.113 | reference |
| R1 | LightGBM ranker, organic + kNN top-200 candidates, 1 train window | 0.262 | 0.129 | 0.217 | 0.260 | 0.119 | superseded |
| R2 | + niche pool candidates, kNN top-500 | 0.375 | 0.129 | 0.215 | 0.261 | 0.119 | superseded |
| R3 | + 2 stacked train windows, 300 negatives/brand | 0.375 | 0.134 | 0.217 | 0.261 | 0.121 | superseded |
| R4 | + brand partner-size features | 0.375 | 0.134 | 0.220 | 0.265 | 0.123 | superseded |
| R5 | + SVD candidates (top-300) and SVD features | 0.424 | 0.137 | 0.230 | 0.281 | 0.126 | superseded |
| R6 | + partner-profile features (niche centroid of paid partners, creator kNN, engagement/experience gaps) | 0.424 | 0.137 | 0.229 | 0.281 | 0.125 | no — no gain, information already in kNN/SVD |
| **R7** | **R5 + LightGCN candidates (top-300) and LightGCN features** | **0.476** | **0.146** | **0.260** | **0.322** | **0.135** | **current** |
| R8 | R7 + time-decayed LightGCN (B7) + audience-quality features (comments/likes, followers/followees) | 0.481 | 0.144 | 0.257 | 0.323 | 0.135 | no — no gain over R7 |
| R9 | R7 + niche-affinity pool (creator niche mix from hashtags + bios, brand affinity learned from paid partners) + `partner_affinity` feature | 0.486 | 0.144 | 0.259 | 0.322 | 0.134 | no — no gain over R7 |
| A2 | ablation: R7 without the niche pool and without niche features (`--no-niche`) | 0.448 | 0.145 | 0.254 | 0.319 | 0.134 | no — same ranking with 18% fewer candidates; R7 kept (already tested) |

## Notes

- **R8 lesson:** time decay made LightGCN alone much better (B6 → B7, Recall@50 0.179 → 0.203), yet the ranker did
  not improve. The ranker already knew about recency from `days_since_org_mention`, so a better component does not
  automatically mean a better system. Audience-quality proxies got ~1% importance each: no demographic signal here.

- **R9 lesson (follow-up to the error analysis, notebook 04):** most missed partners are in another niche than the
  brand, so creators got a niche *mix* (bios fill in creators who use few hashtags: coverage of new partners
  52% → 80%) and brands an *affinity* learned from the creators they paid. Candidate recall on validation:
  adding the affinity pool +1.0 point (hashtags) / +1.1 (with bios) for ~90 extra candidates per brand; replacing
  the old niche pool with it −1.2. In the ranker the new feature got 1.7% of the gain, but Recall@50 stayed at
  R7's level. Probably the partners it adds are hard cases the ranker does not lift into its top 50, and the niche
  signal was already partly in `niche_cosine`, kNN and LightGCN. Not adopted; the code stays behind `--affinity` for reproducibility.

- **A2 lesson (ablation):** removing niches entirely costs 2.7 points of candidate recall but nothing measurable in
  Recall@50 (0.2540 vs R7's 0.2553 in the same run setup). Niches help people (filters, explanations in the app),
  not ranking: the graph signals already carry that information. A niche is a coarse filter: each niche holds
  1,300–6,900 experienced creators, missed partners sit around position 1,300 in their niche list, and about half
  of them are on no niche list at all. R7 stays final because it is the model evaluated on the test window.

- **Noise level:** re-running R5 gave Recall@50 0.2301 vs 0.2298 (negative sampling only). With LightGCN the
  runs vary more: R7 on validation gave 0.2596 and, re-run inside walk-forward, 0.2553. Treat differences
  below ~0.005 as noise.
- **LightGCN (B6, R7)** is the best single model (Recall@50 0.179 alone, above organic mentions and kNN).
  Its gain is largest for brands with little history (1–9 creators: ranker Recall@50 0.257 → 0.311), as expected
  from propagating information over neighbours-of-neighbours. For brands with 100+ creators it adds little.

- **Candidate recall is the ceiling.** Recall@100 of the ranker sits close to it, so the biggest gains came from
  better candidate generation (R1 → R5), not from more features.
- 91% of future partners had been paid by some brand before, 98% were active in the last 90 days, only 14% had
  mentioned the brand organically. Most collaborations are not predictable from this data alone.
- R6 is within noise of R5. A feature that does not help is removed: it adds cost and overfitting risk.

## Walk-forward validation (R7)

Time-series cross-validation: each fold trains only on data before its evaluation window.

| fold | train windows | evaluated on | heuristic Recall@50 | ranker Recall@50 | gain |
|---|---|---|---|---|---|
| fold1 | Jan–Mar + Apr–Jun 2018 | Jul–Sep 2018 | 0.187 | 0.226 | +21% |
| val | Apr–Jun + Jul–Sep 2018 | Oct–Dec 2018 | 0.207 | 0.255 | +23% |

Mean ± std over folds:

| model | Recall@10 | Recall@50 | Recall@100 | NDCG@50 |
|---|---|---|---|---|
| organic mentions + kNN ties (heuristic) | 0.130 ± 0.003 | 0.197 ± 0.014 | 0.232 ± 0.022 | 0.113 ± 0.001 |
| **R7 ranker** | **0.142 ± 0.004** | **0.241 ± 0.021** | **0.300 ± 0.030** | **0.131 ± 0.005** |

The ranker beats the heuristic in every fold. With only two folds the std is a rough estimate.

## Final test (run once, model frozen at R7)

Trained on Jul–Sep + Oct–Dec 2018, evaluated on new paid collaborations Jan–Apr 2019 (5,502 brands).
April 2019 is incomplete (data collection ended), so some real collaborations are missing for all models.

| model | candidate recall | Recall@10 | Recall@50 | Recall@100 | NDCG@50 |
|---|---|---|---|---|---|
| kNN | — | 0.075 | 0.145 | 0.188 | 0.070 |
| heuristic (organic mentions, kNN breaks ties) | — | 0.124 | 0.214 | 0.261 | 0.113 |
| **R7 ranker** | 0.518 | **0.150** | **0.276** | **0.344** | **0.142** |
| gain over heuristic | | +21% | +29% | +32% | +26% |

Recall@50 by brand history: 1–9 creators 0.245 → **0.333**, 10–99 0.226 → **0.284**, 100+ 0.142 → **0.194**.

The test numbers are slightly **higher** than validation. Likely reasons: the model is trained on more recent data
(Jul–Dec 2018 instead of Apr–Sep), brands have more history by 2019, and candidate recall is higher (0.52). The gain
over the heuristic (+29%) is consistent with walk-forward (+21%, +23%), which is the main evidence that it generalises.
Popularity bias is visible: for the largest brands the ranker's top-10 median is ~46k followers vs ~26k for the heuristic.

## Error analysis of candidate generation (validation, Oct–Dec 2018)

Candidate recall 47.5% (pair-weighted; 53.7% per-brand average). The ranker puts about half of the retrieved
partners in its top 50, so both stages lose about half. Misses by cause: creator with history but another niche
than the brand 46%, creator without a niche (too few hashtags) 20%, same niche 15%, giant brands (>50 new partners
in 3 months) 14%, creators with almost no brand history 5%. Reading 50 misses showed noisy brand niches for brands
outside fashion and beauty. Ceiling estimates: niche pool from the brand's top-2 niches +2.3 points (≤300 extra
candidates per brand), 300 most active paid creators +1.2, 1,000 most active +5.0. Details in
[notebook 04](notebooks/04_error_analysis.ipynb).
