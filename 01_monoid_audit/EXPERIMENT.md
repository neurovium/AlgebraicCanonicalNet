# Experiment 01 — Transition-monoid audit (Table I)

## Purpose

Each canonical motif is treated as a finite-state machine. Divisive
normalization (DN) — pooled-activity gain control in the sense of Carandini &
Heeger (2012) — becomes a 4-state (and, as a baseline, 3-state) system whose
inputs are discretized drive levels; winner-take-all (WTA) — recurrent
excitation with a shared inhibitory pool, in the sense of Hahnloser et al.
(2000) and Wang (2002) — becomes an 8-state system whose state encodes the two
winner bits plus a gate bit. Each input symbol induces a *transformation* of
the state set, and the set of all input words generates the **transition
monoid** M: the complete algebra of state changes the circuit can express.

The audit answers, for nine systems (DN3, DN4, WTA, and six DN⊗WTA
compositions — independent product, two one-way cascades, and three recurrent
schemes): how big is M, how many idempotents (stable operations) does it
contain, how many elements are **non-aperiodic** (elements with a nontrivial
cycle — the algebraic signature of reversible, group-like computation), and
what is the *shortest witness*: the shortest input word whose action contains
a nontrivial cycle, found by breadth-first search over words.

The headline phenomenon: in the WTA→DN cascade, **all four generators are
individually aperiodic, yet the generated monoid contains 361 non-aperiodic
elements**, and the shortest witness cycles two states that differ in *both*
the DN and the WTA coordinate — reversible structure that exists only by
composition.

## What is computed

For each system: exact monoid closure under composition
((f∘g)(x) = f(g(x)); a word (a₁,…,a_k) acts as f_{a_k}∘…∘f_{a₁}),
idempotent count, per-element aperiodicity (every cycle of the functional
graph is a fixed point), group of units, rank distributions, and a BFS
witness search over words up to length 6 for the 32-state composites.

## How to run

```bash
conda activate algcanet
cd 01_monoid_audit
PYTHONPATH=$PWD python audit.py        # writes audit_results.json in cwd
PYTHONPATH=$PWD python export_gap.py   # writes gap_systems.g (+ meta json) for experiment 02
```

Runtime: well under a minute on one core (the largest closure is 3,149
elements on 32 states). Memory: negligible (<100 MB).

## Expected output

`audit_results.json` must be byte-identical to
`expected_output/audit_results.json`. The stdout summary:

| system | n | \|M\| | idempotents | non-aperiodic | gens all aperiodic | \|U\| | shortest witness | cycle |
|---|---|---|---|---|---|---|---|---|
| DN_3state | 3 | 13 | 6 | 3 | no (D1, D2 have cycles) | 2 | D1 | (0 2) |
| DN_4state | 4 | 24 | 8 | 3 | yes | 1 | D1,D3,D3 | (2 1) |
| WTA | 8 | 326 | 55 | 49 | yes | 1 | W00,W10 | (4 5) |
| prod | 32 | 576 | 103 | 88 | yes | 1 | g0,g1 | (12 13) |
| D_to_W | 32 | 3149 | 274 | 401 | yes | 1 | g0,g1 | (12 13) |
| W_to_D | 32 | 3084 | 186 | 361 | yes | 1 | g0,g1 | **(4 13)** |
| rec_sync | 32 | 9 | 2 | 6 | no (all 4 non-aperiodic) | 1 | g0 | (17 18 11) |
| rec_async_D | 32 | 8 | 2 | 0 | yes | 1 | — | — |
| rec_async_W | 32 | 8 | 2 | 0 | yes | 1 | — | — |

Composite states are encoded s = 8·d + w, so the W_to_D witness cycle
(4, 13) reads **(D:0, W:4) ↔ (D:1, W:5)**: both coordinates change. In prod
and D_to_W the cycle (12, 13) = (D:1, W:4) ↔ (D:1, W:5) changes only the WTA
coordinate (competition-local).

## Mapping to the paper

- **Table I (`tab:composition-summary`)**: every row is a line of this audit.
- The claim that the WTA-to-DN cascade has "every primitive composite
  generator … aperiodic, but the generated monoid contains non-aperiodic
  elements, and the shortest witness changes both the DN and WTA coordinates"
  is exactly the W_to_D row plus its witness cycle (4, 13).
- The DN3 baseline (\|M\| = 13, units ≅ Z₂) is the noted exception to
  "trivial group of units".
- Appendices on generator vectors and rank distributions are generated from
  the same `audit_results.json` fields (`gens`, `rank_dist`,
  `rank_dist_nonaperiodic`).

## Pitfalls

- **PYTHONSAFEPATH**: if set, Python does not put the script directory on
  `sys.path`; `export_gap.py` (`import audit`) then fails. Run with
  `PYTHONPATH=$PWD`.
- **Composition order** is (f∘g)(x) = f(g(x)) with words acting
  right-to-left; reversing it permutes witness words.
- **Witness search is capped at word length 6** for the 32-state systems
  here; the sweep code in `03_interface_sweep` uses an uncapped Cayley-graph
  BFS and agrees on every audited system, so the caps never bind.
- **Shortest-witness ties**: BFS tie-breaking can return symmetric
  counterparts (see `provenance/ORIGINAL_CODE.md`, reconciliation 1).
