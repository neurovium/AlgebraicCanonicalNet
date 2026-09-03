# Environment: Python + GAP/SgpDec for AlgCanNet

Everything runs inside one conda/mamba environment, called `algcanet` here:

```
/home/nimad/miniforge3/envs/algcanet
```

## Contents (verified to load)

| component | version | role |
|---|---|---|
| Python | 3.12 | monoid audit, interface sweeps, figures |
| numpy / scipy / pandas / matplotlib / networkx / sympy | conda-forge current | analysis and figures |
| GAP | 4.15.1 (conda-forge `gap-defaults`) | computer algebra host |
| SgpDec | 1.2.0 (built from source) | holonomy (Krohn–Rhodes) decompositions |
| Semigroups | 5.6.3 (built from source) | transformation-semigroup backend |
| GAPDoc 1.6.7, IO 4.10.0, orb 5.1.0, datastructures 0.4.3, Digraphs 1.15.0, images 1.4.0, genss 1.6.9 | source builds | dependencies of the above |

## Creating the environment

```bash
mamba create -n algcanet -c conda-forge python=3.12 numpy scipy pandas \
    matplotlib networkx sympy gap-defaults
```

conda-forge has **no `gap-pkg-*` recipes**, so SgpDec, Semigroups and their
dependencies must be built from source into `$PREFIX/share/gap/pkg`.
`build_gap_pkgs.sh` (this directory) does that: place the package tarballs in
`pkgsrc/` and it configures and builds each package in dependency order
(io, orb, datastructures, digraphs, semigroups, genss, sgpdec — plus images).

### Two fixes the conda-forge GAP layout requires (they will bite again)

1. **`--with-gaproot` must point at `$PREFIX/lib/gap`, not `$PREFIX/share/gap`.**
   The conda-forge layout puts `sysinfo.gap` in `lib/gap` while the package
   tree lives in `share/gap/pkg`; package `configure` scripts look for
   `sysinfo.gap`.
2. **`sysinfo.gap` ships with unreachable compiler paths.** `GAP_CC`/`GAP_CXX`
   are baked as `/home/conda/feedstock_root/build_artifacts/...`, which do not
   exist on the installing machine, so `gac` fails with `c++: not found` when
   building Semigroups. Rewrite them to the env's own
   `x86_64-conda-linux-gnu-{gcc,g++}` (keep the original as
   `sysinfo.gap.orig`).

Also note: `images` is a hard dependency of Semigroups and is easy to miss —
without it Semigroups reports "no installed version fits" and silently fails
to load.

## Running things

Python (note: if `PYTHONSAFEPATH` is set in your shell, the script directory is
not on `sys.path` automatically, so prepend it):

```bash
conda activate algcanet          # or: export PATH=$PREFIX/bin:$PATH
cd <experiment directory>
PYTHONPATH=$PWD python audit.py
```

GAP:

```bash
P=/home/nimad/miniforge3/envs/algcanet
export PATH=$P/bin:$PATH
gap -q -A script.g               # -A: skip autoloading, scripts load sgpdec explicitly
```

## Verifying the install

```bash
gap -q -A -c 'LoadPackage("sgpdec", false); Print(GAPInfo.Version, " sgpdec ok\n"); QUIT;'
```

should print the GAP version followed by `sgpdec ok`. Then run the smoke test
described in the top-level README (Quick start step 1): loading
`02_holonomy/gap_systems.g` and checking `Size(Monoid(gens_WTA)) = 326` and
`Size(Monoid(gens_W_to_D)) = 3084` confirms both the GAP install and the
generator export in one step.

## API note for SgpDec 1.2.0

`HolonomyDecomposition` does **not** exist in this version. The working
surface used by `02_holonomy/holonomy.g` is:

```gap
sk := Skeleton(S);                  # S from Monoid(gens), not Semigroup(gens)
DepthOfSkeleton(sk);
DisplayHolonomyComponents(sk);
GroupComponents(sk);
PermutatorGroup(sk, FiniteSet(set, n));
RepresentativeSets(sk);
HolonomyCascadeSemigroup(S);
HomomorphismTransformationSemigroup(hcs);
SgpDecOptionsRec.SMALL_GROUPS := true;
```

Use `Monoid(gens)` throughout: `Semigroup(gens)` omits the identity unless the
identity happens to be a product of generators, which makes every monoid order
come out one too small (see the pitfalls sections of the EXPERIMENT.md files).

## LaTeX caveat

The conda-forge `texlive-core` package ships only fonts and configuration —
no macro packages and no REVTeX — so the manuscript cannot be compiled in this
environment. Use a full TeX Live installation for `Paper/updated_draft_PRXstyle.tex`.
