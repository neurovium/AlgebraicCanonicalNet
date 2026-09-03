# Experiment 03 — Exhaustive interface-robustness sweep

## Purpose, in plain language

Is the composite reversible structure a property of the *specific* biological
interface (winner-pooling: the DN pool reads out which unit won the
competition and whether the gate is open), or of *coupling as such*? This
experiment replaces the sampled robustness control of the original pipeline
(n = 100 random interfaces) with **exhaustive enumeration**:

- **ψ sweep**: all 4⁸ = 65,536 maps ψ : X_W → {0,1,2,3} (WTA state → DN drive
  symbol), scheme W_to_D. Every one of the 8 arguments is live (the four WTA
  generators are jointly surjective onto X_W), and the 65,536 maps give
  65,536 distinct generator tuples — the interface space does not collapse.
- **φ sweep**: all 4⁴ = 256 maps φ : X_D → {0,1,2,3} (DN state → WTA drive),
  scheme D_to_W.
- **Recurrent grid**: the full 256 × 65,536 × 3 = 50,331,648 (φ, ψ, schedule)
  grid for rec_sync / rec_async_D / rec_async_W, plus 111,360 row-level
  records (256 φ × 145 stratified ψ × 3 schemes).

For every case: exact monoid closure, aperiodicity, and an *uncapped*
Cayley-graph BFS for the shortest witness word, with each cycle classified as
DN-local (only the normalization coordinate changes), WTA-local (only the
competition coordinate changes), or **composite** (both change).

## The code

- `fastmon.py` — enumeration core. Elements are `bytes` of length n;
  composition (f∘g)(x) = f(g(x)) is `g.translate(table(f))`, pushing the hot
  loop into C. Aperiodicity via f³² == f³³ by repeated squaring.
- `sweep.py` — generator constructions for all schemes and the three sweep
  drivers (`run_psi_sweep`, `run_phi_sweep`, `run_rec_grid`, `run_rec_rows`),
  multiprocessing over all cores.
- `analyse.py` — aggregates the raw sweeps into `sweep_summary.{json,csv}`,
  `schedule_summary.csv`, `rec_grid_counts.csv`, `interface_sweep.csv`, and
  pickled dataframes for verification.
- `verify_fast.py` — checks `fastmon` element-for-element against `audit.py`
  on all nine audited systems (monoid sets identical; \|M\|, idempotents,
  non-aperiodic count, units, witnesses all reproduce `audit_results.json`).
- `verify_findings.py` — re-derives 102 numbers quoted in `findings.md`
  straight from the sweep outputs; expected result: 0 failures.

## How to run

```bash
conda activate algcanet
cd 03_interface_sweep
cp ../01_monoid_audit/audit.py ../01_monoid_audit/expected_output/audit_results.json .

# 1. quick verification of the enumeration core (~1 min)
PYTHONPATH=$PWD python verify_fast.py

# 2. the sweeps (WARNING: the full grid is the expensive part)
PYTHONPATH=$PWD python -c "import sweep; sweep.run_psi_sweep()"    # ~20 min, 20 cores
PYTHONPATH=$PWD python -c "import sweep; sweep.run_phi_sweep()"    # seconds
PYTHONPATH=$PWD python -c "import sweep; sweep.run_rec_grid()"     # bulk of the ~6.5 h
PYTHONPATH=$PWD python -c "import sweep; sweep.run_rec_rows()"     # ~minutes

# 3. aggregation + verification
PYTHONPATH=$PWD python analyse.py
PYTHONPATH=$PWD python verify_findings.py    # expects findings.md in cwd
```

**Honest cost statement**: the complete pipeline (65,536-map ψ sweep +
50,331,648-case recurrent grid + row-level records + aggregation) took
**≈6.5 hours wall-clock on 20 cores** (Python 3.12, multiprocessing). Memory
stays modest (a few GB total across workers; each case's monoid is ≤22,581
elements on 32 states). If you only want to *check* the machinery, run
`verify_fast.py` (~1 min); if you want to check the *numbers*, the shipped
`expected_output/` files plus `verify_findings.py` do so without re-sweeping.

## Large raw outputs (regenerated, not shipped)

Two raw files are deliberately **not** in this repository; both are recreated
by the sweep commands above:

- `psi_sweep.jsonl` (~40 MB, 65,536 lines) — one JSON object per ψ. Fields:
  `monoid_size, n_idempotents, n_nonaperiodic, n_units, units_trivial,
  classes_present, has_composite, has_dn_local, has_wta_local,
  gens_all_aperiodic, n_gens_nonaperiodic, witness_word, witness_len,
  witness_cycles, witness_class, comp_witness_word, comp_witness_len,
  comp_witness_cycles, shortest_is_composite, psi_code, psi, psi_class,
  psi_nvals, is_bio_psi`. First row (ψ = constant 0):
  `{"monoid_size": 326, "n_idempotents": 55, ..., "witness_word": ["g0","g1"],
  "witness_cycles": [[4, 5]], "witness_class": "WTA-local", "psi": "00000000",
  "psi_class": "constant", "is_bio_psi": false}`
  (`phi_sweep.jsonl`, 256 lines, has the same shape with `phi_*` keys.)
- `interface_sweep.csv` (~28 MB, 65,536 + 256 + 111,360 rows) — the unified
  row-level table over ψ sweep, φ sweep and recurrent row records. Header:
  `sweep,scheme,psi,psi_code,psi_class,psi_nvals,phi,phi_code,phi_class,
  phi_nvals,is_bio_psi,is_bio_phi,is_bio,monoid_size,n_idempotents,
  n_nonaperiodic,n_units,units_trivial,gens_all_aperiodic,n_gens_nonaperiodic,
  classes_present,has_composite,has_dn_local,has_wta_local,witness_word,
  witness_len,witness_cycles,witness_class,shortest_is_composite,
  comp_witness_word,comp_witness_len,comp_witness_cycles`. First data row:
  `psi_W_to_D,,00000000,0.0,constant,1.0,...,326,55,49,1,True,True,0,
  WTA-local,False,False,True,"g0,g1",2.0,"(4,5)",WTA-local,False,,,`

## Expected results (headline numbers, in `expected_output/`)

**ψ sweep** (`sweep_summary.json`, strata in `sweep_summary.csv`):

- \|M\| ranges 326–22,581, median 832. All 65,536 interfaces have four
  aperiodic generators and a trivial group of units; **0** generate an
  aperiodic monoid.
- Composite cycle present: 65,278 / 65,536 overall; **65,278 / 65,532 coupled
  = 0.9961**.
- **Exact characterization of absence** (`charac.json`; verified over all
  65,536 with zero exceptions): composite cycle absent ⇔ image(ψ) ⊆ {1,2},
  or ψ ≡ 0, or ψ ≡ 3 — i.e. 256 + 1 + 1 = 258 maps, of which 254 are coupled.
  The exceptions are exactly the interfaces that never deliver an extreme
  drive symbol.
- Witness length is **2 for every one of the 65,536 interfaces**; what varies
  is the witness *class*: composite for 43,008, WTA-local for 22,528. So the
  shortest witness is composite for **43,008 / 65,532 = 65.6%** of coupled
  interfaces (0.6588 conditional on a composite cycle existing).
- Biological ψ = (0,3,2,3,1,3,3,3), string `03231333`: \|M\| = 3,084, witness
  (g0,g1) with cycle (4,13) = (D:0,W:4) ↔ (D:1,W:5), class composite. Its
  \|M\| sits at the **95.7th percentile** (2,816 interfaces give a larger
  monoid; 6 tie).

**φ sweep** (reverse direction): composite present for 224 / 252 coupled maps
(0.889), but shortest witness composite for only **30 / 252 = 11.9%**. The
biological φ's shortest witness is WTA-local (cycle (12,13)); its shortest
*composite* witness has length 3. Legibility tracks coupling **direction**,
not interface detail.

**Recurrent grid** (`schedule_summary.csv`, `rec_grid_counts.csv`,
`rec_grid.json`):

- rec_sync: 8,616,638 / 16,777,216 cases (0.514) contain a composite cycle;
  rec_async_D and rec_async_W: 6,274,480 (0.374) each — the two asynchronous
  orders are numerically indistinguishable in every aggregate.
- In **0 of all 50,331,648** recurrent cases does a non-aperiodic monoid
  arise from four aperiodic generators — under recurrent coupling the
  non-aperiodicity always enters at the generator level.
- Every nontrivial cycle arising under recurrent coupling is composite: no
  recurrent case anywhere in the grid has a DN-local or WTA-local shortest
  witness.
- At the biological interfaces: rec_sync gives \|M\| = 9 with 6 non-aperiodic
  elements (all four generators non-aperiodic); both asynchronous variants
  give \|M\| = 8, fully aperiodic.

## Mapping to the paper

This experiment resolves the draft's `[SWEEP NUMBERS]` placeholder and
underwrites the Results paragraphs on robustness:

- "A composite cycle is present for 65,278 of the 65,536 maps, and for 65,278
  of the 65,532 coupled maps, a fraction of 0.9961" — `sweep_summary.json`,
  `charac.json`.
- The exact characterization of the 258 exceptions ("absent precisely when
  the interface never delivers either extreme drive symbol … 254 are
  coupled") — `charac.json`.
- "Composite for 43,008 interfaces and competition-local for 22,528 … 65.6%
  of coupled interfaces" and the 95.7th-percentile statement — the
  legibility paragraph; `sweep_summary.json`.
- The reverse-direction contrast (0.889 present vs 11.9% shortest) — the φ
  sweep block.
- "In none of the 50,331,648 recurrent cases does a non-aperiodic monoid
  arise from four aperiodic generators" and the asynchrony numbers (0.514 →
  0.374, 6,274,480 cases per asynchronous scheme) — `schedule_summary.csv`.
- Fig. 2 (`04_figures/sweep_figure.png`) is drawn from these outputs.

## Pitfalls

- **PYTHONSAFEPATH / imports**: `sweep.py` imports `audit` and `fastmon`;
  `verify_fast.py` additionally reads `audit_results.json` from cwd. Copy or
  link both from `01_monoid_audit/` and run with `PYTHONPATH=$PWD`.
- **verify_findings.py** reads the pickles written by `analyse.py`
  (`psi_df.pkl`, `phi_df.pkl`, `grid_df.pkl`) plus `rec_grid.json`,
  `rec_rows.jsonl` and `findings.md`; run it only after a full sweep +
  `analyse.py`.
- Witness words here are exact minima from an **uncapped** BFS, unlike
  `audit.py`'s capped search; the two agree on every audited system.
- Recurrent coupling collapses the reachable state space severely
  (max \|M\| = 212 synchronous, 62 asynchronous, vs 22,581 in the ψ sweep);
  recurrent and one-way schemes are not comparable in monoid size.
- All sweeps hold the component dynamics fixed (the paper's 4-state DN with
  round-half-to-even and 8-state WTA generators); nothing here bounds
  robustness to changes in the DN or WTA generators themselves.

## Regenerating the figure input tables

`04_figures/make_sweep_figure.py` reads two small tables derived from the full
`interface_sweep.csv`, both shipped in `expected_output/`. If you re-run the
sweep, rebuild them with:

```python
import pandas as pd
d = pd.read_csv("interface_sweep.csv", low_memory=False)
for c in ["is_bio_psi", "has_composite", "shortest_is_composite"]:
    d[c] = d[c].astype(str).str.strip().str.lower().isin(["true", "1", "1.0"])
psi = d[d.sweep == "psi_W_to_D"]
phi = d[d.sweep == "phi_D_to_W"]

vc = psi.monoid_size.value_counts().sort_index()
pd.DataFrame({"monoid_size": vc.index, "n_interfaces": vc.values}) \
  .to_csv("psi_monoid_size_counts.csv", index=False)

def three(g):
    n = len(g)
    a = int(g.shortest_is_composite.sum())
    b = int((g.has_composite & ~g.shortest_is_composite).sum())
    return n, a, b, n - a - b

rows  = [("psi", k, *three(psi[psi.psi_class == k]))
         for k in ["constant", "g_only", "winner_only", "both"]]
rows += [("phi", k, *three(phi[phi.phi_class == k]))
         for k in ["constant", "partial", "injective"]]
pd.DataFrame(rows, columns=["sweep", "stratum", "n", "shortest_composite",
                            "composite_longer", "no_composite"]) \
  .to_csv("figure_strata.csv", index=False)
```

Sanity values: the `both` ψ stratum must give n = 65,268 with 42,934
shortest-composite, and the biological ψ must sit at \|M\| = 3,084.
