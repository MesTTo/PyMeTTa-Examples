"""Purpose: the sorted map and the priority queue from Python.

Both are VALUES, so each operation answers a new one and the Python name holds
whichever version it was given. A pair is a two-element tuple and a map or a
queue is whatever the library answered, passed straight back.

Guarantees: the same claims as 21-datastructures_lib.metta
[tested: python extensions/python/tools/twin_coverage.py examples/ch08-data/08-03-the-shipped-libraries/21-datastructures_lib.metta; commit=9c9e60542491416e2c5e431a2672bb20f04264fa].
Open Obligations:
  To Do: None
  Hacks: None
  Future Enhancements: None.
"""

from metta import S, V, lib
from metta._errors.errors import MettaError


def twin(m):
    """A sorted map, a priority queue, the functional queue and a finger tree."""
    m += lib.datastructures

    empty_map, put, remove = m.fn["map-empty"], m.fn["map-put"], m.fn["map-remove"]
    get, get_or, has = m.fn["map-get"], m.fn["map-get-or"], m.fn["map-has"]
    keys, values, pairs = m.fn["map-keys"], m.fn["map-values"], m.fn["map-pairs"]
    from_pairs, size = m.fn["map-from-pairs"], m.fn["map-size"]
    smallest, largest = m.fn["map-min"], m.fn["map-max"]

    def refused(call):
        """Whether evaluating a call raises, which is what if-error reads."""
        try:
            list(m.eval(call))
        except MettaError:
            return True
        return False

    def rows(answers):
        """One answer's expression of pairs, as a list of tuples."""
        return [tuple(pair) for pair in answers.one()]

    # Keys compare in the standard order of terms, so the pairs come back sorted
    # however they went in.
    prices = from_pairs(((S.pear, 5), (S.apple, 3), (S.plum, 7))).one()
    assert size(prices) == [3]
    assert list(keys(prices).one()) == [S.apple, S.pear, S.plum]
    assert list(values(prices).one()) == [3, 5, 7]
    assert rows(pairs(prices)) == [(S.apple, 3), (S.pear, 5), (S.plum, 7)]

    # A lookup that finds nothing has NO answer; get-or takes the answer to give.
    assert get(prices, S.pear) == [5]
    assert get(prices, S.durian) == []
    assert get_or(prices, S.durian, 0) == [0]
    assert has(prices, S.apple) == [True]
    assert has(prices, S.durian) == [False]
    assert tuple(smallest(prices).one()) == (S.apple, 3)
    assert tuple(largest(prices).one()) == (S.plum, 7)

    # A put answers a NEW map and leaves the old one alone.
    raised = put(prices, S.pear, 6).one()
    assert rows(pairs(raised)) == [(S.apple, 3), (S.pear, 6), (S.plum, 7)]
    assert rows(pairs(prices)) == [(S.apple, 3), (S.pear, 5), (S.plum, 7)]
    assert rows(pairs(remove(prices, S.pear).one())) == [(S.apple, 3), (S.plum, 7)]
    assert rows(pairs(remove(prices, S.durian).one())) == [
        (S.apple, 3), (S.pear, 5), (S.plum, 7),
    ]
    assert size(empty_map().one()) == [0]
    assert rows(pairs(put(empty_map().one(), S.k, S.v).one())) == [(S.k, S.v)]

    # A key holds one value, so two values for one key is refused where it is
    # written rather than silently keeping the last.
    assert refused(S.map_from_pairs(((S.k, 1), (S.k, 2))))
    assert refused(S.map_get(42, S.k))

    # Priority order retains every inserted occurrence.
    empty_queue, insert = m.fn["pq-empty"], m.fn["pq-insert"]
    queue_min, pop, queue_size = m.fn["pq-min"], m.fn["pq-pop"], m.fn["pq-size"]
    queue_pairs, queue_from = m.fn["pq-pairs"], m.fn["pq-from-pairs"]
    merge, cancel = m.fn["pq-merge"], m.fn["pq-remove"]

    work = queue_from(((3, S.sweep), (1, S.wake), (2, S.boil))).one()
    assert queue_size(work) == [3]
    assert tuple(queue_min(work).one()) == (1, S.wake)
    assert rows(queue_pairs(work)) == [(1, S.wake), (2, S.boil), (3, S.sweep)]

    # Pop decomposes the first entry and remaining queue together.
    priority, value, rest = pop(work).one()
    assert (priority, value) == (1, S.wake)
    assert queue_size(rest) == [2]
    assert rows(queue_pairs(rest)) == [(2, S.boil), (3, S.sweep)]
    assert queue_size(work) == [3]

    # Repeated priorities are kept; merging is one operation over both queues,
    # and removing a named entry cancels it.
    assert queue_size(queue_from(((1, S.a), (1, S.b))).one()) == [2]
    assert rows(queue_pairs(insert(work, 0, S.rise).one())) == [
        (0, S.rise), (1, S.wake), (2, S.boil), (3, S.sweep),
    ]
    assert rows(queue_pairs(merge(work, queue_from(((0, S.rise),)).one()).one())) == [
        (0, S.rise), (1, S.wake), (2, S.boil), (3, S.sweep),
    ]
    assert rows(queue_pairs(cancel(work, 2, S.boil).one())) == [(1, S.wake), (3, S.sweep)]
    assert cancel(work, 2, S.absent) == []
    assert queue_size(empty_queue().one()) == [0]
    assert queue_min(empty_queue().one()) == []
    assert pop(empty_queue().one()) == []
    assert refused(S.pq_size(42))

    # The functional queue that was here before: two lists, amortized constant
    # time at both ends.
    enqueue, dequeue = m.fn.enqueue, m.fn.dequeue
    one = enqueue(1, m.fn["empty-queue"]().one()).one()
    two = enqueue(2, one).one()
    # `cons` builds the expression, so the stored queue reads (queue (2 1) () 2).
    assert two == S.queue((2, 1), (), 2)
    assert dequeue(1, two) == [S.queue((), (2,), 1)]

    # And the finger tree, which is the deque: both ends in amortized constant
    # time and concatenation in O(log n).
    tree, to_list = m.fn["ft-from-list"], m.fn["ft-to-list"]
    assert list(to_list(tree((1, 2, 3)).one()).one()) == [1, 2, 3]
    assert m.fn["ft-front"](tree((1, 2, 3)).one()) == [1]
    assert m.fn["ft-back"](tree((1, 2, 3)).one()) == [3]
    joined = m.fn["ft-concat"](tree((1, 2)).one(), tree((3, 4)).one()).one()
    assert list(to_list(joined).one()) == [1, 2, 3, 4]
    assert m.fn["ft-is-empty"](m.fn["ft-empty"]().one()) == [True]

    assert prices == S.SortedMap(((S.apple, 3), (S.pear, 5), (S.plum, 7)))
    assert m.fn.pairs_lookup(prices[1], S.pear) == [5]
    assert merge() == [empty_queue().one()]
    assert merge(work) == [work]
    assert queue_size(merge(work, work, work).one()) == [9]
    queues = (work, work)
    assert queue_size(merge(*queues).one()) == [6]
    tied = queue_from(((1, S.a), (1, S.b), (1, S.c))).one()
    assert rows(queue_pairs(tied)) == [(1, S.a), (1, S.b), (1, S.c)]
    tied = insert(queue_from(((1, S.a), (1, S.b))).one(), 1, S.c).one()
    assert rows(queue_pairs(tied)) == [(1, S.a), (1, S.b), (1, S.c)]
    repeated = queue_from(((1, S.a), (1, S.a), (2, S.b))).one()
    assert rows(queue_pairs(cancel(repeated, 1, S.a).one())) == [(1, S.a), (2, S.b)]
    assert refused(S.map_from_pairs(S.quote(((V.x, S.a), (V.x, S.b)))))
    assert refused(S.map_from_pairs(S.quote((V.pair,))))
    shared = S.quote(((V.x, S.a), (V.y, S.b)))
    assert get(S.map_from_pairs(shared), V.x) == [S.a]
    literal = S.map_from_pairs(S.quote(((S["+"](1, 2), S.Error(S.data, S.code)),)))
    assert get(literal, S.quote(S["+"](1, 2))) == [S.Error(S.data, S.code)]
    assert refused(S.map_size(empty_queue().one()))
    assert refused(S.pq_size(empty_map().one()))
    choices = S.superpose((((S.a, 1),), ((S.a, 2),)))
    assert get(S.map_from_pairs(choices), S.a) == [1, 2]
    row = m.match(S["="](S.map_remove(V.map, V.key), V.body)).one()
    recipe = m.eval(S["|->"]((row.map, row.key), row.body))[0]
    assert rows(pairs(m.eval((recipe, prices, S.pear))[0])) == [(S.apple, 3), (S.plum, 7)]
    row = m.match(S["="](S.map_remove(prices, V.key), V.body)).one()
    recipe = m.eval(S["|->"]((row.key,), row.body))[0]
    assert rows(pairs(m.eval((recipe, S.plum))[0])) == [(S.apple, 3), (S.pear, 5)]


#: The native 41-claim fixture was pinned at 240981. The derived fixture adds
#: stable ties, variadic merge, literal values and reflection.
#: [measured: 3062103 inferences; command=python
#: extensions/python/tools/twin_coverage.py --measure --rounds 3
#: examples/ch08-data/08-03-the-shipped-libraries/21-datastructures_lib.metta;
#: fixture=59 claims, fresh serial processes after engine/lib QLF purge,
#: MeTTa 3172046; commit=9c9e60542491416e2c5e431a2672bb20f04264fa].
#: RE-PINNED 2026-09-14, 3062103 to 3108074 (+45971), Functional applies
#: finished callback arguments through reduce; Statistics derives exact
#: coefficient rows and Combinatorics retires its native probability provider
#: [measured 2026-09-14: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=e1be99ea1c08f70444c1c35cada441e089777906].
#: RE-PINNED 2026-09-14, 3108074 to 3108080 (+6), Closure publishes the shared
#: rendering and IEEE services, refreshes the callable projection and annotates
#: native protocol domains; every direct and transitive library consumer is
#: measured again [measured 2026-09-14: min-of-3 serial fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=b7866b4d874879ff0cb212eb1c6af60dddaa39c6].
#: RE-PINNED 2026-09-21, 3108080 to 3111872 (+3792), the sixty libraries
#: derived in MeTTa landed with merge 97763e7fa eight hours after the previous
#: pin 55d451b67, so every example importing one now pays a MeTTa derivation
#: where it paid a Prolog body instead, which the 2026-09-14 ruling accepts
#: explicitly as the price of a library that survives the engine swap [measured
#: 2026-09-21: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=6e09cb25d5495c2db3283166e6ce4e07eefecfb2].
#: RE-PINNED 2026-09-24, 3111872 to 3124413 (+12541), placed on the full-
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
#: the 20 commits 6167a0fb2..864c4bac0, where the sweep puts the probes' only
#: step at e1acacad2, which clears a space's import bookkeeping from the module
#: that owns it; da91bc244 confines an exact removal's selection to its own
#: atom: native_retract_one/2 now records the selected clause's head, a
#: clause/3 lookup per exact removal, and checks each removal made while the
#: selector is live against it, a few inferences per removal (+8 on most twins,
#: +24 to +192 on the library twins that withdraw package rows); where a twin's
#: move exceeds these steps, the remainder is drift that stayed inside its band
#: (four inferences, or its own declared allowance) on every other interval
#: [measured 2026-09-24: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=WORKTREE].
#: RE-PINNED 2026-09-24, 3124413 to 3122617 (-1796), 0a81c782f loads a
#: library's Prolog half through the boot's claim (metta_load_source/2 in
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
#: RE-PINNED 2026-09-24, 3122617 to 3122650 (+33), 0847c3d4c decides a platform
#: capability the first time anything reads it, by whether every library its
#: census row names resolves, where only a failed load used to record anything,
#: and 984eabe23 keeps each verdict in a flag decided under a mutex so two
#: threads' first reads agree; the count moves by what the twin's reads now
#: decide, about 660 inferences for a one-library capability and 1,964 for
#: markup's three, and by a few where it reads the census without deciding
#: [measured 2026-09-24: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=d832d20e8edfdad28ad52815757ba9e685ad2de3].
#: RE-PINNED 2026-09-24, 3122650 to 3139945 (+17295), +36 at aaeea643a, whose
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
#: RE-PINNED 2026-09-24, 3139945 to 3139770 (-175), d4a365c16 holds the support
#: graph's visited set and the reference refresh's space sets in SWI tries
#: instead of library(nb_set): a membership check is one foreign call where
#: nb_set probed in Prolog, four inferences a step past a taken slot, from a
#: slot a library space's path-bearing name decided, and a walk over a node or
#: two pays a few inferences more for the trie's setup (-57); gate-perf's
#: d781eab8f carries an exact removal's selected head from the code that
#: selected it, so a withdrawal copies its equation once: 23 inferences fewer
#: for each equation removal the twin adopts and 4 for each it selects (-184);
#: the packages job's 90be572a9 and 4003462fe register Prolog through one
#: engine service: +22 for each library the twin imports (ten new engine
#: predicates and two user imports in the registration walk at two inferences
#: each, less the retired loaded_extension_file/2), and 146 inferences for a
#: Prolog file's origin or 220 for a text's SHA-256 on a twin that registers
#: Prolog (+66); each step read serially on its own committed tree, from gate-
#: perf's pin at c7d7244fb, and the fixed tree 4ff69551e reads what 4003462fe
#: does [measured 2026-09-24: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=4ff69551e0e226442cf7257b96af858adda957a4].
#: RE-PINNED 2026-09-24, 3139770 to 3139776 (+6), +6 at the change this re-pin
#: lands with, which groups a whole reference face's heads in one pass over its
#: sorted entries where each head searched the whole face, and whose three
#: imports into the engine module are one more predicate filereader's
#: registration walk reads above twelve names, pairs_keys/2, and three a
#: restricted space's core steps over as it enumerates that module's predicates
#: [measured 2026-09-24: the twins lane alone on the base 8d651070d and on the
#: base with this change, one after the other in battery 117's one path, every
#: component at its pin; command=sh tools/check.sh twins (twin_coverage.py
#: inside tools/bounded.sh); commit=8bda9d5525a8174a8304376e111df8da258076a9].
#: RE-PINNED 2026-09-24, 3139776 to 3139997 (+221), +221 at the change this re-
#: pin lands with, which publishes a from row by itself when rows are all a
#: space owes: its 36 predicates visible to filereader's registration walk cost
#: a batch above twelve names 72 inferences, each restricted space's core about
#: 28 a predicate, and every whole publication and face event its ledger's
#: bookkeeping [measured 2026-09-24: the twins lane alone on 8d651070d with the
#: change before this one and with this change too, one after the other in
#: battery 117's one path, every component at its pin; command=sh
#: tools/check.sh twins (twin_coverage.py inside tools/bounded.sh);
#: commit=e4b7448d1f1bd98733f1b04c3906aaa42f35ef1a].
#: RE-PINNED 2026-09-24, 3139997 to 3139909 (-88), the host switch of
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
#: RE-PINNED 2026-09-25, 3139909 to 3139915 (+6), the pragma refusal defines
#: require_metta_pragma_capability/2 in the engine module, and on the same tree
#: defining it without calling it moves this twin by the whole of the change's
#: move, so the cost is one more engine predicate and functor met through the
#: engine's walks over its predicate and functor tables, among them
#: filereader:existing_predicate_arities/2, which charges two inferences for
#: each predicate visible from the loading module at every load of a source
#: registering more than twelve names (i-arity-walk-all-predicates); the
#: change's work at a pragma write does not reach this twin [measured
#: 2026-09-25T00:48:04+10:00: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-25, 3139915 to 3139975 (+60), the py-* doors change makes
#: more predicates visible from filereader, and
#: filereader:existing_predicate_arities/2 walks every predicate visible there
#: at two inferences each whenever a source registering more than twelve names
#: loads: on one tree the change's new engine predicates alone, defined with
#: their two boot uses taken out, make eight more visible and move this twin by
#: 16 for each such load, and the whole change by 20, ten more at its loads
#: (i-arity-walk-all-predicates) [measured 2026-09-25T02:51:31+10:00: min-of-3
#: serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-25, 3139975 to 3135288 (-4687), the host evaluation door
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
#: more than twelve names [measured 2026-09-25T06:47:08+10:00: min-of-3 serial
#: fresh processes; command=python extensions/python/tools/twin_coverage.py
#: --repin].
#: RE-PINNED 2026-09-25, 3135288 to 3135318 (+30), Runtime.reclaim(), the
#: reclamation barrier metta_py_reclaim/1, adds five predicates to user, and
#: existing_predicate_arities/2 walks every user predicate about twice per
#: large load (i-arity-walk-all-predicates) [measured
#: 2026-09-25T11:25:25+10:00: one full twins lane before this commit and one
#: with it, the two read on one battery path at the landing's HEAD;
#: command=python extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-25, 3135318 to 3135612 (+294), both specializer doors
#: prepare a specialization's predicate with
#: spaces:metta_prepare_function_predicate/3 before asserting its clauses
#: [measured 2026-09-25T11:29:10+10:00: one full twins lane before this commit
#: and one with it, the two read on one battery path at the landing's HEAD;
#: command=python extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-25, 3135612 to 3135624 (+12), retiring a library importer
#: derives the arity row again from any backing head a library home still
#: registers, journalled to the load that owns it [measured
#: 2026-09-25T11:33:06+10:00: one full twins lane before this commit and one
#: with it, the two read on one battery path at the landing's HEAD;
#: command=python extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-25, 3135624 to 3136279 (+655), every force of a waiting
#: function names the module it is made from, through fun_home_in/3, and a
#: write forces only its own space [measured 2026-09-25T16:54:32+10:00: one
#: full twins lane before this commit and one with it, the two read on one
#: battery path at the landing's HEAD; command=python
#: extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-25, 3136279 to 3107037 (-29242), lambdas are named by
#: their content and a copy restores its source's rows as a program [measured
#: 2026-09-25T17:00:15+10:00: one full twins lane before this commit and one
#: with it, the two read on one battery path at the landing's HEAD;
#: command=python extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-25, 3107037 to 3107044 (+7), engine/source_loading.pl's
#: load-error clause moved from the thread_local user:thread_message_hook/3 to
#: the global user:message_hook/3, so every thread and engine now runs the
#: check the main thread always ran: one inference per message while no load is
#: open there (clause(watching, true, _) fails) and two inside one
#: (load_failure/2 rejects the silent kind); the Python seat prints a twin's
#: library-load messages inside engines, where no clause ran before, and the
#: original's side does not move; +8 of it, and the pin stood 1 above trunk
#: 113c5c928's count at base, 3107036 min-of-3 against the pin 3107037, before
#: this change [measured 2026-09-25T18:45:40+10:00: min-of-3 serial fresh
#: processes; command=python extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-25, 3107044 to 3107050 (+6), a sweep of a module's
#: generated predicates retires the records describing each swept predicate,
#: and a release the rest of the module's [measured 2026-09-25T23:29:52+10:00:
#: one full twins lane before this commit and one with it, the two read on one
#: battery path at the landing's HEAD; command=python
#: extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-26, 3107050 to 3107104 (+54), engine/metta/control.pl's
#: partial/3 to partial/11, the clauses that let a Prolog meta-predicate call a
#: partial function value, are nine more predicates visible from filereader,
#: and filereader:existing_predicate_arities/2's batch walk, which a load
#: registering more than twelve names runs, pays two inferences for each: 18 a
#: batch, the original and the twin alike, and nine inert facts of those
#: arities move it the same [measured 2026-09-26T01:30:32+10:00: min-of-3
#: serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-26, 3107104 to 3107164 (+60), the reference faces of a
#: strongly connected component of from rows are computed together by label-
#: setting, which makes ten more predicates visible from metta_engine, and a
#: control adding only ten unused predicates to metta_engine reads the same, so
#: none of the move is face work; existing_predicate_arities/2 walks every
#: visible predicate at two inferences for each batch of more than twelve names
#: a load registers (i-arity-walk-all-predicates) [measured
#: 2026-09-26T03:08:32+10:00: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-26, 3107164 to 3107175 (+11), this twin reads 3107163 at
#: the base and 3107175 with the change (+12): the change adds
#: metta_reference_enroll/1 and metta_reference_source_bound/5 to the
#: metta_engine module (engine/metta/reference_refresh.pl and
#: reference_sources.pl), and on a tree that defines them and never calls them
#: this twin reads 3107175 (+12), which only a walk over SWI's predicate or
#: atom tables can move, by visiting more entries or visiting them in another
#: order; it read 3107163 against its pin 3107164 at the base, so -1 of the
#: distance is the trunk's own and is not attributed here [measured
#: 2026-09-26T11:17:09+10:00: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-26, 3107175 to 3107191 (+16), Registering a source's names
#: answers each name's Prolog arities in standard order, one msort/2 per
#: registration that adds names, where they came in the procedure table's order
#: and set the order of the arity/2 facts [measured 2026-09-26T12:29:52+10:00:
#: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-26, 3107191 to 3107252 (+61), A Prolog function registered
#: without its arity is claimed from its lowest arity's file through
#: aggregate_all(min(Arity, File), ...), where the scan took the first arity
#: the procedure table answered [measured 2026-09-26T13:03:00+10:00: min-of-3
#: serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-26, 3107252 to 3107270 (+18), The engine module defines
#: three predicates more, builtin_seat_prefixes/1,
#: builtin_implementation_gap/2, validate_builtin_implementation_gaps/2 and
#: builtin_surface_predicate/3 in and builtin_surface_predicate_name/1 out, and
#: a program pays for each predicate visible from the engine wherever it walks
#: them: existing_predicate_arities/2 two inferences a predicate for each load
#: that registers more than twelve names, and a restricted space twenty-seven a
#: predicate when it publishes the engine's core; three facts appended to
#: engine/metta/registration.pl on 07b75d16e move 14-lib_roman_pair_helpers,
#: 02-restricted_spaces and 37-statistics_lib by the same +6, +87 and +30
#: [measured 2026-09-26T14:28:58+10:00: min-of-3 serial fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-26, 3107270 to 3108011 (+741), the specializer substitutes
#: only ground bindings into a specialization's stored row: it tests each
#: binding with ground/1, which SWI calls as a builtin where nonvar/1 compiled
#: inline, and leaves a binding with variables as the row's own parameter
#: instead of substituting it into the body [measured
#: 2026-09-26T18:25:19+10:00: one full twins lane before this commit and one
#: with it, each read in one battery of the landing's HEAD after a QLF purge
#: and one warm-up; command=python extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-27, 3108011 to 3108477 (+466), the host switch to swipl-
#: patched.7 and the seat changes it needs: +65 the host switch to swipl-
#: patched.7, which delivers the heartbeat inside loops, so a held engine ticks
#: and the held goals read its ticks from the raw counter, 9 inferences a tick,
#: and whose three new system predicates ('$heartbeat'/0, '$file_hash'/2,
#: '$qlf_source_changed'/2) filereader's walk of every visible predicate
#: (existing_predicate_arities/2) meets, 2 inferences each; +33 the seat's
#: interrupt poll crossing only on its arming thread, whose hook costs 3
#: inferences a tick more and whose start goal runs on every new thread and
#: engine; +15 the poll's tick record updated in place, 3 inferences a tick
#: more than replacing it; +353 the held goals reading Used through
#: metta_py_work/2, which leaves a held engine's own ticks out and reads the
#: tick term inside its opening edge, 5 inferences a held reading [measured
#: 2026-09-27T03:41:21+10:00: one full twins lane of the trunk and one with
#: this landing, wt-merge battery 1, the trunk on swipl-patched.6 and every
#: part on .7, each through a same-shape host shim; command=python
#: extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-27, 3108477 to 3108824 (+347), a force of a waiting
#: function takes the typing policy and the specializer's lock before
#: translation: spaces:metta_ensure_compiled/2 stabilises the policy and takes
#: the specializer's mutex around the translation once per force, and the
#: translation's own per-pair stabilisation re-enters through
#: with_typing_policy_stable/1's first clause [measured
#: 2026-09-27T09:56:55+10:00: one full twins lane before this commit and one
#: with it, each read in one battery of the landing's HEAD after a QLF purge
#: and one warm-up; command=python extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-27, 3108824 to 3109023 (+199), the constructive negation's
#: engine additions, each counted in this twin's own run: 3 registration walks
#: over more than twelve names (filereader:existing_predicate_arities/2), each
#: now reading 31 more predicates at 2 inferences (+186); 7 == or != on
#: compound terms that differ, each now decided by metta_same_term/3 (+14); 1
#: == or != on a pair holding an unbound variable, each now read through the
#: open-mark test (+7); -8 that the counted mechanisms do not account for
#: [measured 2026-09-27T18:31:56+10:00: one full twins lane with this landing,
#: in a battery of its tree at 775d3cf35, beside one of the base in a battery
#: of 775d3cf35 from 2026-09-27T18:40:06+10:00, which reads the old pin;
#: command=python extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-28, 3109023 to 3109021 (-2), -2 at tsm-licence's notices
#: reader as its block lookahead amended it: engine/host_notices.pl, which
#: every boot loads, opens a component block only where its Component field
#: directly follows the line of 78 '=', the calls not traced; read on swipl-
#: patched.8, the count above on .7, which no longer runs [measured
#: 2026-09-28T12:31:49+10:00: full twins lanes in wt-merge's battery 1 on
#: swipl-patched.8 at this boundary, engine/host_notices.pl as amended against
#: the day before's as first written; command=sh tools/check.sh twins].
#: RE-PINNED 2026-09-27, 3109021 to 3108732 (-289), +2 at the host switch to
#: swipl-patched.8, whose swi-heartbeat-inferences-charged-to-the-program
#: leaves the interrupt poll's own inferences out of every count, so a window
#: the seat's calibrated poll correction read 1 to 3 low on .7 reads exactly;
#: -291 at interrupts B's seat change, which drops the poll's boot calibration,
#: its tick charges and its tick record: a held reading through metta_py_work/2
#: brackets 3 inferences where it bracketed 6, a registration walk over more
#: than twelve names meets 6 fewer seat predicates (12 or 14 fewer), and a
#: thread the twin joins credits it 11 where it credited 16 [measured
#: 2026-09-27T20:07:01+10:00: full twins lanes in wt-merge's battery 1, tsm-
#: licence's series and its engine reader on swipl-patched.7, the series on
#: swipl-patched.8, and the stack through janus-contract B on swipl-patched.8
#: twice; command=sh tools/check.sh twins]. With step 4's notices reader as
#: amended both counts read -2 [measured 2026-09-28T12:34:38+10:00: full twins
#: lanes in wt-merge's battery 1 on swipl-patched.8 at this boundary,
#: engine/host_notices.pl as amended against the day before's as first written;
#: command=sh tools/check.sh twins].
#: RE-PINNED 2026-09-27, 3108732 to 3108738 (+6), +6 at janus-contract A, whose
#: seat loader adds metta_extension_require_patches/3 and the format/3 it
#: imports to the engine module a registration walk enumerates, and reads the
#: seat's requirement into its own module where host_patch/2 used to stand
#: there, so a walk over more than twelve names meets one more predicate at 2
#: inferences [measured 2026-09-27T20:31:29+10:00: full twins lanes on swipl-
#: patched.8 in wt-merge's battery 1, two of the stack through janus-contract B
#: and two with janus-contract A; command=sh tools/check.sh twins]. With step
#: 4's notices reader as amended both counts read -2 [measured
#: 2026-09-28T12:37:38+10:00: full twins lanes in wt-merge's battery 1 on
#: swipl-patched.8 at this boundary, engine/host_notices.pl as amended against
#: the day before's as first written; command=sh tools/check.sh twins].
#: RE-PINNED 2026-09-27, 3108738 to 3073154 (-35584), -35,584 at walk-tax B,
#: which registers a batch's Prolog arities by asking each name, so a
#: registration walk over more than twelve names no longer reads every
#: predicate visible from the loading module at 2 inferences each [measured
#: 2026-09-27T20:38:05+10:00: full twins lanes on swipl-patched.8 in wt-merge's
#: battery 1, two with janus-contract A and two with walk-tax B; command=sh
#: tools/check.sh twins]. With step 4's notices reader as amended both counts
#: read -2 [measured 2026-09-28T12:40:25+10:00: full twins lanes in wt-merge's
#: battery 1 on swipl-patched.8 at this boundary, engine/host_notices.pl as
#: amended against the day before's as first written; command=sh tools/check.sh
#: twins].
#: RE-PINNED 2026-09-29, 3073154 to 3073482 (+328), this twin reads 3073154
#: before the change and 3073482 with the change (+328): each definition
#: through the define doors asks whether its module holds a shadow-import
#: receipt for the name, holds it in flight until the write is visible when it
#: does, and a sweep leaves a receipt another live thread holds: with that use
#: this twin reads 3073482 where the definitions alone read 3073154 (+328)
#: [measured 2026-09-29T06:36:33+10:00: min-of-3 serial fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-29, 3073482 to 3076250 (+2768), this twin reads 3073482
#: before the change and 3076250 with the change (+2768): each definition marks
#: its name as changed and a sweep repairs only the receipts naming a marked
#: name, where it re-checked every receipt the process held: with that use this
#: twin reads 3076250 where the definitions alone read 3073482 (+2768)
#: [measured 2026-09-29T06:43:21+10:00: min-of-3 serial fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-29, 3076250 to 3076267 (+17), this twin reads 3076252
#: before the change and 3076267 with the change (+15): a mark names the module
#: its definition changed in, and a sweep repairs only the receipts held by
#: that module and its declared descendants: with that use this twin reads
#: 3076267 where the definitions alone read 3076252 (+15); it read 3076252
#: against its pin 3076250 before this step, a distance of +2 that is not this
#: step's (the moves since an earlier step of this landing re-pinned it) and is
#: not attributed here [measured 2026-09-29T06:56:25+10:00: min-of-3 serial
#: fresh processes; command=python extensions/python/tools/twin_coverage.py
#: --repin].
#: RE-PINNED 2026-09-29, 3076267 to 3077406 (+1139), this twin reads 3076267
#: before the change and 3077406 with the change (+1139): every operation that
#: registers a name outside a load opens a registration unit, files there the
#: repairs its registrations owe, and drains them once when it finishes, so a
#: caller compiled before the name became a function is repaired: with that use
#: this twin reads 3077406 where the definitions alone read 3076267 (+1139)
#: [measured 2026-09-29T20:22:58+10:00: min-of-3 serial fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-29, 3077406 to 3074606 (-2800), this twin reads 3077406
#: before the change and 3074606 with the change (-2800): a call site forces
#: the function it names before deciding the call's shape, so a call of a
#: waiting function builds the application protocol an eager load builds, and
#: the protocol's marker test around a value the translation already holds is
#: decided at compile time: with that use this twin reads 3074606 where the
#: definitions alone read 3077406 (-2800) [measured 2026-09-29T20:34:55+10:00:
#: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-30, 3074606 to 3047901 (-26705), this twin reads 3074606
#: before the change and 3047901 with the change (-26705): a named space's
#: prelude-tier type readers look the prelude's row up before asking whether it
#: governs there, and builtin_result_type/3 asks whether a program took a
#: builtin over only for a builtin whose result is evaluated
#: (engine/metta/types.pl, engine/translator/lowering.pl), so a lookup of a
#: name the prelude does not declare costs one indexed miss and no ownership
#: probe [measured 2026-09-30T04:16:54+10:00: min-of-3 serial fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --repin].
BUDGET = 3047901
