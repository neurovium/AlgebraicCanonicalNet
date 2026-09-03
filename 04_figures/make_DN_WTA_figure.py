#!/usr/bin/env python3
"""
make_DN_WTA_figure.py
=====================

Produces the main four-panel figure for the DN--WTA composition paper:

  (A) Architecture schematic of the three coupling schemes (product,
      DN->WTA cascade, WTA->DN cascade), with the headline WTA->DN system
      drawn in full.
  (B) Witness functional graphs on the product state grid (rows = DN state d,
      cols = WTA state w). Top: the WTA-alone witness cycle W:4<->W:5. Bottom:
      the genuinely composite WTA->DN witness (D:0,W:4)<->(D:1,W:5). The grid
      axes make "both coordinates change" visually unambiguous.
  (C) Rank distribution |Im(f)| over every element of the transition monoid,
      uncoupled product vs WTA->DN cascade -- showing the collapse structure
      that supports low-rank reversible images.
  (D) Structured-vs-null robustness bars: fraction of interfaces for which a
      composite cycle exists at all, and for which it is the SHORTEST witness,
      across product / passthrough / biological / random couplings.

Self-contained (embeds the validated generators); requires only numpy +
matplotlib. Outputs figure_DN_WTA.png (raster, 300 dpi) plus figure_DN_WTA.pdf
and figure_DN_WTA.svg (both vector); use --formats to select a subset.

    python make_DN_WTA_figure.py --n-random 100
"""

from __future__ import annotations

import argparse
import random
from collections import deque
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Circle

# ----------------------------------------------------------------------------
# Validated generators / maps (identical to compose_DN_WTA_audit.py)
# ----------------------------------------------------------------------------
DN = {0: (0, 0, 0, 0), 1: (1, 1, 0, 0), 2: (2, 1, 1, 1), 3: (3, 2, 2, 1)}
WTA = {0: (0, 0, 3, 1, 5, 1, 1, 1), 1: (4, 4, 7, 1, 5, 5, 5, 5),
       2: (2, 2, 3, 3, 7, 1, 3, 3), 3: (6, 6, 7, 3, 7, 5, 7, 7)}
N_D, N_W, N_DW = 4, 8, 32

def idx(d, w): return 8 * d + w
def dec(s): return divmod(s, 8)
def wbits(w): return ((w >> 2) & 1, (w >> 1) & 1, w & 1)
def compose(g, f): return tuple(g[f[x]] for x in range(len(f)))

def psi_winner_pool(g, w):
    b1, b2, gg = wbits(w)
    if gg == 1 or (b1 == 1 and b2 == 1): return 3
    if b1 == 1 and b2 == 0: return 1
    if b1 == 0 and b2 == 1: return 2
    return 0
def psi_gate_sensitive(g, w):
    _, _, gg = wbits(w); return 3 if gg == 1 else g[0]
def psi_passthrough(g, w): return g[0]

def shared_alpha(): return [(g, g) for g in range(4)]

def build_wta_to_dn(psi):
    gens = []
    for gamma in shared_alpha():
        j = gamma[1]; out = [0] * N_DW
        for d in range(N_D):
            for w in range(N_W):
                wp = WTA[j][w]; out[idx(d, w)] = idx(DN[psi(gamma, wp)][d], wp)
        gens.append(tuple(out))
    return gens

def build_independent_product():
    gens = []
    for gamma in shared_alpha():
        i, j = gamma; out = [0] * N_DW
        for d in range(N_D):
            for w in range(N_W):
                out[idx(d, w)] = idx(DN[i][d], WTA[j][w])
        gens.append(tuple(out))
    return gens

def enumerate_monoid(gens, n=N_DW):
    I = tuple(range(n)); seen = {I: ()}; q = deque([I])
    while q:
        cur = q.popleft()
        for k, g in enumerate(gens):
            t = compose(g, cur)
            if t not in seen:
                seen[t] = seen[cur] + (k,); q.append(t)
    return seen

def all_cycles(f):
    n = len(f); seen = [False] * n; out = []
    for s in range(n):
        if seen[s]: continue
        path = []; x = s
        while not seen[x]:
            seen[x] = True; path.append(x); x = f[x]
        if x in path:
            c = path[path.index(x):]
            if len(c) > 1: out.append(c)
    return out

def classify(c):
    ds = {dec(s)[0] for s in c}; ws = {dec(s)[1] for s in c}
    if len(ds) > 1 and len(ws) > 1: return "composite"
    if len(ds) > 1: return "DN_local"
    if len(ws) > 1: return "WTA_local"
    return "fixed"

def analyze(gens):
    M = enumerate_monoid(gens)
    any_comp = False; short_comp = None; short_any = None
    for t, word in M.items():
        cs = all_cycles(t)
        if not cs: continue
        L = len(word)
        for c in cs:
            cl = classify(c)
            if short_any is None or L < short_any[0]: short_any = (L, cl)
            if cl == "composite":
                any_comp = True
                if short_comp is None or L < short_comp: short_comp = L
    shortest_is_comp = (short_any is not None and short_any[1] == "composite")
    return len(M), any_comp, shortest_is_comp

# ----------------------------------------------------------------------------
# Style
# ----------------------------------------------------------------------------
plt.rcParams.update({
    "font.size": 9, "axes.titlesize": 10, "axes.labelsize": 9,
    "axes.spines.top": False, "axes.spines.right": False,
    "figure.dpi": 150, "savefig.dpi": 300,
    # Vector output: embed TrueType (editable, journal-safe) rather than Type 3,
    # and keep SVG text as text instead of converting glyphs to paths.
    "pdf.fonttype": 42, "ps.fonttype": 42, "svg.fonttype": "none",
})
C_DN = "#2c6fbb"      # divisive normalization
C_WTA = "#d1495b"     # winner-take-all
C_CYC = "#e07a00"     # highlighted composite cycle
C_GREY = "#b9b9b9"
C_PROD = "#8a8d91"
C_BIO = "#2a9d8f"
C_RAND = "#9d6db0"

# ----------------------------------------------------------------------------
# Panel A: architecture schematic
# ----------------------------------------------------------------------------
def panel_A(ax):
    ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis("off")
    ax.set_title("A   Coupling architectures", loc="left", fontweight="bold")

    def box(x, y, w, h, color, label):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08,rounding_size=0.15",
                                    linewidth=1.4, edgecolor=color, facecolor=color + "22"))
        ax.text(x + w / 2, y + h / 2, label, ha="center", va="center",
                color=color, fontweight="bold", fontsize=9)

    def arrow(x1, y1, x2, y2, color, lw=1.6, style="-|>", rad=0.0, label=None, ls="-"):
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style,
                                     mutation_scale=12, lw=lw, color=color,
                                     connectionstyle=f"arc3,rad={rad}", linestyle=ls))
        if label:
            ax.text((x1 + x2) / 2, (y1 + y2) / 2 + 0.35, label, ha="center",
                    va="bottom", color=color, fontsize=8, style="italic")

    # Main: WTA -> DN cascade (headline)
    ax.text(5, 9.4, "WTA\u2192DN cascade  (headline)", ha="center", fontsize=8.5, fontweight="bold")
    box(0.6, 7.0, 2.6, 1.5, C_WTA, "WTA")
    box(6.8, 7.0, 2.6, 1.5, C_DN, "DN")
    arrow(2.0, 8.9, 2.0, 8.55, "#444", label=r"drive $\gamma$")  # external in
    arrow(3.2, 7.75, 6.8, 7.75, C_WTA, label=r"$w'\!\to\!\psi$")  # WTA out to DN
    ax.text(5.0, 7.05, r"$\psi$: winner $\to$ normalization condition",
            ha="center", fontsize=7.2, color=C_WTA)
    arrow(8.1, 8.9, 8.1, 8.55, "#444", label=None)
    ax.text(8.1, 9.05, r"$\gamma$", ha="center", fontsize=8, color="#444")
    arrow(9.4, 7.75, 9.9, 7.75, C_DN, style="-|>")
    ax.text(9.7, 7.2, r"$(d',w')$", ha="center", fontsize=7.5, color=C_DN)

    # Three small icons
    iy = 3.7
    ax.text(5, 5.7, "coupling variants compared", ha="center", fontsize=8.5, fontweight="bold")
    # product
    box(0.4, iy, 1.4, 1.0, C_DN, "DN"); box(0.4, iy + 1.15, 1.4, 1.0, C_WTA, "WTA")
    ax.text(1.1, iy - 0.5, "product\n(no coupling)", ha="center", va="top", fontsize=7)
    # DN->WTA
    box(3.6, iy + 1.15, 1.4, 1.0, C_DN, "DN"); box(3.6, iy, 1.4, 1.0, C_WTA, "WTA")
    arrow(4.3, iy + 1.1, 4.3, iy + 1.02, C_DN, rad=0, style="-|>")
    ax.text(5.15, iy + 0.6, r"$\phi$", color=C_DN, fontsize=9)
    ax.text(4.3, iy - 0.5, "DN\u2192WTA\n(composite buried)", ha="center", va="top", fontsize=7)
    # WTA->DN
    box(6.9, iy + 1.15, 1.4, 1.0, C_WTA, "WTA"); box(6.9, iy, 1.4, 1.0, C_DN, "DN")
    arrow(7.6, iy + 1.1, 7.6, iy + 1.02, C_WTA, rad=0, style="-|>")
    ax.text(8.45, iy + 0.6, r"$\psi$", color=C_WTA, fontsize=9)
    ax.text(7.6, iy - 0.5, "WTA\u2192DN\n(composite at\nshortest witness)", ha="center", va="top", fontsize=7)
    # highlight WTA->DN icon
    ax.add_patch(FancyBboxPatch((6.55, iy - 0.25), 2.1, 2.65, boxstyle="round,pad=0.05",
                                linewidth=1.6, edgecolor=C_CYC, facecolor="none", linestyle="--"))

# ----------------------------------------------------------------------------
# Panel B: witness functional graphs on the state grid
# ----------------------------------------------------------------------------
def draw_grid_witness(ax, f, rows, title, cycle, sub_d=None):
    """f: transformation; rows: list of D rows to draw; cycle: set of cycle states."""
    cyc_edges = set()
    for c in all_cycles(f):
        if classify(c) in ("composite", "WTA_local"):
            for a, b in zip(c, c[1:] + c[:1]):
                cyc_edges.add((a, b))

    def pos(s):
        d, w = dec(s)
        return (w, -d)

    # nodes
    for d in rows:
        for w in range(N_W):
            s = idx(d, w)
            x, y = pos(s)
            on_cyc = s in cycle
            ax.add_patch(Circle((x, y), 0.16, facecolor=(C_CYC if on_cyc else "white"),
                                edgecolor=(C_CYC if on_cyc else "#888"),
                                lw=1.6 if on_cyc else 0.8, zorder=3))
            if on_cyc:
                d_, w_ = dec(s); b1, b2, g = wbits(w_)
                ax.text(x, y - 0.42, f"D{d_}\nW{w_}", ha="center", va="top",
                        fontsize=6.0, color=C_CYC, zorder=4)
    # edges (only non-fixed, to reduce clutter), cycle edges highlighted
    for d in rows:
        for w in range(N_W):
            s = idx(d, w); t = f[s]
            if t == s: continue
            if dec(t)[0] not in rows: continue
            x1, y1 = pos(s); x2, y2 = pos(t)
            hi = (s, t) in cyc_edges
            ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                         mutation_scale=8 if hi else 6,
                         lw=2.0 if hi else 0.6,
                         color=C_CYC if hi else C_GREY,
                         connectionstyle="arc3,rad=0.25", zorder=2 if hi else 1,
                         alpha=1.0 if hi else 0.55))
    ax.set_xlim(-0.7, 7.7)
    ax.set_ylim(min(-d for d in rows) - 0.9, max(-d for d in rows) + 0.7)
    ax.set_xticks(range(8)); ax.set_xticklabels([f"W{w}" for w in range(8)], fontsize=6.5)
    ax.set_yticks([-d for d in rows]); ax.set_yticklabels([f"D{d}" for d in rows], fontsize=7)
    ax.set_title(title, loc="left", fontsize=8.5)
    for sp in ax.spines.values(): sp.set_visible(False)
    ax.tick_params(length=0)

def panel_B(fig, gs):
    axt = fig.add_subplot(gs[0])
    axb = fig.add_subplot(gs[1])
    # WTA-alone witness embedded on D=0 row for display
    fw = compose(WTA[1], WTA[0])  # f10 . f00, cycle 4<->5
    f_embed = list(range(N_DW))
    for w in range(N_W):
        f_embed[idx(0, w)] = idx(0, fw[w])
    draw_grid_witness(axt, tuple(f_embed), rows=[0],
                      title="B   WTA alone: winner-gating cycle  W4\u2194W5  (D fixed)",
                      cycle={idx(0, 4), idx(0, 5)})
    # WTA->DN composite witness
    g = build_wta_to_dn(psi_winner_pool)
    fc = compose(g[1], g[0])  # g0 then g1
    cyc = set()
    for c in all_cycles(fc):
        if classify(c) == "composite":
            cyc |= set(c)
    draw_grid_witness(axb, fc, rows=[0, 1, 2, 3],
                      title="     WTA\u2192DN: composite cycle  (D:0,W4)\u2194(D:1,W5)  (both change)",
                      cycle=cyc)

# ----------------------------------------------------------------------------
# Panel C: rank distribution
# ----------------------------------------------------------------------------
def panel_C(ax):
    prod = enumerate_monoid(build_independent_product())
    casc = enumerate_monoid(build_wta_to_dn(psi_winner_pool))
    rp = [len(set(f)) for f in prod]
    rc = [len(set(f)) for f in casc]
    bins = np.arange(0.5, N_DW + 1.5, 1)
    ax.hist(rc, bins=bins, color=C_WTA, alpha=0.75, label=f"WTA\u2192DN  (|M|={len(casc)})")
    ax.hist(rp, bins=bins, color=C_PROD, alpha=0.7, label=f"product  (|M|={len(prod)})")
    ax.set_xlabel(r"rank  $|\mathrm{Im}(f)|$"); ax.set_ylabel("# monoid elements")
    ax.set_title("C   Rank distribution of the monoid", loc="left", fontweight="bold")
    ax.set_xlim(0, 33)
    ax.legend(frameon=False, fontsize=7.5, loc="upper right")
    ax.text(0.02, 0.96, "reversible cycles live\non low-rank images",
            transform=ax.transAxes, fontsize=7, color="#555", va="top")

# ----------------------------------------------------------------------------
# Panel D: structured vs null robustness bars
# ----------------------------------------------------------------------------
def panel_D(ax, n_random, seed0):
    def shuffled_psi(s):
        vals = [psi_winner_pool((0, 0), w) for w in range(8)]
        random.Random(s).shuffle(vals); mp = {w: vals[w] for w in range(8)}
        return lambda g, w: mp[w]
    def uniform_psi(s):
        r = random.Random(s); mp = {w: r.randrange(4) for w in range(8)}
        return lambda g, w: mp[w]

    cats, any_frac, short_frac, colors = [], [], [], []

    def det(name, gens, color):
        _, ac, sc = analyze(gens)
        cats.append(name); any_frac.append(100.0 * ac); short_frac.append(100.0 * sc); colors.append(color)

    det("product", build_independent_product(), C_PROD)
    det("passthrough", build_wta_to_dn(psi_passthrough), C_PROD)
    det("winner_pool\n(bio)", build_wta_to_dn(psi_winner_pool), C_BIO)
    det("gate_sensitive\n(bio)", build_wta_to_dn(psi_gate_sensitive), C_BIO)

    def rand(name, gen, base, color):
        a = s = 0
        for k in range(n_random):
            _, ac, sc = analyze(build_wta_to_dn(gen(base + k)))
            a += ac; s += sc
        cats.append(name); any_frac.append(100.0 * a / n_random)
        short_frac.append(100.0 * s / n_random); colors.append(color)

    rand(f"shuffled\n(n={n_random})", shuffled_psi, seed0, C_RAND)
    rand(f"uniform\n(n={n_random})", uniform_psi, seed0 + 50000, C_RAND)

    x = np.arange(len(cats)); w = 0.38
    ax.bar(x - w / 2, any_frac, w, color=colors, edgecolor="k", lw=0.4, label="any composite cycle exists")
    ax.bar(x + w / 2, short_frac, w, color=colors, alpha=0.45, edgecolor="k", lw=0.4,
           hatch="///", label="composite is shortest witness")
    ax.set_xticks(x); ax.set_xticklabels(cats, fontsize=6.6)
    ax.set_ylabel("% of interfaces"); ax.set_ylim(0, 112)
    ax.set_title("D   Composite cycle: existence vs accessibility (WTA\u2192DN)",
                 loc="left", fontweight="bold")
    ax.axhspan(0, 0.5, color="none")
    # legend via proxies
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(facecolor="#777", label="any composite cycle exists"),
                       Patch(facecolor="#777", alpha=0.45, hatch="///", label="composite is shortest witness")],
              frameon=False, fontsize=7, loc="lower center", bbox_to_anchor=(0.5, -0.02))
    for xi, a in zip(x, any_frac):
        ax.text(xi - w / 2, a + 2, f"{a:.0f}", ha="center", fontsize=6.2)

# ----------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-random", type=int, default=100)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--outdir", type=Path, default=Path("."))
    ap.add_argument("--dpi", type=int, default=300, help="raster resolution for the PNG")
    ap.add_argument("--formats", default="png,pdf,svg",
                    help="comma-separated output formats (default png,pdf,svg)")
    args = ap.parse_args()

    fig = plt.figure(figsize=(11, 8.2), constrained_layout=True)
    outer = fig.add_gridspec(2, 2)
    panel_A(fig.add_subplot(outer[0, 0]))
    # Panel B is two stacked subplots in the top-right cell
    gsB = outer[0, 1].subgridspec(2, 1, height_ratios=[1, 2.4], hspace=0.45)
    panel_B(fig, gsB)
    panel_C(fig.add_subplot(outer[1, 0]))
    panel_D(fig.add_subplot(outer[1, 1]), args.n_random, args.seed)

    fig.suptitle("Composition of divisive normalization and winner-take-all: "
                 "emergence of a genuinely composite reversible component",
                 fontsize=11, fontweight="bold")

    args.outdir.mkdir(parents=True, exist_ok=True)
    for ext in [e.strip() for e in args.formats.split(",") if e.strip()]:
        path = args.outdir / f"figure_DN_WTA.{ext}"
        # dpi applies to the raster backend; the vector backends ignore it
        fig.savefig(path, bbox_inches="tight", dpi=args.dpi)
        print(f"wrote {path}")

if __name__ == "__main__":
    main()
