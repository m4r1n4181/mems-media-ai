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
| H | heuristic: organic mentions, kNN breaks ties (same candidates as R5) | — | 0.128 | 0.207 | 0.247 | 0.113 | reference |
| R1 | LightGBM ranker, organic + kNN top-200 candidates, 1 train window | 0.262 | 0.129 | 0.217 | 0.260 | 0.119 | superseded |
| R2 | + niche pool candidates, kNN top-500 | 0.375 | 0.129 | 0.215 | 0.261 | 0.119 | superseded |
| R3 | + 2 stacked train windows, 300 negatives/brand | 0.375 | 0.134 | 0.217 | 0.261 | 0.121 | superseded |
| R4 | + brand partner-size features | 0.375 | 0.134 | 0.220 | 0.265 | 0.123 | superseded |
| **R5** | **+ SVD candidates (top-300) and SVD features** | **0.424** | **0.137** | **0.230** | **0.281** | **0.126** | **current** |
| R6 | + partner-profile features (niche centroid of paid partners, creator kNN, engagement/experience gaps) | 0.424 | 0.137 | 0.229 | 0.281 | 0.125 | no — no gain, information already in kNN/SVD |

## Notes

- **Candidate recall is the ceiling.** Recall@100 of the ranker sits close to it, so the biggest gains came from
  better candidate generation (R1 → R5), not from more features.
- 91% of future partners had been paid by some brand before, 98% were active in the last 90 days, only 14% had
  mentioned the brand organically. Most collaborations are not predictable from this data alone.
- R6 is within noise of R5. A feature that does not help is removed: it adds cost and overfitting risk.
