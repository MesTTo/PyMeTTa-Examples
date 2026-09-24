"""Purpose: the functional and iteration utilities from Python.

Beside them are lib_patrick's four idioms, which this library grew out of.

A collection is a tuple, a function argument is the symbol of a defined
function or a written lambda, and a held body is a written expression, so each
claim reads as its MeTTa twin does with the parentheses moved. The loop with
state keeps its counter in a named space, whose handle crosses into the two
compiled helpers as the argument it is; `odd?` keeps its question mark through
the explicit `name=`, because no Python identifier can spell it, and the three
helpers take their arithmetic and comparisons by the engine's words, `fn.mul`,
`fn.mod`, `fn.eq` and `fn.gt`, where Python's own operators on an unannotated
parameter would cross to the host once per element.

Guarantees: the same claims as 22-functional_lib.metta
[tested: python extensions/python/tools/twin_coverage.py examples/ch08-data/08-03-the-shipped-libraries/22-functional_lib.metta; commit=6471fbad35eced5ed6440ebf2c25a053b20221f3].
Open Obligations:
  To Do: None
  Hacks: None
  Future Enhancements: None.
"""

import metta
from metta import FALSE, TRUE, Expression, G, S, V, fn, if_, lib, match
from metta._errors.errors import MettaError


def twin(m):
    """Zip, slice, flatten, partition, group, sort, scan, unfold, pipe and loop."""
    m += lib.functional
    # lib_unicode is imported for one claim below, whose test is a head the
    # library declares deterministic: that is the case a verdict has to be read
    # rather than asked for.
    m += lib.unicode

    # The three helpers take their arithmetic and comparisons by the engine's
    # WORDS, so each body is the MeTTa form it stands for rather than a host
    # operator crossing once per element.
    @m.define
    def double(x):
        return fn.mul(2, x)

    @m.define(name="odd?")
    def odd(x):
        return fn.eq(1, fn.mod(x, 2))  # engine equality is intentional

    @m.define
    def grade(score):
        return S["pass"] if fn.gt(score, 50) else S.fail

    def refused(call):
        """Whether evaluating a call raises, which is what if-error reads."""
        try:
            list(m.eval(call))
        except MettaError:
            return True
        return False

    def rows(answers):
        """One answer's expression of expressions, as a list of tuples."""
        return [tuple(row) for row in answers.one()]

    # `zip` pairs corresponding elements and stops at the shorter collection, so
    # a long one zipped with a short one is the short one's length. `unzip`
    # inverts it.
    assert rows(m.fn.zip((1, 2, 3), (S.a, S.b, S.c))) == [(1, S.a), (2, S.b), (3, S.c)]
    assert rows(m.fn.zip((1, 2, 3), (S.a, S.b))) == [(1, S.a), (2, S.b)]
    assert list(m.fn.zip((), (S.a,)).one()) == []
    assert rows(m.fn.unzip(((1, S.a), (2, S.b)))) == [(1, 2), (S.a, S.b)]
    assert rows(m.fn.unzip(m.fn.zip((1, 2), (S.a, S.b)).one())) == [(1, 2), (S.a, S.b)]
    assert refused(S.unzip((1,)))

    # `drop` is the suffix. The PREFIX is lib_combinatorics' `takeK`, so this
    # library adds no second spelling of it.
    assert list(m.fn.drop((1, 2, 3, 4), 2).one()) == [3, 4]
    assert list(m.fn.drop((1, 2), 5).one()) == []
    assert list(m.fn.drop((1, 2), 0).one()) == [1, 2]

    # `chunk` cuts a collection into pieces, the last one short when the size
    # does not divide the length. `window` slides instead of cutting, so
    # consecutive windows overlap by all but one element.
    assert rows(m.fn.chunk((1, 2, 3, 4, 5), 2)) == [(1, 2), (3, 4), (5,)]
    assert rows(m.fn.chunk((1, 2, 3, 4), 2)) == [(1, 2), (3, 4)]
    assert list(m.fn.chunk((), 2).one()) == []
    assert rows(m.fn.window((1, 2, 3, 4), 2)) == [(1, 2), (2, 3), (3, 4)]
    assert rows(m.fn.window((1, 2, 3), 3)) == [(1, 2, 3)]
    assert list(m.fn.window((1, 2), 3).one()) == []
    assert refused(S.chunk((1, 2), 0))
    assert refused(S.window((1, 2), 0))

    # `flatten-once` removes ONE level of nesting and `flatten-deep` removes
    # every one, which is the difference between concatenating and collecting
    # the leaves. Both say the depth in the name, because the bare name
    # `flatten` is the host Prolog's own every-level flatten and the library
    # leaves it alone.
    assert list(m.fn.flatten_once(((1, 2), (3,), (), 4)).one()) == [1, 2, 3, 4]
    # An inner collection's own nesting is data one level does not touch.
    assert list(m.fn.flatten_once((((1, (2,)),), 3)).one()) == [Expression((1, Expression((2,)))), 3]
    assert list(m.fn.flatten_deep(((1, (2, (3,))), 4)).one()) == [1, 2, 3, 4]
    assert list(m.fn.flatten_deep((((),),)).one()) == []

    # `partition` splits on a test and loses nothing: whatever the test does not
    # answer True for lands in the second side.
    assert rows(m.fn.partition(S["odd?"], (1, 2, 3, 4))) == [(1, 3), (2, 4)]
    assert rows(m.fn.partition(S["odd?"], ())) == [(), ()]
    assert rows(m.fn.partition(S["|->"]((V.x,), S.gt(V.x, 10)), (1, 2))) == [(), (1, 2)]
    # The test's verdict is READ and compared, never threaded into the call as an
    # expected answer, so a test whose own head is declared deterministic answers
    # False rather than failing: this one is lib_unicode's, over one-character
    # strings.
    assert rows(m.fn.partition(S["|->"]((V.c,), S.unicode_is(V.c, S.letter)),
                               (G("a"), G("1")))) == [(G("a"),), (G("1"),)]

    # `group-by` gathers by what a key function answers, keys in
    # first-appearance order and members in the collection's order, so grouping
    # needs no sort.
    assert rows(m.fn.group_by(S["odd?"], (1, 2, 3, 4))) == [(True, Expression((1, 3))), (False, Expression((2, 4)))]
    assert rows(m.fn.group_by(S.grade, (80, 20, 90))) == [(S["pass"], Expression((80, 90))), (S.fail, Expression((20,)))]
    assert list(m.fn.group_by(S["odd?"], ()).one()) == []

    # `sort-by` orders by the key and is STABLE, so equal keys keep their order.
    assert list(m.fn.sort_by(S.double, (3, 1, 2)).one()) == [1, 2, 3]
    second = S["|->"]((V.p,), S.index_atom(V.p, 1))
    assert rows(m.fn.sort_by(second, ((S.b, 1), (S.a, 1), (S.c, 0)))) == [(S.c, 0), (S.b, 1), (S.a, 1)]

    # `scan` is a fold that answers its running results, so a prefix sum is scan
    # with +. The answer is one longer than the input, because the start is
    # first.
    assert list(m.fn.scan(S["+"], 0, (1, 2, 3)).one()) == [0, 1, 3, 6]
    assert list(m.fn.scan(S["+"], 0, ()).one()) == [0]
    consing = S["|->"]((V.acc, V.x), S.cons_atom(V.x, V.acc))
    assert rows(m.fn.scan(consing, (), (1, 2))) == [(), (1,), (2, 1)]

    # `unfold` is the opposite of a fold: a seed grows into a collection while
    # the step answers (Value NextSeed), and stops when it answers nothing.
    counting = S["|->"]((V.n,), if_(S.lt(V.n, 4), Expression((V.n, V.n + 1)), S.empty()))
    assert list(m.fn.unfold(counting, 1).one()) == [1, 2, 3]
    assert list(m.fn.unfold(S["|->"]((V.n,), S.empty()), 1).one()) == []

    # `pipe` applies functions left to right, which is the reading order;
    # lib_patrick's `compose` applies them right to left, the mathematical
    # order. The collection of functions is HELD, so it is not read as a call.
    assert m.fn.pipe((S.double, S.double), 3) == [12]
    assert m.fn.pipe((), 3) == [3]
    assert m.fn.pipe((S.double, S["odd?"]), 3) == [False]

    # `apply-to` turns a collection of arguments into a call, which is what a
    # fold over a variable number of arguments needs.
    assert m.fn.apply_to(S["+"], (1, 2)) == [3]
    assert m.fn.apply_to(S.double, (5,)) == [10]

    # The three control forms hold their body: `repeat` runs it a fixed number
    # of times, `while` runs it until its condition stops answering True, and
    # `unless` runs it when the condition answers False.
    assert list(m.fn.repeat(3, S["+"](3, 4))) == [7, 7, 7]
    assert list(m.fn.repeat(0, S["+"](3, 4))) == []
    # The condition is MeTTa's own Bool atom where it is written as a literal:
    # a Python bool would be a host value crossing into a held parameter.
    assert list(m.fn.unless(FALSE, S["+"](1, 1))) == [2]
    assert list(m.fn.unless(TRUE, S["+"](1, 1))) == []
    assert list(m.fn["while"](FALSE, S.never)) == []

    # A while loop with state: the counter lives in the space, the condition
    # reads it and the body advances it, so the loop ends when the space says
    # so. Held parameters are what make this work: an evaluated body would run
    # once.
    counter = metta.space(S.ticks)
    counter += S.count(0)

    @m.define
    def ticks():
        # (= (ticks) (car-atom (collapse (match &ticks (count $n) $n))))
        return fn.car_atom(S.collapse(match(counter, S.count(V.n), V.n)))  # rung: `collapse` is list(), which a compiled body has no lowering for (P14.4)

    @m.define
    def tick():
        # (= (tick) (let $now (ticks) (let $gone (remove-atom &ticks (count $now))
        #             (let $next (+ $now 1) (let $added (add-atom &ticks (count $next)) $next)))))
        now = ticks()
        _gone = fn.remove_atom(counter, S.count(now))
        after = fn.add(now, 1)
        _added = fn.add_atom(counter, S.count(after))
        return after

    assert list(m.fn["while"](S.lt(S.ticks(), 3), S.tick())) == [1, 2, 3]
    assert m.fn.ticks() == [3]

    # And lib_patrick's own four, unchanged, from their own library.
    m += lib.patrick
    assert m.fn.compose((S.double, S.double), (3,)) == [12]
    # The same composition written both ways: double then odd? left to right is
    # odd? after double right to left, and 6 is even either way.
    assert m.fn.compose((S["odd?"], S.double), (3,)) == [False]
    assert m.fn["@"](V.x, S["+"](1, 2)) == [3]
    assert m.fn["for"](V.x, (1, 2, 3), V.x * 10) == [10, 20, 30]
    step = S["|->"](Expression((V.i, V.s)), V.s + V.i)
    assert m.fn.iterate(0, 3, 0, step) == [3]

    @m.define
    def branch_add(a, b):
        yield fn.add(a, b)
        yield fn.add(1, fn.add(a, b))

    @m.define
    def branch_key(x):
        yield fn.mod(x, 2)
        yield fn.add(2, fn.mod(x, 2))

    @m.define
    def branch_step(seed):
        yield (seed, fn.add(seed, 1)) if fn.lt(seed, 2) else fn.empty()
        yield (fn.add(seed, 10), fn.add(seed, 1)) if fn.lt(seed, 2) else fn.empty()

    @m.define
    def increment_function():
        yield lambda x: fn.add(x, 1)
        yield lambda x: fn.add(x, 2)

    assert list(m.fn.scan(S.branch_add, 0, (1, 2))) == [
        (0, 1, 3), (0, 1, 4), (0, 2, 4), (0, 2, 5),
    ]
    assert list(m.fn.unfold(S.branch_step, 0)) == [(0, 1), (0, 11), (10, 1), (10, 11)]
    assert list(m.fn.group_by(S.branch_key, (0, 1))) == [
        ((0, (0,)), (1, (1,))), ((0, (0,)), (3, (1,))),
        ((2, (0,)), (1, (1,))), ((2, (0,)), (3, (1,))),
    ]
    assert list(m.fn.pipe((S.increment_function(), S.increment_function()), 0)) == [2, 3, 3, 4]
    assert list(m.fn.apply_to(S.increment_function(), (1,))) == [2, 3]
    both = S["|->"]((V.x,), S.superpose((FALSE, TRUE)))
    none = S["|->"]((V.x,), S.empty())
    assert rows(m.fn.partition(both, (1, 2))) == [(1, 2), ()]
    assert rows(m.fn.partition(none, (1, 2))) == [(), (1, 2)]
    assert list(m.fn.scan(S["|->"]((V.a, V.b), S.empty()), 0, (1,))) == []
    malformed = S["|->"]((V.n,), if_(S.eq(V.n, 0), (1, 2, 3), S.empty()))
    assert refused(S.unfold(malformed, 0))

    arithmetic, error_data = S["+"](1, 2), S.Error(S.a, S.b)
    literal = (arithmetic, error_data)
    assert rows(m.fn.zip(S.quote(literal), (S.a, S.b))) == [
        (arithmetic, S.a), (error_data, S.b),
    ]
    assert rows(m.fn.unzip(S.quote(((S["+"], S.a), (S.Error, S.b))))) == [
        (S["+"], S.Error), (S.a, S.b),
    ]
    assert list(m.fn.flatten_once(S.quote(((arithmetic,), error_data))).one()) == [
        arithmetic, S.Error, S.a, S.b,
    ]
    assert list(m.fn.flatten_deep(S.quote(((arithmetic,), error_data))).one()) == [
        S["+"], 1, 2, S.Error, S.a, S.b,
    ]
    expression = S["|->"]((V.x,), S.eq(S.get_metatype(V.x), S.Expression))
    assert rows(m.fn.partition(expression, S.quote((*literal, 3)))) == [literal, (3,)]
    metatype = S["|->"]((V.x,), S.get_metatype(V.x))
    assert m.fn.group_by(metatype, S.quote(literal)) == [((S.Expression, literal),)]
    constant = S["|->"]((V.x,), 0)
    assert m.fn.sort_by(constant, S.quote(literal)) == [literal]
    item = S["|->"]((V.acc, V.item), S.quote(V.item))
    assert m.fn.scan(item, S.a, S.quote(literal)) == [(S.a, *literal)]
    assert rows(m.fn.chunk(S.quote(literal), 1)) == [(arithmetic,), (error_data,)]
    assert rows(m.fn.window(S.quote(literal), 2)) == [literal]
    identity = S["|->"]((V.data,), S.quote(V.data))
    assert m.fn.apply_to(identity, S.quote((arithmetic,))) == [arithmetic]
    assert m.fn.pipe((identity,), S.quote(arithmetic)) == [arithmetic]


#: MEASURED on this branch rather than inherited: this twin is new, so there is
#: no earlier pin to move. The 51 claims cover the fourteen registered heads,
#: the three held control forms and lib_patrick's four idioms; the example pays
#: 127,108 inferences for the same work, and the twin's surplus is the three
#: compiled helpers and the loop's two, each a definition the example writes
#: as an equation and the twin compiles from a Python body
#: [measured 2026-09-12: 135975 inferences, minimum of three serial fresh
#: processes; command=python extensions/python/tools/twin_coverage.py --measure
#: --rounds 3 examples/ch08-data/08-03-the-shipped-libraries/22-functional_lib.metta;
#: fixture=lib_functional at its functional commit, artifacts purged before
#: the run; commit=a2a80061cd8264d8f714b14c76b94d00f44a0755].
#: RE-PINNED 2026-09-12, 135975 to 134567 (-1408), lib_patrick keeps its own
#: four idioms and does not import this library, so the example asks for both
#: halves itself and pays the second import once [measured 2026-09-12: min-of-3
#: serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=a2a80061cd8264d8f714b14c76b94d00f44a0755].
#: RE-PINNED 2026-09-12, 134567 to 151546 (+16979), the partition claim that
#: reads its test's verdict rather than threading an expected answer, and the
#: lib_unicode import it needs [measured 2026-09-12: min-of-3 serial fresh
#: processes; command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=b2a180eace9ff7e51677b1a40a8d6374ee05972b].
#: RE-PINNED 2026-09-13, 151546 to 1091943: collection operations now compose
#: MeTTa matching, folds and application; segment continuations are protected
#: compiler helpers. The example measures 1074085 for the same claims
#: [measured: 1091943 inferences; command=python extensions/python/tools/twin_coverage.py --measure --rounds 3 examples/ch08-data/08-03-the-shipped-libraries/22-functional_lib.metta;
#: fixture=minimum of three serial fresh processes after purging engine/lib QLF;
#: commit=6471fbad35eced5ed6440ebf2c25a053b20221f3].
#: RE-PINNED 2026-09-13, 1091943 to 1093280 (+1337), The validated range
#: continuation now lives in the private support file rather than appearing as
#: a public library head. The import adds its measured loading cost without
#: changing the continuation body [measured 2026-09-13: min-of-3 serial fresh
#: processes; command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=6471fbad35eced5ed6440ebf2c25a053b20221f3].
#: RE-PINNED 2026-09-13, 1093280 to 1093245 (-35), Math and Statistics derive
#: their recipes from MeTTa equations; Statistics consolidates finite laws and
#: adds reflective claims. Their collection dependencies share the proper
#: finite expression boundary in lib/_support/collections_data.pl [measured
#: 2026-09-13: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=6fa571d1b7059b610f73e9feed657711414251e5].
#: RE-PINNED 2026-09-13, 1093245 to 1093269 (+24), Vector, Math and the shared
#: collection boundary declare their native effects. The engine reads late
#: provider declarations and retains definition analysis for computed function
#: heads [measured 2026-09-13: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=1d0b78a359f58de49f2f98bed50a6480d56cd5f6].
#: RE-PINNED 2026-09-14, 1093269 to 1189061 (+95792), Functional applies
#: finished callback arguments through reduce; Statistics derives exact
#: coefficient rows and Combinatorics retires its native probability provider
#: [measured 2026-09-14: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=e1be99ea1c08f70444c1c35cada441e089777906].
#: RE-PINNED 2026-09-21, 1189061 to 1189601 (+540), the sixty libraries derived
#: in MeTTa landed with merge 97763e7fa eight hours after the previous pin
#: 55d451b67, so every example importing one now pays a MeTTa derivation where
#: it paid a Prolog body instead, which the 2026-09-14 ruling accepts
#: explicitly as the price of a library that survives the engine swap [measured
#: 2026-09-21: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=6e09cb25d5495c2db3283166e6ce4e07eefecfb2].
#: RE-PINNED 2026-09-24, 1189601 to 1201254 (+11653), placed on the full-
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
#: RE-PINNED 2026-09-24, 1201254 to 1180440 (-20814), 0a81c782f loads a
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
#: RE-PINNED 2026-09-24, 1180440 to 1181115 (+675), 0847c3d4c decides a
#: platform capability the first time anything reads it, by whether every
#: library its census row names resolves, where only a failed load used to
#: record anything, and 984eabe23 keeps each verdict in a flag decided under a
#: mutex so two threads' first reads agree; the count moves by what the twin's
#: reads now decide, about 660 inferences for a one-library capability and
#: 1,964 for markup's three, and by a few where it reads the census without
#: deciding [measured 2026-09-24: min-of-3 serial fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=d832d20e8edfdad28ad52815757ba9e685ad2de3].
#: RE-PINNED 2026-09-24, 1181115 to 1204238 (+23123), +23,111 at ae1cc8936,
#: where a registration batch of thirteen names or more walks the visible
#: predicate table at two inferences a predicate that asking per name spent
#: inside one C call, and a batch above forty tests each predicate with a dict
#: at one inference fewer than the AVL; +12 at b5eb39acd, whose three new
#: engine exports the registration walk above twelve names reads at two
#: inferences each [measured 2026-09-24: min-of-3 serial fresh processes at
#: HEAD in battery 118 holding the committed tree alone (BATTERY_KEEP='',
#: 11:56); each step read with its parent and child in turn in battery 115
#: (10:42 to 11:18), 117 (11:01 to 12:10) or 120 (12:04 to 12:13) from
#: committed trees or this job's patched copies of them, none from a working
#: tree; 850d2a660's and 0f6d29ba6's split from provider-carry's own pairs,
#: aaeea643a's on the ladder before 10:05; command=python
#: extensions/python/tools/twin_coverage.py --measure --rounds 3;
#: commit=c7d7244fbe6d32d024ca8c61b336008e98b156ef].
#: RE-PINNED 2026-09-24, 1204238 to 1203546 (-692), d4a365c16 holds the support
#: graph's visited set and the reference refresh's space sets in SWI tries
#: instead of library(nb_set): a membership check is one foreign call where
#: nb_set probed in Prolog, four inferences a step past a taken slot, from a
#: slot a library space's path-bearing name decided, and a walk over a node or
#: two pays a few inferences more for the trie's setup (-552); gate-perf's
#: d781eab8f carries an exact removal's selected head from the code that
#: selected it, so a withdrawal copies its equation once: 23 inferences fewer
#: for each equation removal the twin adopts and 4 for each it selects (-184);
#: the packages job's 90be572a9 and 4003462fe register Prolog through one
#: engine service: +22 for each library the twin imports (ten new engine
#: predicates and two user imports in the registration walk at two inferences
#: each, less the retired loaded_extension_file/2), and 146 inferences for a
#: Prolog file's origin or 220 for a text's SHA-256 on a twin that registers
#: Prolog (+44); each step read serially on its own committed tree, from gate-
#: perf's pin at c7d7244fb, and the fixed tree 4ff69551e reads what 4003462fe
#: does [measured 2026-09-24: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=4ff69551e0e226442cf7257b96af858adda957a4].
#: RE-PINNED 2026-09-24, 1203546 to 1203723 (+177), +173 at the change this re-
#: pin lands with, which publishes a from row by itself when rows are all a
#: space owes: its 36 predicates visible to filereader's registration walk cost
#: a batch above twelve names 72 inferences, each restricted space's core about
#: 28 a predicate, and every whole publication and face event its ledger's
#: bookkeeping [measured 2026-09-24: the twins lane alone on 8d651070d with the
#: change before this one and with this change too, one after the other in
#: battery 117's one path, every component at its pin; command=sh
#: tools/check.sh twins (twin_coverage.py inside tools/bounded.sh);
#: commit=e4b7448d1f1bd98733f1b04c3906aaa42f35ef1a].
#: RE-PINNED 2026-09-24, 1203723 to 1203683 (-40), the host switch of
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
#: extensions/python/tools/twin_coverage.py --repin; commit=622e425d40c126681c04c7f7f81d92618ab83d0d].
BUDGET = 1203683

#: DIVERGED 2026-09-12, the example holds 1 atom the twin does not (1 =) and
#: the twin holds 1 atom the example does not (1 =): the loop's tick helper is
#: a sequence of four Python statements, which compile to four nested one-
#: binding let* forms where the example writes four nested let forms; the
#: bindings, the effects and the answer are the same [measured 2026-09-12: the
#: two stored-atom surpluses, one fresh process per side; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=a2a80061cd8264d8f714b14c76b94d00f44a0755].
#: DIVERGED 2026-09-13, the example holds 5 atoms the twin does not (2 :, 3 =)
#: and the twin holds 5 atoms the example does not (2 :, 3 =): The tick helper
#: still compiles Python assignments to nested let* while the example writes
#: nested let. The two Python lambda bodies yielded by increment_function
#: consume two generated names before later calls, shifting the otherwise
#: identical partition and unfold specializations from lambda_67 and lambda_66
#: to lambda_69 and lambda_68; the branch and literal claims verify both paths
#: [measured 2026-09-13: the two stored-atom surpluses, one fresh process per
#: side; command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=6471fbad35eced5ed6440ebf2c25a053b20221f3].
#: DIVERGED 2026-09-14, the example holds 3 atoms the twin does not (1 :, 2 =)
#: and the twin holds 3 atoms the example does not (1 :, 2 =): the existing tick
#: helper still lowers through let versus let*. The existing unfold
#: specialization now calls apply-to; its two otherwise identical atoms name
#: lambda_63 in the example and lambda_65 after Python's two generated lambdas
#: [measured 2026-09-14: the two stored-atom surpluses, one fresh process per
#: side; command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=e1be99ea1c08f70444c1c35cada441e089777906].
#: DIVERGED 2026-09-21, the example holds 5 atoms the twin does not (1 :, 4 =)
#: and the twin holds 7 atoms the example does not (1 :, 4 =, 2 @python-
#: callable): the sixty libraries derived in MeTTa landed with merge 97763e7fa
#: eight hours after the previous pin 55d451b67, so every example importing one
#: now pays a MeTTa derivation where it paid a Prolog body instead, which the
#: 2026-09-14 ruling accepts explicitly as the price of a library that survives
#: the engine swap [measured 2026-09-21: the two stored-atom surpluses, one
#: fresh process per side; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=6e09cb25d5495c2db3283166e6ce4e07eefecfb2].
DIVERGENCE = "c7b14f8f47ab37b73864d216e444ba5e6354e2f12eafe15f00c190c1962daf2f"
