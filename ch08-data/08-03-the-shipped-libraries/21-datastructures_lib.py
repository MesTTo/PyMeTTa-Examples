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
#: /home/user/Dev/swipl-patched from .2 to .5, the native host of build 9's 36
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
#: extensions/python/tools/twin_coverage.py --repin; commit=WORKTREE].
BUDGET = 3139909
