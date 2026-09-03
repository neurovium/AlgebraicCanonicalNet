"""
Reproduce the transition-monoid audit of the AlgCanNet draft from the Methods
section, and export GAP-compatible generators for the SgpDec holonomy analysis.

Conventions follow the draft:
  transformation f on X={0..n-1} is the tuple (f(0),...,f(n-1));
  composition (f o g)(x) = f(g(x));
  a word (a_1,...,a_k) acts as f_{a_k} o ... o f_{a_1}.
"""
import itertools, json
from collections import deque

# ---------- transformation utilities ----------------------------------------

def comp(f, g):
    """(f o g)(x) = f(g(x))"""
    return tuple(f[g[x]] for x in range(len(g)))

def rank(f):
    return len(set(f))

def cycles(f):
    """All cycles of the functional graph of f, as tuples."""
    n = len(f)
    seen = [0] * n          # 0 unvisited, 1 on stack, 2 done
    out = []
    for s in range(n):
        if seen[s]:
            continue
        path, pos = [], {}
        x = s
        while True:
            if seen[x] == 2:
                break
            if seen[x] == 1:          # closed a cycle inside this walk
                out.append(tuple(path[pos[x]:]))
                break
            seen[x] = 1
            pos[x] = len(path)
            path.append(x)
            x = f[x]
        for y in path:
            seen[y] = 2
    return out

def is_aperiodic_elt(f):
    """f is aperiodic iff every cycle of its functional graph is a fixed point."""
    return all(len(c) == 1 for c in cycles(f))

def monoid(gens, n):
    """Exact closure under composition, including the identity."""
    idt = tuple(range(n))
    M = {idt}
    M.update(gens)
    frontier = list(M)
    while frontier:
        new = []
        for a in frontier:
            for g in gens:
                for p in (comp(a, g), comp(g, a)):
                    if p not in M:
                        M.add(p)
                        new.append(p)
        frontier = new
    return M

def units(M, n):
    idt = tuple(range(n))
    return sorted(m for m in M if any(comp(m, k) == idt and comp(k, m) == idt for k in M))

def shortest_witness(gens, names, n, maxlen=8):
    """BFS over words; return the first non-aperiodic composite transformation."""
    idt = tuple(range(n))
    seen = {idt}
    q = deque([(idt, [])])
    while q:
        f, w = q.popleft()
        if len(w) >= maxlen:
            continue
        for i, g in enumerate(gens):
            h = comp(g, f)                      # append symbol i on the right of the word
            wd = w + [names[i]]
            if not is_aperiodic_elt(h):
                return wd, h, [c for c in cycles(h) if len(c) > 1]
            if h not in seen:
                seen.add(h)
                q.append((h, wd))
    return None, None, None

def audit(label, gens, names, n, maxlen=8):
    M = monoid(gens, n)
    idem = [m for m in M if comp(m, m) == m]
    nonap = [m for m in M if not is_aperiodic_elt(m)]
    U = units(M, n)
    w, h, cyc = shortest_witness(gens, names, n, maxlen)
    rk = {}
    for m in M:
        rk[rank(m)] = rk.get(rank(m), 0) + 1
    rk_nonap = {}
    for m in nonap:
        rk_nonap[rank(m)] = rk_nonap.get(rank(m), 0) + 1
    return dict(label=label, n=n, n_gens=len(gens),
                gens={names[i]: list(g) for i, g in enumerate(gens)},
                gens_all_aperiodic=all(is_aperiodic_elt(g) for g in gens),
                gens_aperiodic={names[i]: is_aperiodic_elt(g) for i, g in enumerate(gens)},
                monoid_size=len(M), n_idempotents=len(idem),
                n_nonaperiodic=len(nonap),
                units=[list(u) for u in U],
                rank_dist=dict(sorted(rk.items())),
                rank_dist_nonaperiodic=dict(sorted(rk_nonap.items())),
                witness_word=w, witness=list(h) if h else None,
                witness_cycles=[list(c) for c in cyc] if cyc else None)

# ---------- divisive normalization ------------------------------------------

def dn3_gens():
    """s' = min(floor(2d/(1+s)), 2) on Q={0,1,2}."""
    return [tuple(min((2 * d) // (1 + s), 2) for s in range(3)) for d in range(3)]

def dn4_gens(N=4, sigma=2, beta=1, alpha=2):
    """s' = clip(round(alpha*d/(sigma+beta*s)), 0, N-1); round = round-half-to-even."""
    g = []
    for d in range(N):
        g.append(tuple(min(max(round(alpha * d / (sigma + beta * s)), 0), N - 1)
                       for s in range(N)))
    return g

# ---------- winner-take-all --------------------------------------------------

WTA_P = dict(G=1, S=0.5, L=0.5, B=0.5, thE=0.5, W=0.5, R=0.0, thI=0.5)

def H(z):
    return 1 if z >= 0 else 0

def wta_dec(q):
    return ((q >> 2) & 1, (q >> 1) & 1, q & 1)

def wta_enc(x1, x2, y):
    return 4 * x1 + 2 * x2 + y

def wta_step(q, d1, d2, p=WTA_P):
    x1, x2, y = wta_dec(q)
    n1 = H(p["G"] * d1 + p["S"] * x1 - p["L"] * x2 - p["B"] * y - p["thE"])
    n2 = H(p["G"] * d2 + p["S"] * x2 - p["L"] * x1 - p["B"] * y - p["thE"])
    ny = H(p["W"] * (x1 + x2) + p["R"] * y - p["thI"])
    return wta_enc(n1, n2, ny)

WTA_IN = [(0, 0), (1, 0), (0, 1), (1, 1)]      # 00, 10, 01, 11

def wta_gens():
    return [tuple(wta_step(q, d1, d2) for q in range(8)) for (d1, d2) in WTA_IN]

# ---------- DN--WTA composition ---------------------------------------------

def idx(d, w):
    return 8 * d + w

def dec(i):
    return divmod(i, 8)

def kappa_W(gamma):
    return WTA_IN[gamma]

def phi(d):
    """DN state -> WTA drive condition (default interface)."""
    return WTA_IN[d]

def psi(w):
    """WTA state -> DN input symbol (default winner-pooling interface)."""
    b1, b2, g = wta_dec(w)
    if g == 1 or (b1 == 1 and b2 == 1):
        return 3
    if b1 == 1 and b2 == 0:
        return 1
    if b1 == 0 and b2 == 1:
        return 2
    return 0

def composite_gens(scheme, fD, fW):
    G = []
    for gamma in range(4):
        t = []
        for i in range(32):
            d, w = dec(i)
            if scheme == "prod":
                dn, wn = fD[gamma][d], fW[gamma][w]
            elif scheme == "D_to_W":
                dn = fD[gamma][d]
                wn = fW[WTA_IN.index(phi(dn))][w]
            elif scheme == "W_to_D":
                wn = fW[gamma][w]
                dn = fD[psi(wn)][d]
            elif scheme == "rec_sync":
                dn = fD[psi(w)][d]
                wn = fW[WTA_IN.index(phi(d))][w]
            elif scheme == "rec_async_D":
                dn = fD[psi(w)][d]
                wn = fW[WTA_IN.index(phi(dn))][w]
            elif scheme == "rec_async_W":
                wn = fW[WTA_IN.index(phi(d))][w]
                dn = fD[psi(wn)][d]
            else:
                raise ValueError(scheme)
            t.append(idx(dn, wn))
        G.append(tuple(t))
    return G

# ---------- run --------------------------------------------------------------

if __name__ == "__main__":
    fD3, fD4, fW = dn3_gens(), dn4_gens(), wta_gens()
    results = []
    results.append(audit("DN_3state", fD3, [f"D{i}" for i in range(3)], 3))
    results.append(audit("DN_4state", fD4, [f"D{i}" for i in range(4)], 4))
    results.append(audit("WTA", fW, ["W00", "W10", "W01", "W11"], 8))
    for scheme, lab in [("prod", "prod"), ("D_to_W", "D_to_W"), ("W_to_D", "W_to_D"),
                        ("rec_sync", "rec_sync"), ("rec_async_D", "rec_async_D"),
                        ("rec_async_W", "rec_async_W")]:
        G = composite_gens(scheme, fD4, fW)
        results.append(audit(lab, G, [f"{lab}[g{i}]" for i in range(4)], 32, maxlen=6))

    with open("audit_results.json", "w") as fh:
        json.dump(results, fh, indent=1)

    for r in results:
        print(f"{r['label']:>14s} n={r['n']:>2d} |M|={r['monoid_size']:>5d} "
              f"idem={r['n_idempotents']:>4d} nonap={r['n_nonaperiodic']:>4d} "
              f"gens_ap={str(r['gens_all_aperiodic']):>5s} |U|={len(r['units'])} "
              f"witness={r['witness_word']} cyc={r['witness_cycles']}")
