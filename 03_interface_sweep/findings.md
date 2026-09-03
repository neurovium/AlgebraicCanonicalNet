# Interface-robustness sweep — resolves `[SWEEP NUMBERS]`

Exhaustive enumeration, no sampling. All monoids computed by exact closure under
composition; aperiodicity by the fixed-point-cycle criterion; witness words by
breadth-first search on the Cayley graph from the identity over the *whole*
monoid, so reported witness lengths are exact minima with no length cap.

**Verification.** The fast enumeration core (`fastmon.py`, `bytes.translate`
composition) was checked element-for-element against `audit.py` on all nine
audited systems: monoid sets identical, and `|M|`, idempotent count,
non-aperiodic count, unit-group order, witness word and witness cycles all
reproduce `audit_results.json` exactly (DN_3state 13/6/3, DN_4state 24/8/3,
WTA 326/55/49, prod 576/103/88, D_to_W 3149/274/401, W_to_D 3084/186/361,
rec_sync 9/2/6, rec_async_D 8/2/0, rec_async_W 8/2/0).

## Scope of the sweep

| sweep | scheme | maps enumerated | held fixed |
|---|---|---|---|
| psi (WTA -> DN) | `W_to_D` | **65 536** = 4^8, exhaustive | phi biological, schedule fixed |
| phi (DN -> WTA) | `D_to_W` | **256** = 4^4, exhaustive | psi biological |
| (phi, psi) | `rec_sync`, `rec_async_D`, `rec_async_W` | **50 331 648** = 3 x 256 x 65 536, exhaustive | — |
| (phi, psi) row-level records | 3 recurrent schemes | 111 360 rows (256 phi x 145 stratified psi x 3) | — |

**Degeneracy: none.** All four WTA generators are jointly surjective onto
X_W = {0,...,7} (image = all 8 states), so every one of the 8 arguments of psi is
live. The 65 536 psi maps give **65 536 distinct generator 4-tuples** — the
interface space does *not* collapse (collapse factor 1.0000), and every measured
quantity (`|M|`, idempotents, non-aperiodic count, witness length) is constant
within each singleton equivalence class by construction. Likewise all 256 phi
maps give 256 distinct generator tuples.

## Headline numbers for the manuscript

- psi sweep, 65 536 interfaces: `|M|` ranges **326 to 22 581**, median **832**.
  All 65 536 have **all four generators aperiodic** and **trivial group of units**;
  **0** of 65 536 generate an aperiodic monoid.
- A composite (both-coordinate) cycle is present in **65 278 of 65 536** psi
  interfaces (0.996063); absent in **258**.
- Coupled (non-constant) psi: **65 278 / 65 532 = 0.996124** carry a composite cycle.
- Uncoupled (constant) psi: **0 / 4** carry a composite cycle; all four have a
  WTA-local shortest witness of length 2, `|M|` in {326, 328, 328, 343}, 55
  idempotents, 49/49/49/55 non-aperiodic elements. The independent product
  reference is `|M|` = 576, 103 idempotents, 88 non-aperiodic, witness `(g0,g1)`
  with cycle (12,13), **WTA-local, no composite cycle anywhere** — same
  qualitative verdict as the constant interfaces.
- **Exact structural characterisation of absence** (verified over all 65 536,
  no exceptions): a composite cycle is absent **iff** image(psi) ⊆ {1, 2}, or psi
  is constant 0, or psi is constant 3. That is **256 + 1 + 1 = 258** maps. Every
  one of these 258 has a WTA-local shortest witness and none contains a composite
  cycle anywhere in the monoid. All 254 *coupled* counterexamples are of the
  image ⊆ {1,2} type — i.e. psi that never delivers the drive symbols 0 or 3
  and so never lets the WTA state change the DN's fixed point structure.
- Biological psi = (0,3,2,3,1,3,3,3) (string `03231333`), class "gate + winner":
  `|M|` = **3 084**, 186 idempotents, 361 non-aperiodic elements, shortest witness
  `(g0, g1)` length **2** with cycle **(4, 13) = (D:0,W:4) -> (D:1,W:5)**, class
  **composite**. Its `|M|` sits at the **95.7th percentile** (2 816 of 65 536
  interfaces give a larger monoid, 6 give exactly 3 084) — the biological
  interface is in the upper tail of complexity, not typical.
- Witness length is **2 for all 65 536** psi interfaces (the global minimum,
  since single generators are always aperiodic here), so the biological
  interface's witness is as short as any interface achieves. What varies is its
  *class*: composite for **43 008** interfaces, WTA-local for **22 528**.
- Shortest witness is composite in **43 008 / 65 532 = 0.656290** of coupled
  interfaces; conditional on a composite cycle existing at all,
  **43 008 / 65 278 = 0.658844**.

### Per-stratum table, psi sweep (`sweep_summary.csv`)

| psi stratum | n | composite present | shortest witness composite | shortest WTA-local | `\|M\|` min / median / max |
|---|---|---|---|---|---|
| constant (no winner info) | 4 | 0 | 0 | 4 | 326 / 328 / 343 |
| gate bit g only | 12 | 10 | 10 | 2 | 328 / 476.5 / 8 950 |
| winner identity (b1,b2) only | 252 | 238 | 64 | 188 | 327 / 588 / 6 204 |
| gate + winner (both) | 65 268 | 65 030 | 42 934 | 22 334 | 326 / 833 / 22 581 |

DN-local cycles occur somewhere in the monoid in 18 143 of 65 536 psi
interfaces; WTA-local in 65 517. 19 interfaces contain composite cycles and
nothing else.

## Verdicts on the draft's three sub-claims

**(i) "Composite cycles appear under essentially all coupled interfaces" —
SUPPORTED.** 65 278 of 65 532 coupled psi maps (0.996124) contain a composite
cycle. The 254 exceptions are not random: they are exactly the coupled maps with
image(psi) ⊆ {1,2}. The manuscript may say "all but 254 of 65 532" and should
name the exception class rather than calling it noise.

**(ii) "Absent only in the uncoupled product and in passthrough interfaces that
carry no winner information" — PARTLY SUPPORTED.** The direction claimed is
correct: all 4 constant psi maps and the independent product lack composite
cycles. But "only" is too strong — a further **254** coupled interfaces also lack
them. Recommended wording: absent in the uncoupled product, in all 4
passthrough interfaces, and in the 254 coupled interfaces whose image omits both
extreme drive symbols (image ⊆ {1,2}); 258 of 65 536 in total.

**(iii) "Under winner-pooling, the composite cycle is also the shortest witness"
— SUPPORTED for the biological interface, and it is NOT generic.** The
biological psi's shortest witness (length 2, cycle (4,13)) is composite. Across
coupled interfaces this coincidence holds in only **43 008 / 65 532 = 0.656290**
of cases (0.658844 conditional on a composite cycle existing), and within the
biologically matched "winner identity only" stratum in just **64 / 252 =
0.253968**. Legibility is therefore a real and non-automatic property of the
biological interface, though it is shared by a two-thirds majority of coupled
interfaces — the manuscript should say "shared by 65.6% of coupled interfaces",
not "unique to".

## Secondary control 1: the phi interface (`D_to_W`, 256 maps, exhaustive)

- `|M|` ranges 27 to 3 795, median 363. All 256 have all generators aperiodic;
  **0** are aperiodic monoids.
- Composite cycle present in **224 / 252** coupled phi maps (0.888889); **0 / 4**
  constant phi maps.
- Shortest witness is composite in only **30 / 252 = 0.119048** of coupled phi
  maps (30 / 224 = 0.133929 conditional on presence). Shortest witness is
  WTA-local in 192 and DN-local in 34 of the 256.
- Biological phi = (0,1,2,3): `|M|` = 3 149, shortest witness `(g0,g1)` length 2
  with cycle (12,13), **WTA-local** — a composite cycle exists but only at word
  length **3**. All 24 injective phi maps have a composite cycle yet **none** has
  it as the shortest witness.
- **Coupling direction matters more than interface detail for legibility.**
  Composite-cycle *presence* is comparable in the two directions (0.996 for
  W->D vs 0.889 for D->W) but *legibility* differs by more than a factor of five
  (0.656 vs 0.119). The W->D direction — the WTA winner controlling the DN drive
  — is what makes the composite cycle the shortest witness.

## Secondary control 2: update schedule (50 331 648 exhaustive cases)

| schedule | cases | composite cycle present | aperiodic monoid | non-aperiodicity at generator level |
|---|---|---|---|---|
| `rec_sync` | 16 777 216 | 8 616 638 (0.513592) | 8 160 578 (0.486408) | 8 616 638 (0.513592) |
| `rec_async_D` | 16 777 216 | 6 274 480 (0.373988) | 10 502 736 (0.626012) | 6 274 480 (0.373988) |
| `rec_async_W` | 16 777 216 | 6 274 480 (0.373988) | 10 502 736 (0.626012) | 6 274 480 (0.373988) |

- **Synchronous coupling puts non-aperiodicity at the generator level —
  SUPPORTED, and stronger than claimed: it is exact.** In all three recurrent
  schemes, the number of cases with a non-aperiodic monoid but *all four
  generators aperiodic* is **0** out of 50 331 648. Whenever a recurrent monoid
  is non-aperiodic, some generator already is; and whenever a recurrent monoid
  contains a non-trivial cycle, that cycle is composite (composite-present but
  witness-class not composite: **0** cases; witness classes over the whole grid
  are composite 21 165 598 and none 29 166 050 — no DN-local or WTA-local
  shortest witnesses ever occur under recurrent coupling).
- **Asynchronous updating tends to kill non-aperiodicity — SUPPORTED as a
  tendency, not as an absolute.** Asynchrony drops the composite-cycle rate from
  0.513592 to 0.373988 (a factor 0.728) but leaves 6 274 480 cases per
  asynchronous scheme with a composite cycle. The draft must not say asynchrony
  *eliminates* the structure: at the biological (phi, psi) it does (rec_async_D
  and rec_async_W both give `|M|` = 8, 0 non-aperiodic elements), but generically
  it does not.
- The two asynchronous orders are **numerically indistinguishable** in every
  aggregate reported here (identical counts to the last digit: 6 274 480 /
  10 502 736 / 6 274 480), and their `|M|` distributions differ only slightly
  (mean 6.448 vs 6.472; both range 3 to 62). Synchronous monoids are larger
  (mean 9.264, range 3 to 212).
- Recurrent coupling collapses the state space drastically relative to the
  one-way schemes: max `|M|` is 212 (sync) and 62 (async), versus 22 581 in the
  psi sweep. Constant phi gives a composite rate of exactly 0 in all three
  recurrent schemes (262 144 cases each); injective phi is highest
  (0.687331 sync, 0.505946 async).

## What the manuscript must not overclaim

- "Absent **only** in the uncoupled product and passthrough interfaces" is false
  as written — 254 coupled interfaces also lack composite cycles, with an exact
  and interpretable characterisation (image(psi) ⊆ {1,2}).
- The biological interface is **not** typical in monoid size: 95.7th percentile.
  Do not present it as a representative draw.
- Legibility (shortest witness composite) is a **majority** property of coupled
  psi interfaces (65.6%), not a signature unique to winner-pooling. It is,
  however, rare in the reverse coupling direction (11.9% of coupled phi).
- Asynchrony **reduces** rather than removes non-aperiodicity (0.374 vs 0.514);
  the total elimination seen at the biological parameters is a property of that
  point, not of asynchronous updating in general.
- All sweeps are over the paper's fixed 4-state DN and 8-state WTA generator
  sets with round-half-to-even DN dynamics; the interface maps are varied, the
  component dynamics are not.
