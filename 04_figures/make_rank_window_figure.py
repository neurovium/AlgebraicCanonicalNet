#!/usr/bin/env python3
"""
make_rank_window_figure.py
==========================

The manuscript's rank/decomposition data figure (successor to panels C-D of
the original figure_DN_WTA):

(a-c) Rank distribution of every monoid element for the three composition
      schemes -- uncoupled product, DN->WTA cascade, WTA->DN cascade -- with
      the non-aperiodic (reversible-containing) elements overlaid. Shows the
      low-rank concentration in all three, from exact enumeration.
(d)   Where group structure lives: for each scheme, the holonomy windows
      (image sets carrying a nontrivial permutation group) classified as
      moving only the WTA coordinate, only the DN coordinate, or BOTH
      (composite). The uncoupled product has zero composite windows; the
      WTA->DN cascade is dominated by them. Exact counts from the SgpDec
      decomposition (02_holonomy/expected_output/compositeness_all.csv).

Inputs:  audit_results.json (rank distributions, experiment 01)
         compositeness_all.csv (window classification, experiment 02)
Outputs: rank_window_figure.{png,pdf,svg}  (300-dpi raster + two vector)

Usage:
  PYTHONPATH=$PWD python make_rank_window_figure.py \
      --audit audit_results.json --windows compositeness_all.csv --outdir .
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

C_ALL = "#9fb6cc"     # all monoid elements
C_NONAP = "#1b4f8a"   # non-aperiodic elements
C_W = "#d1495b"       # windows moving only the WTA coordinate
C_D = "#2c6fbb"       # windows moving only the DN coordinate
C_COMP = "#e07a00"    # composite windows (move both)

SCHEMES = [("prod", "independent product"),
           ("D_to_W", r"DN$\to$WTA cascade"),
           ("W_to_D", r"WTA$\to$DN cascade")]


def style(sizes=(8, 7, 6)) -> None:
    base, mid, small = sizes
    mpl.rcParams.update({
        "figure.dpi": 150, "savefig.dpi": 300,
        "savefig.bbox": "tight", "savefig.pad_inches": 0.02,
        "font.size": base, "axes.titlesize": base, "axes.labelsize": base,
        "legend.fontsize": mid, "xtick.labelsize": small, "ytick.labelsize": small,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.linewidth": 0.6, "xtick.major.width": 0.6, "ytick.major.width": 0.6,
        "xtick.major.size": 2.5, "ytick.major.size": 2.5, "axes.titlepad": 4.0,
        "pdf.fonttype": 42, "ps.fonttype": 42, "svg.fonttype": "none",
    })


def load(audit_path: str, windows_path: str):
    res = {r["label"]: r for r in json.load(open(audit_path))}
    win = pd.read_csv(windows_path)
    counts = (win.groupby(["system", "classification"]).size()
                 .unstack(fill_value=0))
    return res, counts


def build(res, counts):
    fig = plt.figure(figsize=(7.1, 4.1))
    gs = fig.add_gridspec(2, 3, height_ratios=[1.0, 1.05],
                          hspace=0.62, wspace=0.30,
                          left=0.155, right=0.975, top=0.895, bottom=0.105)

    # ---- (a-c) rank distributions, shared axes ---------------------------
    axes = [fig.add_subplot(gs[0, k]) for k in range(3)]
    ymax = 0
    for ax, (key, label) in zip(axes, SCHEMES):
        rd = {int(k): v for k, v in res[key]["rank_dist"].items()}
        rn = {int(k): v for k, v in res[key]["rank_dist_nonaperiodic"].items()}
        ranks = np.arange(1, 33)
        allv = np.array([rd.get(r, 0) for r in ranks])
        nonv = np.array([rn.get(r, 0) for r in ranks])
        ax.bar(ranks, allv, width=0.85, color=C_ALL, zorder=3,
               label="all elements")
        ax.bar(ranks, nonv, width=0.85, color=C_NONAP, zorder=4,
               label="non-aperiodic")
        # rank axis: the tail is sparse; show to rank 12 with a broken hint at 32
        ax.set_xlim(0.2, 12.8)
        ax.set_xticks([1, 4, 8, 12])
        n32 = rd.get(32, 0)
        ax.set_title(f"{label}\n" + rf"$|M|$ = {res[key]['monoid_size']:,}",
                     loc="left")
        ax.text(0.97, 0.86,
                f"rank 32: {n32}\n(identity)",
                transform=ax.transAxes, fontsize=6, color="#6e7276",
                ha="right", va="top")
        ymax = max(ymax, allv.max())
    for k, ax in enumerate(axes):
        ax.set_ylim(0, 2300)
        ax.set_yticks([0, 1000, 2000])
        if k == 0:
            ax.set_yticklabels(["0", "1k", "2k"])
            ax.set_ylabel("monoid elements")
            ax.legend(loc="upper right", frameon=False, fontsize=6,
                      bbox_to_anchor=(1.02, 0.72), handlelength=1.0)
        else:
            ax.set_yticklabels([])
        ax.set_xlabel(r"rank $|\mathrm{Im}(f)|$")

    # ---- (d) composite windows from the holonomy decomposition -----------
    axD = fig.add_subplot(gs[1, :])
    order = ["prod", "D_to_W", "W_to_D"]
    labels = {k: lab for k, lab in SCHEMES}
    cols = [("W-ONLY-inherited", C_W, "moves WTA coordinate only (inherited)"),
            ("D-ONLY", C_D, "moves DN coordinate only"),
            ("COMPOSITE", C_COMP, "composite: moves both")]
    y = np.arange(len(order))[::-1]
    left = np.zeros(len(order))
    for cls, color, lab in cols:
        vals = np.array([counts.loc[s, cls] if cls in counts.columns else 0
                         for s in order], dtype=float)
        axD.barh(y, vals, left=left, height=0.58, color=color, zorder=3, label=lab)
        for yy, v, l in zip(y, vals, left):
            if v > 2:
                axD.text(l + v / 2, yy, f"{int(v)}", ha="center", va="center",
                         fontsize=6.5, color="white", zorder=5)
            elif v > 0:
                axD.text(l + v / 2, yy - 0.45, f"{int(v)}", ha="center",
                         va="top", fontsize=6.5, color=color, zorder=5)
            else:
                axD.plot([l], [yy], marker="|", ms=6, mew=1.2, color=color,
                         zorder=5)
        left = left + vals
    totals = [int(counts.loc[s].sum()) for s in order]
    axD.set_yticks(y)
    axD.set_yticklabels([f"{labels[s]}\n{t} windows" for s, t in zip(order, totals)])
    axD.set_xlabel("group-carrying image sets (holonomy windows), exact count")
    axD.set_xlim(0, 60)
    axD.set_title("No composite window in the product; 35 of 57 in the "
                  "WTA$\\to$DN cascade", loc="left")
    axD.legend(loc="upper right", frameon=False, fontsize=6.5, ncol=1,
               handlelength=1.0, bbox_to_anchor=(0.995, 1.02))

    # panel letters
    for ax, L in zip(axes + [axD], "abcd"):
        ax.text(-0.06 if L != "d" else -0.018, 1.18, L, transform=ax.transAxes,
                fontsize=10, fontweight="bold", va="top", ha="right")
    return fig


def verify(fig) -> None:
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    texts = [(t, t.get_window_extent(r)) for t in fig.findobj(mpl.text.Text)
             if t.get_text().strip() and t.get_visible()]
    ticklabels = {ax: set(ax.get_xticklabels(which="both") +
                          ax.get_yticklabels(which="both")) for ax in fig.axes}
    spines = [(s, s.get_window_extent(r)) for ax in fig.axes
              for s in ax.spines.values() if s.get_visible()]
    ov = [(a.get_text()[:28], b.get_text()[:28])
          for i, (a, ba) in enumerate(texts) for b, bb in texts[i + 1:]
          if ba.overlaps(bb)]
    ov += [(t.get_text()[:28], "spine") for t, bt in texts for s, bs in spines
           if bt.overlaps(bs) and t not in ticklabels[s.axes]]
    outside = [t.get_text()[:28] for t, bt in texts
               if not (fig.bbox.contains(bt.x0, bt.y0)
                       and fig.bbox.contains(bt.x1, bt.y1))]
    print(f"overlaps: {ov}")
    print(f"outside canvas: {outside}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--audit", default="audit_results.json")
    ap.add_argument("--windows", default="compositeness_all.csv")
    ap.add_argument("--outdir", type=Path, default=Path("."))
    ap.add_argument("--dpi", type=int, default=300)
    ap.add_argument("--formats", default="png,pdf,svg")
    args = ap.parse_args()

    style()
    res, counts = load(args.audit, args.windows)
    # hard checks against the paper's quoted numbers
    assert int(counts.loc["prod"].sum()) == 34 and counts.loc["prod"].get("COMPOSITE", 0) == 0
    assert int(counts.loc["W_to_D"].sum()) == 57 and counts.loc["W_to_D"]["COMPOSITE"] == 35
    assert int(counts.loc["D_to_W"].sum()) == 46 and counts.loc["D_to_W"]["COMPOSITE"] == 15
    fig = build(res, counts)
    args.outdir.mkdir(parents=True, exist_ok=True)
    for ext in [e.strip() for e in args.formats.split(",") if e.strip()]:
        path = args.outdir / f"rank_window_figure.{ext}"
        fig.savefig(path, dpi=args.dpi)
        print(f"wrote {path}")
    verify(fig)


if __name__ == "__main__":
    main()
