"""Purpose: sets as ordered expressions, from Python.

A set is an expression, so it comes back as one and a tuple goes in as one;
`len` is the cardinality and `==` the equality, because the representation is
canonical. A refusal is what `if-error` reads, so it is caught as the error it is.

Guarantees: the same claims as 23-sets_lib.metta
[tested: python extensions/python/tools/twin_coverage.py examples/ch08-data/08-03-the-shipped-libraries/23-sets_lib.metta; commit=6471fbad35eced5ed6440ebf2c25a053b20221f3].
Open Obligations:
  To Do: None
  Hacks: None
  Future Enhancements: None.
"""

from metta import S, V, lib
from metta._errors.errors import MettaError


def twin(m):
    """Build, ask, insert, remove, merge, compare and refuse."""
    m += lib.sets
    m += lib.functional

    def refused(call):
        """Whether evaluating a call raises, which is what if-error reads."""
        try:
            list(m.eval(call))
        except MettaError:
            return True
        return False

    def elements(answers):
        """One answer's expression, as a list."""
        return list(answers.one())

    set_of, is_set = m.fn.set_of, m.fn.set_is
    member, insert, remove = m.fn.set_member, m.fn.set_insert, m.fn.set_remove
    union, intersection = m.fn.set_union, m.fn.set_intersection
    difference, symmetric = m.fn.set_difference, m.fn.set_symmetric_difference
    subset, disjoint = m.fn.set_subset, m.fn.set_disjoint

    # A set is an expression in the standard order of terms with no duplicates,
    # so set-of sorts and deduplicates once and the answer is an ordinary
    # expression: len counts it, == compares it and () is the empty set.
    assert elements(set_of((3, 1, 2, 1))) == [1, 2, 3]
    assert elements(set_of(())) == []
    assert len(set_of((S.b, S.a, S.b)).one()) == 2
    assert set_of((2, 1)).one() == set_of((1, 2, 2)).one()
    # Numbers sort before symbols in the standard order, and a symbol before an
    # expression, so a mixed set has a fixed shape whatever order it was written in.
    assert elements(set_of((S.b, (S.x,), 2, S.a, 1))) == [1, 2, S.a, S.b, S.x()]

    # set-is asks whether an expression already is one: ordered and without
    # duplicates. Every other head asks the same question before it merges.
    assert is_set((1, 2, 3)) == [True]
    assert is_set((2, 1)) == [False]
    assert is_set((1, 1)) == [False]
    assert is_set(3) == [False]

    # Membership compares TERMS rather than unifying, so a variable is not a
    # member of a set of numbers, where a match would have bound it to the first.
    assert member((1, 2, 3), 2) == [True]
    assert member((1, 2, 3), 4) == [False]
    assert member((1, 2, 3), V.x) == [False]

    # Insertion and removal answer a new set and leave the input alone; adding
    # what is there and removing what is not both answer the set unchanged.
    assert elements(insert((1, 3), 2)) == [1, 2, 3]
    assert elements(insert((1, 3), 3)) == [1, 3]
    assert elements(remove((1, 2, 3), 2)) == [1, 3]
    assert elements(remove((1, 2, 3), 9)) == [1, 2, 3]
    primes = set_of((2, 3, 5)).one()
    assert elements(insert(primes, 7)) == [2, 3, 5, 7]
    assert list(primes) == [2, 3, 5]

    # The four combinations preserve the canonical representation.
    assert elements(union((1, 3), (2, 3))) == [1, 2, 3]
    assert elements(intersection((1, 2, 3), (2, 3, 4))) == [2, 3]
    assert elements(difference((1, 2, 3), (2, 3, 4))) == [1]
    assert elements(difference((2, 3, 4), (1, 2, 3))) == [4]
    assert elements(symmetric((1, 2, 3), (2, 3, 4))) == [1, 4]
    assert elements(union((), ())) == []
    assert elements(intersection((1, 2), (3, 4))) == []

    # The same operations take any number of sets. Union has an empty identity;
    # intersection requires a set to supply its universe.
    assert elements(union((1, 2), (2, 3), (5,))) == [1, 2, 3, 5]
    assert elements(union()) == []
    assert elements(intersection((1, 2, 3), (2, 3, 4), (3, 4, 5))) == [3]
    assert refused(S.set_intersection())

    # The two questions between sets. A set is a subset of itself, the empty set
    # is a subset of everything and disjoint from everything, itself included.
    assert subset((1, 2), (1, 2, 3)) == [True]
    assert subset((1, 2, 3), (1, 2)) == [False]
    assert subset((), (1,)) == [True]
    assert subset((1, 2), (1, 2)) == [True]
    assert disjoint((1, 2), (3, 4)) == [True]
    assert disjoint((1, 2), (2, 3)) == [False]
    assert disjoint((), ()) == [True]

    # The laws hold because the representation is canonical: a union is the same
    # set whichever way round, and De Morgan's law is an equality of expressions.
    assert union((1, 2), (3,)).one() == union((3,), (1, 2)).one()
    universe = (1, 2, 3, 4)
    assert difference(universe, union((1,), (2,)).one()).one() == intersection(
        difference(universe, (1,)).one(), difference(universe, (2,)).one()
    ).one()

    # An argument that is not a set is refused rather than merged into nonsense:
    # the host's own merge over an unordered list answers (2 1 1) with nothing
    # said, which is the wrong answer with no symptom this library exists to remove.
    assert refused(S.set_union((2, 1), (1,)))
    assert refused(S.set_member((1, 1), 1))
    assert refused(S.set_union((1,), (2, 1)))

    arithmetic, error_data = S["+"](1, 2), S.Error(S.a, S.b)
    assert set_of(S.quote((arithmetic, error_data, arithmetic))) == [(arithmetic, error_data)]
    assert is_set(S.quote(error_data)) == [True]
    # Iteration keeps Error-headed collections as data, as it does any answer.
    assert list(union(S.quote(error_data), (S.a, S.c))) == [S.Error(S.a, S.b, S.c)]
    assert list(intersection(S.quote(error_data), S.quote(S.Error(S.a)))) == [S.Error(S.a)]
    assert member(S.quote((V.x,)), V.x) == [True]
    assert len(set_of((1, 1.0)).one()) == 2
    assert is_set(V.x) == [False]
    assert refused(S.set_intersection((2, 1)))

    assert elements(union((1, 2))) == [1, 2]
    assert elements(intersection((1, 2))) == [1, 2]
    assert elements(union((1,), (2,), (3,), (4,), (5,), (6,), (7,), (8,), (9,))) == list(range(1, 10))
    assert elements(m.fn.apply_to(S.set_union, S.quote(((1, 2), (2, 3), (4,))))) == [1, 2, 3, 4]
    assert elements(m.fn.apply_to(S.set_intersection, S.quote(((1, 2, 3), (2, 3, 4), (3,))))) == [3]


#: MEASURED on this branch rather than inherited: this twin is new, so there is
#: no earlier pin to move. The 41 claims cover the thirteen heads, the laws and
#: the refusals; the example pays 63,725 inferences for the same work
#: [measured 2026-09-12: 71496 inferences, minimum of three serial fresh
#: processes; command=python extensions/python/tools/twin_coverage.py --measure
#: --rounds 3 examples/ch08-data/08-03-the-shipped-libraries/23-sets_lib.metta;
#: fixture=lib_sets at its functional commit, artifacts purged before the run;
#: commit=e3e8c891065765765ee8fe567c5eb6864e79b652].
#: RE-PINNED 2026-09-13, 71496 to 366379: collection operations now compose
#: MeTTa matching, folds and application; segment continuations are protected
#: compiler helpers. The example measures 348761 for the same claims
#: [measured: 366379 inferences; command=python extensions/python/tools/twin_coverage.py --measure --rounds 3 examples/ch08-data/08-03-the-shipped-libraries/23-sets_lib.metta;
#: fixture=minimum of three serial fresh processes after purging engine/lib QLF;
#: commit=6471fbad35eced5ed6440ebf2c25a053b20221f3].
#: RE-PINNED 2026-09-13, 366379 to 367716 (+1337), The validated range
#: continuation now lives in the private support file rather than appearing as
#: a public library head. The import adds its measured loading cost without
#: changing the continuation body [measured 2026-09-13: min-of-3 serial fresh
#: processes; command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=6471fbad35eced5ed6440ebf2c25a053b20221f3].
#: RE-PINNED 2026-09-13, 367716 to 363631 (-4085), Math and Statistics derive
#: their recipes from MeTTa equations; Statistics consolidates finite laws and
#: adds reflective claims. Their collection dependencies share the proper
#: finite expression boundary in lib/_support/collections_data.pl [measured
#: 2026-09-13: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=6fa571d1b7059b610f73e9feed657711414251e5].
#: RE-PINNED 2026-09-13, 363631 to 363653 (+22), Vector, Math and the shared
#: collection boundary declare their native effects. The engine reads late
#: provider declarations and retains definition analysis for computed function
#: heads [measured 2026-09-13: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=1d0b78a359f58de49f2f98bed50a6480d56cd5f6].
#: RE-PINNED 2026-09-14, 363653 to 354572 (-9081), Functional applies finished
#: callback arguments through reduce; Statistics derives exact coefficient rows
#: and Combinatorics retires its native probability provider [measured
#: 2026-09-14: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=e1be99ea1c08f70444c1c35cada441e089777906].
#: RE-PINNED 2026-09-21, 354572 to 360948 (+6376), the sixty libraries derived
#: in MeTTa landed with merge 97763e7fa eight hours after the previous pin
#: 55d451b67, so every example importing one now pays a MeTTa derivation where
#: it paid a Prolog body instead, which the 2026-09-14 ruling accepts
#: explicitly as the price of a library that survives the engine swap [measured
#: 2026-09-21: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=6e09cb25d5495c2db3283166e6ce4e07eefecfb2].
#: RE-PINNED 2026-09-24, 360948 to 371620 (+10672), placed on the full-
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
#: RE-PINNED 2026-09-24, 371620 to 369821 (-1799), 0a81c782f loads a library's
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
#: RE-PINNED 2026-09-24, 369821 to 393032 (+23211), +23,199 at ae1cc8936, where
#: a registration batch of thirteen names or more walks the visible predicate
#: table at two inferences a predicate that asking per name spent inside one C
#: call, and a batch above forty tests each predicate with a dict at one
#: inference fewer than the AVL; +12 at b5eb39acd, whose three new engine
#: exports the registration walk above twelve names reads at two inferences
#: each [measured 2026-09-24: min-of-3 serial fresh processes at HEAD in
#: battery 118 holding the committed tree alone (BATTERY_KEEP='', 11:56); each
#: step read with its parent and child in turn in battery 115 (10:42 to 11:18),
#: 117 (11:01 to 12:10) or 120 (12:04 to 12:13) from committed trees or this
#: job's patched copies of them, none from a working tree; 850d2a660's and
#: 0f6d29ba6's split from provider-carry's own pairs, aaeea643a's on the ladder
#: before 10:05; command=python extensions/python/tools/twin_coverage.py
#: --measure --rounds 3; commit=c7d7244fbe6d32d024ca8c61b336008e98b156ef].
#: RE-PINNED 2026-09-24, 393032 to 392913 (-119), d4a365c16 holds the support
#: graph's visited set and the reference refresh's space sets in SWI tries
#: instead of library(nb_set): a membership check is one foreign call where
#: nb_set probed in Prolog, four inferences a step past a taken slot, from a
#: slot a library space's path-bearing name decided, and a walk over a node or
#: two pays a few inferences more for the trie's setup (-25); gate-perf's
#: d781eab8f carries an exact removal's selected head from the code that
#: selected it, so a withdrawal copies its equation once: 23 inferences fewer
#: for each equation removal the twin adopts and 4 for each it selects (-138);
#: the packages job's 90be572a9 and 4003462fe register Prolog through one
#: engine service: +22 for each library the twin imports (ten new engine
#: predicates and two user imports in the registration walk at two inferences
#: each, less the retired loaded_extension_file/2), and 146 inferences for a
#: Prolog file's origin or 220 for a text's SHA-256 on a twin that registers
#: Prolog (+44); each step read serially on its own committed tree, from gate-
#: perf's pin at c7d7244fb, and the fixed tree 4ff69551e reads what 4003462fe
#: does [measured 2026-09-24: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=4ff69551e0e226442cf7257b96af858adda957a4].
#: RE-PINNED 2026-09-24, 392913 to 393066 (+153), +149 at the change this re-
#: pin lands with, which publishes a from row by itself when rows are all a
#: space owes: its 36 predicates visible to filereader's registration walk cost
#: a batch above twelve names 72 inferences, each restricted space's core about
#: 28 a predicate, and every whole publication and face event its ledger's
#: bookkeeping [measured 2026-09-24: the twins lane alone on 8d651070d with the
#: change before this one and with this change too, one after the other in
#: battery 117's one path, every component at its pin; command=sh
#: tools/check.sh twins (twin_coverage.py inside tools/bounded.sh);
#: commit=e4b7448d1f1bd98733f1b04c3906aaa42f35ef1a].
#: RE-PINNED 2026-09-25, 393066 to 393110 (+44), the py-* doors change makes
#: more predicates visible from filereader, and
#: filereader:existing_predicate_arities/2 walks every predicate visible there
#: at two inferences each whenever a source registering more than twelve names
#: loads: on one tree the change's new engine predicates alone, defined with
#: their two boot uses taken out, make eight more visible and move this twin by
#: 16 for each such load, and the whole change by 20, ten more at its loads
#: (i-arity-walk-all-predicates) [measured 2026-09-25T02:51:40+10:00: min-of-3
#: serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-25, 393110 to 388872 (-4238), the host evaluation door
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
#: more than twelve names [measured 2026-09-25T06:47:14+10:00: min-of-3 serial
#: fresh processes; command=python extensions/python/tools/twin_coverage.py
#: --repin].
#: RE-PINNED 2026-09-25, 388872 to 388892 (+20), Runtime.reclaim(), the
#: reclamation barrier metta_py_reclaim/1, adds five predicates to user, and
#: existing_predicate_arities/2 walks every user predicate about twice per
#: large load (i-arity-walk-all-predicates) [measured
#: 2026-09-25T11:25:25+10:00: one full twins lane before this commit and one
#: with it, the two read on one battery path at the landing's HEAD;
#: command=python extensions/python/tools/twin_coverage.py].
BUDGET = 388892

#: OVERRUN 2026-09-12, 1399: the example nests its law claims in one evaluation
#: each, where Python reads them as separate calls whose intermediate sets cross
#: into the host and back: the two equalities, De Morgan's five calls and the
#: bound primes are eight evaluations the example makes as three. Measured
#: 71496 against a ceiling of 70097.5, and the distance is those crossings
#: [measured 2026-09-12: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --measure --rounds 3
#: examples/ch08-data/08-03-the-shipped-libraries/23-sets_lib.metta;
#: commit=e3e8c891065765765ee8fe567c5eb6864e79b652].
#: RETIRED 2026-09-13: the new 366379 cost is within the example's 10% band;
#: the measured composition above needs no additional allowance.
