"""Figures for the README, drawn from the result files in ml/results (run from the repository root)."""
import json
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "img"
INK, MUTED, GRID = "#1f1f1d", "#6b6a66", "#e6e5e0"
BLUE, ORANGE, GRAY = "#2a78d6", "#eb6834", "#b4b2aa"
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 11, "axes.spines.top": False, "axes.spines.right": False,
    "axes.spines.left": False, "axes.edgecolor": GRID, "axes.labelcolor": MUTED, "xtick.color": MUTED,
    "ytick.color": INK, "axes.grid": True, "grid.color": GRID, "axes.axisbelow": True, "figure.dpi": 200,
})


def test_results():
    s = json.loads((ROOT / "ml" / "results" / "ranker_test.json").read_text())["summary"]
    ks = ["recall@10", "recall@50", "recall@100"]
    models = [("brand kNN", s["kNN only"], GRAY), ("best heuristic (organic mentions)", s["organic only"], ORANGE),
              ("two-stage model", s["ranker"], BLUE)]
    fig, ax = plt.subplots(figsize=(8, 3.6))
    w = 0.26
    for i, (name, m, c) in enumerate(models):
        xs = [j + (i - 1) * w for j in range(len(ks))]
        bars = ax.bar(xs, [m[k] for k in ks], w * 0.92, color=c, label=name)
        if name == "two-stage model":
            for x, k in zip(xs, ks):
                ax.text(x, m[k] + 0.006, f"{m[k]:.1%}", ha="center", va="bottom", color=INK, fontsize=10)
    ax.set_xticks(range(len(ks)), ["top 10", "top 50", "top 100"])
    ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0%}")
    ax.set_ylabel("share of real new partners found")
    ax.set_ylim(0, 0.40)
    fig.suptitle("Held-out future period (Jan–Apr 2019): who did each brand actually start working with?",
                 x=0.01, ha="left", color=INK, fontsize=11)
    ax.legend(frameon=False, loc="upper left", fontsize=10)
    ax.tick_params(axis="x", length=0)
    fig.tight_layout()
    fig.savefig(OUT / "test-results.png", facecolor="white")


def cold_start():
    r = json.loads((ROOT / "ml" / "results" / "cold_start_val.json").read_text())
    m, sens = r["recall@50"], r["sensitivity"]
    rows = [
        ("brand known to the model", m["warm model (own history)"], BLUE),
        ("new brand: 3 look-alikes by shared creators + niche", sens["behaviour look-alikes + niche list"], BLUE),
        ("new brand: niche only", m["niche heuristic (no look-alikes)"], GRAY),
        ("new brand: look-alikes by niche and size", m["look-alikes: niche + size"], GRAY),
        ("new brand: random look-alikes", m["look-alikes: random"], GRAY),
    ][::-1]
    fig, ax = plt.subplots(figsize=(8, 3.2))
    ax.barh([n for n, _, _ in rows], [v for _, v, _ in rows], color=[c for _, _, c in rows], height=0.62)
    for i, (_, v, _) in enumerate(rows):
        ax.text(v + 0.003, i, f"{v:.3f}", va="center", color=INK, fontsize=10)
    ax.set_xlabel("Recall@50 (validation, 6,508 brands)")
    fig.suptitle("Cold start: recommendations for a brand the model has never seen", x=0.01, ha="left",
                 color=INK, fontsize=11)
    ax.tick_params(axis="y", length=0)
    ax.grid(axis="y", visible=False)
    ax.set_xlim(0, 0.29)
    fig.tight_layout()
    fig.savefig(OUT / "cold-start.png", facecolor="white")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    test_results()
    cold_start()
    print("figures written to", OUT)
