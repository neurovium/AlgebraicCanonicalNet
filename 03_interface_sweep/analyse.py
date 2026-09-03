"""Aggregate the interface sweeps into the manuscript tables + figure inputs."""
import json, itertools
import pandas as pd, numpy as np
import sweep as S

def load(fn): return pd.DataFrame([json.loads(l) for l in open(fn)])

psi = load("psi_sweep.jsonl").sort_values("psi_code").reset_index(drop=True)
assert len(psi) == 65536 and psi.psi_code.nunique() == 65536

# ---- distinct systems: dedupe on the generated generator tuple ----
gk = {}
for k in range(65536):
    p = tuple((k >> (2*j)) & 3 for j in range(8))
    gk[k] = S.gens_W_to_D(p)
psi["gen_key"] = psi.psi_code.map(lambda k: gk[k])
n_distinct_gens = psi.gen_key.nunique()
# also dedupe on the induced psi-restriction (psi only ever evaluated on image of fW)
img = sorted({g[w] for g in S.fW for w in range(8)})
psi["psi_eff"] = psi.psi.map(lambda s: "".join(s[w] for w in img))
n_distinct_eff = psi.psi_eff.nunique()

psi["coupled"] = psi.psi_class != "constant"
BIO = psi[psi.is_bio_psi].iloc[0]

def frac(d, col):
    return pd.crosstab(d.psi_class, d[col], normalize="index"), pd.crosstab(d.psi_class, d[col])

rows = []
for cls, d in psi.groupby("psi_class"):
    rows.append(dict(
        stratum=cls, n=len(d),
        n_distinct_systems=d.gen_key.nunique(),
        has_composite=int(d.has_composite.sum()),
        frac_has_composite=d.has_composite.mean(),
        shortest_is_composite=int(d.shortest_is_composite.sum()),
        frac_shortest_composite=d.shortest_is_composite.mean(),
        aperiodic_monoid=int((d.witness_class == "none").sum()),
        wc_none=int((d.witness_class=="none").sum()),
        wc_dn=int((d.witness_class=="DN-local").sum()),
        wc_wta=int((d.witness_class=="WTA-local").sum()),
        wc_comp=int((d.witness_class=="composite").sum()),
        M_min=int(d.monoid_size.min()), M_med=float(d.monoid_size.median()),
        M_max=int(d.monoid_size.max()), M_mean=float(d.monoid_size.mean()),
        nonap_med=float(d.n_nonaperiodic.median()),
        gens_all_ap=int(d.gens_all_aperiodic.sum()),
        units_trivial=int(d.units_trivial.sum()),
        wlen_med=float(d.witness_len.dropna().median()) if d.witness_len.notna().any() else None,
        complen_med=float(d.comp_witness_len.dropna().median()) if d.comp_witness_len.notna().any() else None,
    ))
strat = pd.DataFrame(rows).set_index("stratum")

cou = psi[psi.coupled]; unc = psi[~psi.coupled]
prod = S.analyse(S.gens_prod())

summary = dict(
    step1=dict(
        n_interfaces=65536,
        n_distinct_generator_tuples=int(n_distinct_gens),
        n_distinct_effective_psi=int(n_distinct_eff),
        wta_image=img,
        n_coupled=int(len(cou)), n_uncoupled=int(len(unc)),
        coupled_has_composite=int(cou.has_composite.sum()),
        coupled_frac_composite=float(cou.has_composite.mean()),
        coupled_shortest_composite=int(cou.shortest_is_composite.sum()),
        coupled_frac_shortest_composite=float(cou.shortest_is_composite.mean()),
        uncoupled_has_composite=int(unc.has_composite.sum()),
        uncoupled_aperiodic=int((unc.witness_class=="none").sum()),
        uncoupled_monoid_sizes=sorted(map(int, unc.monoid_size.unique())),
        uncoupled_witness_classes=dict(unc.witness_class.value_counts().astype(int)),
        prod_reference=dict(monoid_size=prod["monoid_size"],
                            n_nonaperiodic=prod["n_nonaperiodic"],
                            has_composite=prod["has_composite"],
                            witness_class=prod["witness_class"],
                            witness_cycles=prod["witness_cycles"]),
        aperiodic_monoids_total=int((psi.witness_class=="none").sum()),
        gens_all_aperiodic_total=int(psi.gens_all_aperiodic.sum()),
        units_trivial_total=int(psi.units_trivial.sum()),
        monoid_size_min=int(psi.monoid_size.min()),
        monoid_size_max=int(psi.monoid_size.max()),
        monoid_size_median=float(psi.monoid_size.median()),
        witness_class_counts=dict(psi.witness_class.value_counts().astype(int)),
    ),
    bio_psi=dict(
        psi=BIO.psi, psi_class=BIO.psi_class, monoid_size=int(BIO.monoid_size),
        n_idempotents=int(BIO.n_idempotents), n_nonaperiodic=int(BIO.n_nonaperiodic),
        witness_word=BIO.witness_word, witness_len=int(BIO.witness_len),
        witness_cycles=BIO.witness_cycles, witness_class=BIO.witness_class,
        comp_witness_len=int(BIO.comp_witness_len),
        shortest_is_composite=bool(BIO.shortest_is_composite),
        pct_smaller_M=float((psi.monoid_size < BIO.monoid_size).mean()),
        rank_of_M_desc=int((psi.monoid_size > BIO.monoid_size).sum()) + 1,
        n_with_larger_M=int((psi.monoid_size > BIO.monoid_size).sum()),
        min_witness_len_overall=int(psi.witness_len.dropna().min()),
        n_with_witness_len_2=int((psi.witness_len == 2).sum()),
        n_coupled_witness_len_2=int((cou.witness_len == 2).sum()),
    ),
    strata=json.loads(strat.reset_index().to_json(orient="records")),
)

# ---------------- STEP 3a: phi ----------------
phi = load("phi_sweep.jsonl").sort_values("phi_code").reset_index(drop=True)
assert len(phi) == 256
phi["coupled"] = phi.phi_class != "constant"
BPHI = phi[phi.is_bio_phi].iloc[0]
prows = []
for cls, d in phi.groupby("phi_class"):
    prows.append(dict(stratum=cls, n=len(d),
        has_composite=int(d.has_composite.sum()),
        frac_has_composite=float(d.has_composite.mean()),
        shortest_is_composite=int(d.shortest_is_composite.sum()),
        wc_none=int((d.witness_class=="none").sum()),
        wc_dn=int((d.witness_class=="DN-local").sum()),
        wc_wta=int((d.witness_class=="WTA-local").sum()),
        wc_comp=int((d.witness_class=="composite").sum()),
        M_min=int(d.monoid_size.min()), M_max=int(d.monoid_size.max()),
        M_med=float(d.monoid_size.median()),
        gens_all_ap=int(d.gens_all_aperiodic.sum())))
summary["step3a_phi"] = dict(
    n_interfaces=256, strata=prows,
    n_distinct_generator_tuples=int(pd.Series(
        [S.gens_D_to_W(tuple((k >> (2*j)) & 3 for j in range(4))) for k in range(256)]).nunique()),
    coupled_has_composite=int(phi[phi.coupled].has_composite.sum()),
    n_coupled=int(phi.coupled.sum()),
    bio=dict(phi=BPHI.phi, monoid_size=int(BPHI.monoid_size),
             witness_word=BPHI.witness_word, witness_class=BPHI.witness_class,
             witness_cycles=BPHI.witness_cycles, has_composite=bool(BPHI.has_composite),
             comp_witness_len=(None if pd.isna(BPHI.comp_witness_len) else int(BPHI.comp_witness_len))),
    witness_class_counts=dict(phi.witness_class.value_counts().astype(int)))

# ---------------- STEP 3b: schedules ----------------
grid = json.load(open("rec_grid.json"))
G = []
for key, v in grid["counts"].items():
    sc, phicls, psicls, wcls, hascomp, genlvl = key.split("|")
    G.append(dict(scheme=sc, phi_class=phicls, psi_class=psicls, witness_class=wcls,
                  has_composite=(hascomp=="True"), gen_level=(genlvl=="True"), n=v))
G = pd.DataFrame(G)
assert G.n.sum() == 3*256*65536, G.n.sum()

sched = []
for sc, d in G.groupby("scheme"):
    tot = d.n.sum()
    sched.append(dict(scheme=sc, n_cases=int(tot),
        frac_has_composite=float(d[d.has_composite].n.sum()/tot),
        n_has_composite=int(d[d.has_composite].n.sum()),
        frac_aperiodic_monoid=float(d[d.witness_class=="none"].n.sum()/tot),
        n_aperiodic_monoid=int(d[d.witness_class=="none"].n.sum()),
        frac_gen_level=float(d[d.gen_level].n.sum()/tot),
        n_gen_level=int(d[d.gen_level].n.sum()),
        wc_comp=int(d[d.witness_class=="composite"].n.sum()),
        wc_dn=int(d[d.witness_class=="DN-local"].n.sum()),
        wc_wta=int(d[d.witness_class=="WTA-local"].n.sum()),
        wc_none=int(d[d.witness_class=="none"].n.sum())))
# same, restricted to coupled psi (non-constant) and coupled phi
Gc = G[(G.psi_class!="constant")]
for sc, d in Gc.groupby("scheme"):
    tot = d.n.sum()
    for row in sched:
        if row["scheme"]==sc:
            row["coupled_psi_n"]=int(tot)
            row["coupled_psi_frac_composite"]=float(d[d.has_composite].n.sum()/tot)
            row["coupled_psi_frac_gen_level"]=float(d[d.gen_level].n.sum()/tot)
            row["coupled_psi_frac_aperiodic"]=float(d[d.witness_class=="none"].n.sum()/tot)
summary["step3b_schedule"] = dict(n_cases=int(G.n.sum()), per_scheme=sched,
    grid="256 phi x 65536 psi x 3 recurrent schemes, exhaustive")

# direction comparison at matched interfaces
summary["direction"] = dict(
    W_to_D_coupled_frac_composite=float(cou.has_composite.mean()),
    D_to_W_coupled_frac_composite=float(phi[phi.coupled].has_composite.mean()),
    prod_has_composite=bool(prod["has_composite"]))

def _clean(o):
    import numpy as _np
    if isinstance(o, dict):  return {str(k): _clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)): return [_clean(v) for v in o]
    if isinstance(o, (_np.integer,)): return int(o)
    if isinstance(o, (_np.floating,)): return float(o)
    if isinstance(o, (_np.bool_,)): return bool(o)
    return o
summary = _clean(summary)
json.dump(summary, open("sweep_summary.json","w"), indent=1)

# ---------------- CSV outputs ----------------
def wjoin(x): return "" if not isinstance(x, list) else ",".join(map(str, x))
def cjoin(x): return "" if not isinstance(x, list) else ";".join("("+",".join(map(str,c))+")" for c in x)

pc = psi.drop(columns=["gen_key"]).copy()
pc["sweep"]="psi_W_to_D"; pc["witness_word"]=pc.witness_word.map(wjoin)
pc["witness_cycles"]=pc.witness_cycles.map(cjoin)
pc["comp_witness_word"]=pc.comp_witness_word.map(wjoin)
pc["comp_witness_cycles"]=pc.comp_witness_cycles.map(cjoin)
pc["classes_present"]=pc.classes_present.map(lambda x: ";".join(x))
ph = phi.copy(); ph["sweep"]="phi_D_to_W"
for c in ["witness_word","comp_witness_word"]: ph[c]=ph[c].map(wjoin)
for c in ["witness_cycles","comp_witness_cycles"]: ph[c]=ph[c].map(cjoin)
ph["classes_present"]=ph.classes_present.map(lambda x: ";".join(x))
rr = load("rec_rows.jsonl")
for c in ["witness_word","comp_witness_word"]: rr[c]=rr[c].map(wjoin)
for c in ["witness_cycles","comp_witness_cycles"]: rr[c]=rr[c].map(cjoin)
rr["classes_present"]=rr.classes_present.map(lambda x: ";".join(x))
rr["sweep"]="rec_"+rr.scheme

allrows = pd.concat([pc, ph, rr], ignore_index=True, sort=False)
cols = ["sweep","scheme","psi","psi_code","psi_class","psi_nvals","phi","phi_code",
        "phi_class","phi_nvals","is_bio_psi","is_bio_phi","is_bio","monoid_size",
        "n_idempotents","n_nonaperiodic","n_units","units_trivial","gens_all_aperiodic",
        "n_gens_nonaperiodic","classes_present","has_composite","has_dn_local",
        "has_wta_local","witness_word","witness_len","witness_cycles","witness_class",
        "shortest_is_composite","comp_witness_word","comp_witness_len","comp_witness_cycles"]
allrows = allrows[[c for c in cols if c in allrows.columns]]
allrows.to_csv("interface_sweep.csv", index=False)
strat.to_csv("sweep_summary.csv")
pd.DataFrame(sched).to_csv("schedule_summary.csv", index=False)
G.to_csv("rec_grid_counts.csv", index=False)
psi.drop(columns=["gen_key"]).to_pickle("psi_df.pkl"); phi.to_pickle("phi_df.pkl")
G.to_pickle("grid_df.pkl")
print(json.dumps(summary["step1"], indent=1))
print(json.dumps(summary["bio_psi"], indent=1))
print(strat.to_string())
print(pd.DataFrame(sched).to_string())
print(json.dumps(summary["step3a_phi"], indent=1))
print("rows in interface_sweep.csv:", len(allrows))
