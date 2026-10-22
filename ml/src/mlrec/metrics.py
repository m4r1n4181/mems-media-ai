from __future__ import annotations

import numpy as np


def recall_at_k(ranked: list, relevant: set, k: int) -> float:
    return len(set(ranked[:k]) & relevant) / len(relevant)


def ndcg_at_k(ranked: list, relevant: set, k: int) -> float:
    gains = [1.0 / np.log2(i + 2) for i, c in enumerate(ranked[:k]) if c in relevant]
    ideal = sum(1.0 / np.log2(i + 2) for i in range(min(len(relevant), k)))
    return sum(gains) / ideal
