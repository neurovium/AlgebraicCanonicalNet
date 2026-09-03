#!/usr/bin/env python3
"""
make_sweep_figure.py
====================

Render Figure 2 of the AlgCanNet manuscript: the exhaustive interface and
schedule sweeps.

Panels
------
(a) Winner-to-normalization interface psi, stratified by what the interface
    reads about the WTA state (nothing / gate bit / winner identity / both).
    Stacked fractions: composite cycle present AND shortest witness; composite
    present but a local cycle is shorter; no composite cycle in the monoid.
(b) The same classification for the normalization-to-competition interface phi.
(c) Update schedule under recurrent coupling, over the full (phi, psi) grid.
(d) Distribution of transition-monoid size across the psi sweep, with the
    biological winner-pooling interface marked.

Inputs (all shipped in 03_interface_sweep/expected_output/, no sweep re-run
needed)
-------------------------------------------------------------------------
  figure_strata.csv          per-stratum three-way counts for psi and phi
  psi_monoid_size_counts.csv monoid-size histogram over the 65,536 psi maps
  rec_grid_counts.csv        recurrent grid counts by scheme and witness class
  sweep_summary.json         headline numbers (used only for the bio |M| marker)

Outputs
-------
  sweep_figure.png (raster, 300 dpi (or --dpi)), sweep_figure.pdf and
  sweep_figure.svg (both vector). PDF is the format the manuscript includes;
  SVG is for editing.

Usage
-----
  PYTHONPATH=$PWD python make_sweep_figure.py --indir <expected_output> --outdir .
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# --- palette: one hue family for the outcome classes, one alarm hue for focus --
C_SHORT = "#1b4f8a"   # composite cycle present AND it is the shortest witness
C_LONG = "#7fa8cf"    # composite present but a local cycle is shorter
C_NONE = "#c9ccd1"    # no composite cycle anywhere in the monoid
FOCAL = "#c2451f"     # marks the class holding the biological interface

PSI_LABELS = {
    "constant": "constant\n(no winner info)",
    "g_only": "gate bit only",
    "winner_only": "winner identity only",
    "both": "gate + winner",
}
PHI_LABELS = {
    "constant": "constant\n(no DN info)",
    "partial": "non-injective",
    "injective": "injective",
}
REC_LABELS = {
    "rec_sync": "synchronous",
    "rec_async_D": "async (DN first)",
    "rec_async_W": "async (WTA first)",
}


def style(sizes=(8, 7, 6)) -> None:
    """Three-size role ladder; open frame; no chartjunk."""
    base, mid, small = sizes
    mpl.rcParams.update({
        "figure.dpi": 150, "savefig.dpi": 300,
        "savefig.bbox": "tight", "savefig.pad_inches": 0.02,
        "font.size": base, "axes.titlesize": base, "axes.labelsize": base,
        "legend.fontsize": mid, "xtick.labelsize": small, "ytick.labelsize": small,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.linewidth": 0.6, "xtick.major.width": 0.6, "ytick.major.width": 0.6,
        "xtick.major.size": 2.5, "ytick.major.size": 2.5,
        "axes.titlepad": 4.0, "axes.grid": False,
        "pdf.fonttype": 42, "ps.fonttype": 42,   # embed as TrueType, keep text editable
        "svg.fonttype": "none",                  # SVG text stays text, not paths
    })


def panel_letter(ax, letter: str) -> None:
    ax.text(-0.055, 1.14, letter, transform=ax.transAxes,
            fontsize=10, fontweight="bold", va="top", ha="right")


def stacked(ax, rows, title, xlab, bio_idx=None) -> None:
    """rows: list of (label, n, shortest_composite, composite_longer, no_composite)."""
    y = np.arange(len(rows))[::-1]
    labels = []
    for i, (lab, n, a, b, c) in enumerate(rows):
        fa, fb, fc = a / n, b / n, c / n
        yy = y[i]
        ec, lw = ((FOCAL, 1.0) if i == bio_idx else ("none", 0.0))
        ax.barh(yy, fa, color=C_SHORT, height=0.60, zorder=3, edgecolor=ec, linewidth=lw)
        ax.barh(yy, fb, left=fa, color=C_LONG, height=0.60, zorder=3, edgecolor=ec, linewidth=lw)
        ax.barh(yy, fc, left=fa + fb, color=C_NONE, height=0.60, zorder=3, edgecolor=ec, linewidth=lw)
        # a zero-width class still needs a visible stub, or it reads as absent
        for f, x0, col in ((fa, 0.0, C_SHORT), (fb, fa, C_LONG), (fc, fa + fb, C_NONE)):
            if f == 0:
                ax.plot([x0], [yy], marker="|", ms=5, mew=1.1, color=col, zorder=5)
        labels.append(f"{lab}\nn = {n:,}")
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.set_xlim(0, 1)
    ax.set_xticks([0, 0.5, 1.0])
    ax.set_xticklabels(["0", "0.5", "1"])
    ax.set_ylim(-0.55, len(rows) - 0.45)
    ax.set_title(title, loc="left")
    ax.set_xlabel(xlab)


def load_rows(indir: Path):
    strata = pd.read_csv(indir / "figure_strata.csv")

    def rows_for(sweep, order, labels):
        out = []
        for key in order:
            r = strata[(strata.sweep == sweep) & (strata.stratum == key)]
            if r.empty:
                raise SystemExit(f"missing stratum {sweep}/{key} in figure_strata.csv")
            r = r.iloc[0]
            out.append((labels[key], int(r.n), int(r.shortest_composite),
                        int(r.composite_longer), int(r.no_composite)))
        return out

    psi_rows = rows_for("psi", ["constant", "g_only", "winner_only", "both"], PSI_LABELS)
    phi_rows = rows_for("phi", ["constant", "partial", "injective"], PHI_LABELS)

    grid = pd.read_csv(indir / "rec_grid_counts.csv")
    rec_rows = []
    for scheme in ["rec_sync", "rec_async_D", "rec_async_W"]:
        g = grid[grid.scheme == scheme]
        n = int(g.n.sum())
        a = int(g.loc[g.witness_class == "composite", "n"].sum())
        b = int(g.loc[(g.has_composite.astype(str).str.lower() == "true")
                      & (g.witness_class != "composite"), "n"].sum())
        rec_rows.append((REC_LABELS[scheme], n, a, b, n - a - b))

    sizes = pd.read_csv(indir / "psi_monoid_size_counts.csv")
    with open(indir / "sweep_summary.json") as fh:
        summary = json.load(fh)
    bio_M = int(summary["bio_psi"]["monoid_size"])
    return psi_rows, phi_rows, rec_rows, sizes, bio_M


def build(psi_rows, phi_rows, rec_rows, sizes, bio_M):
    fig = plt.figure(figsize=(7.1, 4.6))
    gs = fig.add_gridspec(3, 2, width_ratios=[1.18, 1.0],
                          height_ratios=[1.0, 1.0, 0.16],
                          hspace=0.72, wspace=0.42,
                          left=0.20, right=0.965, top=0.905, bottom=0.06)
    axA = fig.add_subplot(gs[0, 0])
    axB = fig.add_subplot(gs[1, 0])
    axC = fig.add_subplot(gs[0, 1])
    axD = fig.add_subplot(gs[1, 1])
    axL = fig.add_subplot(gs[2, :])
    axL.axis("off")
    for s in axL.spines.values():
        s.set_visible(False)
    axL.set_frame_on(False)

    stacked(axA, psi_rows, r"What the DN reads: winner-pooling interface $\psi$",
            "fraction of interface maps", bio_idx=3)
    stacked(axB, phi_rows, r"What the WTA reads: drive interface $\varphi$",
            "fraction of interface maps", bio_idx=2)
    stacked(axC, rec_rows, "Update schedule, recurrent coupling",
            r"fraction of $(\varphi,\psi)$ pairs", bio_idx=None)

    # Panel d: monoid-size distribution over the psi sweep, from precomputed counts
    edges = np.logspace(np.log10(320), np.log10(23000), 46)
    axD.hist(sizes.monoid_size, bins=edges, weights=sizes.n_interfaces,
             color="#9fb6cc", edgecolor="none", zorder=3)
    axD.set_xscale("log")
    axD.set_ylim(0, 7100)
    axD.axvline(bio_M, color=FOCAL, lw=1.2, zorder=4)
    axD.text(0.95, 0.88, f"biological $\\psi$\n$|M|$ = {bio_M:,}",
             transform=axD.transAxes, fontsize=7, color=FOCAL, ha="right", va="top")
    axD.set_xlabel("transition-monoid size $|M|$")
    axD.set_ylabel("interface maps")
    axD.set_xticks([1000, 10000])
    axD.set_xticklabels(["$10^3$", "$10^4$"])
    axD.set_yticks([0, 2000, 4000, 6000])
    axD.set_yticklabels(["0", "2k", "4k", "6k"])
    axD.set_title(r"$\psi$ sweep: monoid sizes span two decades", loc="left")

    handles = [
        mpl.patches.Patch(fc=C_SHORT, ec="none", label="composite cycle; it is the shortest witness"),
        mpl.patches.Patch(fc=C_LONG, ec="none", label="composite cycle; a local cycle is shorter"),
        mpl.patches.Patch(fc=C_NONE, ec="none", label="no composite cycle in the monoid"),
        mpl.patches.Patch(fc="none", ec=FOCAL, lw=1.0, label="class holding the biological interface"),
    ]
    axL.legend(handles=handles, loc="center", ncol=2, frameon=False, fontsize=7,
               handlelength=1.1, handletextpad=0.5, labelspacing=0.34, columnspacing=1.4)

    for ax, L in ((axA, "a"), (axB, "b"), (axC, "c"), (axD, "d")):
        panel_letter(ax, L)
    return fig


def verify(fig) -> None:
    """Geometric check: no text-text or text-spine overlaps, nothing off-canvas."""
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    texts = [(t, t.get_window_extent(r)) for t in fig.findobj(mpl.text.Text)
             if t.get_text().strip() and t.get_visible()]
    ticklabels = {ax: set(ax.get_xticklabels(which="both") + ax.get_yticklabels(which="both"))
                  for ax in fig.axes}
    spines = [(s, s.get_window_extent(r)) for ax in fig.axes
              for s in ax.spines.values() if s.get_visible()]
    ov = [(a.get_text()[:30], b.get_text()[:30])
          for i, (a, ba) in enumerate(texts) for b, bb in texts[i + 1:] if ba.overlaps(bb)]
    ov += [(t.get_text()[:30], "spine") for t, bt in texts for s, bs in spines
           if bt.overlaps(bs) and t not in ticklabels[s.axes]]
    outside = [t.get_text()[:30] for t, bt in texts
               if not (fig.bbox.contains(bt.x0, bt.y0) and fig.bbox.contains(bt.x1, bt.y1))]
    print(f"overlaps: {ov}")
    print(f"outside canvas: {outside}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[3])
    ap.add_argument("--indir", type=Path, default=Path("../03_interface_sweep/expected_output"),
                    help="directory holding the sweep summary files")
    ap.add_argument("--outdir", type=Path, default=Path("."))
    ap.add_argument("--dpi", type=int, default=300, help="raster resolution for the PNG")
    ap.add_argument("--formats", default="png,pdf,svg",
                    help="comma-separated output formats (default png,pdf,svg)")
    args = ap.parse_args()

    style()
    fig = build(*load_rows(args.indir))

    args.outdir.mkdir(parents=True, exist_ok=True)
    for ext in [e.strip() for e in args.formats.split(",") if e.strip()]:
        path = args.outdir / f"sweep_figure.{ext}"
        # dpi is honoured by raster backends and ignored by the vector ones
        fig.savefig(path, dpi=args.dpi)
        print(f"wrote {path}")
    verify(fig)


if __name__ == "__main__":
    main()
