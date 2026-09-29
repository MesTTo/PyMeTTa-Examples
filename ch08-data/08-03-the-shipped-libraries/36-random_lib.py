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
#: RE-PINNED 2026-09-25, 1229272 to 1224922 (-4350), the host evaluation door
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
#: more than twelve names [measured 2026-09-25T06:47:54+10:00: min-of-3 serial
#: fresh processes; command=python extensions/python/tools/twin_coverage.py
#: --repin].
#: RE-PINNED 2026-09-25, 1224922 to 1224951 (+29), Runtime.reclaim(), the
#: reclamation barrier metta_py_reclaim/1, adds five predicates to user, and
#: existing_predicate_arities/2 walks every user predicate about twice per
#: large load (i-arity-walk-all-predicates) [measured
#: 2026-09-25T11:25:25+10:00: one full twins lane before this commit and one
#: with it, the two read on one battery path at the landing's HEAD;
#: command=python extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-25, 1224951 to 1224987 (+36), both specializer doors
#: prepare a specialization's predicate with
#: spaces:metta_prepare_function_predicate/3 before asserting its clauses
#: [measured 2026-09-25T11:29:10+10:00: one full twins lane before this commit
#: and one with it, the two read on one battery path at the landing's HEAD;
#: command=python extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-25, 1224987 to 1224999 (+12), retiring a library importer
#: derives the arity row again from any backing head a library home still
#: registers, journalled to the load that owns it [measured
#: 2026-09-25T11:33:06+10:00: one full twins lane before this commit and one
#: with it, the two read on one battery path at the landing's HEAD;
#: command=python extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-25, 1224999 to 1225454 (+455), every force of a waiting
#: function names the module it is made from, through fun_home_in/3, and a
#: write forces only its own space; the lanes' tree read this twin +1 off its
#: pin before the step, an offset that is not this step's, so the pin moves by
#: the step's delta alone [measured 2026-09-25T16:54:32+10:00: one full twins
#: lane before this commit and one with it, the two read on one battery path at
#: the landing's HEAD; command=python
#: extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-25, 1225454 to 1227971 (+2517), lambdas are named by their
#: content and a copy restores its source's rows as a program; the lanes' tree
#: read this twin +1 off its pin before the step, an offset that is not this
#: step's, so the pin moves by the step's delta alone [measured
#: 2026-09-25T17:00:15+10:00: one full twins lane before this commit and one
#: with it, the two read on one battery path at the landing's HEAD;
#: command=python extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-25, 1227971 to 1227988 (+17), engine/source_loading.pl's
#: load-error clause moved from the thread_local user:thread_message_hook/3 to
#: the global user:message_hook/3, so every thread and engine now runs the
#: check the main thread always ran: one inference per message while no load is
#: open there (clause(watching, true, _) fails) and two inside one
#: (load_failure/2 rejects the silent kind); the Python seat prints a twin's
#: library-load messages inside engines, where no clause ran before, and the
#: original's side does not move; +16 of it, and the other +1 was already in
#: trunk 113c5c928's count at base, 1227972 min-of-3 against the pin 1227971,
#: before this change [measured 2026-09-25T18:45:49+10:00: min-of-3 serial
#: fresh processes; command=python extensions/python/tools/twin_coverage.py
#: --repin].
#: RE-PINNED 2026-09-25, 1227988 to 1227993 (+5), a sweep of a module's
#: generated predicates retires the records describing each swept predicate,
#: and a release the rest of the module's [measured 2026-09-25T23:29:52+10:00:
#: one full twins lane before this commit and one with it, the two read on one
#: battery path at the landing's HEAD; command=python
#: extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-26, 1227993 to 1228047 (+54), engine/metta/control.pl's
#: partial/3 to partial/11, the clauses that let a Prolog meta-predicate call a
#: partial function value, are nine more predicates visible from filereader,
#: and filereader:existing_predicate_arities/2's batch walk, which a load
#: registering more than twelve names runs, pays two inferences for each: 18 a
#: batch, the original and the twin alike, and nine inert facts of those
#: arities move it the same [measured 2026-09-26T01:31:09+10:00: min-of-3
#: serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-26, 1228047 to 1228108 (+61), the reference faces of a
#: strongly connected component of from rows are computed together by label-
#: setting, which makes ten more predicates visible from metta_engine, and a
#: control adding only ten unused predicates to metta_engine reads the same, so
#: none of the move is face work; existing_predicate_arities/2 walks every
#: visible predicate at two inferences for each batch of more than twelve names
#: a load registers (i-arity-walk-all-predicates) [measured
#: 2026-09-26T03:09:06+10:00: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-26, 1228108 to 1228099 (-9), engine/source_loading.pl
#: hears a load's printed failures through a user:thread_message_hook/3 clause
#: each load asserts on the thread or engine running it and erases, where
#: c83b6bb1e's clause of the global user:message_hook/3 ran for every message:
#: 4 loads each call prolog_current_frame/1 once more (+4); 1 registration walk
#: over a batch of more than twelve names
#: (filereader:existing_predicate_arities/2) enumerates one more predicate than
#: the trunk's (+2), since SWI's autoImport() links prolog_current_frame/1 into
#: every module on metta_source_loading's import chain, user included, at the
#: boot's first load, where the trunk links it into user only at its first
#: library import; 15 messages this twin's count reads, printed outside a load,
#: no longer run the loader's clause (-15) [measured 2026-09-26T06:55:43+10:00:
#: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-26, 1228099 to 1228110 (+11), this twin reads 1228099 at
#: the base and 1228110 with the change (+11): the change adds
#: metta_reference_enroll/1 and metta_reference_source_bound/5 to the
#: metta_engine module (engine/metta/reference_refresh.pl and
#: reference_sources.pl), and on a tree that defines them and never calls them
#: this twin reads 1228110 (+11), which only a walk over SWI's predicate or
#: atom tables can move, by visiting more entries or visiting them in another
#: order [measured 2026-09-26T11:18:44+10:00: min-of-3 serial fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-26, 1228110 to 1228128 (+18), Registering a source's names
#: answers each name's Prolog arities in standard order, one msort/2 per
#: registration that adds names, where they came in the procedure table's order
#: and set the order of the arity/2 facts [measured 2026-09-26T12:30:30+10:00:
#: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-26, 1228128 to 1228189 (+61), A Prolog function registered
#: without its arity is claimed from its lowest arity's file through
#: aggregate_all(min(Arity, File), ...), where the scan took the first arity
#: the procedure table answered [measured 2026-09-26T13:03:50+10:00: min-of-3
#: serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-26, 1228189 to 1228269 (+80), Automatic caching asks every
#: arity of a candidate function whether SWI already tables it through
#: findall/3 and a non-empty list, one findall/3 more per candidate that
#: reaches the explicit-tabling ground, where it stopped at the first tabled
#: arity the procedure table answered [measured 2026-09-26T13:38:30+10:00: min-
#: of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-26, 1228269 to 1228287 (+18), The engine module defines
#: three predicates more, builtin_seat_prefixes/1,
#: builtin_implementation_gap/2, validate_builtin_implementation_gaps/2 and
#: builtin_surface_predicate/3 in and builtin_surface_predicate_name/1 out, and
#: a program pays for each predicate visible from the engine wherever it walks
#: them: existing_predicate_arities/2 two inferences a predicate for each load
#: that registers more than twelve names, and a restricted space twenty-seven a
#: predicate when it publishes the engine's core; three facts appended to
#: engine/metta/registration.pl on 07b75d16e move 14-lib_roman_pair_helpers,
#: 02-restricted_spaces and 37-statistics_lib by the same +6, +87 and +30
#: [measured 2026-09-26T14:29:54+10:00: min-of-3 serial fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-26, 1228287 to 1228351 (+64), the specializer substitutes
#: only ground bindings into a specialization's stored row: it tests each
#: binding with ground/1, which SWI calls as a builtin where nonvar/1 compiled
#: inline, and leaves a binding with variables as the row's own parameter
#: instead of substituting it into the body [measured
#: 2026-09-26T18:25:19+10:00: one full twins lane before this commit and one
#: with it, each read in one battery of the landing's HEAD after a QLF purge
#: and one warm-up; command=python extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-27, 1228351 to 1228917 (+566), the host switch to swipl-
#: patched.7 and the seat changes it needs: +38 the host switch to swipl-
#: patched.7, which delivers the heartbeat inside loops, so a held engine ticks
#: and the held goals read its ticks from the raw counter, 9 inferences a tick,
#: and whose three new system predicates ('$heartbeat'/0, '$file_hash'/2,
#: '$qlf_source_changed'/2) filereader's walk of every visible predicate
#: (existing_predicate_arities/2) meets, 2 inferences each; +24 the seat's
#: interrupt poll crossing only on its arming thread, whose hook costs 3
#: inferences a tick more and whose start goal runs on every new thread and
#: engine; +6 the poll's tick record updated in place, 3 inferences a tick more
#: than replacing it; +498 the held goals reading Used through metta_py_work/2,
#: which leaves a held engine's own ticks out and reads the tick term inside
#: its opening edge, 5 inferences a held reading [measured
#: 2026-09-27T03:41:21+10:00: one full twins lane of the trunk and one with
#: this landing, wt-merge battery 1, the trunk on swipl-patched.6 and every
#: part on .7, each through a same-shape host shim; command=python
#: extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-27, 1228917 to 1229127 (+210), a force of a waiting
#: function takes the typing policy and the specializer's lock before
#: translation: spaces:metta_ensure_compiled/2 stabilises the policy and takes
#: the specializer's mutex around the translation once per force, and the
#: translation's own per-pair stabilisation re-enters through
#: with_typing_policy_stable/1's first clause [measured
#: 2026-09-27T09:56:55+10:00: one full twins lane before this commit and one
#: with it, each read in one battery of the landing's HEAD after a QLF purge
#: and one warm-up; command=python extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-27, 1229127 to 1229342 (+215), the constructive negation's
#: engine additions, each counted in this twin's own run: 3 registration walks
#: over more than twelve names (filereader:existing_predicate_arities/2), each
#: now reading 31 more predicates at 2 inferences (+186); 16 == or != on
#: compound terms that differ, each now decided by metta_same_term/3 (+32); -3
#: of clause-indexing layout [measured 2026-09-27T18:31:56+10:00: one full
#: twins lane with this landing, in a battery of its tree at 775d3cf35, beside
#: one of the base in a battery of 775d3cf35 from 2026-09-27T18:40:06+10:00,
#: which reads the old pin; command=python
#: extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-28, 1229342 to 1229340 (-2), -2 at tsm-licence's notices
#: reader as its block lookahead amended it: engine/host_notices.pl, which
#: every boot loads, opens a component block only where its Component field
#: directly follows the line of 78 '=', the calls not traced; read on swipl-
#: patched.8, the count above on .7, which no longer runs [measured
#: 2026-09-28T12:31:49+10:00: full twins lanes in wt-merge's battery 1 on
#: swipl-patched.8 at this boundary, engine/host_notices.pl as amended against
#: the day before's as first written; command=sh tools/check.sh twins].
#: RE-PINNED 2026-09-27, 1229340 to 1229018 (-322), +2 at the host switch to
#: swipl-patched.8, whose swi-heartbeat-inferences-charged-to-the-program
#: leaves the interrupt poll's own inferences out of every count, so a window
#: the seat's calibrated poll correction read 1 to 3 low on .7 reads exactly;
#: -324 at interrupts B's seat change, which drops the poll's boot calibration,
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
#: RE-PINNED 2026-09-27, 1229018 to 1229024 (+6), +6 at janus-contract A, whose
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
#: RE-PINNED 2026-09-27, 1229024 to 1193356 (-35668), -35,668 at walk-tax B,
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
#: RE-PINNED 2026-09-29, 1193356 to 1193452 (+96), this twin reads 1193356
#: before the change and 1193452 with the change (+96): each definition through
#: the define doors asks whether its module holds a shadow-import receipt for
#: the name, holds it in flight until the write is visible when it does, and a
#: sweep leaves a receipt another live thread holds: with that use this twin
#: reads 1193452 where the definitions alone read 1193356 (+96) [measured
#: 2026-09-29T06:36:47+10:00: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-29, 1193452 to 1195124 (+1672), this twin reads 1193452
#: before the change and 1195124 with the change (+1672): each definition marks
#: its name as changed and a sweep repairs only the receipts naming a marked
#: name, where it re-checked every receipt the process held: with that use this
#: twin reads 1195124 where the definitions alone read 1193452 (+1672)
#: [measured 2026-09-29T06:43:35+10:00: min-of-3 serial fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-29, 1195124 to 1195164 (+40), this twin reads 1195124
#: before the change and 1195164 with the change (+40): a definition that
#: cannot move its space's source map leaves the space's source reader
#: published, so a load beside a from row publishes the face once per runnable
#: instead of once per definition: with that use this twin reads 1195164 where
#: the definitions alone read 1195124 (+40) [measured
#: 2026-09-29T06:51:27+10:00: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-29, 1195164 to 1195274 (+110), this twin reads 1195164
#: before the change and 1195274 with the change (+110): a mark names the
#: module its definition changed in, and a sweep repairs only the receipts held
#: by that module and its declared descendants: with that use this twin reads
#: 1195274 where the definitions alone read 1195164 (+110) [measured
#: 2026-09-29T06:56:44+10:00: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-29, 1195274 to 1196045 (+771), this twin reads 1195274
#: before the change and 1196045 with the change (+771): every operation that
#: registers a name outside a load opens a registration unit, files there the
#: repairs its registrations owe, and drains them once when it finishes, so a
#: caller compiled before the name became a function is repaired: with that use
#: this twin reads 1196045 where the definitions alone read 1195274 (+771)
#: [measured 2026-09-29T20:23:24+10:00: min-of-3 serial fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-29, 1196045 to 1195151 (-894), this twin reads 1196045
#: before the change and 1195151 with the change (-894): a call site forces the
#: function it names before deciding the call's shape, so a call of a waiting
#: function builds the application protocol an eager load builds, and the
#: protocol's marker test around a value the translation already holds is
#: decided at compile time: with that use this twin reads 1195151 where the
#: definitions alone read 1196045 (-894) [measured 2026-09-29T20:35:26+10:00:
#: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-30, 1195151 to 1183394 (-11757), this twin reads 1195151
#: before the change and 1183394 with the change (-11757): a named space's
#: prelude-tier type readers look the prelude's row up before asking whether it
#: governs there, and builtin_result_type/3 asks whether a program took a
#: builtin over only for a builtin whose result is evaluated
#: (engine/metta/types.pl, engine/translator/lowering.pl), so a lookup of a
#: name the prelude does not declare costs one indexed miss and no ownership
#: probe [measured 2026-09-30T04:17:17+10:00: min-of-3 serial fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --repin].
BUDGET = 1183394
