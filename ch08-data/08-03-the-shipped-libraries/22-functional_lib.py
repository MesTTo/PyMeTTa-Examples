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
#: RE-PINNED 2026-09-25, 1203683 to 1203728 (+45), the py-* doors change makes
#: more predicates visible from filereader, and
#: filereader:existing_predicate_arities/2 walks every predicate visible there
#: at two inferences each whenever a source registering more than twelve names
#: loads: on one tree the change's new engine predicates alone, defined with
#: their two boot uses taken out, move this twin by 16 for each such load and
#: the whole change by 20, each give or take one or two inferences that move
#: with where the new names land in SWI's tables and that SWI's profiler, which
#: lists no system predicate, does not place (i-arity-walk-all-predicates)
#: [measured 2026-09-25T02:56:19+10:00: min-of-3 serial fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-25, 1203728 to 1203712 (-16), the registration refusal
#: kind makes the (vocabulary refusal-kind ...) catalog row fifteen members
#: long instead of fourteen, which moves it from storage arity 17 to 18, where
#: the Python seat's (vocabulary door-answers ...) already sits, so &metta
#: keeps one storage arity fewer and each open-tail catalog lookup,
#: metta_catalog_clause/2 visiting every arity, costs five inferences less; and
#: metta_host_signal_message//2 is one more predicate the engine module
#: defines, which every walk over the engine's predicates pays: filereader's
#: existing_predicate_arities/2 two inferences a registration of more than
#: twelve names, each restricted space's core 29, and 11-reference_rows' walk
#: 240, each reproduced exactly by one inert predicate added to the engine on
#: the base [measured 2026-09-25T06:28:58+10:00: min-of-3 serial fresh
#: processes; command=python extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-25, 1203712 to 1198987 (-4725), the host evaluation door
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
#: more than twelve names [measured 2026-09-25T06:47:11+10:00: min-of-3 serial
#: fresh processes; command=python extensions/python/tools/twin_coverage.py
#: --repin].
#: RE-PINNED 2026-09-25, 1198987 to 1199007 (+20), Runtime.reclaim(), the
#: reclamation barrier metta_py_reclaim/1, adds five predicates to user, and
#: existing_predicate_arities/2 walks every user predicate about twice per
#: large load (i-arity-walk-all-predicates) [measured
#: 2026-09-25T11:25:25+10:00: one full twins lane before this commit and one
#: with it, the two read on one battery path at the landing's HEAD;
#: command=python extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-25, 1199007 to 1199179 (+172), both specializer doors
#: prepare a specialization's predicate with
#: spaces:metta_prepare_function_predicate/3 before asserting its clauses
#: [measured 2026-09-25T11:29:10+10:00: one full twins lane before this commit
#: and one with it, the two read on one battery path at the landing's HEAD;
#: command=python extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-25, 1199179 to 1199187 (+8), retiring a library importer
#: derives the arity row again from any backing head a library home still
#: registers, journalled to the load that owns it [measured
#: 2026-09-25T11:33:06+10:00: one full twins lane before this commit and one
#: with it, the two read on one battery path at the landing's HEAD;
#: command=python extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-25, 1199187 to 1199541 (+354), every force of a waiting
#: function names the module it is made from, through fun_home_in/3, and a
#: write forces only its own space [measured 2026-09-25T16:54:32+10:00: one
#: full twins lane before this commit and one with it, the two read on one
#: battery path at the landing's HEAD; command=python
#: extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-25, 1199541 to 1080157 (-119384), lambdas are named by
#: their content and a copy restores its source's rows as a program [measured
#: 2026-09-25T17:00:15+10:00: one full twins lane before this commit and one
#: with it, the two read on one battery path at the landing's HEAD;
#: command=python extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-25, 1080157 to 1080173 (+16), engine/source_loading.pl's
#: load-error clause moved from the thread_local user:thread_message_hook/3 to
#: the global user:message_hook/3, so every thread and engine now runs the
#: check the main thread always ran: one inference per message while no load is
#: open there (clause(watching, true, _) fails) and two inside one
#: (load_failure/2 rejects the silent kind); the Python seat prints a twin's
#: library-load messages inside engines, where no clause ran before, and the
#: original's side does not move [measured 2026-09-25T18:42:04+10:00: min-of-3
#: serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-25, 1080173 to 1080177 (+4), a sweep of a module's
#: generated predicates retires the records describing each swept predicate,
#: and a release the rest of the module's [measured 2026-09-25T23:29:52+10:00:
#: one full twins lane before this commit and one with it, the two read on one
#: battery path at the landing's HEAD; command=python
#: extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-26, 1080177 to 1080213 (+36), engine/metta/control.pl's
#: partial/3 to partial/11, the clauses that let a Prolog meta-predicate call a
#: partial function value, are nine more predicates visible from filereader,
#: and filereader:existing_predicate_arities/2's batch walk, which a load
#: registering more than twelve names runs, pays two inferences for each: 18 a
#: batch, the original and the twin alike, and nine inert facts of those
#: arities move it the same [measured 2026-09-26T01:30:35+10:00: min-of-3
#: serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-26, 1080213 to 1080253 (+40), the reference faces of a
#: strongly connected component of from rows are computed together by label-
#: setting, which makes ten more predicates visible from metta_engine, and a
#: control adding only ten unused predicates to metta_engine reads the same, so
#: none of the move is face work; existing_predicate_arities/2 walks every
#: visible predicate at two inferences for each batch of more than twelve names
#: a load registers (i-arity-walk-all-predicates) [measured
#: 2026-09-26T03:08:36+10:00: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-26, 1080253 to 1080263 (+10), this twin reads 1080255 at
#: the base and 1080263 with the change (+8): the change adds
#: metta_reference_enroll/1 and metta_reference_source_bound/5 to the
#: metta_engine module (engine/metta/reference_refresh.pl and
#: reference_sources.pl), and on a tree that defines them and never calls them
#: this twin reads 1080263 (+8), which only a walk over SWI's predicate or atom
#: tables can move, by visiting more entries or visiting them in another order;
#: it read 1080255 against its pin 1080253 at the base, so +2 of the distance
#: is the trunk's own and is not attributed here [measured
#: 2026-09-26T11:17:17+10:00: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-26, 1080263 to 1080277 (+14), Registering a source's names
#: answers each name's Prolog arities in standard order, one msort/2 per
#: registration that adds names, where they came in the procedure table's order
#: and set the order of the arity/2 facts [measured 2026-09-26T12:29:55+10:00:
#: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-26, 1080277 to 1080338 (+61), A Prolog function registered
#: without its arity is claimed from its lowest arity's file through
#: aggregate_all(min(Arity, File), ...), where the scan took the first arity
#: the procedure table answered [measured 2026-09-26T13:03:04+10:00: min-of-3
#: serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-26, 1080338 to 1080350 (+12), The engine module defines
#: three predicates more, builtin_seat_prefixes/1,
#: builtin_implementation_gap/2, validate_builtin_implementation_gaps/2 and
#: builtin_surface_predicate/3 in and builtin_surface_predicate_name/1 out, and
#: a program pays for each predicate visible from the engine wherever it walks
#: them: existing_predicate_arities/2 two inferences a predicate for each load
#: that registers more than twelve names, and a restricted space twenty-seven a
#: predicate when it publishes the engine's core; three facts appended to
#: engine/metta/registration.pl on 07b75d16e move 14-lib_roman_pair_helpers,
#: 02-restricted_spaces and 37-statistics_lib by the same +6, +87 and +30
#: [measured 2026-09-26T14:29:03+10:00: min-of-3 serial fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-26, 1080350 to 1080231 (-119), the specializer substitutes
#: only ground bindings into a specialization's stored row: it tests each
#: binding with ground/1, which SWI calls as a builtin where nonvar/1 compiled
#: inline, and leaves a binding with variables as the row's own parameter
#: instead of substituting it into the body [measured
#: 2026-09-26T18:25:19+10:00: one full twins lane before this commit and one
#: with it, each read in one battery of the landing's HEAD after a QLF purge
#: and one warm-up; command=python extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-26, 1080231 to 1080397 (+166), the compiler's call-or-data
#: decisions ask _callable_here where they asked the process-wide is_function:
#: the catalogue first, and the defining space's own functions only when the
#: catalogue lacks the name, so a decision the catalogue answers asks a
#: different question and one it cannot answer asks two [measured
#: 2026-09-26T18:36:57+10:00: one full twins lane before this commit and one
#: with it, each read in one battery of the landing's HEAD after a QLF purge
#: and one warm-up; command=python extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-27, 1080397 to 1080920 (+523), the host switch to swipl-
#: patched.7 and the seat changes it needs: +14 the host switch to swipl-
#: patched.7, which delivers the heartbeat inside loops, so a held engine ticks
#: and the held goals read its ticks from the raw counter, 9 inferences a tick,
#: and whose three new system predicates ('$heartbeat'/0, '$file_hash'/2,
#: '$qlf_source_changed'/2) filereader's walk of every visible predicate
#: (existing_predicate_arities/2) meets, 2 inferences each; +12 the seat's
#: interrupt poll crossing only on its arming thread, whose hook costs 3
#: inferences a tick more and whose start goal runs on every new thread and
#: engine; +497 the held goals reading Used through metta_py_work/2, which
#: leaves a held engine's own ticks out and reads the tick term inside its
#: opening edge, 5 inferences a held reading [measured
#: 2026-09-27T03:41:21+10:00: one full twins lane of the trunk and one with
#: this landing, wt-merge battery 1, the trunk on swipl-patched.6 and every
#: part on .7, each through a same-shape host shim; command=python
#: extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-27, 1080920 to 1081063 (+143), a force of a waiting
#: function takes the typing policy and the specializer's lock before
#: translation: spaces:metta_ensure_compiled/2 stabilises the policy and takes
#: the specializer's mutex around the translation once per force, and the
#: translation's own per-pair stabilisation re-enters through
#: with_typing_policy_stable/1's first clause [measured
#: 2026-09-27T09:56:55+10:00: one full twins lane before this commit and one
#: with it, each read in one battery of the landing's HEAD after a QLF purge
#: and one warm-up; command=python extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-27, 1081063 to 1081192 (+129), the constructive negation's
#: engine additions, each counted in this twin's own run: 2 registration walks
#: over more than twelve names (filereader:existing_predicate_arities/2), each
#: now reading 31 more predicates at 2 inferences (+124); 3 == or != on
#: compound terms that differ, each now decided by metta_same_term/3 (+6); -1
#: of clause-indexing layout [measured 2026-09-27T18:31:56+10:00: one full
#: twins lane with this landing, in a battery of its tree at 775d3cf35, beside
#: one of the base in a battery of 775d3cf35 from 2026-09-27T18:40:06+10:00,
#: which reads the old pin; command=python
#: extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-28, 1081192 to 1081190 (-2), -2 at tsm-licence's notices
#: reader as its block lookahead amended it: engine/host_notices.pl, which
#: every boot loads, opens a component block only where its Component field
#: directly follows the line of 78 '=', the calls not traced; read on swipl-
#: patched.8, the count above on .7, which no longer runs [measured
#: 2026-09-28T12:31:49+10:00: full twins lanes in wt-merge's battery 1 on
#: swipl-patched.8 at this boundary, engine/host_notices.pl as amended against
#: the day before's as first written; command=sh tools/check.sh twins].
#: RE-PINNED 2026-09-27, 1081190 to 1080904 (-286), +2 at the host switch to
#: swipl-patched.8, whose swi-heartbeat-inferences-charged-to-the-program
#: leaves the interrupt poll's own inferences out of every count, so a window
#: the seat's calibrated poll correction read 1 to 3 low on .7 reads exactly;
#: -288 at interrupts B's seat change, which drops the poll's boot calibration,
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
#: RE-PINNED 2026-09-27, 1080904 to 1080908 (+4), +4 at janus-contract A, whose
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
#: RE-PINNED 2026-09-27, 1080908 to 1057147 (-23761), -23,761 at walk-tax B,
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
#: RE-PINNED 2026-09-29, 1057147 to 1057321 (+174), this twin reads 1057147
#: before the change and 1057321 with the change (+174): each definition
#: through the define doors asks whether its module holds a shadow-import
#: receipt for the name, holds it in flight until the write is visible when it
#: does, and a sweep leaves a receipt another live thread holds: with that use
#: this twin reads 1057321 where the definitions alone read 1057147 (+174)
#: [measured 2026-09-29T06:36:33+10:00: min-of-3 serial fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-29, 1057321 to 1060597 (+3276), this twin reads 1057321
#: before the change and 1060597 with the change (+3276): each definition marks
#: its name as changed and a sweep repairs only the receipts naming a marked
#: name, where it re-checked every receipt the process held: with that use this
#: twin reads 1060597 where the definitions alone read 1057321 (+3276)
#: [measured 2026-09-29T06:43:21+10:00: min-of-3 serial fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-29, 1060597 to 1060615 (+18), this twin reads 1060597
#: before the change and 1060615 with the change (+18): a definition that
#: cannot move its space's source map leaves the space's source reader
#: published, so a load beside a from row publishes the face once per runnable
#: instead of once per definition: with that use this twin reads 1060615 where
#: the definitions alone read 1060597 (+18) [measured
#: 2026-09-29T06:51:16+10:00: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-29, 1060615 to 1060960 (+345), this twin reads 1060615
#: before the change and 1060960 with the change (+345): a mark names the
#: module its definition changed in, and a sweep repairs only the receipts held
#: by that module and its declared descendants: with that use this twin reads
#: 1060960 where the definitions alone read 1060615 (+345) [measured
#: 2026-09-29T06:56:25+10:00: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-29, 1060960 to 1063230 (+2270), this twin reads 1060960
#: before the change and 1063230 with the change (+2270): every operation that
#: registers a name outside a load opens a registration unit, files there the
#: repairs its registrations owe, and drains them once when it finishes, so a
#: caller compiled before the name became a function is repaired: with that use
#: this twin reads 1063230 where the definitions alone read 1060960 (+2270)
#: [measured 2026-09-29T20:22:58+10:00: min-of-3 serial fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-29, 1063230 to 1062263 (-967), this twin reads 1063230
#: before the change and 1062263 with the change (-967): a call site forces the
#: function it names before deciding the call's shape, so a call of a waiting
#: function builds the application protocol an eager load builds, and the
#: protocol's marker test around a value the translation already holds is
#: decided at compile time: with that use this twin reads 1062263 where the
#: definitions alone read 1063230 (-967) [measured 2026-09-29T20:34:56+10:00:
#: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-30, 1062263 to 1054343 (-7920), this twin reads 1062263
#: before the change and 1054343 with the change (-7920): a named space's
#: prelude-tier type readers look the prelude's row up before asking whether it
#: governs there, and builtin_result_type/3 asks whether a program took a
#: builtin over only for a builtin whose result is evaluated
#: (engine/metta/types.pl, engine/translator/lowering.pl), so a lookup of a
#: name the prelude does not declare costs one indexed miss and no ownership
#: probe [measured 2026-09-30T04:16:54+10:00: min-of-3 serial fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-30, 1054343 to 1054397 (+54), the twins lane reads this
#: twin at 1054343 before this change and at 1054397 with it (+54): a module
#: takes a name over only when the name's equations compile to a predicate of
#: that name (engine/metta/registration.pl, fun_overrides_in/2), so each reader
#: that asked fun_in/2 whether a module took a name over now also asks
#: compiled_function_name/2 when the module registers the name, one call per
#: such lookup of a module's own name [measured 2026-09-30T04:29:01+10:00: min-
#: of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-30, 1054397 to 1054728 (+331), the twins lane reads this
#: twin at 1054397 before this change and at 1054728 with it (+331): every
#: import request that succeeds, a load or a receipt still current, now records
#: who asked for the source (engine/metta/interop.pl, record_import_request/2
#: writing import_request/3), so unimport! of a package can leave a file
#: another live requester still asks for [measured 2026-09-30T04:34:13+10:00:
#: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
BUDGET = 1054728

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
#: DIVERGED 2026-09-25, the example holds 3 atoms the twin does not (3 =) and
#: the twin holds 5 atoms the example does not (3 =, 2 @python-callable): a
#: lambda is named by its content, lambda_ and 16 hex digits of its closed
#: clause's variant_sha1/2, so a stored row naming a lambda names that digest
#: where it named a process-wide counter, and a row both spaces hold under two
#: counter names is one row [measured 2026-09-25T17:00:15+10:00: the two
#: stored-atom surpluses, one fresh process per side; command=python
#: extensions/python/tools/twin_coverage.py].
DIVERGENCE = "f28bf3cd4c2dae21534c716a0b0a0ab0c82617943e05f5253f1e002bd91b6c51"
