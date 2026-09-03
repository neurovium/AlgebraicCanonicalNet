##############################################################################
##  compositeness.g -- is a holonomy group component INHERITED from a factor,
##  or genuinely COMPOSITE?
##
##  For each of the three 32-state cascade systems (prod, D_to_W, W_to_D) we
##  enumerate every image set C of the skeleton that carries a nontrivial
##  PERMUTATOR group P (the group of states permuted by round-trip words), and
##  classify the action of P on the composite coordinates idx = 8*d + w:
##
##    W-ONLY / inherited : every nontrivial cycle of every generator of P
##                         preserves the DN coordinate d (only w moves)
##    D-ONLY             : every nontrivial cycle preserves the WTA coordinate w
##    COMPOSITE          : some state is moved to a state with a DIFFERENT d
##                         AND a different w -- the permutation is not a
##                         permutation of either factor alone
##
##  This is the sharp form of the paper's prod-vs-W_to_D contrast.  We also
##  report the holonomy image (the action on TILES), since a nontrivial
##  permutator can have a trivial tile action.
##
##  Run:  gap -q -A -o 8g -c 'ONLY:=["prod"];;' compositeness.g
##############################################################################

LoadPackage("sgpdec", false);;
SgpDecOptionsRec.SMALL_GROUPS := true;;
Read("gap_systems.g");

if not IsBound(ONLY) then ONLY := ["prod", "D_to_W", "W_to_D"]; fi;
if not IsBound(OUTTAG) then OUTTAG := ""; fi;
OUT := Concatenation("compositeness", OUTTAG, ".csv");;
##  disable GAP's 80-column line breaking, which would corrupt the CSV
OUTS := OutputTextFile(OUT, false);;
SetPrintFormattingStatus(OUTS, false);;

DCoord := function(x) return QuoInt(x, 8); end;;
WCoord := function(x) return x mod 8; end;;
PaperOf := function(bl, deg)
  return List(ListBlist([1..deg], bl), p -> p - 1);
end;;
Fmt := function(x)
  return Concatenation(String(x), "=(D:", String(DCoord(x)), ",W:",
                       String(WCoord(x)), ")");
end;;

AppendTo(OUTS, "system,window_size,depth,is_representative,permutator_order,",
        "permutator_sd,holonomy_order,holonomy_sd,n_tiles,classification,",
        "moves_D,moves_W,composite_pairs,window_paper\n");

for sysrec in SYSTEMS do
  if not (sysrec.name in ONLY) then continue; fi;
  name := sysrec.name;; deg := sysrec.deg;;
  Print("\n########################################################\n");
  Print("### ", name, "\n");
  Print("########################################################\n");
  M := Monoid(sysrec.gens);;
  sk := Skeleton(M);;
  ## Only sets in the FORWARD ORBIT admit round-trip words; ExtendedImageSet
  ## also contains non-image singletons, for which PermutatorGroup errors out.
  ## Singletons cannot carry a nontrivial group anyway.
  fo := ForwardOrbit(sk);;
  sets := Filtered(AsList(fo), C -> SizeBlist(C) >= 2);;
  Print("image sets in forward orbit with >=2 states: ", Length(sets), "\n");
  reps := Concatenation(RepresentativeSets(sk));;

  nnt := 0;; ncomposite := 0;; nwonly := 0;; ndonly := 0;;
  compex := [];;
  for C in sets do
    P := PermutatorGroup(sk, C);
    if IsTrivial(P) then continue; fi;
    nnt := nnt + 1;
    H := Image(PermutatorHolonomyHomomorphism(sk, C));
    tiles := TilesOf(sk, C);
    movesD := false;; movesW := false;; cpairs := [];;
    for g in GeneratorsOfGroup(P) do
      for p in ListBlist([1..deg], C) do
        q := p^g;
        if q = p then continue; fi;
        if DCoord(p-1) <> DCoord(q-1) then movesD := true; fi;
        if WCoord(p-1) <> WCoord(q-1) then movesW := true; fi;
        if DCoord(p-1) <> DCoord(q-1) and WCoord(p-1) <> WCoord(q-1) then
          Add(cpairs, Concatenation(Fmt(p-1), "->", Fmt(q-1)));
        fi;
      od;
    od;
    if not IsEmpty(cpairs) then
      cls := "COMPOSITE"; ncomposite := ncomposite + 1;
      if Length(compex) < 8 then
        Add(compex, rec(C := C, P := P, H := H, cp := cpairs,
                        nt := Length(tiles)));
      fi;
    elif movesD and not movesW then
      cls := "D-ONLY"; ndonly := ndonly + 1;
    elif movesW and not movesD then
      cls := "W-ONLY-inherited"; nwonly := nwonly + 1;
    else
      cls := "MIXED-separable"; nwonly := nwonly + 1;
    fi;
    AppendTo(OUTS, name, ",", SizeBlist(C), ",", DepthOfSet(sk, C), ",",
             C in reps, ",", Size(P), ",\"", StructureDescription(P), "\",",
             Size(H), ",\"", StructureDescription(H), "\",", Length(tiles),
             ",", cls, ",", movesD, ",", movesW, ",\"",
             JoinStringsWithSeparator(cpairs, " ; "), "\",\"",
             JoinStringsWithSeparator(List(PaperOf(C, deg), Fmt), " "), "\"\n");
  od;
  Print("windows with NONTRIVIAL permutator group : ", nnt, "\n");
  Print("   classified COMPOSITE (d and w both change on one state) : ",
        ncomposite, "\n");
  Print("   classified W-ONLY / separable (inherited)               : ",
        nwonly, "\n");
  Print("   classified D-ONLY                                      : ",
        ndonly, "\n");
  if ncomposite = 0 then
    Print(">>> VERDICT for ", name,
          ": every group action is INHERITED from a factor",
          " (no state is moved in both coordinates at once).\n");
  else
    Print(">>> VERDICT for ", name, ": ", ncomposite,
          " window(s) carry a GENUINELY COMPOSITE group action.\n");
    Print("    examples:\n");
    for e in compex do
      Print("      window {", JoinStringsWithSeparator(
              List(PaperOf(e.C, deg), Fmt), " "), "}\n");
      Print("        permutator=", e.P, " sd=", StructureDescription(e.P),
            "  holonomy=", e.H, " sd=", StructureDescription(e.H),
            "  ntiles=", e.nt, "\n");
      Print("        composite moves: ",
            JoinStringsWithSeparator(e.cp, " ; "), "\n");
    od;
  fi;
od;
CloseStream(OUTS);;
Print("\n=== WROTE ", OUT, " ===\n");
