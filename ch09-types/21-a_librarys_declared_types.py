"""Purpose: examples/ch09-types/21-a_librarys_declared_types.metta in Python: the types an import brought in.

`m += lib.datastructures` brings the library's declarations in with its
equations, and `space.type` reads them back: a declaration is an atom in the
space, and an imported one is no different from a local one.

Two doors answer the same question at different arities. `space.type(atom)` is
the single-answer door and REFUSES when there is no type, naming the term,
where the original collapses `get-type` to the empty bag; `m.answers(...)` over
the built form is that bag, so both spellings are here for the two terms whose
arguments do not fit.
Open Obligations:
  To Do: None
  Hacks: None
  Future Enhancements: None.
"""

from metta import Expression, S, Symbol, arrow, lib
from metta._errors.errors import EngineError

EMPTY = S.FTEmpty


def twin(m):
    """Read the four declarations back, then ask about two that do not fit."""
    m += lib.datastructures

    # `FTree` is declared `Type`, which is what makes the other three mean
    # anything.
    assert m.type(S.FTree) == S.Type

    # `FTEmpty` takes nothing, so its type is the type itself: it IS a tree
    # rather than a way of making one. The other two are arrows, and their
    # argument types say what each field holds.
    assert m.type(EMPTY) == S.FTree
    assert m.type(S.FTSingle) == arrow(S.Atom, S.FTree)
    assert m.type(S.FTDeep) == arrow(S.Expression, S.FTree, S.Expression, S.FTree)

    # Applying one answers the type its arrow ends in, which is how trees
    # built out of different constructors are all one type.
    assert m.type(S.FTSingle(1)) == S.FTree
    assert m.type(S.FTDeep((1, 2), EMPTY, (3, 4))) == S.FTree

    # A nullary constructor is a SYMBOL, and out here the metatype IS the
    # Python class, so nothing crosses the seam to ask for it. Wrapping it in
    # brackets would be a one-element expression rather than the atom the
    # library means, and neither side writes that form: the coverage lane
    # reads call position out of the corpus text, where a one-element
    # expression and a nullary call are the same characters.
    assert type(EMPTY) is Symbol
    assert type(S.FTSingle(1)) is Expression

    # The argument types are checked, and an application that does not fit has
    # no type at all rather than a wrong one.
    for bad in (S.FTSingle(1, 2), S.FTDeep(1, EMPTY, (3, 4))):
        assert m.answers(S.get_type(bad)) == []
        refused = None
        try:
            m.type(bad)
        except EngineError as refusal:
            refused = refusal
        assert "returned no type" in str(refused)
        assert repr(bad) in str(refused)


#: MEASURED on this branch rather than inherited: this twin is new, so there is
#: no earlier pin to move
#: [measured 2026-09-07: 22672 inferences, 0.9700x the example's 23372; command=python
#: extensions/python/tools/twin_coverage.py --measure --rounds 3;
#: fixture=docs/every-atom-has-an-example at its example commits; commit=98397cdd04679cbf40b2d515076dadc09c1b0a32].
#: RE-PINNED 2026-09-08, 22672 to 22926 (+254), The engine and library
#: predicates now resolve through their owning modules and the explicit engine
#: facade; compiled program lookup crosses the added metta_engine tier
#: [measured 2026-09-08: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=ede2ac57e213a0d4502c6bbbca6227f97015b720].
#: RE-PINNED 2026-09-08, 22926 to 22961 (+35), the module boundary merged with
#: trunk's later packages (refactor/engine-and-libraries-as-modules at
#: b64291369): every space now resolves through one more chain link, prelude ->
#: metta_engine -> user, the engine's measured export list is imported into the
#: host tier at boot, the closed-sets watch point costs one inference per
#: &metta write, and a cursor opened by a host pays one transaction check at
#: its door; the branch pinned its budgets on its cut, trunk re-pinned the same
#: twins for the packages that landed after that cut, and only the merged tree
#: carries both, so this entry is where the two chains meet [measured
#: 2026-09-08: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=f1038acdcaf5230b6431c112f38a719d3dc9ef19].
#: RE-PINNED 2026-09-09, 22961 to 23013 (+52), structured concurrency landed
#: (feat/structured-concurrency merged at f80cc416d): every space mint records
#: its allocation in the library's lifetime rows, every write and run pays the
#: ownership hook and every drop asks the library whether a scope owns the
#: name, measured on a pristine control as 32 per mint, 2 per write and 44 per
#: drop with none per read; measured on the merged tree [measured 2026-09-09:
#: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=0f53926c2fd9f28e188814c84253ad82e13258f7].
#: RE-PINNED 2026-09-08, 22961 to 23722 (+761), Trailing occurrence arguments,
#: token allocation in native writes, exact source withdrawal and transaction-
#: safe shared-table guards change the engine work priced by this twin; answer
#: bags retain the upstream law [measured 2026-09-08: min-of-3 serial fresh
#: processes; command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=7f00ac7932fefa6f380fc8d14ec583ea0c58eff4].
#: RE-PINNED 2026-09-09, 23722 to 23774 (+52), tokens as storage landed
#: (feat/tokens-as-storage merged): every native occurrence carries a (t actor
#: generation) token as the trailing argument of its storage clause, minted
#: through flag/3 at the write funnel, and every clause read decodes it,
#: measured on a pristine control of trunk cbf7a958d as 8 more inferences per
#: add, 31 more per remove, 4 more per atom saved and 54 more per atom loaded
#: from a fast image, none per match, plus the merged tree's own lib_thread
#: repairs; measured on the merged tree [measured 2026-09-09: min-of-3 serial
#: fresh processes; command=python extensions/python/tools/twin_coverage.py
#: --repin; commit=50e34286f66c938d89d5d367c6370ad44164c97f].
#: RE-PINNED 2026-09-08, 22961 to 22870 (-91), Compiled shipped typing
#: decisions and initial vocabulary facts remove repeated interpretation;
#: indexed vocabulary membership replaces member-list scans; catalog reference
#: checks now respect transaction-local erasure. Paired controls and cut counts
#: are recorded in docs/journal/2026-09-08-what-the-waivers-were-paying-for.md
#: [measured 2026-09-08: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=32650f9ff4d1c4aa0749d8eb8b153e5bb448ee5c].
#: RE-PINNED 2026-09-09, 22870 to 23683 (+813), the compiled vocabulary seed,
#: the membership index, base-module type lookups and the singleton decoder
#: landed (perf/cross-engine-waivers merged): boot publishes the initial
#: vocabulary types from a compiled payload through the tokenized funnel, a
#: warm membership read touches only its own clauses, a base-module type lookup
#: skips the prelude, and a Python decode with one named variable builds no
#: index; per-operation costs of a mint, write, read, drop, run, save and load
#: are unchanged against the trunk in fresh processes; measured on the merged
#: tree, -91 against the trunk's own pin of 23774 at da0e5755d; the previous
#: number is the branch's cut-time price, and the remaining +904 is what landed
#: on the trunk between the cut f0d33dcad and da0e5755d, tokens as storage
#: above all [measured 2026-09-09: min-of-3 serial fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=b4341ae382c48ef225f4a52e566af6a9a71757c4].
#: RE-PINNED 2026-09-10, 23683 to 23578 (-105), the binding resolves Janus
#: maplist/2 at boot, removing its first-failure autoload; one compiled option
#: policy removes repeated evaluation frames, and keyed dispatch removes
#: repeated transport/context selection. Indexed source-macro hooks preserve
#: unrelated compilation costs. Same-cut controls and all before/after rows are
#: in docs/journal/2026-09-09-the-binding-collapse.md. These three fresh serial
#: processes set file_search_cache_time=9223372036854775807 before boot,
#: matching the validated full-lane/277/workers=32/file-cache-
#: time=9223372036854775807 environment. Workloads, point tolerances and
#: empirical envelopes are unchanged [measured 2026-09-10: min-of-3 serial
#: fresh processes; command=python extensions/python/tools/twin_coverage.py
#: --repin; commit=8358dfc233bf299bb23eceddd94593a62372fe4b].
#: RE-PINNED 2026-09-13, 23578 to 103861 (+80283), Immutable maps and priority
#: queues are MeTTa equations over the shared collection libraries, replacing
#: the native tree adaptation [measured 2026-09-13: min-of-3 serial fresh
#: processes; command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=9c9e60542491416e2c5e431a2672bb20f04264fa].
#: RE-PINNED 2026-09-14, 103861 to 99859 (-4002), Functional applies finished
#: callback arguments through reduce; Statistics derives exact coefficient rows
#: and Combinatorics retires its native probability provider [measured
#: 2026-09-14: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=e1be99ea1c08f70444c1c35cada441e089777906].
#: RE-PINNED 2026-09-14, 99859 to 99865 (+6), Closure publishes the shared
#: rendering and IEEE services, refreshes the callable projection and annotates
#: native protocol domains; every direct and transitive library consumer is
#: measured again [measured 2026-09-14: min-of-3 serial fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=b7866b4d874879ff0cb212eb1c6af60dddaa39c6].
#: RE-PINNED 2026-09-11, 23578 to 23987 (+409), end-of-wave re-pin on the
#: merged tree after FROM's reference rows and four engine units, the closed-
#: set derivations and two host services, BINDING's one native evaluation entry
#: and boot import, W-OBSERVE's observer guard, PERF's receipts batching and
#: cursor retirement, and the three REDS repairs (derived runtime resources and
#: the shared loader, the tool-lane repairs, the corpus example); serial
#: minimum of three fresh processes through the lane's run_twin with
#: file_search_cache_time=9223372036854775807 set before child boot [measured
#: 2026-09-11: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=57f84148ba2684015f052d533f3197eca07b1f7b].
#: RE-PINNED 2026-09-18, 23578 to 25326 (+1748), the branch's landings since
#: the 09-10 pins, re-taken on the tip f06186a96: the compiled call law
#: (e59104ace: an Atom argument enters as written, a Python object crosses as a
#: value, a positional call of a bound callee is the plain application and a
#: compiled lambda is bare where it is applied), the one codec at the grounded
#: call (fd0af38f7, whose read of a call site's written keyword tail costs
#: about six inferences per translated site, read once since 7cc8fb863), the
#: runnable cache's dependency index written by the producer (a9e2c06d3, which
#: takes back the walk of the generated code 5416e741d charged at every miss),
#: the host patches of 09-17 and the class units of 09-13 to 09-16 the ladder
#: in docs/journal/2026-09-14-runnable-artifact-dependencies.md places; serial
#: minimum of three fresh processes through the lane's run_twin with
#: file_search_cache_time=9223372036854775807 set before child boot [measured
#: 2026-09-18: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=6944d06ce96fdbcd1faefb640f15dbfa0cf286dd].
#: RE-PINNED 2026-09-18, 25326 to 25027 (-299), the trunk merged (f97c4b0a3,
#: petta's 61 commits since c75181adc) with the definition batch's load pushed
#: as the running load (2da1155e3): every example moved with the engine, 279 of
#: 294 cheaper (median -0.78%), through the compiled runnable envelope
#: executing each runnable form's fixed answer, name and fuel envelope from
#: compiled clauses, the trunk's trailed scopes and compiled context readers (a
#: b_getval/2 read per recorded assertion in place of the branch's thread-local
#: rows), the host listener door and the receipts loop probing the owner once
#: per set; serial minimum of three fresh processes through the lane's run_twin
#: [measured 2026-09-18: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=55d451b670949c2dc9d2ab7bc678f33f21094bd2].
#: RE-PINNED 2026-09-21, 25027 to 114422 (+89395), the sixty libraries derived
#: in MeTTa landed with merge 97763e7fa eight hours after the previous pin
#: 55d451b67, so every example importing one now pays a MeTTa derivation where
#: it paid a Prolog body instead, which the 2026-09-14 ruling accepts
#: explicitly as the price of a library that survives the engine swap [measured
#: 2026-09-21: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=6e09cb25d5495c2db3283166e6ce4e07eefecfb2].
#: RE-PINNED 2026-09-24, 114422 to 128216 (+13794), placed on the full-
#: configuration first-parent ladder from the pin commit 6e09cb25d: the 120
#: commits 43e964002..c09dc4868, where the per-commit probe sweep puts each
#: step at one commit: 5b4e7e53d reads a translator rule's declared type where
#: the rule lives; aea2e5e03 and 6922f54c9 carry the csv and lib_file refusal
#: vocabulary; d27805154 carries lib 19a231b, whose regenerated faces declare
#: six libraries' inputs %Undefined%, so their calls stop paying a declared-
#: type check (vector_lib -7278, statistics_lib -6453); 33219ffa0 resolves a
#: bare library name to its pkg.metta; 0cd329450 adds the platform refusal
#: kind, one metta_refusal_declaration/4 row that metta_catalog_preset/1 turns
#: into one more (refusal ...) catalog row and one more refusal-kind vocabulary
#: member, measured at +10 to +15 on most twins; and d8231f103 refuses a
#: library spec that walks out of the library root; a7955cd07 carried lib
#: 629c86c, the library split, which moved every library's surface out of its
#: pkg.metta manifest into lib.metta beside it, so an import reads the manifest
#: and then imports the library's own source as a second file; 54784fded reads
#: the builtin type surface from every .metta in lib_builtin_types' directory,
#: which restored the 195 builtin cost rows the split's manifest-only read had
#: dropped; 63b910f4f added a clause to metta_reference_internal/2 that asks
#: the specializer's ho_specialization/3 registry, so every reference grade a
#: load computes pays that lookup, which is how defined-name, documented and
#: undocumented stopped reporting specializer residues; d6e09995c retires a
#: load's package rows from every space but its library home after
#: package_load/3, withdrawing each through metta_remove_atom_reference/1,
#: which uncompiles the row's equation, so every import into an importing space
#: pays that withdrawal; 6167a0fb2 makes import currency transitive: each
#: nested load records an import_nested_source/3 edge to every import still in
#: flight above it, and a cached import answers current only when every nested
#: receipt does; the 20 commits 6167a0fb2..864c4bac0, where the sweep puts the
#: probes' only step at e1acacad2, which clears a space's import bookkeeping
#: from the module that owns it; da91bc244 confines an exact removal's
#: selection to its own atom: native_retract_one/2 now records the selected
#: clause's head, a clause/3 lookup per exact removal, and checks each removal
#: made while the selector is live against it, a few inferences per removal (+8
#: on most twins, +24 to +192 on the library twins that withdraw package rows);
#: where a twin's move exceeds these steps, the remainder is drift that stayed
#: inside its band (four inferences, or its own declared allowance) on every
#: other interval [measured 2026-09-24: min-of-3 serial fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=WORKTREE].
#: RE-PINNED 2026-09-24, 128216 to 126420 (-1796), 0a81c782f loads a library's
#: Prolog half through the boot's claim (metta_load_source/2 in
#: package_load_native/2), so the half, and every governed half or support file
#: it loads in turn, reads the .qlf the claim's hermetic child wrote where it
#: had compiled from source in every process; the same commit starts that child
#: from the running home's own swipl, where it had been the stock swipl the
#: lane's PATH finds, which the host check has refused since f2822e2ae, so no
#: child had written an artifact and lib/_support/native_build.pl compiled in
#: every process that loaded a library with a native half, the +10.3k that
#: f2822e2ae's paragraph charges to the boot host check [measured 2026-09-24:
#: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=0a81c782fd6ba00984c36e58e228f73bca810dee].
#: RE-PINNED 2026-09-24, 126420 to 126453 (+33), 0847c3d4c decides a platform
#: capability the first time anything reads it, by whether every library its
#: census row names resolves, where only a failed load used to record anything,
#: and 984eabe23 keeps each verdict in a flag decided under a mutex so two
#: threads' first reads agree; the count moves by what the twin's reads now
#: decide, about 660 inferences for a one-library capability and 1,964 for
#: markup's three, and by a few where it reads the census without deciding
#: [measured 2026-09-24: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=d832d20e8edfdad28ad52815757ba9e685ad2de3].
#: RE-PINNED 2026-09-24, 126453 to 143748 (+17295), +36 at aaeea643a, whose
#: seat 5b0b92274 adds twelve predicates to module user that filereader's
#: registration walk above forty names reads at three inferences each; +9 at
#: b7e3d3bcb, whose three new metta_engine predicates that walk reads at three
#: inferences each; +17,232 at ae1cc8936, where a registration batch of
#: thirteen names or more walks the visible predicate table at two inferences a
#: predicate that asking per name spent inside one C call, and a batch above
#: forty tests each predicate with a dict at one inference fewer than the AVL;
#: +18 at b5eb39acd, whose three new engine exports the registration walk above
#: twelve names reads at two inferences each [measured 2026-09-24: min-of-3
#: serial fresh processes at HEAD in battery 118 holding the committed tree
#: alone (BATTERY_KEEP='', 11:56); each step read with its parent and child in
#: turn in battery 115 (10:42 to 11:18), 117 (11:01 to 12:10) or 120 (12:04 to
#: 12:13) from committed trees or this job's patched copies of them, none from
#: a working tree; 850d2a660's and 0f6d29ba6's split from provider-carry's own
#: pairs, aaeea643a's on the ladder before 10:05; command=python
#: extensions/python/tools/twin_coverage.py --measure --rounds 3;
#: commit=c7d7244fbe6d32d024ca8c61b336008e98b156ef].
BUDGET = 143748
