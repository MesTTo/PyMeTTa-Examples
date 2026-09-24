"""Purpose: inspect, rewrite and run sample programs through ordinary MeTTa control.

Guarantees: the same 68 claims as 36-random_lib.metta.
[tested: python extensions/python/tools/twin_coverage.py examples/ch08-data/08-03-the-shipped-libraries/36-random_lib.metta; commit=1d0b78a359f58de49f2f98bed50a6480d56cd5f6].
"""

from metta import G, S, V, lib
from metta._errors.errors import MettaError


def twin(m):
    """Construct sample code, then use the existing evaluation and repetition doors."""
    m += lib.random
    seed = m.fn.with_seed
    choice = m.fn.random_choice
    shuffle, sample = m.fn["random-shuffle!"], m.fn["random-sample!"]
    normal, uniform = m.fn.random_normal, m.fn.random_uniform
    lognormal, triangular = m.fn.random_lognormal, m.fn.random_triangular
    bernoulli, exponential = m.fn.random_bernoulli, m.fn.random_exponential
    gamma, beta = m.fn.random_gamma, m.fn.random_beta
    pareto, weibull = m.fn.random_pareto, m.fn.random_weibull

    def refused(call):
        """Read a refusal through the same catch and if-error boundary."""
        try:
            return m.eval(S.if_error(S.catch(call), S.refused, S.fine)) == [S.refused]
        except MettaError:
            return True

    def drawn(program, count=1, seed_value=11):
        """Use the existing seed and repeat forms on an already constructed program."""
        return seed(seed_value, S.repeat(count, program))

    assert m.fn.get_metatype(normal(0, 1)[0]) == [S.Expression]
    assert m.fn.get_type(S.random_normal) == [S["->"](S.Number, S.Number, S.Expression)]
    assert m.eval(choice((G("only"),))[0]) == [G("only")]
    assert len(m.eval(choice((S["+"](1, 2),))[0])[0]) == 3
    assert shuffle(()) == [()]
    assert tuple(seed(42, S.sort_atom(S["random-shuffle!"]((1, 1, 2, 3)))).one()) == (1, 1, 2, 3)
    assert seed(42, S["random-shuffle!"]((1, 2, 3, 4))) == seed(42, S["random-shuffle!"]((1, 2, 3, 4)))
    assert sample((), 0) == [()]
    assert tuple(seed(42, S.sort_atom(S["random-sample!"]((1, 1, 2, 3), 4))).one()) == (1, 1, 2, 3)
    assert m.fn.repeat(3, choice((G("x"),))[0]) == [G("x"), G("x"), G("x")]
    assert len(seed(42, S["random-sample!"]((1, 2, 3, 4, 5), 3)).one()) == 3
    assert tuple(seed(42, S["random-sample!"]((G("x"), G("x")), 2)).one()) == (G("x"), G("x"))
    choices = choice((1, 2, 3, 4))[0]
    assert seed(9, choices) == seed(9, choices)
    choices = choice((V.x,))[0]
    repeated = m.fn.map_atom((0, 1, 2), V.i, S.eval(choices))[0]
    assert len(repeated.vars) == 1 and tuple(repeated) == (repeated[0],) * 3
    pair = seed(42, S["random-sample!"]((V.x, V.x), 2))[0]
    assert len(pair.vars) == 1 and pair[0] == pair[1]
    assert sample((S.Error(S.data, S.code),), 1)[0] == (S.Error(S.data, S.code),)

    assert m.fn.repeat(0, normal(0, 1)[0]) == []
    assert m.fn.repeat(3, uniform(4, 4)[0]) == [4.0, 4.0, 4.0]
    assert m.eval(normal(7, 0)[0]) == [7.0]
    assert m.eval(lognormal(0, 0)[0]) == [1.0]
    assert m.eval(triangular(3, 3, 3)[0]) == [3.0]
    assert m.fn.repeat(2, bernoulli(0)[0]) == [False, False]
    assert m.fn.repeat(2, bernoulli(1)[0]) == [True, True]
    gaussian = normal(0, 1)[0]
    assert len(drawn(gaussian, 5, 42)) == 5
    assert drawn(gaussian, 4, 42) == drawn(gaussian, 4, 42)
    assert seed(42, S.once(S.repeat(100, gaussian))) == drawn(gaussian, 1, 42)
    assert m.eval(normal(m.fn.math_rational(1, 2)[0], 0)[0]) == [0.5]

    u = drawn(uniform(-4, 9)[0]).one()
    assert -4 <= u <= 9
    assert m.fn.math_class(drawn(gaussian).one()) == [S.normal]
    assert drawn(lognormal(0, 1)[0]).one() > 0
    assert drawn(exponential(2)[0]).one() > 0
    t = drawn(triangular(-4, 9, 2)[0]).one()
    assert -4 <= t <= 9
    assert drawn(gamma(2, 3)[0]).one() > 0
    b = drawn(beta(2, 5)[0]).one()
    assert 0 < b < 1
    assert m.fn.get_type(drawn(bernoulli(0.25)[0])[0]) == [S.Bool]
    assert drawn(pareto(3)[0]).one() >= 1
    assert drawn(weibull(2, 3)[0]).one() > 0
    assert drawn(gamma(1.0e308, 1)[0], seed_value=42) == [1.0e308]
    assert drawn(beta(1.0e308, 1.0e308)[0], seed_value=42) == [0.5]
    assert drawn(gamma(0.001, 1)[0], seed_value=2) == [0.0]
    assert drawn(gamma(0.001, 1.0e300)[0], seed_value=2).one() > 0
    assert drawn(weibull(1.0e308, 1.0e308)[0], seed_value=42) == [1.0e308]
    assert m.fn.math_class(m.eval(lognormal(1000, 0)[0])[0]) == [S.infinite]
    assert m.eval(lognormal(-1000, 0)[0]) == [0.0]

    m.add(S.saved_sampler(normal(12, 0)[0]))
    stored = m.match(S.saved_sampler(V.code)).one().code
    assert m.eval(stored) == [12.0]
    head, _entropy, low, high = uniform(2, 10)[0]
    assert m.eval((head, 0.25, low, high)) == [4.0]
    row = m.match(S["="](S.random_normal(V.mean, V.deviation), V.body)).one()
    constructor = m.eval(S["|->"]((row.mean, row.deviation), row.body))[0]
    assert m.eval(m.eval((constructor, 9, 0))[0]) == [9.0]
    alternatives = normal(S.superpose((1, 2)), 0)
    assert [answer for program in alternatives for answer in m.eval(program)] == [1.0, 2.0]
    assert m.fn.repeat(2, S.superpose((S.a, S.b))) == [S.a, S.b, S.a, S.b]
    a, b = normal(2, 0)[0], uniform(3, 3)[0]
    assert m.eval(S["+"](S.eval(a), S.eval(b))) == [5.0]

    assert refused(S.random_choice(()))
    assert refused(S["random-shuffle!"](G("text")))
    assert refused(S["random-sample!"]((), 1))
    assert refused(S["random-sample!"]((1, 2), 3))
    assert refused(S["random-sample!"]((1,), -1))
    assert refused(S["random-sample!"]((1,), 1.0))
    assert refused(S.random_normal(0, -1))
    assert refused(S.random_uniform(2, 1))
    assert refused(S.random_triangular(0, 1, 2))
    assert refused(S.random_exponential(0))
    assert refused(S.random_gamma(-1, 2))
    assert refused(S.random_beta(2, 0))
    assert refused(S.random_bernoulli(1.1))
    assert refused(S.random_pareto(0))
    assert refused(S.random_weibull(0, 1))
    assert refused(S.random_normal(G("x"), 1))
    assert refused(S.random_normal(S.math_real(S.inf, ()), 1))
    try:
        invalid = normal(0, -1)[0]
        m.fn.repeat(0, invalid)
    except MettaError:
        refused_before_repeat = True
    else:
        refused_before_repeat = False
    assert refused_before_repeat


#: MEASURED 2026-09-13: 68 equal claims over inspectable sample programs,
#: including variable sharing, reflection, exact extreme parameters and
#: validation before drawing. min-of-3 serial fresh processes reads
#: metta=1075529 and twin=1134846 [measured: 1134846;
#: command=python extensions/python/tools/twin_coverage.py --measure --rounds 3 examples/ch08-data/08-03-the-shipped-libraries/36-random_lib.metta;
#: fixture=68 Random example claims with core seeded entropy; commit=1d0b78a359f58de49f2f98bed50a6480d56cd5f6].
#: RE-PINNED 2026-09-14, 1134846 to 1148657 (+13811), Functional applies
#: finished callback arguments through reduce; Statistics derives exact
#: coefficient rows and Combinatorics retires its native probability provider
#: [measured 2026-09-14: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=e1be99ea1c08f70444c1c35cada441e089777906].
#: RE-PINNED 2026-09-14, 1148657 to 1150796 (+2139), Vector derives fill,
#: random construction and normalized-dot through MeTTa equations;
#: Combinatorics supplies ranges, literal validation folds once before core
#: seeded draws, and the Vector example adds nine construction and refusal
#: claims. Native Math also imports the shared Vector kernels, so every MeTTa
#: and native consumer is renewed [measured 2026-09-14: min-of-3 serial fresh
#: processes; command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=c7bacead4feb29b9761d026b52b952e91b26b10b].
#: RE-PINNED 2026-09-21, 1150796 to 1231749 (+80953), the sixty libraries
#: derived in MeTTa landed with merge 97763e7fa eight hours after the previous
#: pin 55d451b67, so every example importing one now pays a MeTTa derivation
#: where it paid a Prolog body instead, which the 2026-09-14 ruling accepts
#: explicitly as the price of a library that survives the engine swap [measured
#: 2026-09-21: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=6e09cb25d5495c2db3283166e6ce4e07eefecfb2].
#: RE-PINNED 2026-09-24, 1231749 to 1252282 (+20533), placed on the full-
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
#: RE-PINNED 2026-09-24, 1252282 to 1194524 (-57758), 0a81c782f loads a
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
#: RE-PINNED 2026-09-24, 1194524 to 1229251 (+34727), +34,708 at ae1cc8936,
#: where a registration batch of thirteen names or more walks the visible
#: predicate table at two inferences a predicate that asking per name spent
#: inside one C call, and a batch above forty tests each predicate with a dict
#: at one inference fewer than the AVL; +18 at b5eb39acd, whose three new
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
#: RE-PINNED 2026-09-24, 1229251 to 1228955 (-296), d4a365c16 holds the support
#: graph's visited set and the reference refresh's space sets in SWI tries
#: instead of library(nb_set): a membership check is one foreign call where
#: nb_set probed in Prolog, four inferences a step past a taken slot, from a
#: slot a library space's path-bearing name decided, and a walk over a node or
#: two pays a few inferences more for the trie's setup (-17); gate-perf's
#: d781eab8f carries an exact removal's selected head from the code that
#: selected it, so a withdrawal copies its equation once: 23 inferences fewer
#: for each equation removal the twin adopts and 4 for each it selects (-345);
#: the packages job's 90be572a9 and 4003462fe register Prolog through one
#: engine service: +22 for each library the twin imports (ten new engine
#: predicates and two user imports in the registration walk at two inferences
#: each, less the retired loaded_extension_file/2), and 146 inferences for a
#: Prolog file's origin or 220 for a text's SHA-256 on a twin that registers
#: Prolog (+66); each step read serially on its own committed tree, from gate-
#: perf's pin at c7d7244fb, and the fixed tree 4ff69551e reads what 4003462fe
#: does [measured 2026-09-24: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=4ff69551e0e226442cf7257b96af858adda957a4].
#: RE-PINNED 2026-09-24, 1228955 to 1228961 (+6), +6 at the change this re-pin
#: lands with, which groups a whole reference face's heads in one pass over its
#: sorted entries where each head searched the whole face, and whose three
#: imports into the engine module are one more predicate filereader's
#: registration walk reads above twelve names, pairs_keys/2, and three a
#: restricted space's core steps over as it enumerates that module's predicates
#: [measured 2026-09-24: the twins lane alone on the base 8d651070d and on the
#: base with this change, one after the other in battery 117's one path, every
#: component at its pin; command=sh tools/check.sh twins (twin_coverage.py
#: inside tools/bounded.sh); commit=8bda9d5525a8174a8304376e111df8da258076a9].
#: RE-PINNED 2026-09-24, 1228961 to 1229239 (+278), +278 at the change this re-
#: pin lands with, which publishes a from row by itself when rows are all a
#: space owes: its 36 predicates visible to filereader's registration walk cost
#: a batch above twelve names 72 inferences, each restricted space's core about
#: 28 a predicate, and every whole publication and face event its ledger's
#: bookkeeping [measured 2026-09-24: the twins lane alone on 8d651070d with the
#: change before this one and with this change too, one after the other in
#: battery 117's one path, every component at its pin; command=sh
#: tools/check.sh twins (twin_coverage.py inside tools/bounded.sh);
#: commit=e4b7448d1f1bd98733f1b04c3906aaa42f35ef1a].
#: RE-PINNED 2026-09-24, 1229239 to 1229207 (-32), the host switch of
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
#: RE-PINNED 2026-09-25, 1229207 to 1229212 (+5), the pragma refusal defines
#: require_metta_pragma_capability/2 in the engine module, and on the same tree
#: defining it without calling it moves this twin by the whole of the change's
#: move, so the cost is one more engine predicate and functor met through the
#: engine's walks over its predicate and functor tables, among them
#: filereader:existing_predicate_arities/2, which charges two inferences for
#: each predicate visible from the loading module at every load of a source
#: registering more than twelve names (i-arity-walk-all-predicates); the
#: change's work at a pragma write does not reach this twin [measured
#: 2026-09-25T00:48:36+10:00: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-25, 1229212 to 1229272 (+60), the py-* doors change makes
#: more predicates visible from filereader, and
#: filereader:existing_predicate_arities/2 walks every predicate visible there
#: at two inferences each whenever a source registering more than twelve names
#: loads: on one tree the change's new engine predicates alone, defined with
#: their two boot uses taken out, move this twin by 16 for each such load and
#: the whole change by 20, each give or take one or two inferences that move
#: with where the new names land in SWI's tables and that SWI's profiler, which
#: lists no system predicate, does not place (i-arity-walk-all-predicates)
#: [measured 2026-09-25T02:56:52+10:00: min-of-3 serial fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --repin].
BUDGET = 1229272
