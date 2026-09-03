"""
Interface-robustness sweep for the AlgCanNet DN/WTA composite monoids.

Resolves the draft's [SWEEP NUMBERS] placeholder.  Three sweeps:

  STEP 1  psi : X_W -> {0,1,2,3}   (WTA state -> DN input symbol)
          exhaustive over all 4^8 = 65536 maps, scheme = W_to_D.
  STEP 3a phi : X_D -> {0,1,2,3}   (DN state -> WTA drive condition)
          exhaustive over all 4^4 = 256 maps, scheme = D_to_W.
  STEP 3b (phi, psi) grid for the three recurrent schemes.

Model conventions and generators are imported from audit.py (unmodified);
the monoid closure / aperiodicity primitives are the C-level `bytes.translate`
implementation in fastmon.py, verified element-for-element against audit.py.
"""
import itertools, json, os, sys, time
from collections import deque

import audit as A
import fastmon as F

fD4 = [bytes(g) for g in A.dn4_gens()]
fW  = [bytes(g) for g in A.wta_gens()]
WTA_IN = A.WTA_IN
N = 32

BIO_PSI = tuple(A.psi(w) for w in range(8))          # (0,3,2,3,1,3,3,3)
BIO_PHI = tuple(WTA_IN.index(A.phi(d)) for d in range(4))   # (0,1,2,3)

# ---------------- generator construction (mirrors audit.composite_gens) ------

def gens_W_to_D(psi):
    G = []
    for gamma in range(4):
        t = bytearray(N)
        fWg = fW[gamma]
        for i in range(N):
            d, w = divmod(i, 8)
            wn = fWg[w]
            dn = fD4[psi[wn]][d]
            t[i] = 8 * dn + wn
        G.append(bytes(t))
    return tuple(G)

def gens_D_to_W(phi):
    G = []
    for gamma in range(4):
        t = bytearray(N)
        fDg = fD4[gamma]
        for i in range(N):
            d, w = divmod(i, 8)
            dn = fDg[d]
            wn = fW[phi[dn]][w]
            t[i] = 8 * dn + wn
        G.append(bytes(t))
    return tuple(G)

def gens_rec(scheme, phi, psi):
    G = []
    for gamma in range(4):
        t = bytearray(N)
        for i in range(N):
            d, w = divmod(i, 8)
            if scheme == "rec_sync":
                dn = fD4[psi[w]][d]
                wn = fW[phi[d]][w]
            elif scheme == "rec_async_D":
                dn = fD4[psi[w]][d]
                wn = fW[phi[dn]][w]
            elif scheme == "rec_async_W":
                wn = fW[phi[d]][w]
                dn = fD4[psi[wn]][d]
            else:
                raise ValueError(scheme)
            t[i] = 8 * dn + wn
        G.append(bytes(t))
    return tuple(G)

def gens_prod():
    G = []
    for gamma in range(4):
        t = bytearray(N)
        for i in range(N):
            d, w = divmod(i, 8)
            t[i] = 8 * fD4[gamma][d] + fW[gamma][w]
        G.append(bytes(t))
    return tuple(G)

# ---------------- cycle classification --------------------------------------

def classify_cycle(c):
    ds = {x // 8 for x in c}
    ws = {x % 8 for x in c}
    if len(ds) > 1 and len(ws) > 1:
        return "composite"
    if len(ds) > 1:
        return "DN-local"
    if len(ws) > 1:
        return "WTA-local"
    return "trivial"

def elt_classes(m):
    """classes of the nontrivial cycles of a single transformation."""
    return {classify_cycle(c) for c in F.nontrivial_cycles(m)}

def primary_class(m):
    cl = elt_classes(m)
    if "composite" in cl: return "composite"
    if "DN-local" in cl:  return "DN-local"
    if "WTA-local" in cl: return "WTA-local"
    return "none"

# ---------------- full analysis of one generated monoid ---------------------

def analyse(gens, names=("g0", "g1", "g2", "g3"), n=N):
    M = F.monoid(list(gens), n)
    idem = 0
    nonap = []
    for m in M:
        if m.translate(F.tab(m)) == m:
            idem += 1
        if not F.is_aperiodic_elt(m):
            nonap.append(m)
    U = F.units(M, n)

    # which cycle classes exist anywhere in the monoid
    present = set()
    for m in nonap:
        present |= elt_classes(m)

    # exact Cayley-graph BFS from the identity over the whole monoid:
    # gives the minimal word length reaching every element (no length cap).
    idt = bytes(range(n))
    parent = {idt: None}
    level = [idt]
    first_any = first_comp = None
    depth = 0
    if not F.is_aperiodic_elt(idt):      # cannot happen; guard
        first_any = idt
    while level and (first_any is None or first_comp is None):
        nxt = []
        for f in level:
            for i, g in enumerate(gens):
                h = f.translate(F.tab(g))       # h = g o f  (append symbol i on right)
                if h in parent:
                    continue
                parent[h] = (f, i)
                nxt.append(h)
                if not F.is_aperiodic_elt(h):
                    if first_any is None:
                        first_any = h
                    if first_comp is None and "composite" in elt_classes(h):
                        first_comp = h
        level = nxt
        depth += 1

    def word(h):
        w = []
        cur = h
        while parent[cur] is not None:
            cur, i = parent[cur]
            w.append(names[i])
        return list(reversed(w))

    def pack(h):
        if h is None:
            return dict(word=None, len=None, elt=None, cycles=None, cls="none")
        cyc = F.nontrivial_cycles(h)
        return dict(word=word(h), len=len(word(h)), elt=list(h),
                    cycles=[list(c) for c in cyc], cls=primary_class(h))

    wa, wc = pack(first_any), pack(first_comp)
    return dict(monoid_size=len(M), n_idempotents=idem, n_nonaperiodic=len(nonap),
                n_units=len(U), units_trivial=(len(U) == 1),
                classes_present=sorted(present),
                has_composite=("composite" in present),
                has_dn_local=("DN-local" in present),
                has_wta_local=("WTA-local" in present),
                gens_all_aperiodic=all(F.is_aperiodic_elt(g) for g in gens),
                n_gens_nonaperiodic=sum(1 for g in gens if not F.is_aperiodic_elt(g)),
                witness_word=wa["word"], witness_len=wa["len"],
                witness_cycles=wa["cycles"], witness_class=wa["cls"],
                comp_witness_word=wc["word"], comp_witness_len=wc["len"],
                comp_witness_cycles=wc["cycles"],
                shortest_is_composite=(wa["cls"] == "composite"))

# ---------------- psi stratification (biological null classes) ---------------

def psi_class(psi):
    """
    How much winner information does psi carry?
      constant        : psi(w) identical for all w  -> passthrough / uncoupled
      g_only          : psi depends only on the gating bit g = w & 1
      winner_only     : psi depends only on the winner identity (b1,b2) = w >> 1
      both            : psi depends on g and on (b1,b2)
    """
    if len(set(psi)) == 1:
        return "constant"
    by_g = all(psi[w] == psi[w ^ 2] and psi[w] == psi[w ^ 4] for w in range(8))
    by_win = all(psi[w] == psi[w ^ 1] for w in range(8))
    if by_g and by_win:
        return "constant"
    if by_g:
        return "g_only"
    if by_win:
        return "winner_only"
    return "both"

def n_psi_values(psi):
    return len(set(psi))

# ---------------- worker (multiprocessing) ----------------------------------

def _work_psi(k):
    psi = tuple((k >> (2 * j)) & 3 for j in range(8))
    r = analyse(gens_W_to_D(psi))
    r["psi_code"] = k
    r["psi"] = "".join(map(str, psi))
    r["psi_class"] = psi_class(psi)
    r["psi_nvals"] = n_psi_values(psi)
    r["is_bio_psi"] = (psi == BIO_PSI)
    return r

def _work_phi(k):
    phi = tuple((k >> (2 * j)) & 3 for j in range(4))
    r = analyse(gens_D_to_W(phi))
    r["phi_code"] = k
    r["phi"] = "".join(map(str, phi))
    r["phi_class"] = ("constant" if len(set(phi)) == 1
                      else "injective" if len(set(phi)) == 4 else "partial")
    r["phi_nvals"] = len(set(phi))
    r["is_bio_phi"] = (phi == BIO_PHI)
    return r

def _work_rec(arg):
    scheme, kphi, kpsi = arg
    phi = tuple((kphi >> (2 * j)) & 3 for j in range(4))
    psi = tuple((kpsi >> (2 * j)) & 3 for j in range(8))
    r = analyse(gens_rec(scheme, phi, psi))
    r["scheme"] = scheme
    r["phi"] = "".join(map(str, phi)); r["phi_code"] = kphi
    r["psi"] = "".join(map(str, psi)); r["psi_code"] = kpsi
    r["psi_class"] = psi_class(psi)
    r["phi_nvals"] = len(set(phi)); r["psi_nvals"] = n_psi_values(psi)
    r["is_bio"] = (psi == BIO_PSI and phi == BIO_PHI)
    return r

# ---------------- drivers ----------------------------------------------------

def run_psi_sweep(out="psi_sweep.jsonl", nproc=None, chunk=256):
    import multiprocessing as mp
    nproc = nproc or os.cpu_count()
    t0 = time.time()
    with mp.Pool(nproc) as pool, open(out, "w") as fh:
        for i, r in enumerate(pool.imap_unordered(_work_psi, range(65536), chunk)):
            fh.write(json.dumps(r) + "\n")
            if (i + 1) % 8192 == 0:
                print("psi %d/65536  %.1fs" % (i + 1, time.time() - t0), flush=True)
    print("psi sweep done %.1fs" % (time.time() - t0), flush=True)

def run_phi_sweep(out="phi_sweep.jsonl", nproc=None):
    import multiprocessing as mp
    nproc = nproc or os.cpu_count()
    with mp.Pool(nproc) as pool, open(out, "w") as fh:
        for r in pool.imap_unordered(_work_phi, range(256), 8):
            fh.write(json.dumps(r) + "\n")
    print("phi sweep done", flush=True)

def run_rec_sweep(tasks, out="rec_sweep.jsonl", nproc=None, chunk=512):
    import multiprocessing as mp
    nproc = nproc or os.cpu_count()
    t0 = time.time()
    with mp.Pool(nproc) as pool, open(out, "w") as fh:
        for i, r in enumerate(pool.imap_unordered(_work_rec, tasks, chunk)):
            fh.write(json.dumps(r) + "\n")
            if (i + 1) % 50000 == 0:
                print("rec %d  %.1fs" % (i + 1, time.time() - t0), flush=True)
    print("rec sweep done %.1fs" % (time.time() - t0), flush=True)

# ---------------- STEP 3b: full (phi,psi) grid for recurrent schemes ---------
# 256 phi x 65536 psi x 3 schemes = 50,331,648 monoid enumerations.  Rows are
# aggregated inside the worker (counts only) so the output stays small; a
# stratified subset is additionally dumped row-wise for the CSV.

def _agg_rec_block(arg):
    """One block = one scheme x one phi x all 65536 psi.  Returns a counter dict."""
    scheme, kphi = arg
    phi = tuple((kphi >> (2 * j)) & 3 for j in range(4))
    phi_nv = len(set(phi))
    phi_cls = ("constant" if phi_nv == 1 else "injective" if phi_nv == 4 else "partial")
    from collections import Counter
    cnt = Counter()
    sizes = Counter()
    for kpsi in range(65536):
        psi = tuple((kpsi >> (2 * j)) & 3 for j in range(8))
        r = analyse(gens_rec(scheme, phi, psi))
        pc = psi_class(psi)
        genlvl = (r["n_gens_nonaperiodic"] > 0)
        key = (scheme, phi_cls, pc, r["witness_class"], r["has_composite"], genlvl)
        cnt[key] += 1
        sizes[(scheme, phi_cls, pc, r["monoid_size"])] += 1
    return {"counts": {"|".join(map(str, k)): v for k, v in cnt.items()},
            "sizes":  {"|".join(map(str, k)): v for k, v in sizes.items()}}

def run_rec_grid(out="rec_grid.json", nproc=None):
    import multiprocessing as mp
    from collections import Counter
    nproc = nproc or os.cpu_count()
    tasks = [(sc, kphi) for sc in ("rec_sync", "rec_async_D", "rec_async_W")
             for kphi in range(256)]
    C, Z = Counter(), Counter()
    t0 = time.time()
    with mp.Pool(nproc) as pool:
        for i, d in enumerate(pool.imap_unordered(_agg_rec_block, tasks, 1)):
            C.update(d["counts"]); Z.update(d["sizes"])
            if (i + 1) % 32 == 0:
                print("rec grid block %d/768  %.1fs" % (i + 1, time.time() - t0), flush=True)
    json.dump({"counts": dict(C), "sizes": dict(Z),
               "n_cases": sum(C.values())}, open(out, "w"))
    print("rec grid done %.1fs  n=%d" % (time.time() - t0, sum(C.values())), flush=True)

def stratified_psi_subset(m=256, seed=11):
    """m psi codes, stratified equally over the four psi classes."""
    import random
    rng = random.Random(seed)
    buckets = {}
    for k in range(65536):
        psi = tuple((k >> (2 * j)) & 3 for j in range(8))
        buckets.setdefault(psi_class(psi), []).append(k)
    per = max(1, m // len(buckets))
    out = []
    for cls, ks in sorted(buckets.items()):
        out += (ks if len(ks) <= per else rng.sample(ks, per))
    for k in (int("".join(str(v) for v in reversed(BIO_PSI)), 4),):
        pass
    bio = sum(BIO_PSI[j] << (2 * j) for j in range(8))
    if bio not in out:
        out.append(bio)
    return sorted(set(out))

def run_rec_rows(out="rec_rows.jsonl", nproc=None):
    import multiprocessing as mp
    nproc = nproc or os.cpu_count()
    psis = stratified_psi_subset(256)
    phis = list(range(256))
    tasks = [(sc, kp, ks) for sc in ("rec_sync", "rec_async_D", "rec_async_W")
             for kp in phis for ks in psis]
    with mp.Pool(nproc) as pool, open(out, "w") as fh:
        for r in pool.imap_unordered(_work_rec, tasks, 512):
            fh.write(json.dumps(r) + "\n")
    print("rec rows done n=%d" % len(tasks), flush=True)
