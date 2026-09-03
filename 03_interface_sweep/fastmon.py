"""
Fast exact transformation-monoid enumeration for the AlgCanNet interface sweep.

Elements are `bytes` of length n (the tuple (f(0),...,f(n-1))).
Composition (f o g)(x) = f(g(x))  ==  g.translate(table(f))
where table(f) = f padded to 256 bytes.  This pushes the hot loop into C.

Aperiodicity: f is aperiodic iff every cycle of its functional graph is a fixed
point, iff f^n == f^(n+1) for n >= |X| (index-period with period 1).  We test
f^32 == f^33 via repeated squaring (n=32 covers every system here).
"""

def tab(f, n=None):
    return f + bytes(256 - len(f))

def comp(f, g):
    """(f o g)(x) = f(g(x))"""
    return g.translate(tab(f))

def _pow_stab(f):
    """f^m for m = 2^ceil(log2(n)) >= n, via repeated squaring."""
    n = len(f)
    m = 1
    p = f
    while m < n:
        p = p.translate(tab(p))
        m *= 2
    return p

def is_aperiodic_elt(f):
    p = _pow_stab(f)               # p = f^m, m >= n  -> p is in the 'stable' range
    return p.translate(tab(f)) == p   # f^(m+1) == f^m

def cycles(f):
    n = len(f)
    seen = [0] * n
    out = []
    for s in range(n):
        if seen[s]:
            continue
        path, pos = [], {}
        x = s
        while True:
            if seen[x] == 2:
                break
            if seen[x] == 1:
                out.append(tuple(path[pos[x]:]))
                break
            seen[x] = 1
            pos[x] = len(path)
            path.append(x)
            x = f[x]
        for y in path:
            seen[y] = 2
    return out

def nontrivial_cycles(f):
    return [c for c in cycles(f) if len(c) > 1]

def monoid(gens, n):
    """Exact closure under composition, including the identity. Returns set of bytes."""
    idt = bytes(range(n))
    gtabs = [tab(g) for g in gens]
    M = {idt}
    M.update(gens)
    frontier = list(M)
    add = M.add
    while frontier:
        new = []
        for a in frontier:
            ta = tab(a)
            for g, tg in zip(gens, gtabs):
                p = g.translate(ta)        # a o g
                if p not in M:
                    add(p); new.append(p)
                p = a.translate(tg)        # g o a
                if p not in M:
                    add(p); new.append(p)
        frontier = new
    return M

def inverse(f):
    n = len(f)
    inv = bytearray(n)
    for x in range(n):
        inv[f[x]] = x
    return bytes(inv)

def units(M, n):
    idt = bytes(range(n))
    U = []
    for m in M:
        if len(set(m)) == n:
            if inverse(m) in M:
                U.append(m)
    return sorted(U)
