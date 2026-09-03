# Experiment 02 — Holonomy (Krohn–Rhodes) decomposition in GAP/SgpDec

## Purpose, in plain language

Experiment 01 shows *that* the composite circuits contain reversible
(non-aperiodic) elements. This experiment asks *where in the hierarchy* that
reversible structure lives, using the holonomy form of the Krohn–Rhodes
decomposition: every finite transformation monoid embeds in a cascade of
levels, each level being either a "flip-flop" (memoryless reset/identity — the
aperiodic part) or a finite permutation group (the reversible part). For a
neuroscientist: this is a principled coordinate system for the circuit's
computations, separating what the circuit can *undo* (group levels) from what
it can only *overwrite* (aperiodic levels).

The decisive question for the paper: in the WTA→DN cascade, is there a group
component that genuinely swaps two states differing in **both** the DN and
the WTA coordinate (a *composite* swap), or is all the reversible structure
inherited from one factor? The control is the independent product, where every
group must be inherited.

## What is computed

`holonomy.g` runs, for each of the nine systems in `gap_systems.g`:
monoid order / aperiodicity / idempotents / group of units (cross-checked
against the Python audit — all 9 systems agree exactly, 0 mismatches);
the SgpDec holonomy skeleton (depth, per-(level, slot) holonomy groups with
their tiles decoded into paper state coordinates); an elementwise
faithfulness check of the holonomy cascade; and targeted claim checks for
specific state pairs. `compositeness.g` classifies every image set carrying a
nontrivial permutator group as **W-only / D-only / COMPOSITE** according to
whether monoid elements move states within the set along the WTA coordinate
only, the DN coordinate only, or both. `transcript.g` replays the headline
computations in `gap> command / output` form to produce the supplementary
transcript.

## How to run

```bash
P=/home/nimad/miniforge3/envs/algcanet
export PATH=$P/bin:$PATH
cd 02_holonomy
gap -q -A holonomy.g            # holonomy_results.csv (+ per-system logs)
gap -q -A compositeness.g       # compositeness.csv (window classification)
gap -q -A -o 8g transcript.g    # gap_transcript.txt (supplementary material)
```

Options for `holonomy.g`:
`gap -q -A -c 'ONLY:=["WTA"];;' holonomy.g` restricts to named systems;
`DO_CASCADE:=false;;` skips the faithfulness check; `OUTTAG:="_x";;` suffixes
the output filenames. Output files are written incrementally, so a killed run
leaves usable partials.

Runtime: DN3/DN4/WTA/rec_* are seconds; prod and D_to_W are minutes. **The
long pole is the W_to_D skeleton** (depth 22, 92 components) — tens of
minutes. The cascade faithfulness check is *skipped automatically* for W_to_D
(see pitfalls). Memory: 8 GB (`-o 8g`) is comfortable for everything that is
actually attempted.

## Expected output (headline numbers)

Per-system decomposition (matches `expected_output/holonomy_results.csv`):

| system | \|M\| | depth | components | nontrivial groups | groups (levels) |
|---|---|---|---|---|---|
| DN3 | 13 | 3 | 2 | 2 | C2 (L1), C2 (L2) |
| DN4 | 24 | 4 | 3 | 1 | C2 (L3) |
| WTA | 326 | 7 | 15 | 2 | C2 (L2), C2 (L5) |
| prod | 576 | 9 | 24 | 3 | C2, C2, C2 (L2, L7) |
| D_to_W | 3149 | 12 | 22 | 5 | C4 (L6) + 4×C2 (L7,L8,L10) |
| W_to_D | 3084 | 22 | 92 | 5 | 5×C2 (L7,L10,L14,L17,L20) |
| rec_sync | 9 | 8 | 7 | 1 | C3 (L7) |
| rec_async_D | 8 | 9 | 8 | 0 | — (IsAperiodicSemigroup = true) |
| rec_async_W | 8 | 9 | 8 | 0 | — (IsAperiodicSemigroup = true) |

The paper's primary claim: in W_to_D the pair {4 = (D:0,W:4), 13 = (D:1,W:5)}
(GAP points {5,14}) is a **depth-17 image set with permutator group
C2 = ⟨(5,14)⟩ and holonomy C2 acting on two singleton tiles** — the group
genuinely swaps the two composite states; 13 monoid elements swap the pair,
and the explicit witness transformation changes both coordinates.

The control (`compositeness.csv`, aggregated in
`expected_output/compositeness_all.csv`):

| system | windows with nontrivial permutator | W-only | D-only | COMPOSITE |
|---|---|---|---|---|
| prod | 34 | 27 | 7 | **0** |
| D_to_W | 46 | 31 | 0 | 15 (12×C2, 3×C4) |
| W_to_D | 57 | 12 | 10 | **35** (all C2) |

The product control is clean: **0 of 34** windows composite — no state is ever
moved to a state differing in both coordinates. D_to_W's three C4's (e.g.
L6S3, cycling (D:0,W:1) → (D:1,W:5) → (D:0,W:3) → (D:1,W:4)) are the only
groups of order > 2 anywhere in the cascade systems.

## Mapping to the paper

- The Results statement that the WTA→DN composite cycle is *certified as a
  group component of the holonomy decomposition* is verdict (c) above:
  {4,13} at depth 17, C2 on singleton tiles.
- The product-control contrast ("inherited rather than composite") is the
  prod row: 27 W-only + 7 D-only + 0 composite.
- The recurrent-schedule rows (C3 for rec_sync; aperiodic for both
  asynchronous schemes) support the schedule section of the Results.
- `gap_transcript.txt` is the supplementary GAP session.

## Pitfalls

- **Monoid vs Semigroup**: GAP's `Semigroup(gens)` omits the identity unless
  it is a product of generators, so `Size(Semigroup)` = \|M\|−1 for eight of
  the nine systems (DN3 is the exception — its identity *is* a generator
  product). All reported orders use `Monoid(gens)`. Relatedly, the setwise
  faithfulness test `AsSortedList(M) = AsSortedList(Range(hom))` fails by
  exactly the identity on six systems and passes on DN3; cite the
  **elementwise round-trip** instead (verified for every element of 7/9
  systems; 125-element sample for D_to_W, 0 mismatches).
- **W_to_D cascade is not machine-verified**: its cascade state space is
  ≈5.78×10²¹ tuples and constructing a single cascade element exhausts memory
  at `-o 14g`. The skeleton, depth, all 92 components and all 5 groups are
  exact; only the explicit cascade round-trip is unavailable for this system.
- **Tiles vs states**: holonomy groups act on *tiles* of an image set, not on
  raw states. Only where tiles are singletons does the group permute
  individual circuit states. WTA's level-2 C2 acts on four size-3 tiles and
  must **not** be described as permuting states; the paper's claims survive
  because their tiles ({4,5} in WTA at L5, {0,1} in DN4 at L3, {4,13} in
  W_to_D at L17) are singletons.
- **Transversal representatives**: {4,13} in W_to_D, {2,3} in WTA and {1,2}
  in DN4 are *not* SgpDec transversal representatives; they carry their
  subduction class's group (conjugate along the class) but do not appear in
  `GroupComponents` output. W_to_D's {4,13} class has size 45 with
  representative {10,19} at L17S1; WTA's {2,3} shares its size-15 class with
  {4,5}; DN4's {1,2} shares its size-3 class with representative {0,1}.
  A referee reproducing the printed component list will find the
  representatives, not the paper's pairs — this is expected.
- **D_to_W's {12,13} is W-only/inherited** (both states have D:1): it must
  not be used as that system's composite witness. D_to_W's composite
  structure lives at other supports (15 windows, including the C4's).
- **rec_sync carries C3, not C2**, and all four of its generators are
  individually non-aperiodic — its group is not an emergent effect of
  composition in the same sense as W_to_D's.
- **One-based indexing**: GAP point p = paper state p−1. `gap_systems.g` is
  exported with the +1 shift already applied; all CSVs decode supports back
  into paper coordinates.
