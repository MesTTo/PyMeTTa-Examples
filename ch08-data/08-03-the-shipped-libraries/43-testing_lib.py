"""Purpose: compose finite domains, traversal, assertions and first witnesses.

Guarantees: every claim in 43-testing_lib.metta uses the same ordinary primitives.
[tested: python extensions/python/tools/twin_coverage.py examples/ch08-data/08-03-the-shipped-libraries/43-testing_lib.metta; commit=7fad61bab72098722b27091a94282ff69989920e].
"""

from metta import FALSE, TRUE, G, S, V, lib
from metta._errors.errors import AssertionFailure, MettaError


def twin(m):
    """Use ordinary generators with assertions, counting and commitment."""
    m += lib.combinatorics
    m += lib.testing

    def unary(body):
        """Hold a function with the parameter x."""
        return S["|->"]((V.x,), body)

    def refused(call):
        """Return the native refusal after consuming the complete call."""
        try:
            list(m.eval(call))
        except MettaError as error:
            return error
        return None

    x = V.x
    literal = S["+"](1, 2)
    power = m.fn.cartesian_power
    assert m.fn.range(-2, 3) == [-2, -1, 0, 1, 2]
    assert m.fn.range(3, 4) == [3]
    assert m.fn.range(3, 3) == []
    assert m.fn.range(10**20, 10**20 + 3) == [10**20, 10**20 + 1, 10**20 + 2]
    assert m.fn.superpose((S.a, S.a, G("π"))) == [S.a, S.a, G("π")]
    assert m.fn.superpose(()) == []
    assert len(m.fn.index_atom(S.quote((literal,)), 0)[0]) == 3
    assert m.fn.index_atom(((),), 0) == [()]
    items = tuple(m.fn.range(1, 4))
    assert m.fn.index_atom(items, S.range(0, S.size_atom(items))) == [1, 2, 3]

    assert power((0, 1), 0) == [()]
    assert power((0, 1), 2) == [(0, 0), (0, 1), (1, 0), (1, 1)]
    assert power((S.a, S.a), 2) == [(S.a, S.a)] * 4
    assert power((), 0) == [()]
    assert power((), 2) == []
    population = tuple(m.fn.range(0, 2))
    assert power(population, S.range(0, 3)) == [(), (0,), (1,), (0, 0), (0, 1), (1, 0), (1, 1)]
    assert power((0, 1), S.range(2, 2)) == []
    choice = m.fn.index_atom((S.row(x, x),), 0).one()
    pair = m.fn.map_atom((1, 2), unary(S["copy_term"](S.quote(choice)))).one()  # rung: both variable copies must travel in one answer to compare their sharing
    assert m.fn["=alpha"](pair, (S.row(V.a, V.a), S.row(V.b, V.b))) == [True]
    assert power(((), (S.a,)), 1) == [((),), ((S.a,),)]

    for value in m.fn.range(-3, 4):
        assert value.value * value.value >= 0
    for values in power((0, 1), S.range(0, 4)):
        assert m.fn.reverse(S.reverse(values)) == [values]
    assert m.fn.forall(S.range(0, 5), S["<="](0)) == [True]
    count = S["|->"]((V.value, V.count), S["+"](V.count, 1))
    assert m.fn.foldall(count, S.superpose((S.a, S.a, S.b)), 0) == [3]
    assert m.fn.forall(S.superpose(()), unary(FALSE)) == [True]
    assert m.fn.foldall(count, S.superpose(()), 0) == [0]

    for _ in m.fn.range(1, 3):
        assert sorted(m.fn.superpose((2, 1, 1))) == [1, 1, 2]
    for _ in m.fn.range(1, 3):
        assert m.fn.empty() == []
    for value in m.fn.index_atom(S.quote((literal,)), 0):
        assert [value] == [literal]
    for value in m.fn.index_atom((S.row(x, x),), 0):
        assert m.fn["=alpha"](value, S.row(V.y, V.y)) == [True]

    assert next(value for value in m.fn.range(0, 6) if value.value >= 3) == 3
    assert (next(value for value in m.fn.range(0, 6) if value.value >= 3),) == (3,)
    assert next((value for value in m.fn.range(0, 3) if value.value >= 3), None) is None
    assert m.fn.superpose(()).first(default=None) is None
    assert next(value for value in m.fn.range(0, 6)
                if sorted(m.fn.superpose((2, 1, 1))) == [1, 1, 2]) == 0
    assert len(m.fn.index_atom(S.quote((literal,)), 0).first()) == 3
    assert next(value for value in m.fn.index_atom(((), (S.a,)), S.range(0, 2))
                if len(value) == 0) == ()
    for value in m.fn.range(0, 3):
        assert next(other for other in m.fn.range(0, 3) if value == other) == value

    checked = 0
    for value in m.fn.range(0, 3):
        assert value.value >= 0
        checked += 1
    assert checked == 3
    assert m.fn.forall(S.range(0, 2), unary(S.superpose((FALSE, TRUE)))) == [True]
    assert m.fn.forall(S.range(0, 2), unary(S.empty())) == [False]
    assert m.fn.forall(S.range(0, 2), unary(7)) == [False]

    error = refused(S.assertEqualToResult(S.superpose((1, 1)), (1, 2)))  # rung: the core assertion's own missing/excess report is the subject
    assert isinstance(error, AssertionFailure) and error.missing == (2,) and error.excess == (1,)
    assert refused(S.cartesian_power((S.a,), -1)) is not None
    assert refused(S.cartesian_power((S.a,), 1.5)) is not None
    assert m.solve(x, S.once(S.unify(x, 3, x, S.empty()))).x == 3


#: MEASURED: domain, assertion, bag, witness and refusal claims through the core.
#: The example pays 76856 inferences.
#: [measured: 74003 inferences, minimum of three fresh serial processes;
#: command=python extensions/python/tools/twin_coverage.py --measure --rounds 3
#: examples/ch08-data/08-03-the-shipped-libraries/43-testing_lib.metta;
#: fixture=lib_testing with engine/lib QLF artifacts purged; commit=7fad61bab72098722b27091a94282ff69989920e].
#: RE-PINNED 2026-09-13, 74003 to 364240: collection operations now compose
#: MeTTa matching, folds and application; segment continuations are protected
#: compiler helpers. The example measures 390681 for the same claims
#: [measured: 364240 inferences; command=python extensions/python/tools/twin_coverage.py --measure --rounds 3 examples/ch08-data/08-03-the-shipped-libraries/43-testing_lib.metta;
#: fixture=minimum of three serial fresh processes after purging engine/lib QLF;
#: commit=6471fbad35eced5ed6440ebf2c25a053b20221f3].
#: RE-PINNED 2026-09-13, 364240 to 365541 (+1301), The validated range
#: continuation now lives in the private support file rather than appearing as
#: a public library head. The import adds its measured loading cost without
#: changing the continuation body [measured 2026-09-13: min-of-3 serial fresh
#: processes; command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=6471fbad35eced5ed6440ebf2c25a053b20221f3].
#: RE-PINNED 2026-09-13, 365541 to 367992 (+2451), Math and Statistics derive
#: their recipes from MeTTa equations; Statistics consolidates finite laws and
#: adds reflective claims. Their collection dependencies share the proper
#: finite expression boundary in lib/_support/collections_data.pl [measured
#: 2026-09-13: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=6fa571d1b7059b610f73e9feed657711414251e5].
#: RE-PINNED 2026-09-13, 367992 to 368014 (+22), Vector, Math and the shared
#: collection boundary declare their native effects. The engine reads late
#: provider declarations and retains definition analysis for computed function
#: heads [measured 2026-09-13: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=1d0b78a359f58de49f2f98bed50a6480d56cd5f6].
#: RE-PINNED 2026-09-14, 368014 to 363965 (-4049), Functional applies finished
#: callback arguments through reduce; Statistics derives exact coefficient rows
#: and Combinatorics retires its native probability provider [measured
#: 2026-09-14: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=e1be99ea1c08f70444c1c35cada441e089777906].
#: RE-PINNED 2026-09-21, 363965 to 370950 (+6985), the sixty libraries derived
#: in MeTTa landed with merge 97763e7fa eight hours after the previous pin
#: 55d451b67, so every example importing one now pays a MeTTa derivation where
#: it paid a Prolog body instead, which the 2026-09-14 ruling accepts
#: explicitly as the price of a library that survives the engine swap [measured
#: 2026-09-21: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=6e09cb25d5495c2db3283166e6ce4e07eefecfb2].
#: RE-PINNED 2026-09-24, 370950 to 380994 (+10044), placed on the full-
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
#: undocumented stopped reporting specializer residues; 814b99468 retains a
#: self-call's function_view dependency, so a recursive body is rebuilt as a
#: caller of its own function whenever an arriving equation changes that view
#: (fib's rebuilds 1 to 2 and newtons_method's energy 2 to 4, each reached from
#: spaces:add_function_atom/7 through lib_memo's automatic reconcile), the fix
#: that took lib_statistics and lib_random to green; d6e09995c retires a load's
#: package rows from every space but its library home after package_load/3,
#: withdrawing each through metta_remove_atom_reference/1, which uncompiles the
#: row's equation, so every import into an importing space pays that
#: withdrawal; 6167a0fb2 makes import currency transitive: each nested load
#: records an import_nested_source/3 edge to every import still in flight above
#: it, and a cached import answers current only when every nested receipt does;
#: the commits 63fc952ac..8d45268e3, which the ladder did not split; their
#: runtime changes are 31c0afd8a (the host refusal's message), 7472c4907, which
#: marks a module's reference face dirty instead of walking its forward
#: closure, so support_stabilize/3 walks the face's dependents only when the
#: recomputed value moved and an event that changes nothing recompiles no
#: caller, 7054c11f7, which carries lib 62ca61c's bisecting bit length in
#: _support/statistics.metta, and the Python-seat pointers; da91bc244 confines
#: an exact removal's selection to its own atom: native_retract_one/2 now
#: records the selected clause's head, a clause/3 lookup per exact removal, and
#: checks each removal made while the selector is live against it, a few
#: inferences per removal (+8 on most twins, +24 to +192 on the library twins
#: that withdraw package rows); where a twin's move exceeds these steps, the
#: remainder is drift that stayed inside its band (four inferences, or its own
#: declared allowance) on every other interval [measured 2026-09-24: min-of-3
#: serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=WORKTREE].
#: RE-PINNED 2026-09-24, 380994 to 379195 (-1799), 0a81c782f loads a library's
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
#: RE-PINNED 2026-09-24, 379195 to 390712 (+11517), +11,511 at ae1cc8936, where
#: a registration batch of thirteen names or more walks the visible predicate
#: table at two inferences a predicate that asking per name spent inside one C
#: call, and a batch above forty tests each predicate with a dict at one
#: inference fewer than the AVL; +6 at b5eb39acd, whose three new engine
#: exports the registration walk above twelve names reads at two inferences
#: each [measured 2026-09-24: min-of-3 serial fresh processes at HEAD in
#: battery 118 holding the committed tree alone (BATTERY_KEEP='', 11:56); each
#: step read with its parent and child in turn in battery 115 (10:42 to 11:18),
#: 117 (11:01 to 12:10) or 120 (12:04 to 12:13) from committed trees or this
#: job's patched copies of them, none from a working tree; 850d2a660's and
#: 0f6d29ba6's split from provider-carry's own pairs, aaeea643a's on the ladder
#: before 10:05; command=python extensions/python/tools/twin_coverage.py
#: --measure --rounds 3; commit=c7d7244fbe6d32d024ca8c61b336008e98b156ef].
#: RE-PINNED 2026-09-24, 390712 to 390617 (-95), d4a365c16 holds the support
#: graph's visited set and the reference refresh's space sets in SWI tries
#: instead of library(nb_set): a membership check is one foreign call where
#: nb_set probed in Prolog, four inferences a step past a taken slot, from a
#: slot a library space's path-bearing name decided, and a walk over a node or
#: two pays a few inferences more for the trie's setup (-2); gate-perf's
#: d781eab8f carries an exact removal's selected head from the code that
#: selected it, so a withdrawal copies its equation once: 23 inferences fewer
#: for each equation removal the twin adopts and 4 for each it selects (-115);
#: the packages job's 90be572a9 and 4003462fe register Prolog through one
#: engine service: +22 for each library the twin imports (ten new engine
#: predicates and two user imports in the registration walk at two inferences
#: each, less the retired loaded_extension_file/2), and 146 inferences for a
#: Prolog file's origin or 220 for a text's SHA-256 on a twin that registers
#: Prolog (+22); each step read serially on its own committed tree, from gate-
#: perf's pin at c7d7244fb, and the fixed tree 4ff69551e reads what 4003462fe
#: does [measured 2026-09-24: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=4ff69551e0e226442cf7257b96af858adda957a4].
#: RE-PINNED 2026-09-24, 390617 to 390696 (+79), +77 at the change this re-pin
#: lands with, which publishes a from row by itself when rows are all a space
#: owes: its 36 predicates visible to filereader's registration walk cost a
#: batch above twelve names 72 inferences, each restricted space's core about
#: 28 a predicate, and every whole publication and face event its ledger's
#: bookkeeping [measured 2026-09-24: the twins lane alone on 8d651070d with the
#: change before this one and with this change too, one after the other in
#: battery 117's one path, every component at its pin; command=sh
#: tools/check.sh twins (twin_coverage.py inside tools/bounded.sh);
#: commit=e4b7448d1f1bd98733f1b04c3906aaa42f35ef1a].
#: RE-PINNED 2026-09-25, 390696 to 390718 (+22), the py-* doors change makes
#: more predicates visible from filereader, and
#: filereader:existing_predicate_arities/2 walks every predicate visible there
#: at two inferences each whenever a source registering more than twelve names
#: loads: on one tree the change's new engine predicates alone, defined with
#: their two boot uses taken out, make eight more visible and move this twin by
#: 16 for each such load, and the whole change by 20, ten more at its loads
#: (i-arity-walk-all-predicates) [measured 2026-09-25T02:52:53+10:00: min-of-3
#: serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-25, 390718 to 387438 (-3280), the host evaluation door
#: replaces the Python binding's own evaluation, and its moves are these, each
#: measured on the superproject's dd36742f5 against the registration change
#: beneath it: every answer reads its well-founded residue through
#: call_delays/2, three inferences an answer; a flat call of a compiled
#: function is translated the first time it is asked, a translation-cache miss
#: the binding's direct call skipped; the gate that direct call ran on every
#: ask, a type-declaration match through the space's storage, the foreign-space
#: hook and the MORK ownership question, is gone; and in a seat process
#: filereader's existing_predicate_arities/2 walks thirteen more predicates,
#: the door, its questions and the host services the binding now calls less the
#: binding predicates the door retired, two inferences each a registration of
#: more than twelve names [measured 2026-09-25T06:48:15+10:00: min-of-3 serial
#: fresh processes; command=python extensions/python/tools/twin_coverage.py
#: --repin].
#: RE-PINNED 2026-09-25, 387438 to 387448 (+10), Runtime.reclaim(), the
#: reclamation barrier metta_py_reclaim/1, adds five predicates to user, and
#: existing_predicate_arities/2 walks every user predicate about twice per
#: large load (i-arity-walk-all-predicates) [measured
#: 2026-09-25T11:25:25+10:00: one full twins lane before this commit and one
#: with it, the two read on one battery path at the landing's HEAD;
#: command=python extensions/python/tools/twin_coverage.py].
BUDGET = 387448
