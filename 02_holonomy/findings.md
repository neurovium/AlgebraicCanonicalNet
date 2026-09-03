# Holonomy / Krohn-Rhodes findings — DN & WTA motifs

GAP 4.15.1, SgpDec 1.2.0, Semigroups 5.6.3. All nine systems cross-checked
against the Python audit: **|M|, idempotent count, non-aperiodic element count,
and |group of units| agree for all 9 — zero mismatches.**

## What a holonomy group acts on (read before quoting any of this)

For an image set `C` of the skeleton, SgpDec exposes two different groups:

- **`PermutatorGroup(sk, C)`** — permutations of the **raw states** of `C`
  induced by words mapping `C` onto itself.
- **holonomy group** — the image of that group acting on the **tiles** of `C`
  (maximal proper subsets of `C` that are themselves image sets).

They coincide only when every tile is a singleton. Where tiles are larger the
group permutes **subsets**, and no statement about individual states is
licensed. Both are reported in `holonomy_compositeness.csv` and the transcript.

Second caveat, load-bearing for (c): `GroupComponents(sk)` only lists groups at
SgpDec's chosen **transversal representatives**. Holonomy groups are conjugate
(hence isomorphic) along a subduction class, so a set that is not the chosen
representative still carries the group of its class — it simply does not show
up in the printed component list. Several of the paper's target sets are of
exactly this kind.

## Per-system results

| system | \|M\| | depth | components | nontrivial | levels w/ group | groups |
|---|---|---|---|---|---|---|
| DN3 | 13 | 3 | 2 | 2 | 1, 2 | C2, C2 |
| DN4 | 24 | 4 | 3 | 1 | 3 | C2 |
| WTA | 326 | 7 | 15 | 2 | 2, 5 | C2, C2 |
| prod | 576 | 9 | 24 | 3 | 2, 7 | C2, C2, C2 |
| D_to_W | 3149 | 12 | 22 | 5 | 6, 7, 8, 10 | **C4**, C2, C2, C2, C2 |
| W_to_D | 3084 | 22 | 92 | 5 | 7, 10, 14, 17, 20 | C2 ×5 |
| rec_sync | 9 | 8 | 7 | 1 | 7 | **C3** |
| rec_async_D | 8 | 9 | 8 | 0 | — | none |
| rec_async_W | 8 | 9 | 8 | 0 | — | none |

Component profiles (`DisplayHolonomyComponents`):
- DN3 `1: (2,C2) / 2: (2,C2)`
- DN4 `1: 2 / 2: 2 / 3: (2,C2)`
- WTA `1: 4 / 2: 2 (4,C2) 4 / 3: 3 3 2 / 4: 3 3 3 3 2 / 5: (2,C2) / 6: 2 2`

Both DN4 and WTA reproduce the smoke test exactly.

### Nontrivial components with decoded supports

- **DN3** L1S1 C2 on rep `{0,1,2}`, tiles `{0,1}|{1,2}`; L2S1 C2 on `{1,2}`,
  tiles `{1}|{2}` (singletons).
- **DN4** L3S1 C2 on rep `{0,1}`, tiles `{0}|{1}` (singletons).
- **WTA** L2S2 C2 on `{1,4,5,7}`, 4 tiles of size 3 (**not** singletons);
  L5S1 C2 on `{4,5}`, tiles `{4}|{5}` (singletons).
- **prod** L2S2 C2 on an 8-state set, 7 tiles; L7S1 C2 on `{12,13}`; L7S2 C2 on
  `{5,13}` — both singleton-tiled.
- **D_to_W** L6S3 **C4** on `{9,13,18,19}` (4 tiles of size 3); L7S1 C2, L7S2 C2,
  L8S3 C2 on `{13,19}`, L10S1 C2 on `{12,13}`.
- **W_to_D** L7S6 C2 on `{10,17,19,31}`; L10S1 C2 on `{4,12,17}`; L14S1 C2 on
  `{17,21,29}`; L17S1 C2 on `{10,19}`; L20S1 C2 on `{4,12}`.
- **rec_sync** L7S1 **C3** on `{0,11,17,18,19}`, all five tiles singletons — a
  genuine 3-cycle on states 11 → 17 → 18.

## Verdicts on (a)–(e)

**(a) WTA C2 on {4,5} and {2,3} — TRUE, both.**
`{4,5}` is the level-5 slot-1 representative: permutator `(5,6)` = C2 on raw
states, holonomy C2 on the two **singleton** tiles `{4}|{5}`. `{2,3}` is *not*
the transversal representative but lies in the **same subduction class** (size
15, representative `{4,5}`), and carries its own C2 with singleton tiles. So the
two are algebraically the same component, not two independent ones — the paper
should say "the class containing both {4,5} and {2,3}", not "two C2's".
The smoke test's level-2 `(1,4)(2,3)` is a **different** object: it acts on
`{1,4,5,7}` whose tiles are size-3 subsets, so it permutes subsets, not states.

**(b) DN4 level-3 C2 ↔ audit witness cycle 2↔1 — TRUE, with a coordinate note.**
The audit witness is `{1,2}`; GAP's chosen representative is `{0,1}`. Both lie in
one subduction class `{{0,1},{1,2},{2,3}}` (size 3) with isomorphic C2 and
singleton tiles. So the level-3 C2 *is* the witness cycle's component — but
`{1,2}` itself is not what `GroupComponents` prints.

**(c) W_to_D — SUPPORTED. This is the paper's primary claim and it holds.**
`C = {4=(D:0,W:4), 13=(D:1,W:5)}` (GAP `{5,14}`) is an image set at depth 17
with `PermutatorGroup = Group([(5,14)]) = C2` and holonomy C2 on two
**singleton** tiles — so the group genuinely swaps the two composite states.
It is **not** a transversal representative: its class has size 45 with
representative `{10,19}`, which is why the printed L17S1 component shows
`{10,19}` instead. Explicit witness: 13 monoid elements stabilise the pair and
swap it; one is
`Transformation([13,13,10,5,14,5,5,5,13,13,18,5,22,5,5,5,13,13,18,5,22,5,5,5,13,13,18,13,22,13,13,13])`,
which maps 4=(D:0,W:4) → 13=(D:1,W:5) and 13 → 4 — **both** coordinates change,
so the swap is genuinely composite, not inherited from either factor.

**(d) prod — group components ARE inherited; no composite action. Control holds.**
Across all 34 image sets of `prod` carrying a nontrivial permutator group:
**27 W-only, 7 D-only, 0 composite.** No state is ever moved to a state
differing in both coordinates. `prod`'s pair `{12,13}` does carry a C2, but it
varies only in W (both are D:1) — inherited from the WTA factor. This is the
clean contrast with (c).

**(e) D_to_W — composite structure present, and it is the richest of the three.**
46 nontrivial-permutator windows: **31 W-only, 15 composite** (12 C2 + **3 C4**).
The C4 at L6S3 is the only group of order > 2 in any cascade system:
permutator `(2,14,4,13)`, mapping 1=(D:0,W:1) → 13=(D:1,W:5) → 3=(D:0,W:3) →
12=(D:1,W:4) → 1. `D_to_W`'s own `{12,13}` pair is W-only (both D:1), so for
this system the composite structure lives at *other* supports — the paper should
not use `{12,13}` as D_to_W's composite witness.

### Compositeness summary (the control-vs-cascade contrast)

| system | windows | W-only (inherited) | D-only | COMPOSITE |
|---|---|---|---|---|
| prod | 34 | 27 | 7 | **0** |
| D_to_W | 46 | 31 | 0 | **15** (C4 ×3, C2 ×12) |
| W_to_D | 57 | 12 | 10 | **35** (C2 ×35) |

## Aperiodicity (verified in GAP independently of Python)

- Per-generator, via `t^n = t^(n+1)`: DN4, WTA, prod, D_to_W, W_to_D,
  rec_async_D, rec_async_W all-aperiodic — **TRUE**, matching the audit.
- DN3 — **FALSE**: D1 has cycle (0 2), D2 has cycle (2 1). Matches the audit.
- rec_sync — all four generators **non**-aperiodic, each with cycle structure;
  matches the audit's `gens_all_aperiodic = False`.
- `IsAperiodicSemigroup(M) = true` for **rec_async_D and rec_async_W only**;
  false for all seven others (each contains a nontrivial group).
- Group of units trivial for all systems **except DN3** (order 2, C2) — matches.

Note the standard subtlety: aperiodic *generators* do not give an aperiodic
*monoid*. DN4, WTA, prod, D_to_W and W_to_D all have every generator aperiodic
yet all contain C2 (or C4) subgroups. That gap is the paper's point.

## Faithfulness of the decompositions

Elementwise `AsHolonomyTransformation(AsHolonomyCascade(t,sk),sk) = t` for
**every** element: DN3 (13), DN4 (24), WTA (326), prod (576), rec_sync (9),
rec_async_D (8), rec_async_W (8).

- **D_to_W**: exhaustive sweep exhausted memory. Bounded probe of 125 distinct
  elements (all generators + identity + 120 sampled) → **125/125, 0 mismatches**.
- **W_to_D**: **not attempted.** Cascade coordinate-value counts
  `[16,26,34,12,12,19,20,21,21,15,12,21,3,9,24,6,2,12,4,2,6]` give a cascade
  state space of 5.78 × 10²¹ tuples; a single cascade element exhausts memory at
  `-o 14g`. The skeleton, depth 22, all 92 components and all 5 groups are exact.

The setwise test `AsSortedList(M) = AsSortedList(Range(hom))` was run on the
seven systems above and returns:

| system | `Size(Range(hom))` | \|M\| | setwise test |
|---|---|---|---|
| DN3 | 13 | 13 | **true** |
| DN4 | 23 | 24 | false |
| WTA | 325 | 326 | false |
| prod | 575 | 576 | false |
| rec_sync | 8 | 9 | false |
| rec_async_D | 7 | 8 | false |
| rec_async_W | 7 | 8 | false |

For the six systems returning false the set difference is **exactly**
`[IdentityTransformation]`: `Range(hom)` is built with `Semigroup(...)` from the
cascade generators, so it omits the identity whenever the identity is not itself
a product of generators. This is a Semigroup-vs-Monoid artefact, **not** a
decomposition failure. **DN3 is the exception** — there the identity *is*
reachable as a product of generators, so `Semigroup(gens_DN3)` already has
size 13 = |M| and the setwise test passes.

No setwise result exists for **D_to_W or W_to_D**: the cascade construction was
not attempted for those (see above), so for them the test is *unproven*, not
false.

Cite the elementwise test, not the setwise one — its outcome does not depend on
whether the identity happens to be a generator product.

## Caveats for the manuscript

1. Do not say a holonomy group is "supported on the witness cycle" without
   naming the tiles. Claims (a)/(b)/(c) survive because their tiles are
   **singletons**; WTA's level-2 C2 does not (its tiles are size-3 subsets).
2. `{2,3}` (WTA) and `{1,2}` (DN4) and `{4,13}` (W_to_D) are **not** transversal
   representatives. They carry their class's group; they do not appear in
   `GroupComponents` output. State it that way or a referee reproducing the
   printed component list will not find them.
3. The W_to_D cascade was never explicitly reconstructed (10²¹ state space). The
   decomposition's existence follows from the holonomy theorem, but the paper
   cannot claim a *machine-verified* cascade for W_to_D as it can for the other
   seven.
4. D_to_W's `{12,13}` is W-only/inherited. Only W_to_D's `{4,13}` is the
   composite pair. Do not conflate them.
5. rec_sync carries **C3**, not C2 — and its generators are individually
   non-aperiodic, so its group is not an emergent effect of coupling in the same
   sense as W_to_D's.
