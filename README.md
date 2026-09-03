# AlgCanNet — final code and results

**Algebraic Emergence of Effective Theories in Canonical Recurrent Motifs of
Biological Neuronal Networks** — complete, verified code and expected outputs
for every numerical experiment in the paper.

## Scientific summary

Two canonical cortical motifs are modeled as finite-state machines: divisive
normalization (DN) — pooled-activity gain control in which a shared
inhibitory pool rescales each unit's drive (Carandini & Heeger 2012) — and
winner-take-all competition (WTA) — recurrent excitation with a common
inhibitory pool that gates and selects a winner (Hahnloser et al. 2000; Wang
2002). Each motif's input symbols act as transformations of its state set,
generating a **transition monoid**: the full algebra of state changes the
circuit can express. The central result is compositional: when the WTA's
winner/gate state is pooled into the DN's drive (the biological
winner-pooling interface), the composite circuit's monoid contains
**reversible, group-like structure that neither motif has at that locus and
that no single generator carries** — all four primitive generators are
aperiodic, yet the generated monoid contains hundreds of non-aperiodic
elements, and the shortest witness word cycles two states differing in *both*
the normalization and the competition coordinate. This structure is (i)
certified by full holonomy (Krohn–Rhodes) decomposition in GAP/SgpDec — the
composite swap appears as a genuine C2 group component on singleton tiles,
absent in the independent-product control — and (ii) shown by exhaustive
enumeration of all interface maps to be a property of the *coupling
direction*, not of the specific interface.

## Repository layout

```
environment/          conda env + GAP/SgpDec build instructions (read first)
01_monoid_audit/      Python transition-monoid audit  -> paper Table I
02_holonomy/          GAP/SgpDec holonomy decompositions + compositeness control
03_interface_sweep/   exhaustive psi/phi/schedule sweeps -> Results robustness numbers
04_figures/           Fig. 1-4 generators (TikZ + matplotlib); PNG + PDF + SVG
```

Each experiment directory contains an `EXPERIMENT.md` (purpose, math, exact
commands, runtime, expected numbers, paper mapping, pitfalls) and an
`expected_output/` folder with the actual result files, so every claim can be
checked without recomputation.

## Results at a glance

Transition-monoid audit (experiment 01; = paper Table I):

| system | states | \|M\| | idempotents | non-aperiodic | shortest witness class |
|---|---|---|---|---|---|
| DN3 | 3 | 13 | 6 | 3 | DN-local (units ≅ Z₂) |
| DN4 | 4 | 24 | 8 | 3 | DN-local |
| WTA | 8 | 326 | 55 | 49 | WTA-local, cycle (4,5) |
| prod (independent) | 32 | 576 | 103 | 88 | WTA-local, cycle (12,13) |
| D_to_W cascade | 32 | 3149 | 274 | 401 | WTA-local, cycle (12,13) |
| **W_to_D cascade** | 32 | **3084** | 186 | **361** | **composite, cycle (4,13) = (D:0,W:4) ↔ (D:1,W:5)** |
| rec_sync | 32 | 9 | 2 | 6 | composite 3-cycle (generators themselves non-aperiodic) |
| rec_async_D | 32 | 8 | 2 | 0 | — (aperiodic monoid) |
| rec_async_W | 32 | 8 | 2 | 0 | — (aperiodic monoid) |

Holonomy certification (experiment 02): the W_to_D pair {4,13} carries
permutator/holonomy **C2 on singleton tiles at depth 17**; the
independent-product control has **0 composite windows of 34** with a
nontrivial group (27 WTA-only, 7 DN-only). Exhaustive robustness (experiment
03), the three headline fractions:

- composite cycle present in **65,278 / 65,532 = 0.9961** of coupled ψ
  interfaces (absence characterized exactly: image(ψ) ⊆ {1,2} or constant
  extremes; 258 maps total);
- shortest witness composite in **43,008 / 65,532 = 65.6%** of coupled ψ
  interfaces (vs 11.9% in the reverse coupling direction — legibility tracks
  direction);
- **0 of 50,331,648** recurrent (φ, ψ, schedule) cases produce a
  non-aperiodic monoid from four aperiodic generators.

## Quick start

Environment build (one-time): see `environment/README_environment.md` — a
conda env with Python 3.12 + GAP 4.15.1, then `build_gap_pkgs.sh` for
SgpDec 1.2.0 / Semigroups 5.6.3 (two conda-forge-specific fixes documented
there).

```bash
# (1) verify the environment
P=/home/nimad/miniforge3/envs/algcanet; export PATH=$P/bin:$PATH
gap -q -A -c 'LoadPackage("sgpdec", false); Print("sgpdec ok\n"); QUIT;'

# (2) run the audit (~30 s) and check it reproduces Table I exactly
cd 01_monoid_audit
PYTHONPATH=$PWD python audit.py
diff audit_results.json expected_output/audit_results.json && echo IDENTICAL

# (3) GAP holonomy (small systems: seconds-to-minutes; W_to_D skeleton is the
#     long pole at tens of minutes; transcript.g needs -o 8g)
cd ../02_holonomy
gap -q -A holonomy.g
gap -q -A compositeness.g
gap -q -A -o 8g transcript.g

# (4) the sweep — honest cost: the exhaustive 65,536-psi sweep plus the
#     50,331,648-case recurrent grid took ~6.5 h wall on 20 cores. The
#     1-minute verification suite checks the enumeration core instead:
cd ../03_interface_sweep
cp ../01_monoid_audit/audit.py ../01_monoid_audit/expected_output/audit_results.json .
PYTHONPATH=$PWD python verify_fast.py       # ~1 min: core vs audit, 9/9 systems
# full sweep commands + schemas: 03_interface_sweep/EXPERIMENT.md
```

**Verified on 2026-08-14** in the `algcanet` env on this machine:
(a) `audit.py` output is byte-identical to
`01_monoid_audit/expected_output/audit_results.json` (`diff` clean;
stdout: DN_3state |M|=13, DN_4state |M|=24, WTA |M|=326, prod |M|=576,
D_to_W |M|=3149, W_to_D |M|=3084, rec_sync |M|=9, rec_async_D |M|=8,
rec_async_W |M|=8);
(b) GAP smoke test — `LoadPackage("sgpdec")` true, `Read("gap_systems.g")`,
`Size(Monoid(gens_WTA)) = 326`, `Size(Monoid(gens_W_to_D)) = 3084`,
`Size(Monoid(gens_D_to_W)) = 3149`, `Size(Monoid(gens_prod)) = 576`,
`DepthOfSkeleton(WTA) = 7`;
(c) `make_DN_WTA_figure.py --n-random 100` regenerates
`figure_DN_WTA.{png,pdf,svg}` with no external inputs.

## Which file backs which paper claim

| paper claim (Results) | number | where it lives |
|---|---|---|
| Table I, all rows ("Transition-monoid audit of DN, WTA, and DN–WTA composite systems") | \|M\|, idempotents, non-aperiodic per system | `01_monoid_audit/expected_output/audit_results.json` |
| "every primitive composite generator is aperiodic, but the generated monoid contains non-aperiodic elements, and the shortest witness changes both the DN and WTA coordinates" | W_to_D: 361 non-aperiodic, witness cycle (4,13) | same file, `W_to_D` entry; certified in `02_holonomy/expected_output/holonomy_results.csv` |
| the composite swap is a genuine holonomy group component (not inherited) | {4,13}: C2 on singleton tiles, depth 17; prod control 0/34 composite | `02_holonomy/expected_output/holonomy_results.csv`, `compositeness_all.csv`, `gap_transcript.txt` |
| "A composite cycle is present for 65,278 of the 65,536 maps, and for 65,278 of the 65,532 coupled maps, a fraction of 0.9961" | 0.996124 | `03_interface_sweep/expected_output/sweep_summary.json`, `charac.json` |
| "A composite cycle is absent precisely when the interface never delivers either extreme drive symbol … 258 maps in total, of which 254 are coupled. This is an exact characterization" | 256 + 1 + 1 = 258; zero exceptions | `charac.json` |
| "composite for 43,008 interfaces and competition-local for 22,528 … 65.6% of coupled interfaces, a majority rather than a signature" | 43,008/65,532 = 0.656290 | `sweep_summary.json`, strata in `sweep_summary.csv` |
| "its monoid size of 3084 sits at the 95.7th percentile, with only 2816 interfaces generating a larger algebra" | 95.7; 2,816 | `sweep_summary.json` (`bio_psi` block) |
| reverse direction: "composite cycles are present for 224 of the 252 coupled maps … but the shortest witness is composite for only" 30/252 | 0.889 vs 0.119 | `sweep_summary.json` (`step3a_phi` block), `charac.json` |
| "in none of the 50,331,648 recurrent cases does a non-aperiodic monoid arise from four aperiodic generators" | 0 / 50,331,648 | `schedule_summary.csv`, `rec_grid_counts.csv` |
| "asynchrony lowers the composite-cycle rate from 0.514 to 0.374 rather than to zero, leaving 6,274,480 cases per asynchronous scheme" | 0.5136 → 0.3740; 6,274,480 | `schedule_summary.csv` |
| Fig. 1 (motif/composition schematic) | — | `04_figures/motif_schematic_tikz.tex` → `motif_schematic.{pdf,svg,png}` |
| Fig. 2 (witness cycles, functional graphs) | — | `04_figures/gen_witness_figure.py` → `witness_figure_tikz.tex` → `witness_figure.{pdf,svg,png}` |
| Fig. 3 (rank distributions + holonomy windows) | — | `04_figures/make_rank_window_figure.py` → `rank_window_figure.{png,pdf,svg}` |
| Fig. 4 (`fig:sweep`) | — | `04_figures/make_sweep_figure.py` → `sweep_figure.{png,pdf,svg}` from experiment 03 outputs |
| (superseded) original 4-panel figure | — | `04_figures/make_DN_WTA_figure.py` → `figure_DN_WTA.{png,pdf,svg}`; kept as provenance |
| supplementary GAP session | — | `02_holonomy/expected_output/gap_transcript.txt` (regenerated by `transcript.g`) |

## Data formats

- `audit_results.json` — list of 9 objects, one per system: `label, n,
  n_gens, gens` (zero-based transformation tuples), `gens_all_aperiodic,
  gens_aperiodic, monoid_size, n_idempotents, n_nonaperiodic, units,
  rank_dist, rank_dist_nonaperiodic, witness_word, witness, witness_cycles`.
- `holonomy_results.csv` — one row per (system, level, slot):
  `system, degree, monoid_order, depth, level, slot, group_order,
  structure_description, is_nontrivial, rep_support_size, n_tiles,
  rep_support_paper, tiles_paper` (supports decoded to zero-based paper
  states).
- `holonomy_compositeness.csv` / `compositeness_all.csv` — one row per image
  set ("window") with a nontrivial permutator group: `system, window_size,
  depth, is_representative, permutator_order, permutator_sd, holonomy_order,
  holonomy_sd, n_tiles, classification` (W-ONLY-inherited / D-ONLY-inherited
  / COMPOSITE), `moves_D, moves_W, composite_pairs, window_paper`.
- `sweep_summary.json` — nested headline numbers (`step1` = ψ sweep,
  `bio_psi`, `step3a_phi`, schedule blocks); `sweep_summary.csv` — ψ-stratum
  table; `schedule_summary.csv` — one row per recurrent scheme;
  `rec_grid_counts.csv` — counts over (scheme, φ class, ψ class, witness
  class, has_composite, generator-level flag); `charac.json` — the exact
  absence characterization; `rec_grid.json` — raw grid aggregates.
- Large regenerated files (not shipped): `psi_sweep.jsonl` (~40 MB),
  `interface_sweep.csv` (~28 MB) — schemas and first rows in
  `03_interface_sweep/EXPERIMENT.md`.
- GAP indexing: **one-based** — GAP point p = paper state p−1; composite
  states are s = 8·d + w. All shipped CSVs already decode to paper
  coordinates.

## Figure formats

Both figure scripts write three files per figure: a 300-dpi PNG for quick
viewing, and a PDF and SVG that are true vector output (no embedded rasters,
TrueType-embedded editable text, no Type 3 fonts). The manuscript includes the
PDFs; the SVGs are for editing in Illustrator or Inkscape. Select a subset with
`--formats` and change raster resolution with `--dpi`.

## Caveats (read before quoting numbers)

1. **Tiles vs states.** Holonomy groups act on *tiles* of an image set, not
   raw states; only singleton tiles permute individual circuit states. The
   paper's key components ({4,13} in W_to_D, {4,5} in WTA, {0,1} in DN4) have
   singleton tiles; WTA's level-2 C2 has size-3 tiles and must not be
   described as permuting states.
2. **Transversal representatives.** {4,13} (W_to_D), {2,3} (WTA) and {1,2}
   (DN4) are not SgpDec transversal representatives: they carry their
   subduction class's group but do not appear in `GroupComponents` output
   (the printed representatives are {10,19}, {4,5} and {0,1} respectively).
3. **W_to_D cascade not machine-verified.** The holonomy *skeleton* of
   W_to_D (depth 22, 92 components, 5 groups) is exact, but the explicit
   cascade could not be reconstructed (≈5.78×10²¹-tuple state space; a single
   cascade element exhausts 14 GB). Elementwise faithfulness was verified for
   all elements of 7/9 systems and a 125-element sample of D_to_W.
4. **D_to_W's {12,13} is WTA-local/inherited**, not composite; only W_to_D's
   {4,13} is the composite pair. rec_sync carries **C3, not C2**, and its
   generators are individually non-aperiodic.
5. **Sampled vs exhaustive robustness.** The superseded original figure's panel D uses the original
   sampled control (n = 100, ~74%/70%); the exhaustive sweep numbers
   (0.9961 presence, 65.6% legibility) supersede it and are consistent with
   it (binomial SE ≈ 4.7% at n = 100). See `provenance/ORIGINAL_CODE.md`.
6. **The biological ψ is not a typical draw** (\|M\| at the 95.7th
   percentile), and legibility is a 65.6% *majority* property of coupled ψ —
   unique to the coupling *direction*, not the specific interface.
   Asynchrony *reduces* (0.514 → 0.374) rather than eliminates composite
   cycles; the complete elimination at the biological operating point does
   not generalize.
7. **Monoid vs Semigroup in GAP.** `Semigroup(gens)` omits the identity
   unless it is a generator product; all orders here use `Monoid(gens)`.
   Cite the elementwise faithfulness round-trip, not the setwise
   `AsSortedList` comparison (which differs by exactly the identity on six
   systems and is unproven for the two large cascades).

