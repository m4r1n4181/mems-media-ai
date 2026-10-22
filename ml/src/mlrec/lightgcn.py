"""LightGCN (He et al., SIGIR 2020) on the bipartite brand–creator graph, in plain PyTorch.

How it works:
  1. every brand and creator node starts with a learnable embedding (dim d);
  2. K rounds of propagation: each node takes the degree-normalised sum of its neighbours' embeddings
     (round 1: a brand learns from its creators, round 2: from other brands of those creators, ...);
  3. the final embedding is the average over all rounds;
  4. trained with BPR: for (brand, creator it is connected to, random creator) the connected pair must score higher.
The interface matches SVDEmbeddings (fit / score / pair_scores / top_pairs), so it plugs into the same pipeline.
"""
from __future__ import annotations

import time

import numpy as np
import pandas as pd
import torch

from .baselines import Index
from .split import Task


class LightGCN:
    def __init__(self, dim: int = 64, layers: int = 3, epochs: int = 20, batch: int = 8192, lr: float = 5e-3,
                 reg: float = 1e-4, paid_share: float = 0.5, half_life_days: float | None = None,
                 seed: int = 0, verbose: bool = True):
        self.dim, self.layers, self.epochs, self.batch = dim, layers, epochs, batch
        self.lr, self.reg, self.paid_share, self.seed, self.verbose = lr, reg, paid_share, seed, verbose
        self.half_life_days = half_life_days

    # ---------- graph ----------
    def _graph(self, task: Task, idx: Index):
        h = task.history
        pairs = h.groupby(["brand", "creator_id"]).agg(sponsored=("sponsored", "max"), last=("ts", "max")).reset_index()
        b = idx.b_pos[pairs.brand].values
        c = idx.c_pos[pairs.creator_id].values
        self.nb, self.nc = len(idx.brands), len(idx.creators)
        n = self.nb + self.nc
        # Edge weight: 1, or decayed by the age of the pair's most recent interaction (recent ties matter more)
        if self.half_life_days:
            age = (task.cutoff - pairs["last"]).dt.days.values
            w = (0.5 ** (age / self.half_life_days)).astype(np.float32)
        else:
            w = np.ones(len(pairs), dtype=np.float32)
        rows = np.concatenate([b, c + self.nb])
        cols = np.concatenate([c + self.nb, b])
        ww = np.concatenate([w, w])
        deg = np.bincount(rows, weights=ww, minlength=n).astype(np.float32)
        vals = ww / np.sqrt(deg[rows] * deg[cols])                 # symmetric normalisation D^-1/2 A D^-1/2
        self.A = torch.sparse_coo_tensor(np.vstack([rows, cols]), torch.tensor(vals, dtype=torch.float32),
                                         (n, n)).coalesce().to_sparse_csr()
        self.edges_b, self.edges_c, self.edge_w = b, c, w
        self.paid_mask = pairs.sponsored.values == 1

    def _propagate(self, E0):
        out, E = [E0], E0
        for _ in range(self.layers):
            E = torch.sparse.mm(self.A, E)
            out.append(E)
        return torch.stack(out).mean(0)

    # ---------- training ----------
    def fit(self, task: Task, idx: Index):
        torch.manual_seed(self.seed)
        rng = np.random.default_rng(self.seed)
        self._graph(task, idx)
        E0 = torch.nn.Parameter(torch.randn(self.nb + self.nc, self.dim) * 0.1)
        opt = torch.optim.Adam([E0], lr=self.lr)
        paid_idx, org_idx = np.flatnonzero(self.paid_mask), np.flatnonzero(~self.paid_mask)
        # recent edges are sampled more often as positives (uniform when there is no time decay)
        p_paid = self.edge_w[paid_idx] / self.edge_w[paid_idx].sum()
        p_org = self.edge_w[org_idx] / self.edge_w[org_idx].sum()
        n_edges = len(self.edges_b)
        steps = max(1, n_edges // self.batch)
        t0 = time.time()
        for ep in range(self.epochs):
            total = 0.0
            for _ in range(steps):
                n_paid = int(self.batch * self.paid_share)            # oversample paid edges: they are the target
                e = np.concatenate([rng.choice(paid_idx, n_paid, p=p_paid),
                                    rng.choice(org_idx, self.batch - n_paid, p=p_org)])
                bb = torch.from_numpy(self.edges_b[e])
                pc = torch.from_numpy(self.edges_c[e] + self.nb)
                nc = torch.from_numpy(rng.integers(0, self.nc, len(e)) + self.nb)
                E = self._propagate(E0)
                pos = (E[bb] * E[pc]).sum(1)
                neg = (E[bb] * E[nc]).sum(1)
                bpr = -torch.nn.functional.logsigmoid(pos - neg).mean()
                l2 = (E0[bb].pow(2).sum() + E0[pc].pow(2).sum() + E0[nc].pow(2).sum()) / len(e)
                loss = bpr + self.reg * l2
                opt.zero_grad()
                loss.backward()
                opt.step()
                total += bpr.item()
            if self.verbose:
                print(f"  LightGCN epoch {ep + 1}/{self.epochs}  bpr={total / steps:.4f}  ({time.time() - t0:.0f}s)",
                      flush=True)
        with torch.no_grad():
            E = self._propagate(E0).numpy()
        self.U, self.V = E[:self.nb], E[self.nb:]
        return self

    # ---------- scoring (same interface as SVDEmbeddings) ----------
    def score(self, rows):
        return self.U[rows] @ self.V.T

    def pair_scores(self, idx: Index, brand_names, creator_ids) -> np.ndarray:
        return (self.U[idx.b_pos[brand_names].values] * self.V[idx.c_pos[creator_ids].values]).sum(axis=1)

    def top_pairs(self, idx: Index, brands: list[str], n: int, batch: int = 400) -> pd.DataFrame:
        parts = []
        for start in range(0, len(brands), batch):
            names = brands[start:start + batch]
            s = self.score(idx.b_pos[names].values)
            top = np.argpartition(-s, n, axis=1)[:, :n]
            parts.append(pd.DataFrame({"brand": np.repeat(names, n), "creator_id": idx.creators[top.ravel()]}))
        return pd.concat(parts)
