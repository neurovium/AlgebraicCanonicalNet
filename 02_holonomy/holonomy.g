##############################################################################
##
##  holonomy.g -- Krohn-Rhodes / holonomy decomposition of the DN/WTA motifs
##
##  Companion to the Python transition-monoid audit (audit.py).  Computes, for
##  each of the nine finite-state systems exported by export_gap.py:
##
##    * monoid / semigroup order, aperiodicity, idempotent count, group of units
##    * the SgpDec holonomy skeleton: depth, component profile, group components
##    * for every (level, slot): the holonomy group, its order, its
##      StructureDescription, the representative set it belongs to, and the
##      TILES that the group actually permutes -- all decoded into the paper's
##      state coordinates
##    * faithfulness of the decomposition: the holonomy cascade semigroup is
##      mapped back down to degree-n transformations and compared setwise with
##      the original monoid (this is SgpDec's own TestHolonomyEmulation check)
##    * targeted claim checks: for a given pair of paper states, whether any
##      holonomy group component actually relates them (see CHECKCLAIM below)
##
##  CONVENTIONS
##    GAP is ONE-BASED.  A GAP point p corresponds to paper state p-1.
##    Holonomy groups act on TILES (subsets of a representative set), not in
##    general on raw states.  Every support printed below is therefore reported
##    both as the representative set and as its tile decomposition.
##
##  USAGE
##    P=/home/nimad/miniforge3/envs/algcanet; export PATH=$P/bin:$PATH
##    gap -q -A holonomy.g
##  Optional pre-set globals (via  gap -q -A -c 'ONLY:=["WTA"];;' holonomy.g ):
##    ONLY         list of system names to process        (default: all nine)
##    DO_CASCADE   whether to run the faithfulness check  (default: true)
##    OUTTAG       suffix for the output files            (default: "")
##
##  OUTPUTS (written incrementally, so a killed run still leaves partials)
##    holonomy_results<TAG>.csv    one row per (system, level, slot)
##    holonomy_summary<TAG>.json   per-system summary record
##    holonomy_claims<TAG>.json    targeted claim checks (a)-(e)
##
##############################################################################

LoadPackage("sgpdec", false);;
SgpDecOptionsRec.SMALL_GROUPS := true;;   # StructureDescription-style names
SEMIGROUPS.DefaultOptionsRec.report := false;;   # quiet FroidurePin progress

## forward declarations (keeps GAP from emitting parse-time warnings for
## globals that are only assigned later in this file)
IsAperiodicTransformation := fail;;
NontrivialCyclesOf := fail;;
HolGroupOfSet := fail;;
CheckClaim := fail;;
DecodePoint := fail;;
PaperStates := fail;;
PaperStr := fail;;
TilesStr := fail;;
WtaDec := fail;;
JQ := fail;; JList := fail;; JSList := fail;; JBool := fail;;

Read("gap_systems.g");

if not IsBound(ONLY) then ONLY := List(SYSTEMS, s -> s.name); fi;
if not IsBound(DO_CASCADE) then DO_CASCADE := true; fi;
if not IsBound(OUTTAG) then OUTTAG := ""; fi;

CSVFILE  := Concatenation("holonomy_results", OUTTAG, ".csv");;
JSONFILE := Concatenation("holonomy_summary", OUTTAG, ".json");;
CLMFILE  := Concatenation("holonomy_claims", OUTTAG, ".json");;

##  GAP breaks printed lines at 80 columns by default, which corrupts CSV and
##  JSON records.  Write through explicit streams with formatting disabled.
CSVOUT := OutputTextFile(CSVFILE, false);;  SetPrintFormattingStatus(CSVOUT, false);;
JSONOUT := OutputTextFile(JSONFILE, false);; SetPrintFormattingStatus(JSONOUT, false);;
CLMOUT := OutputTextFile(CLMFILE, false);;  SetPrintFormattingStatus(CLMOUT, false);;

##############################################################################
##  Ground truth from the verified Python audit.  Any disagreement is FLAGGED
##  loudly rather than silently accepted.
##    M     : |M|, order of the transition monoid (identity included)
##    idem  : number of idempotents
##    nonap : number of non-aperiodic elements
##    allap : whether every GENERATOR is aperiodic
##    units : order of the group of units
##    wit   : shortest witness cycle (paper coordinates, zero-based)
##############################################################################
AUDIT := rec(
  DN3         := rec(M:=13,   idem:=6,   nonap:=3,  allap:=false, units:=2, wit:=[0,2]),
  DN4         := rec(M:=24,   idem:=8,   nonap:=3,  allap:=true,  units:=1, wit:=[2,1]),
  WTA         := rec(M:=326,  idem:=55,  nonap:=49, allap:=true,  units:=1, wit:=[4,5]),
  prod        := rec(M:=576,  idem:=103, nonap:=88, allap:=true,  units:=1, wit:=[12,13]),
  D_to_W      := rec(M:=3149, idem:=274, nonap:=401,allap:=true,  units:=1, wit:=[12,13]),
  W_to_D      := rec(M:=3084, idem:=186, nonap:=361,allap:=true,  units:=1, wit:=[4,13]),
  rec_sync    := rec(M:=9,    idem:=2,   nonap:=6,  allap:=false, units:=1, wit:=[17,18,11]),
  rec_async_D := rec(M:=8,    idem:=2,   nonap:=0,  allap:=true,  units:=1, wit:=[]),
  rec_async_W := rec(M:=8,    idem:=2,   nonap:=0,  allap:=true,  units:=1, wit:=[])
);;

##  Extra target pairs/sets for the paper's specific claims (paper coords).
##  Each entry: rec(sys, label, states)
CLAIMTARGETS := [
  rec(sys:="WTA",    label:="wta_hi_pair_{4,5}",        states:=[4,5]),
  rec(sys:="WTA",    label:="wta_lo_pair_{2,3}",        states:=[2,3]),
  rec(sys:="DN4",    label:="dn4_witness_{2,1}",        states:=[1,2]),
  rec(sys:="DN3",    label:="dn3_witness_{0,2}",        states:=[0,2]),
  rec(sys:="W_to_D", label:="wtod_KEY_{4,13}",          states:=[4,13]),
  rec(sys:="prod",   label:="prod_{12,13}",             states:=[12,13]),
  rec(sys:="D_to_W", label:="dtow_{12,13}",             states:=[12,13]),
  rec(sys:="rec_sync", label:="recsync_witness_{17,18,11}", states:=[11,17,18])
];;

##############################################################################
##  DECODERS: GAP point -> paper coordinate string.
##  deg 3/4  : DN state d            -> "d"
##  deg 8    : WTA state w           -> "w=(b1,b2,g)"
##  deg 32   : composite idx = 8d+w  -> "idx=(D:d,W:w)"
##############################################################################
WtaDec := function(w)   # w in 0..7  ->  [b1,b2,g]
  return [ QuoInt(w,4), QuoInt(w,2) mod 2, w mod 2 ];
end;;

DecodePoint := function(deg, p)   # p is a ONE-BASED GAP point
  local x, d, w, b;
  x := p - 1;                     # paper (zero-based) state
  if deg = 8 then
    b := WtaDec(x);
    return Concatenation(String(x), "=(", String(b[1]), ",", String(b[2]), ",",
                         String(b[3]), ")");
  elif deg = 32 then
    d := QuoInt(x, 8); w := x mod 8;
    return Concatenation(String(x), "=(D:", String(d), ",W:", String(w), ")");
  else
    return String(x);
  fi;
end;;

##  A blist (FiniteSet) -> list of paper states, and -> pretty decoded string.
PaperStates := function(deg, bl)
  return List(ListBlist([1..deg], bl), p -> p - 1);
end;;

PaperStr := function(deg, bl)
  return Concatenation("{",
    JoinStringsWithSeparator(List(ListBlist([1..deg], bl),
                                 p -> DecodePoint(deg, p)), " "), "}");
end;;

##  Tile list -> "{...}|{...}" string
TilesStr := function(deg, tiles)
  return JoinStringsWithSeparator(List(tiles, t -> PaperStr(deg, t)), " | ");
end;;

##############################################################################
##  APERIODICITY OF A SINGLE TRANSFORMATION.
##  For a transformation of degree n the index of the cyclic semigroup <t> is
##  at most n, so the eventual period is 1 iff t^n = t^(n+1).  That is exactly
##  the paper's definition (every cycle of the functional graph is a fixed
##  point).  We cross-check against IsAperiodicSemigroup(Semigroup(t)).
##############################################################################
IsAperiodicTransformation := function(t, n)
  local a, b;
  a := t^n; b := t^(n+1);
  return a = b;
end;;

##  The nontrivial cycles of the functional graph of t (paper coords), so the
##  claim "generator g is/is not aperiodic" can be inspected by eye.
NontrivialCyclesOf := function(t, n)
  local seen, cycs, p, path, q, i, start, cyc;
  seen := BlistList([1..n], []);
  cycs := [];
  for p in [1..n] do
    if seen[p] then continue; fi;
    path := []; q := p;
    while not (q in path) and not seen[q] do
      Add(path, q); q := q^t;
    od;
    if not seen[q] then
      start := Position(path, q);
      cyc := path{[start..Length(path)]};
      if Length(cyc) > 1 then Add(cycs, List(cyc, x -> x - 1)); fi;
    fi;
    for i in path do seen[i] := true; od;
  od;
  return cycs;
end;;

##############################################################################
##  MINIMAL JSON WRITER (GAP has no json package guaranteed here).
##############################################################################
JQ := function(s) return Concatenation("\"", String(s), "\""); end;;
JList := function(l) return Concatenation("[",
    JoinStringsWithSeparator(List(l, String), ", "), "]"); end;;
JSList := function(l) return Concatenation("[",
    JoinStringsWithSeparator(List(l, JQ), ", "), "]"); end;;
JBool := function(b) if b then return "true"; else return "false"; fi; end;;

##############################################################################
##  HOLONOMY GROUP OF AN ARBITRARY IMAGE SET (not only a representative).
##  GroupComponents(sk) only exposes the groups at the chosen transversal
##  representatives.  For claim checking we need the holonomy group of a
##  specific set C that contains the states of interest; SgpDec's
##  PermutatorHolonomyHomomorphism gives exactly that: its image is the group
##  induced on TilesOf(sk,C).
##############################################################################
HolGroupOfSet := function(sk, C)
  return Image(PermutatorHolonomyHomomorphism(sk, C));
end;;

##############################################################################
##  CHECKCLAIM(sk, deg, targets)
##  Asks: is there an image set C of the skeleton that contains ALL the given
##  paper states, whose holonomy group is nontrivial, AND in which the tiles
##  holding those states are genuinely moved onto one another by that group?
##
##  This is the honest test.  A nontrivial group somewhere in the same
##  subduction class is NOT enough: the paper may only claim that the group
##  relates two states if some group element maps a tile containing one onto a
##  tile containing the other.
##
##  Returns a record with the best (smallest, nontrivially-acted) witness set.
##############################################################################
CheckClaim := function(sk, deg, paperstates)
  local eis, Tbl, cands, C, H, tiles, ia, ib, res, best, h, moved, i, j,
        a, b, relates, orbsame, tilesof, sizes, cand, ok, allc, gapts;
  gapts := List(paperstates, x -> x + 1);
  Tbl := FiniteSet(gapts, deg);
  # ExtendedImageSet is a HashSet; SortedExtendedImageSet returns it as a list
  eis := SortedExtendedImageSet(sk);
  # all image sets containing every target state
  cands := Filtered(eis, C -> IsSubsetBlist(C, Tbl));
  best := rec(found := false, ncands := Length(cands),
              nontrivial_cands := 0, detail := [], detail_permonly := []);
  # smallest first: the tightest window is the most informative
  cands := ShallowCopy(cands);
  SortBy(cands, C -> SizeBlist(C));
  for C in cands do
    H := HolGroupOfSet(sk, C);
    tiles := TilesOf(sk, C);
    ## PermutatorGroup acts on the RAW STATES of C; the holonomy group H is its
    ## image on the TILES of C.  Recording both is what keeps the paper honest:
    ## a nontrivial permutator with trivial holonomy means the states are
    ## permuted by the monoid but the permutation is invisible to this level of
    ## the holonomy decomposition.
    PG := PermutatorGroup(sk, C);
    if IsTrivial(H) then
      if not IsTrivial(PG) then
        Add(best.detail_permonly, rec(
          setsize := SizeBlist(C), depth := DepthOfSet(sk, C),
          supportstr := PaperStr(deg, C),
          pgsize := Size(PG), pgsd := StructureDescription(PG),
          pg := String(PG), ntiles := Length(tiles),
          tilesstr := TilesStr(deg, tiles)));
      fi;
      continue;
    fi;
    best.nontrivial_cands := best.nontrivial_cands + 1;
    # for each pair of targets, do the tiles containing them get swapped?
    relates := [];
    for i in [1..Length(gapts)] do
      for j in [i+1..Length(gapts)] do
        a := gapts[i]; b := gapts[j];
        ia := Filtered([1..Length(tiles)], k -> tiles[k][a]);
        ib := Filtered([1..Length(tiles)], k -> tiles[k][b]);
        # some group element mapping a tile containing a to one containing b
        moved := false;
        for h in H do
          if ForAny(ia, k -> (k^h) in ib) then moved := true; break; fi;
        od;
        Add(relates, rec(a := a-1, b := b-1,
                         tiles_a := ia, tiles_b := ib,
                         same_tile := Length(Intersection(ia, ib)) > 0,
                         group_relates := moved));
      od;
    od;
    Add(best.detail, rec(
      setsize   := SizeBlist(C),
      depth     := DepthOfSet(sk, C),
      support   := PaperStates(deg, C),
      supportstr:= PaperStr(deg, C),
      ntiles    := Length(tiles),
      tilesstr  := TilesStr(deg, tiles),
      grpsize   := Size(H),
      grpsd     := StructureDescription(H),
      grp       := String(H),
      pgsize    := Size(PG),
      pgsd      := StructureDescription(PG),
      pg        := String(PG),
      isrep     := C in RepresentativeSets(sk)[DepthOfSet(sk, C)],
      relates   := relates,
      allrelate := ForAll(relates, r -> r.group_relates)));
    if not best.found then best.found := true; fi;
    if Length(best.detail) >= 6 then break; fi;   # keep the report bounded
  od;
  return best;
end;;

##############################################################################
##  MAIN LOOP
##############################################################################
AppendTo(CSVOUT, "system,degree,monoid_order,depth,level,slot,group_order,",
        "structure_description,is_nontrivial,rep_support_size,n_tiles,",
        "rep_support_paper,tiles_paper\n");
AppendTo(JSONOUT, "[\n");
AppendTo(CLMOUT, "[\n");

FIRSTJ := true;;
FIRSTC := true;;

for sysrec in SYSTEMS do
  if not (sysrec.name in ONLY) then continue; fi;

  name := sysrec.name;; deg := sysrec.deg;; gens := sysrec.gens;;
  t0 := Runtime();;
  Print("\n");
  Print("################################################################\n");
  Print("### SYSTEM ", name, "   (degree ", deg, ", ", Length(gens),
        " generators: ", JoinStringsWithSeparator(sysrec.gennames, ", "), ")\n");
  Print("################################################################\n");

  ## ---- 1. basic monoid invariants -------------------------------------
  M := Monoid(gens);;
  S := Semigroup(gens);;
  szM := Size(M);; szS := Size(S);;
  apM := IsAperiodicSemigroup(M);;
  nidem := Length(Idempotents(M));;
  U := GroupOfUnits(M);;
  if U = fail then
    szU := 1;; sdU := "1";;
  else
    szU := Size(U);;
    sdU := StructureDescription(Range(IsomorphismPermGroup(U)));;
  fi;
  ## non-aperiodic ELEMENTS (paper's count)
  nonap := Number(AsList(M), t -> not IsAperiodicTransformation(t, deg));;

  Print("Size(Monoid(gens))      = ", szM, "\n");
  Print("Size(Semigroup(gens))   = ", szS, "\n");
  Print("IsAperiodicSemigroup(M) = ", apM, "\n");
  Print("Nr idempotents          = ", nidem, "\n");
  Print("Nr non-aperiodic elts   = ", nonap, "\n");
  Print("GroupOfUnits            = order ", szU, ", ", sdU, "\n");

  ## ---- 1b. cross-check against the Python audit -----------------------
  aud := AUDIT.(name);;
  mismatch := [];;
  if szM   <> aud.M     then Add(mismatch, Concatenation("|M| GAP=", String(szM),   " audit=", String(aud.M))); fi;
  if nidem <> aud.idem  then Add(mismatch, Concatenation("idem GAP=", String(nidem)," audit=", String(aud.idem))); fi;
  if nonap <> aud.nonap then Add(mismatch, Concatenation("nonap GAP=", String(nonap)," audit=", String(aud.nonap))); fi;
  if szU   <> aud.units then Add(mismatch, Concatenation("|U| GAP=", String(szU),   " audit=", String(aud.units))); fi;
  if IsEmpty(mismatch) then
    Print(">>> AUDIT CROSS-CHECK: OK (|M|, idempotents, non-aperiodic count, |U| all agree)\n");
  else
    Print("*** AUDIT MISMATCH *** ", JoinStringsWithSeparator(mismatch, " ; "), "\n");
  fi;

  ## ---- 1c. per-generator aperiodicity --------------------------------
  Print("Per-generator aperiodicity (paper definition: every cycle a fixed point):\n");
  genap := [];;
  for i in [1..Length(gens)] do
    ga := IsAperiodicTransformation(gens[i], deg);;
    gb := IsAperiodicSemigroup(Semigroup([gens[i]]));;
    Add(genap, ga);
    Print("   ", sysrec.gennames[i], ": aperiodic=", ga,
          " (IsAperiodicSemigroup agrees: ", ga = gb, ")",
          "  nontrivial cycles(paper coords)=", NontrivialCyclesOf(gens[i], deg), "\n");
  od;
  allap := ForAll(genap, x -> x);;
  if allap <> aud.allap then
    Print("*** GENERATOR-APERIODICITY MISMATCH *** GAP=", allap, " audit=", aud.allap, "\n");
  else
    Print(">>> generator aperiodicity matches audit: all_aperiodic=", allap, "\n");
  fi;

  ## ---- 2. holonomy skeleton ------------------------------------------
  sk := Skeleton(M);;
  depth := DepthOfSkeleton(sk);;
  Print("\nDepthOfSkeleton = ", depth, "\n");
  Print("DisplayHolonomyComponents:\n");
  DisplayHolonomyComponents(sk);

  gc := GroupComponents(sk);;
  rs := RepresentativeSets(sk);;
  nlev_nontriv := 0;; ncomp_nontriv := 0;; grpnames := [];;
  Print("\nGroup components (level: slot -> group, order, structure, support, tiles):\n");
  for d in [1..Length(gc)] do
    levhas := false;;
    for i in [1..Length(gc[d])] do
      G := gc[d][i];;
      tiles := TilesOf(sk, rs[d][i]);;
      sd := StructureDescription(G);;
      nt := IsTrivial(G);;
      if not nt then levhas := true; ncomp_nontriv := ncomp_nontriv + 1;
        Add(grpnames, Concatenation("L", String(d), "S", String(i), ":", sd));
      fi;
      Print("  level ", d, " slot ", i, ": ", G, "  |G|=", Size(G),
            "  sd=", sd, "  ntiles=", Length(tiles), "\n");
      Print("        rep support = ", PaperStr(deg, rs[d][i]), "\n");
      Print("        tiles       = ", TilesStr(deg, tiles), "\n");
      AppendTo(CSVOUT, name, ",", deg, ",", szM, ",", depth, ",", d, ",", i, ",",
               Size(G), ",\"", sd, "\",", not nt, ",",
               SizeBlist(rs[d][i]), ",", Length(tiles), ",\"",
               PaperStr(deg, rs[d][i]), "\",\"", TilesStr(deg, tiles), "\"\n");
    od;
    if levhas then nlev_nontriv := nlev_nontriv + 1; fi;
  od;
  Print("Levels carrying a NONTRIVIAL group: ", nlev_nontriv,
        " of ", Length(gc), " group levels (skeleton depth ", depth, ")\n");
  Print("Nontrivial components: ", ncomp_nontriv, "  ",
        JoinStringsWithSeparator(grpnames, " "), "\n");

  ## ---- 3. faithfulness of the decomposition ---------------------------
  ##  Two tests are run, because the setwise test has a known artefact:
  ##    (i)  SETWISE  AsSortedList(M) = AsSortedList(Range(hom)).
  ##         Range(hom) is built by Semigroup(...) from the images of the
  ##         cascade GENERATORS, so it omits the identity transformation
  ##         whenever the identity is not itself a product of generators.
  ##         The set difference is then exactly [IdentityTransformation] --
  ##         a bookkeeping artefact of Semigroup vs Monoid, not a failure of
  ##         the decomposition.
  ##    (ii) ELEMENTWISE  for every t in M,
  ##             AsHolonomyTransformation(AsHolonomyCascade(t, sk), sk) = t.
  ##         This is the real faithfulness statement (the holonomy relational
  ##         morphism composed with the projection is the identity on M) and
  ##         it covers the identity element too.  The paper should cite (ii).
  casc_setwise := "skipped";; casc_elementwise := "skipped";;
  casc_missing := "skipped";; szR := -1;;
  if DO_CASCADE then
    Print("\nCascade faithfulness check ...\n");
    hcs := HolonomyCascadeSemigroup(M);;
    hom := HomomorphismTransformationSemigroup(hcs);;
    R := Range(hom);;
    szR := Size(R);;
    eq := AsSortedList(M) = AsSortedList(R);;
    miss := Difference(AsSortedList(M), AsSortedList(R));;
    spur := Difference(AsSortedList(R), AsSortedList(M));;
    Print("   Size(Range(hom)) = ", szR, "   Size(M) = ", szM, "\n");
    Print("   (i)  setwise  AsSortedList(M) = AsSortedList(Range(hom)) : ", eq, "\n");
    Print("        missing from Range(hom) : ", miss, "\n");
    Print("        spurious in Range(hom)  : ", spur, "\n");
    if not eq then
      if miss = [ One(M) ] and IsEmpty(spur) then
        Print("        ^ difference is EXACTLY the identity => Semigroup-vs-Monoid",
              " artefact, not a decomposition failure\n");
        casc_missing := "identity_only";
      else
        Print("        *** UNEXPECTED difference -- investigate ***\n");
        casc_missing := "unexpected";
      fi;
    else
      casc_missing := "none";
    fi;
    rt := ForAll(AsList(M),
                 t -> AsHolonomyTransformation(AsHolonomyCascade(t, sk), sk) = t);;
    Print("   (ii) ELEMENTWISE round-trip for all ", szM, " elements of M : ", rt, "\n");
    if eq then casc_setwise := "true"; else casc_setwise := "false"; fi;
    if rt then casc_elementwise := "true"; else casc_elementwise := "false"; fi;
    if not rt then
      Print("   *** FAITHFULNESS FAILURE: the holonomy decomposition does NOT",
            " reproduce M elementwise ***\n");
    else
      Print("   >>> decomposition is FAITHFUL on every element of M\n");
    fi;
  fi;

  el := Runtime() - t0;;
  Print("\n[", name, " done in ", el, " ms]\n");

  ## ---- JSON summary ---------------------------------------------------
  if not FIRSTJ then AppendTo(JSONOUT, ",\n"); fi; FIRSTJ := false;
  AppendTo(JSONOUT, "  {", JQ("system"), ": ", JQ(name),
    ", ", JQ("degree"), ": ", deg,
    ", ", JQ("monoid_order"), ": ", szM,
    ", ", JQ("semigroup_order"), ": ", szS,
    ", ", JQ("audit_monoid_order"), ": ", aud.M,
    ", ", JQ("is_aperiodic_monoid"), ": ", JBool(apM),
    ", ", JQ("n_idempotents"), ": ", nidem,
    ", ", JQ("n_nonaperiodic_elements"), ": ", nonap,
    ", ", JQ("group_of_units_order"), ": ", szU,
    ", ", JQ("group_of_units_sd"), ": ", JQ(sdU),
    ", ", JQ("all_generators_aperiodic"), ": ", JBool(allap),
    ", ", JQ("audit_mismatches"), ": ", JSList(mismatch),
    ", ", JQ("depth"), ": ", depth,
    ", ", JQ("component_profile"), ": ",
        JQ(ReplacedString(DisplayStringHolonomyComponents(sk), "\n", " / ")),
    ", ", JQ("n_group_levels"), ": ", Length(gc),
    ", ", JQ("n_levels_nontrivial"), ": ", nlev_nontriv,
    ", ", JQ("n_components_nontrivial"), ": ", ncomp_nontriv,
    ", ", JQ("nontrivial_groups"), ": ", JSList(grpnames),
    ", ", JQ("cascade_range_order"), ": ", szR,
    ", ", JQ("cascade_faithful_setwise"), ": ", JQ(casc_setwise),
    ", ", JQ("cascade_setwise_difference"), ": ", JQ(casc_missing),
    ", ", JQ("cascade_faithful_elementwise"), ": ", JQ(casc_elementwise),
    ", ", JQ("runtime_ms"), ": ", el, "}");

  ## ---- 4. targeted claim checks ---------------------------------------
  for ct in CLAIMTARGETS do
    if ct.sys <> name then continue; fi;
    Print("\n--- CLAIM CHECK [", name, "] ", ct.label,
          "  paper states ", ct.states, " (GAP points ",
          List(ct.states, x -> x+1), ")\n");
    cc := CheckClaim(sk, deg, ct.states);;
    Print("    image sets containing all targets: ", cc.ncands,
          ";  of these with nontrivial holonomy: ", cc.nontrivial_cands, "\n");
    if not cc.found then
      Print("    RESULT: NO image set containing these states has a nontrivial",
            " holonomy group.\n");
      if not IsEmpty(cc.detail_permonly) then
        Print("    However ", Length(cc.detail_permonly), " window(s) have a",
              " nontrivial PERMUTATOR group with trivial holonomy image:\n");
        for det in cc.detail_permonly do
          Print("       ", det.supportstr, " |C|=", det.setsize, " depth ",
                det.depth, "  permutator ", det.pg, " sd=", det.pgsd,
                "  ntiles=", det.ntiles, "\n");
        od;
      fi;
    else
      for det in cc.detail do
        Print("    window ", det.supportstr, "  (|C|=", det.setsize,
              ", depth ", det.depth, ", representative=", det.isrep, ")\n");
        Print("       holonomy group ", det.grp, " |G|=", det.grpsize,
              " sd=", det.grpsd, " acting on ", det.ntiles, " tiles\n");
        Print("       permutator group (on RAW STATES of the window) ", det.pg,
              " |P|=", det.pgsize, " sd=", det.pgsd, "\n");
        Print("       tiles: ", det.tilesstr, "\n");
        for r in det.relates do
          Print("       pair (", DecodePoint(deg, r.a+1), ", ",
                DecodePoint(deg, r.b+1), "): tiles ", r.tiles_a, " vs ",
                r.tiles_b, "  same_tile=", r.same_tile,
                "  GROUP_RELATES=", r.group_relates, "\n");
        od;
      od;
    fi;
    if not FIRSTC then AppendTo(CLMOUT, ",\n"); fi; FIRSTC := false;
    AppendTo(CLMOUT, "  {", JQ("system"), ": ", JQ(name),
      ", ", JQ("label"), ": ", JQ(ct.label),
      ", ", JQ("paper_states"), ": ", JList(ct.states),
      ", ", JQ("n_candidate_sets"), ": ", cc.ncands,
      ", ", JQ("n_nontrivial_candidates"), ": ", cc.nontrivial_cands,
      ", ", JQ("found_nontrivial"), ": ", JBool(cc.found),
      ", ", JQ("windows"), ": [",
      JoinStringsWithSeparator(List(cc.detail, det -> Concatenation("{",
         JQ("setsize"), ": ", String(det.setsize),
         ", ", JQ("depth"), ": ", String(det.depth),
         ", ", JQ("is_representative"), ": ", JBool(det.isrep),
         ", ", JQ("support_paper"), ": ", JList(det.support),
         ", ", JQ("support_str"), ": ", JQ(det.supportstr),
         ", ", JQ("n_tiles"), ": ", String(det.ntiles),
         ", ", JQ("tiles_str"), ": ", JQ(det.tilesstr),
         ", ", JQ("group_order"), ": ", String(det.grpsize),
         ", ", JQ("group_sd"), ": ", JQ(det.grpsd),
         ", ", JQ("permutator_order"), ": ", String(det.pgsize),
         ", ", JQ("permutator_sd"), ": ", JQ(det.pgsd),
         ", ", JQ("all_pairs_related"), ": ", JBool(det.allrelate),
         ", ", JQ("pairs"), ": [",
         JoinStringsWithSeparator(List(det.relates, r -> Concatenation("{",
             JQ("a"), ": ", String(r.a), ", ", JQ("b"), ": ", String(r.b),
             ", ", JQ("tiles_a"), ": ", JList(r.tiles_a),
             ", ", JQ("tiles_b"), ": ", JList(r.tiles_b),
             ", ", JQ("same_tile"), ": ", JBool(r.same_tile),
             ", ", JQ("group_relates"), ": ", JBool(r.group_relates), "}")), ", "),
         "]}")), ", "),
      "]}");
  od;
od;

AppendTo(JSONOUT, "\n]\n");
AppendTo(CLMOUT, "\n]\n");
CloseStream(CSVOUT);; CloseStream(JSONOUT);; CloseStream(CLMOUT);;
Print("\n=== WROTE ", CSVFILE, ", ", JSONFILE, ", ", CLMFILE, " ===\n");
