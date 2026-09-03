"""Re-derive every number quoted in findings.md straight from the sweep outputs."""
import json, re, pandas as pd, numpy as np, sweep as S

psi = pd.read_pickle("psi_df.pkl"); phi = pd.read_pickle("phi_df.pkl"); G = pd.read_pickle("grid_df.pkl")
txt = open("findings.md").read()
checks = []
def ck(name, val, expect=None):
    ok = (val == expect) if expect is not None else None
    checks.append((name, val, expect, ok))

cou = psi[psi.psi_class != "constant"]; unc = psi[psi.psi_class == "constant"]
ck("psi_n", len(psi), 65536)
ck("distinct_gen_tuples", psi.psi_code.map(lambda k: S.gens_W_to_D(tuple((k>>(2*j))&3 for j in range(8)))).nunique(), 65536)
ck("M_min", int(psi.monoid_size.min()), 326)
ck("M_max", int(psi.monoid_size.max()), 22581)
ck("M_med", float(psi.monoid_size.median()), 832.0)
ck("gens_all_ap", int(psi.gens_all_aperiodic.sum()), 65536)
ck("units_trivial", int(psi.units_trivial.sum()), 65536)
ck("aperiodic_monoids", int((psi.witness_class == "none").sum()), 0)
ck("has_comp_total", int(psi.has_composite.sum()), 65278)
ck("no_comp_total", int((~psi.has_composite).sum()), 258)
ck("has_comp_total_frac", round(float(psi.has_composite.mean()), 6), 0.996063)
ck("coupled_n", len(cou), 65532)
ck("coupled_has_comp", int(cou.has_composite.sum()), 65278)
ck("coupled_frac", round(float(cou.has_composite.mean()), 6), 0.996124)
ck("uncoupled_has_comp", int(unc.has_composite.sum()), 0)
ck("uncoupled_sizes", sorted(map(int, unc.monoid_size)), [326, 328, 328, 343])
ck("uncoupled_idem", sorted(map(int, unc.n_idempotents)), [55, 55, 55, 55])
ck("uncoupled_nonap", sorted(map(int, unc.n_nonaperiodic)), [49, 49, 49, 55])
ck("uncoupled_wlen", sorted(map(int, unc.witness_len)), [2, 2, 2, 2])
ck("uncoupled_all_wta", list(unc.witness_class.unique()), ["WTA-local"])
prod = S.analyse(S.gens_prod())
ck("prod_M", prod["monoid_size"], 576); ck("prod_idem", prod["n_idempotents"], 103)
ck("prod_nonap", prod["n_nonaperiodic"], 88); ck("prod_has_comp", prod["has_composite"], False)
ck("prod_wcls", prod["witness_class"], "WTA-local")
ck("prod_cyc", prod["witness_cycles"], [[12, 13]])

img = psi.psi.map(lambda t: frozenset(int(c) for c in t))
pred = img.map(lambda s: s <= {1, 2}) | (psi.psi == "0"*8) | (psi.psi == "3"*8)
ck("charac_exact", bool((pred == ~psi.has_composite).all()), True)
ck("n_img_in_12", int(img.map(lambda s: s <= {1, 2}).sum()), 256)
ck("charac_total", int(pred.sum()), 258)
ck("coupled_no_comp", int((~cou.has_composite).sum()), 254)
ck("coupled_no_comp_all_img12", bool(cou[~cou.has_composite].psi.map(lambda t: {int(c) for c in t} <= {1,2}).all()), True)
ck("no_comp_all_wta_witness", list(psi[~psi.has_composite].witness_class.unique()), ["WTA-local"])

BIO = psi[psi.is_bio_psi].iloc[0]
ck("bio_psi_str", BIO.psi, "03231333")
ck("bio_M", int(BIO.monoid_size), 3084); ck("bio_idem", int(BIO.n_idempotents), 186)
ck("bio_nonap", int(BIO.n_nonaperiodic), 361); ck("bio_wlen", int(BIO.witness_len), 2)
ck("bio_word", BIO.witness_word, ["g0", "g1"]); ck("bio_cyc", BIO.witness_cycles, [[4, 13]])
ck("bio_wcls", BIO.witness_class, "composite")
ck("bio_pctile", round(float((psi.monoid_size < BIO.monoid_size).mean())*100, 1), 95.7)
ck("bio_n_larger", int((psi.monoid_size > BIO.monoid_size).sum()), 2816)
ck("bio_n_equal", int((psi.monoid_size == BIO.monoid_size).sum()), 6)
ck("all_wlen_2", set(map(int, psi.witness_len)), {2})
ck("wcls_comp", int((psi.witness_class == "composite").sum()), 43008)
ck("wcls_wta", int((psi.witness_class == "WTA-local").sum()), 22528)
ck("coupled_short_comp", int(cou.shortest_is_composite.sum()), 43008)
ck("coupled_short_frac", round(float(cou.shortest_is_composite.mean()), 6), 0.656290)
sub = cou[cou.has_composite]
ck("cond_short_frac", round(float(sub.shortest_is_composite.mean()), 6), 0.658844)
ck("has_dn_local", int(psi.has_dn_local.sum()), 18143)
ck("has_wta_local", int(psi.has_wta_local.sum()), 65517)
ck("comp_only", int(psi.classes_present.map(lambda x: x == ["composite"]).sum()), 19)

for cls, exp in [("constant", (4,0,0,4,326,328.0,343)), ("g_only", (12,10,10,2,328,476.5,8950)),
                 ("winner_only", (252,238,64,188,327,588.0,6204)), ("both", (65268,65030,42934,22334,326,833.0,22581))]:
    d = psi[psi.psi_class == cls]
    got = (len(d), int(d.has_composite.sum()), int(d.shortest_is_composite.sum()),
           int((d.witness_class=="WTA-local").sum()), int(d.monoid_size.min()),
           float(d.monoid_size.median()), int(d.monoid_size.max()))
    ck("strat_"+cls, got, exp)
ck("winner_only_frac", round(64/252, 6), 0.253968)

cp = phi[phi.phi_class != "constant"]
ck("phi_M_min", int(phi.monoid_size.min()), 27); ck("phi_M_max", int(phi.monoid_size.max()), 3795)
ck("phi_M_med", float(phi.monoid_size.median()), 363.0)
ck("phi_aperiodic", int((phi.witness_class=="none").sum()), 0)
ck("phi_gens_ap", int(phi.gens_all_aperiodic.sum()), 256)
ck("phi_coupled_comp", int(cp.has_composite.sum()), 224)
ck("phi_coupled_n", len(cp), 252)
ck("phi_coupled_frac", round(float(cp.has_composite.mean()), 6), 0.888889)
ck("phi_const_comp", int(phi[phi.phi_class=="constant"].has_composite.sum()), 0)
ck("phi_short_comp", int(cp.shortest_is_composite.sum()), 30)
ck("phi_short_frac", round(float(cp.shortest_is_composite.mean()), 6), 0.119048)
ck("phi_cond_frac", round(30/224, 6), 0.133929)
ck("phi_wta", int((phi.witness_class=="WTA-local").sum()), 192)
ck("phi_dn", int((phi.witness_class=="DN-local").sum()), 34)
BP = phi[phi.is_bio_phi].iloc[0]
ck("bphi_M", int(BP.monoid_size), 3149); ck("bphi_wcls", BP.witness_class, "WTA-local")
ck("bphi_cyc", BP.witness_cycles, [[12,13]]); ck("bphi_wlen", int(BP.witness_len), 2)
ck("bphi_comp_len", int(BP.comp_witness_len), 3)
inj = phi[phi.phi_class=="injective"]
ck("phi_inj_comp", int(inj.has_composite.sum()), 24)
ck("phi_inj_short", int(inj.shortest_is_composite.sum()), 0)

for sc, exp in [("rec_sync", (16777216, 8616638, 8160578, 8616638)),
                ("rec_async_D", (16777216, 6274480, 10502736, 6274480)),
                ("rec_async_W", (16777216, 6274480, 10502736, 6274480))]:
    d = G[G.scheme == sc]
    got = (int(d.n.sum()), int(d[d.has_composite].n.sum()),
           int(d[d.witness_class=="none"].n.sum()), int(d[d.gen_level].n.sum()))
    ck("sched_"+sc, got, exp)
ck("grid_total", int(G.n.sum()), 50331648)
ck("rec_nonap_no_genlevel", int(G[(G.witness_class!="none") & (~G.gen_level)].n.sum()), 0)
ck("rec_comp_not_witness", int(G[(G.has_composite) & (G.witness_class!="composite")].n.sum()), 0)
ck("rec_wcls", dict(G.groupby("witness_class").n.sum().astype(int)),
   {"composite": 21165598, "none": 29166050})
ck("sync_frac", round(8616638/16777216, 6), 0.513592)
ck("async_frac", round(6274480/16777216, 6), 0.373988)
ck("async_ratio", round((6274480/16777216)/(8616638/16777216), 3), 0.728)
sz = pd.DataFrame([dict(zip(["scheme","phi_class","psi_class","size"], k.split("|")), n=v)
                   for k, v in json.load(open("rec_grid.json"))["sizes"].items()])
sz["size"] = sz["size"].astype(int)
for sc, exp in [("rec_sync", (3, 212, 9.264)), ("rec_async_D", (3, 62, 6.448)), ("rec_async_W", (3, 62, 6.472))]:
    d = sz[sz.scheme == sc]
    got = (int(d["size"].min()), int(d["size"].max()), round(float((d["size"]*d.n).sum()/d.n.sum()), 3))
    ck("recsize_"+sc, got, exp)
for sc, cls, exp in [("rec_sync","constant",0.0),("rec_async_D","constant",0.0),("rec_async_W","constant",0.0),
                     ("rec_sync","injective",0.687331),("rec_async_D","injective",0.505946)]:
    d = G[(G.scheme==sc) & (G.phi_class==cls)]
    ck(f"recphi_{sc}_{cls}", round(float(d[d.has_composite].n.sum()/d.n.sum()), 6), exp)
ck("rec_const_phi_n", int(G[(G.scheme=="rec_sync") & (G.phi_class=="constant")].n.sum()), 262144)
rr = pd.read_json("rec_rows.jsonl", lines=True)
b = rr[rr.is_bio].set_index("scheme")
ck("bio_rec_sync", (int(b.loc["rec_sync"].monoid_size), int(b.loc["rec_sync"].n_nonaperiodic),
                    int(b.loc["rec_sync"].n_gens_nonaperiodic)), (9, 6, 4))
ck("bio_rec_async_D", (int(b.loc["rec_async_D"].monoid_size), int(b.loc["rec_async_D"].n_nonaperiodic)), (8, 0))
ck("bio_rec_async_W", (int(b.loc["rec_async_W"].monoid_size), int(b.loc["rec_async_W"].n_nonaperiodic)), (8, 0))
ck("rec_rows_n", len(rr), 111360)
ck("wta_image_full", sorted({g[w] for g in S.fW for w in range(8)}), list(range(8)))

bad = [c for c in checks if c[3] is False]
print("checks run:", len(checks), " FAILED:", len(bad))
for c in bad: print("  FAIL", c[0], "got", c[1], "expected", c[2])
if not bad: print("ALL FINDINGS NUMBERS VERIFIED AGAINST SWEEP OUTPUT")
