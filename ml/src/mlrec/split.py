"""Temporal task: for each brand, rank creators that will start a NEW paid collaboration in a future window."""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass
class Task:
    cutoff: pd.Timestamp
    end: pd.Timestamp
    history: pd.DataFrame          # interactions strictly before cutoff (the only thing models may see)
    positives: pd.DataFrame        # (brand, creator_id) new paid collaborations in [cutoff, end)
    candidates: pd.Index           # creators active before cutoff
    known_pairs: set               # (brand, creator_id) paid before cutoff, excluded from ranking


def make_task(inter: pd.DataFrame, cutoff: str, end: str) -> Task:
    cutoff, end = pd.Timestamp(cutoff), pd.Timestamp(end)
    history = inter[inter.ts < cutoff]
    window = inter[(inter.ts >= cutoff) & (inter.ts < end) & (inter.sponsored == 1)]

    known = set(map(tuple, history.loc[history.sponsored == 1, ["brand", "creator_id"]].drop_duplicates().values))
    candidates = pd.Index(history.creator_id.unique())
    pos = window[["brand", "creator_id"]].drop_duplicates()
    pos = pos[pos.creator_id.isin(candidates)]
    pos = pos[[ (b, c) not in known for b, c in pos.itertuples(index=False) ]]
    return Task(cutoff, end, history, pos.reset_index(drop=True), candidates, known)
