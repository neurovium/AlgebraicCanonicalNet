# Experiment 04 — Figures

## Figure 1 (schematic) (`motif_schematic_tikz.tex` → `motif_schematic.{pdf,svg,png}`)

The manuscript's Fig. 1 is a TikZ circuit schematic of the two motifs and their
four compositions (DN with divisive pool feedback; WTA with self-excitation,
mutual inhibition, and the shared inhibitory gate; product / two cascades /
recurrent, with the WTA→DN cascade highlighted). It is compiled in-document by
`main.tex` via `\input`. To render it alone:

```bash
conda activate algcanet
tectonic motif_schematic_standalone.tex
pdftocairo -svg motif_schematic_standalone.pdf motif_schematic.svg
pdftocairo -png -r 300 -singlefile motif_schematic_standalone.pdf motif_schematic
```

Requires TikZ libraries `arrows.meta`, `calc`. Glyph conventions: arrowhead =
excitatory/drive, bar terminal = inhibitory/divisive; colors match the data
figures (DN blue, WTA red, headline orange).

## Figure 2 (`witness_figure_tikz.tex` → `witness_figure.{pdf,svg,png}`) — witness cycles

Generated TikZ: `gen_witness_figure.py` computes the witness transformations
from the audited generators (`audit.py` + `audit_results.json`), **verifies
their cycles against the audit**, and emits one TikZ node/edge per
state/transition — the arrows cannot drift from the data. Three panels:
(a) the state-decoding table (WTA code w = 4x1+2x2+y with circuit readings,
composite index 8d+w); (b) the WTA witness h = f_W10∘f_W00 as a functional
graph on 8 states with the {4,5} gate-toggle cycle highlighted (and the
symmetric {2,3} cycle noted); (c) the composite witness t = G1∘G0 on the 4×8
product grid with the (D:0,W:4)↔(D:1,W:5) cycle highlighted.

```bash
conda activate algcanet
cd 04_figures
PYTHONPATH=$PWD python gen_witness_figure.py \
    --audit ../01_monoid_audit/expected_output/audit_results.json
tectonic witness_figure_standalone.tex
pdftocairo -svg witness_figure_standalone.pdf witness_figure.svg
pdftocairo -png -r 300 -singlefile witness_figure_standalone.pdf witness_figure
```

The generator asserts: WTA witness cycle = (4,5), symmetric = (2,3),
composite cycle = (4,13). A drifted audit file fails loudly.

## Figure 3 (`make_rank_window_figure.py` → `rank_window_figure.{png,pdf,svg}`) — ranks and windows

Successor to panels C–D of the original figure, extended from one system to
the full three-scheme contrast:
(a–c) rank distribution with non-aperiodic overlay for product / DN→WTA /
WTA→DN (from `audit_results.json`, experiment 01);
(d) all group-carrying holonomy windows per scheme classified as
WTA-only / DN-only / composite (from
`../02_holonomy/expected_output/compositeness_all.csv`, experiment 02):
0/34 composite in the product, 15/46 in DN→WTA, 35/57 in WTA→DN.
The script asserts those totals before writing anything.

```bash
conda activate algcanet
cd 04_figures
PYTHONPATH=$PWD python make_rank_window_figure.py \
    --audit ../01_monoid_audit/expected_output/audit_results.json \
    --windows ../02_holonomy/expected_output/compositeness_all.csv
```

## Figure 4 (`sweep_figure.png` / `.pdf` / `.svg`) — exhaustive sweep figure

Produced by `make_sweep_figure.py`. It reads only small precomputed summary
tables, so it renders in about a second and needs **no sweep re-run**:

```bash
conda activate algcanet
cd 04_figures
PYTHONPATH=$PWD python make_sweep_figure.py \
    --indir ../03_interface_sweep/expected_output --outdir .
# writes sweep_figure.png (raster, 300 dpi), .pdf and .svg (both vector),
# then runs a geometric check for text overlaps and off-canvas labels
```

Inputs, all in `03_interface_sweep/expected_output/`:
`figure_strata.csv` (per-stratum three-way counts for ψ and φ),
`psi_monoid_size_counts.csv` (monoid-size histogram over the 65,536 ψ maps),
`rec_grid_counts.csv` (recurrent grid counts), and `sweep_summary.json`
(only for the biological \|M\| marker). The first two are derived from the
full `interface_sweep.csv` — regenerate them with the snippet in
`03_interface_sweep/EXPERIMENT.md` if you re-run the sweep.

Four panels summarizing experiment 03: composite-cycle presence and shortest-witness
legibility across the exhaustive ψ enumeration and strata, the reverse (φ)
direction contrast, and the recurrent schedule grid. This is the figure the
merged draft references as `fig:sweep`.

## Superseded: `figure_DN_WTA.{png,pdf,svg}` (original four-panel figure)

**No longer used by the manuscript.** Its four panels were redesigned into
three dedicated figures (see below): panel A became the TikZ motif schematic
(Fig. 1), panel B grew into the witness/functional-graph figure (Fig. 2),
and panels C–D became the rank/window data figure (Fig. 3), which replaces
the sampled robustness bars of panel D with the exhaustive-sweep figure
(Fig. 4). The script and outputs are kept as provenance of the original
pipeline.

Produced by `make_DN_WTA_figure.py` (copied verbatim from the original
pipeline, `Code/Original/add-on/`). The script is **self-contained**: it
embeds the validated DN and WTA generators (identical to those in
`compose_DN_WTA_audit.py` and `audit.py`) and needs only numpy + matplotlib —
no input files.

```bash
conda activate algcanet
cd 04_figures
PYTHONPATH=$PWD python make_DN_WTA_figure.py --n-random 100
# writes figure_DN_WTA.png (raster, 300 dpi), .pdf and .svg (both vector)
# to --outdir (default: cwd). Use --formats/--dpi to change that, e.g.
#   --formats pdf          only the vector PDF
#   --formats png --dpi 600  a 600-dpi raster only
```

Runtime ≈ 1–2 minutes (panel D enumerates monoids for 100 shuffled + 100
random interfaces). Verified to regenerate in this environment (2026-08-14).

Panels:

- **(A) Architecture schematic** of the three coupling schemes — independent
  product, DN→WTA cascade, WTA→DN cascade — with the headline WTA→DN system
  drawn in full: the WTA's winner/gate state is pooled by ψ into a drive
  symbol for divisive normalization, the shared drive α feeding both motifs.
- **(B) Witness functional graphs** on the product state grid (rows = DN
  state d, cols = WTA state w). Top: the WTA-alone witness cycle W:4 ↔ W:5.
  Bottom: the genuinely composite WTA→DN witness (D:0,W:4) ↔ (D:1,W:5). The
  grid makes "both coordinates change" visually unambiguous. Data source:
  the audit's witness cycles (experiment 01).
- **(C) Rank distribution** \|Im(f)\| over every element of the transition
  monoid, uncoupled product vs WTA→DN cascade — the collapse structure that
  supports low-rank reversible images. Data source: monoid enumeration
  (recomputed internally; agrees with `audit_results.json` rank_dist).
- **(D) Structured-vs-null robustness bars**: fraction of interfaces with a
  composite cycle at all, and with it as the shortest witness, across
  product / passthrough / biological / random couplings. **Note: this panel
  is SAMPLED** (`--n-random 100` shuffled and uniform ψ draws, seed 0),
  reproducing the original pipeline's control (~74% / ~70%). The exhaustive
  sweep of experiment 03 supersedes these numbers with 65,278/65,532 = 99.6%
  (presence) and 43,008/65,532 = 65.6% (shortest-witness legibility) over
  *all* coupled ψ; the sampled bars are consistent with the exhaustive values
  (binomial SE ≈ 4.7% at n = 100). See `provenance/ORIGINAL_CODE.md`,
  reconciliation 3.

## Pitfalls

- Panel D's sampled fractions must not be quoted as the paper's robustness
  numbers; the exhaustive numbers from experiment 03 are the ones in the
  Results text.
- `make_DN_WTA_figure.py --seed` changes panel D's draws only; panels A–C are
  deterministic.
