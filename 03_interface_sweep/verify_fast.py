import json, itertools
import audit as A
import fastmon as F

res = {r["label"]: r for r in json.load(open("audit_results.json"))}

def B(t):  return bytes(t)

def check(label, gens_t, names, n, maxlen):
    gens = [B(g) for g in gens_t]
    # cross-check primitives against audit.py on many random pairs
    M = F.monoid(gens, n)
    Ma = A.monoid([tuple(g) for g in gens], n)
    assert {tuple(m) for m in M} == Ma, (label, "monoid mismatch", len(M), len(Ma))
    for m in list(M)[:400]:
        assert F.is_aperiodic_elt(m) == A.is_aperiodic_elt(tuple(m)), (label, m)
    idem = sum(1 for m in M if m.translate(F.tab(m)) == m)
    nonap = sum(1 for m in M if not F.is_aperiodic_elt(m))
    U = F.units(M, n)
    Ua = A.units(Ma, n)
    assert sorted(tuple(u) for u in U) == Ua, (label, "units")
    r = res[label]
    out = (len(M), idem, nonap, len(U))
    exp = (r["monoid_size"], r["n_idempotents"], r["n_nonaperiodic"], len(r["units"]))
    assert out == exp, (label, out, exp)
    return out

fD3, fD4, fW = A.dn3_gens(), A.dn4_gens(), A.wta_gens()
print(check("DN_3state", fD3, None, 3, 8))
print(check("DN_4state", fD4, None, 4, 8))
print(check("WTA", fW, None, 8, 8))
for scheme in ["prod","D_to_W","W_to_D","rec_sync","rec_async_D","rec_async_W"]:
    G = A.composite_gens(scheme, fD4, fW)
    print(scheme, check(scheme, G, None, 32, 6))
print("ALL PRIMITIVES MATCH audit.py AND audit_results.json")
