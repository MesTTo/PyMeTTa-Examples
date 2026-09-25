"""Purpose: examples/ch08-data/08-03-the-shipped-libraries/11-combinatorics_lib.metta in Python: choosing from a finite collection.

Streams can be consumed a value at a time or collected. The existing collected
choice forms use the same generators. Literal expressions remain data.

Guarantees: the same claims as 11-combinatorics_lib.metta
[tested: lib_combinatorics_surface; commit=6471fbad35eced5ed6440ebf2c25a053b20221f3].
Open Obligations:
  To Do: None
  Hacks: None
  Future Enhancements: None.
"""

from metta import S, lib
from metta._errors.errors import MettaError


def refused(m, call):
    """Whether evaluating a call raises, which is what if-error reads."""
    try:
        list(m.eval(call))
    except MettaError:
        return True
    return False

#: The collection every claim is about, and its three unordered pairs.
LETTERS = (S.a, S.b, S.c)
PAIRS = ((S.a, S.b), (S.a, S.c), (S.b, S.c))


def twin(m):
    """Pairs, k-subsets in both shapes, and the prefix that is neither."""
    m += lib.combinatorics
    two, two_list = m.fn.choose2, m.fn.choose2l
    k_list, k_stream, prefix = m.fn.chooseKl, m.fn.chooseK, m.fn.takeK

    # Every unordered pair, one per solution: (a b) but never (b a), and
    # never (a a).
    assert sorted(two(LETTERS), key=str) == list(PAIRS)
    assert two((S.a,)) == []
    assert two(()) == []

    # The same answer set as one value rather than as multiplicity.
    assert two_list(LETTERS) == [PAIRS]
    assert two_list((S.a,)) == [()]

    # k of them, still unordered, still without repetition, in the list's own
    # order because the recursion counts down through it.
    assert k_list(LETTERS, 2) == [PAIRS]
    assert k_list((S.a, S.b, S.c, S.d), 3) == [
        ((S.a, S.b, S.c), (S.a, S.b, S.d), (S.a, S.c, S.d), (S.b, S.c, S.d))
    ]
    assert k_list(LETTERS, 2) == two_list(LETTERS)

    # The two base cases that make the recursion total: choosing none of
    # anything is one choice, the empty one, and choosing some of nothing is
    # no choice at all.
    assert k_list(LETTERS, 0) == [((),)]
    assert k_list((), 2) == [()]
    assert k_list((), 0) == [((),)]

    # The streamed version, which is what a search wants: the consumer can
    # stop without the rest being built.
    assert sorted(k_stream(LETTERS, 2), key=str) == list(PAIRS)
    assert k_stream(LETTERS, 0) == [()]

    # `takeK` is the prefix rather than a choice: the first k in order, and
    # the whole list when there are fewer than k.
    assert prefix(2, LETTERS) == [(S.a, S.b)]
    assert prefix(0, LETTERS) == [()]
    assert prefix(5, LETTERS) == [LETTERS]
    assert prefix(2, ()) == [()]

    # `range` counts up, n excluded; `range-step` strides, and a negative stride
    # counts down. A stride of zero would never arrive, so it is refused.
    step = m.fn["range-step"]
    assert list(m.fn.range(0, 4)) == [0, 1, 2, 3]
    assert list(step(0, 10, 3)) == [0, 3, 6, 9]
    assert list(step(5, 0, -2)) == [5, 3, 1]
    assert list(step(0, 0, 1)) == []
    assert list(step(0, 5, -1)) == []
    assert refused(m, S.range_step(0, 5, 0))

    # Every ordering, one per answer. A permutation counts POSITIONS, so a
    # repeated item makes repeated answers.
    orderings = m.fn.permutations
    assert list(orderings(LETTERS)) == [
        (S.a, S.b, S.c), (S.a, S.c, S.b), (S.b, S.a, S.c),
        (S.b, S.c, S.a), (S.c, S.a, S.b), (S.c, S.b, S.a),
    ]
    assert list(orderings(())) == [()]
    assert len(list(orderings((S.a, S.a)))) == 2

    # The powerset, one subset per answer, each in the items' own order.
    every = m.fn.subsets
    assert list(every((S.a, S.b))) == [(S.a, S.b), (S.b,), (S.a,), ()]
    assert list(every(())) == [()]
    assert len(list(every((S.a, S.b, S.c, S.d)))) == 16

    # One element from each set, the last varying fastest: an empty set anywhere
    # means no answers, and no sets at all mean one answer, the empty tuple.
    product, power = m.fn.tuples, m.fn["cartesian-power"]
    assert list(product(((1, 2), (S.x, S.y)))) == [
        (1, S.x), (1, S.y), (2, S.x), (2, S.y),
    ]
    assert list(product(((1, 2), ()))) == []
    assert list(product(())) == [()]

    # The product of one set with itself k times, repetition allowed.
    assert list(power((0, 1), 2)) == [(0, 0), (0, 1), (1, 0), (1, 1)]
    assert len(list(power((0, 1), 3))) == 8
    assert list(power((S.a, S.b), 0)) == [()]

    # The counts are exact and never build the choices they count.
    factorial, binomial = m.fn.factorial, m.fn.binomial
    ordered = m.fn["permutation-count"]
    assert factorial(5) == [120]
    assert factorial(0) == [1]
    assert binomial(5, 2) == [10]
    assert binomial(52, 5) == [2598960]
    assert binomial(5, 0) == [1]
    assert binomial(5, 9) == [0]
    assert ordered(5, 2) == [20]
    assert ordered(5, 5) == factorial(5)
    assert ordered(5, 0) == [1]
    assert refused(m, S.factorial(-1))

    # And the counts agree with the enumerations, which is the same question
    # asked two ways.
    assert len(list(orderings(LETTERS))) == factorial(3).one()
    assert len(list(k_stream((S.a, S.b, S.c, S.d), 2))) == binomial(4, 2).one()
    assert len(list(every(LETTERS))) == 2**3
    assert len(list(power((S.a, S.b), 3))) == 2**3

    arithmetic, error_data = S["+"](1, 2), S.Error(S.a, S.b)
    literal = (arithmetic, S.a)
    assert two(S.quote(literal)) == [literal]
    assert k_list(S.quote(literal), 1) == [((arithmetic,), (S.a,))]
    assert prefix(1, S.quote(literal)) == [(arithmetic,)]
    assert list(orderings(S.quote((arithmetic, error_data)))) == [
        (arithmetic, error_data), (error_data, arithmetic),
    ]
    assert list(every(S.quote(literal))) == [literal, (S.a,), (arithmetic,), ()]
    assert list(product(S.quote(((arithmetic, error_data), (S.a,))))) == [
        (arithmetic, S.a), (error_data, S.a),
    ]

    # Taking the first answer does not collect the remaining combinations.
    assert k_stream(tuple(range(100)), 50).first() == tuple(range(50))
    assert list(power((), 9999999999999999999999999999999)) == []
    assert refused(m, S.tuples(((), 3)))
    assert refused(m, S.cartesian_power((0, 1), 1.0))
    assert refused(m, S.factorial(1.0))
    assert binomial(100, 50) == [100891344545564193334812497256]
    assert list(step(0.5, 2.0, 1)) == [0.5, 1.5]
    advancement = []
    try:
        advancement.extend(S.fine for _ in step(1.0e20, 1.0e21, 1))
    except MettaError:
        advancement.append(S.refused)
    assert advancement == [S.fine, S.refused]


#: MEASURED on this branch rather than inherited: this twin is new, so there is
#: no earlier pin to move
#: [measured 2026-09-07: 119167 inferences, 1.0981x the example's 108518; command=python
#: extensions/python/tools/twin_coverage.py --measure --rounds 3;
#: fixture=docs/every-atom-has-an-example at its example commits; commit=98397cdd04679cbf40b2d515076dadc09c1b0a32].
#: RE-PINNED 2026-09-08, 119167 to 119116 (-51), metta_substitute_self/3 probes
#: the term for the text &self before walking it, one C write and one C
#: substring probe, where the twins-lane merge's one-equation door (08f6f4df)
#: walked every natively added equation in a named space unconditionally, so
#: every twin that adds or defines an equation in a named space drops by about
#: that equation's size in inferences; the same probe now guards the reader's
#: per-form door (record_translated_from/4), the deferred door's fallback
#: (stored_equation_source/4), a batch's arriving equations
#: (mark_or_translate_equation/5) and the removal probe (remove_equation/6),
#: where the walk is new and skipped for a term that never says &self, and a
#: twin that only removes or re-adds such equations pays the two-inference
#: probe per door crossing instead. Every twin here re-reads its budget on this
#: tree, minimum of three fresh processes [measured 2026-09-08: min-of-3 serial
#: fresh processes; command=python extensions/python/tools/twin_coverage.py
#: --repin; commit=856434d7c1d381b3f3d7cbbd008f46c0d41b61aa].
#: RE-PINNED 2026-09-08, 119116 to 117376 (-1740), the evaluation-fuel scope
#: marker is a trailed write (fix/every-intermittent-root-caused, f6e05ca9):
#: `$metta_fuel_scope` is written open with b_setval/2 at scope open and read
#: with b_getval/2 where nb_current/2 used to answer, so an abandoned scope
#: closes itself when an exception unwinds the trail and the cleanup is the
#: fast ordinary exit, and every runnable form pays fewer inferences per scope;
#: a twin drops by about the count of its runnables, and the engine bench reads
#: evaluate and translate 1642 lower each on the same tree. Every twin here re-
#: reads its budget on the merged tree, minimum of three fresh processes
#: [measured 2026-09-08: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=3fc65f02ce807c359f1a52026f950f345da2a9af].
#: RE-PINNED 2026-09-08, 117376 to 119336 (+1960), The engine and library
#: predicates now resolve through their owning modules and the explicit engine
#: facade; compiled program lookup crosses the added metta_engine tier
#: [measured 2026-09-08: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=ede2ac57e213a0d4502c6bbbca6227f97015b720].
#: RE-PINNED 2026-09-08, 119336 to 119605 (+269), the module boundary merged
#: with trunk's later packages (refactor/engine-and-libraries-as-modules at
#: b64291369): every space now resolves through one more chain link, prelude ->
#: metta_engine -> user, the engine's measured export list is imported into the
#: host tier at boot, the closed-sets watch point costs one inference per
#: &metta write, and a cursor opened by a host pays one transaction check at
#: its door; the branch pinned its budgets on its cut, trunk re-pinned the same
#: twins for the packages that landed after that cut, and only the merged tree
#: carries both, so this entry is where the two chains meet [measured
#: 2026-09-08: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=f1038acdcaf5230b6431c112f38a719d3dc9ef19].
#: RE-PINNED 2026-09-09, 119605 to 119929 (+324), structured concurrency landed
#: (feat/structured-concurrency merged at f80cc416d): every space mint records
#: its allocation in the library's lifetime rows, every write and run pays the
#: ownership hook and every drop asks the library whether a scope owns the
#: name, measured on a pristine control as 32 per mint, 2 per write and 44 per
#: drop with none per read; measured on the merged tree [measured 2026-09-09:
#: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=0f53926c2fd9f28e188814c84253ad82e13258f7].
#: RE-PINNED 2026-09-08, 119605 to 121384 (+1779), Trailing occurrence
#: arguments, token allocation in native writes, exact source withdrawal and
#: transaction-safe shared-table guards change the engine work priced by this
#: twin; answer bags retain the upstream law [measured 2026-09-08: min-of-3
#: serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=7f00ac7932fefa6f380fc8d14ec583ea0c58eff4].
#: RE-PINNED 2026-09-09, 121384 to 121708 (+324), tokens as storage landed
#: (feat/tokens-as-storage merged): every native occurrence carries a (t actor
#: generation) token as the trailing argument of its storage clause, minted
#: through flag/3 at the write funnel, and every clause read decodes it,
#: measured on a pristine control of trunk cbf7a958d as 8 more inferences per
#: add, 31 more per remove, 4 more per atom saved and 54 more per atom loaded
#: from a fast image, none per match, plus the merged tree's own lib_thread
#: repairs; measured on the merged tree [measured 2026-09-09: min-of-3 serial
#: fresh processes; command=python extensions/python/tools/twin_coverage.py
#: --repin; commit=50e34286f66c938d89d5d367c6370ad44164c97f].
#: RE-PINNED 2026-09-08, 119605 to 119728 (+123), Compiled shipped typing
#: decisions and initial vocabulary facts remove repeated interpretation;
#: indexed vocabulary membership replaces member-list scans; catalog reference
#: checks now respect transaction-local erasure. Paired controls and cut counts
#: are recorded in docs/journal/2026-09-08-what-the-waivers-were-paying-for.md
#: [measured 2026-09-08: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=32650f9ff4d1c4aa0749d8eb8b153e5bb448ee5c].
#: RE-PINNED 2026-09-09, 119728 to 121831 (+2103), the compiled vocabulary
#: seed, the membership index, base-module type lookups and the singleton
#: decoder landed (perf/cross-engine-waivers merged): boot publishes the
#: initial vocabulary types from a compiled payload through the tokenized
#: funnel, a warm membership read touches only its own clauses, a base-module
#: type lookup skips the prelude, and a Python decode with one named variable
#: builds no index; per-operation costs of a mint, write, read, drop, run, save
#: and load are unchanged against the trunk in fresh processes; measured on the
#: merged tree, +123 against the trunk's own pin of 121708 at da0e5755d; the
#: previous number is the branch's cut-time price, and the remaining +1980 is
#: what landed on the trunk between the cut f0d33dcad and da0e5755d, tokens as
#: storage above all [measured 2026-09-09: min-of-3 serial fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=b4341ae382c48ef225f4a52e566af6a9a71757c4].
#: RE-PINNED 2026-09-09, 121831 to 87047 (-34784), a library's Prolog half
#: compiles beside itself on its first import and loads from the artifact after
#: (metta_load_source/2, seam:compiled_source/1): a twin whose example imports
#: a library with a Prolog half pays the artifact load where both sides paid
#: the source consult and its compile-time expansion in every process,
#: lib_thread's import 278,309 to 5,925 inferences; every import now resolves
#: its spec and asks the boot's claim, about 180 inferences an import, and the
#: boot's content moved (the door, the seam and the three library imports the
#: tokens, receipts and seed units gained), which shifts clause layout by tens;
#: measured on this tree with the artifacts warm [measured 2026-09-09: min-of-3
#: serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=f26de01fbf3e0e3c64bb691c66a59fa959fee7f3].
#: RE-PINNED 2026-09-10, 87047 to 86991 (-56), the binding resolves Janus
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
#: RE-PINNED 2026-09-12, 86991 to 122318 (+35327), lib_combinatorics adds
#: permutations, subsets, tuples, cartesian-power, range-step, factorial,
#: binomial and permutation-count, and gives its two weighted-subset heads
#: declared modes, so the face is generated and the example proves 27 further
#: claims [measured 2026-09-12: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=08b21037caed98b220eb50b39630b32bea62e535].
#: RE-PINNED 2026-09-13, 122318 to 747785: collection operations now compose
#: MeTTa matching, folds and application; segment continuations are protected
#: compiler helpers. The example measures 850820 for the same claims
#: [measured: 747785 inferences; command=python extensions/python/tools/twin_coverage.py --measure --rounds 3 examples/ch08-data/08-03-the-shipped-libraries/11-combinatorics_lib.metta;
#: fixture=minimum of three serial fresh processes after purging engine/lib QLF;
#: commit=6471fbad35eced5ed6440ebf2c25a053b20221f3].
#: RE-PINNED 2026-09-13, 747785 to 749122 (+1337), The validated range
#: continuation now lives in the private support file rather than appearing as
#: a public library head. The import adds its measured loading cost without
#: changing the continuation body [measured 2026-09-13: min-of-3 serial fresh
#: processes; command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=6471fbad35eced5ed6440ebf2c25a053b20221f3].
#: RE-PINNED 2026-09-13, 749122 to 741230 (-7892), Math and Statistics derive
#: their recipes from MeTTa equations; Statistics consolidates finite laws and
#: adds reflective claims. Their collection dependencies share the proper
#: finite expression boundary in lib/_support/collections_data.pl [measured
#: 2026-09-13: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=6fa571d1b7059b610f73e9feed657711414251e5].
#: RE-PINNED 2026-09-13, 741230 to 741252 (+22), Vector, Math and the shared
#: collection boundary declare their native effects. The engine reads late
#: provider declarations and retains definition analysis for computed function
#: heads [measured 2026-09-13: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=1d0b78a359f58de49f2f98bed50a6480d56cd5f6].
#: RE-PINNED 2026-09-14, 741252 to 737251 (-4001), Functional applies finished
#: callback arguments through reduce; Statistics derives exact coefficient rows
#: and Combinatorics retires its native probability provider [measured
#: 2026-09-14: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=e1be99ea1c08f70444c1c35cada441e089777906].
#: RE-PINNED 2026-09-11, 86991 to 87957 (+966), end-of-wave re-pin on the
#: merged tree after FROM's reference rows and four engine units, the closed-
#: set derivations and two host services, BINDING's one native evaluation entry
#: and boot import, W-OBSERVE's observer guard, PERF's receipts batching and
#: cursor retirement, and the three REDS repairs (derived runtime resources and
#: the shared loader, the tool-lane repairs, the corpus example); serial
#: minimum of three fresh processes through the lane's run_twin with
#: file_search_cache_time=9223372036854775807 set before child boot [measured
#: 2026-09-11: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=57f84148ba2684015f052d533f3197eca07b1f7b].
#: RE-PINNED 2026-09-18, 86991 to 90172 (+3181), the branch's landings since
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
#: RE-PINNED 2026-09-18, 90172 to 89557 (-615), the trunk merged (f97c4b0a3,
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
#: RE-PINNED 2026-09-21, 89557 to 738402 (+648845), the sixty libraries derived
#: in MeTTa landed with merge 97763e7fa eight hours after the previous pin
#: 55d451b67, so every example importing one now pays a MeTTa derivation where
#: it paid a Prolog body instead, which the 2026-09-14 ruling accepts
#: explicitly as the price of a library that survives the engine swap [measured
#: 2026-09-21: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=6e09cb25d5495c2db3283166e6ce4e07eefecfb2].
#: RE-PINNED 2026-09-24, 738402 to 742866 (+4464), placed on the full-
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
#: RE-PINNED 2026-09-24, 742866 to 741067 (-1799), 0a81c782f loads a library's
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
#: RE-PINNED 2026-09-24, 741067 to 752584 (+11517), +11,511 at ae1cc8936, where
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
#: RE-PINNED 2026-09-24, 752584 to 752535 (-49), d4a365c16 holds the support
#: graph's visited set and the reference refresh's space sets in SWI tries
#: instead of library(nb_set): a membership check is one foreign call where
#: nb_set probed in Prolog, four inferences a step past a taken slot, from a
#: slot a library space's path-bearing name decided, and a walk over a node or
#: two pays a few inferences more for the trie's setup (-2); gate-perf's
#: d781eab8f carries an exact removal's selected head from the code that
#: selected it, so a withdrawal copies its equation once: 23 inferences fewer
#: for each equation removal the twin adopts and 4 for each it selects (-69);
#: the packages job's 90be572a9 and 4003462fe register Prolog through one
#: engine service: +22 for each library the twin imports (ten new engine
#: predicates and two user imports in the registration walk at two inferences
#: each, less the retired loaded_extension_file/2), and 146 inferences for a
#: Prolog file's origin or 220 for a text's SHA-256 on a twin that registers
#: Prolog (+22); each step read serially on its own committed tree, from gate-
#: perf's pin at c7d7244fb, and the fixed tree 4ff69551e reads what 4003462fe
#: does [measured 2026-09-24: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=4ff69551e0e226442cf7257b96af858adda957a4].
#: RE-PINNED 2026-09-24, 752535 to 752614 (+79), +77 at the change this re-pin
#: lands with, which publishes a from row by itself when rows are all a space
#: owes: its 36 predicates visible to filereader's registration walk cost a
#: batch above twelve names 72 inferences, each restricted space's core about
#: 28 a predicate, and every whole publication and face event its ledger's
#: bookkeeping [measured 2026-09-24: the twins lane alone on 8d651070d with the
#: change before this one and with this change too, one after the other in
#: battery 117's one path, every component at its pin; command=sh
#: tools/check.sh twins (twin_coverage.py inside tools/bounded.sh);
#: commit=e4b7448d1f1bd98733f1b04c3906aaa42f35ef1a].
#: RE-PINNED 2026-09-24, 752614 to 752582 (-32), the host switch of
#: swipl-patched from .2 to .5, the native host of build 9's 36
#: patches, measured .2 against .5 through two environment shims of one shape
#: on one tree. Its channel here is library/prolog_wrap.qlf: .2's, written
#: 2026-09-17 a minute after swi-wrapper-roundtrip-merges-closures changed
#: prolog_wrap.pl, compiles I < Arity in body_closure_args/6 as a call to
#: system:(<)/2, and .5's, recompiled by the build's QLF step, evaluates it
#: inline, so each argument that predicate walks costs one inference fewer.
#: That channel is measured on engine-bench's translate and evaluate cases,
#: whose port profiles on the two hosts differ in system:(<)/2 alone; on this
#: twin it is read from the move's shape, a multiple of 8 to within the lane's
#: deterministic allowance of 4, not profiled [measured 2026-09-24: min-of-3
#: serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=622e425d40c126681c04c7f7f81d92618ab83d0d].
#: RE-PINNED 2026-09-25, 752582 to 752604 (+22), the py-* doors change makes
#: more predicates visible from filereader, and
#: filereader:existing_predicate_arities/2 walks every predicate visible there
#: at two inferences each whenever a source registering more than twelve names
#: loads: on one tree the change's new engine predicates alone, defined with
#: their two boot uses taken out, make eight more visible and move this twin by
#: 16 for each such load, and the whole change by 20, ten more at its loads
#: (i-arity-walk-all-predicates) [measured 2026-09-25T02:50:32+10:00: min-of-3
#: serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-25, 752604 to 748264 (-4340), the host evaluation door
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
#: more than twelve names [measured 2026-09-25T06:46:39+10:00: min-of-3 serial
#: fresh processes; command=python extensions/python/tools/twin_coverage.py
#: --repin].
#: RE-PINNED 2026-09-25, 748264 to 748274 (+10), Runtime.reclaim(), the
#: reclamation barrier metta_py_reclaim/1, adds five predicates to user, and
#: existing_predicate_arities/2 walks every user predicate about twice per
#: large load (i-arity-walk-all-predicates) [measured
#: 2026-09-25T11:25:25+10:00: one full twins lane before this commit and one
#: with it, the two read on one battery path at the landing's HEAD;
#: command=python extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-25, 748274 to 748276 (+2), both specializer doors prepare
#: a specialization's predicate with spaces:metta_prepare_function_predicate/3
#: before asserting its clauses [measured 2026-09-25T11:29:10+10:00: one full
#: twins lane before this commit and one with it, the two read on one battery
#: path at the landing's HEAD; command=python
#: extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-25, 748276 to 748280 (+4), retiring a library importer
#: derives the arity row again from any backing head a library home still
#: registers, journalled to the load that owns it [measured
#: 2026-09-25T11:33:06+10:00: one full twins lane before this commit and one
#: with it, the two read on one battery path at the landing's HEAD;
#: command=python extensions/python/tools/twin_coverage.py].
BUDGET = 748280
#: OVERRUN 2026-09-09, 0 to 242 (+242): the compiled vocabulary seed, the
#: membership index, base-module type lookups and the singleton decoder landed
#: (perf/cross-engine-waivers merged): a Python decode with one named variable
#: builds no index and one with more builds it at the second distinct name,
#: which moves a twin's engine-side cost while its example, which decodes
#: nothing, holds; boot content and clause layout moved the rest; against the
#: trunk's own run at da0e5755d the twin moved +123 and the example +141, and
#: the twin sat 273 over its ceiling there already. Measured 121831 against a
#: ceiling of 121590; a minimal twin costs 110063 against the band's 121590,
#: within that ceiling, so the rest is this twin's own program [measured
#: 2026-09-09: one fresh process per side; command=python
#: extensions/python/benchmarks/probes/twin_floor.py; commit=b4341ae382c48ef225f4a52e566af6a9a71757c4].
#: OVERRUN 2026-09-09, 242 to 3637 (+3395): a library's Prolog half compiles
#: beside itself on its first import and loads from the artifact after
#: (metta_load_source/2, seam:compiled_source/1): the example imports one, so
#: the import's consult and its compile-time expansion left both sides in
#: equal measure and the tenth of it that padded this twin's ceiling left with
#: them, which shows the twin's own excess whole; the lane's authoring
#: constants are re-derived on this tree in the same change; against the run
#: before the compiled halves (b4341ae38) the twin moved -34784 and the
#: example -34708, and the twin sat 1 within its ceiling there. Measured 87047
#: against a ceiling of 87048; a minimal twin costs 75354 against the band's
#: 83411, within that ceiling, so the rest is this twin's own program
#: [measured 2026-09-09: one fresh process per side; command=python
#: extensions/python/benchmarks/probes/twin_floor.py;
#: commit=f26de01fbf3e0e3c64bb691c66a59fa959fee7f3].
