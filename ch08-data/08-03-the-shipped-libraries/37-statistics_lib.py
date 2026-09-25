"""Purpose: exact finite descriptive statistics and explicit sample domains.

Guarantees: the same 78 claims as 37-statistics_lib.metta.
[tested: python extensions/python/tools/twin_coverage.py examples/ch08-data/08-03-the-shipped-libraries/37-statistics_lib.metta; commit=6fa571d1b7059b610f73e9feed657711414251e5].
"""

from metta import FALSE, TRUE, G, S, V, lib
from metta._errors.errors import MettaError


def twin(m):
    """Reduce observations, interpolate quantiles and fit exact paired data."""
    m += lib.statistics
    fn = m.fn

    def refused(call):
        """Read an operation refusal through the public evaluation boundary."""
        try:
            list(m.eval(call))
        except MettaError:
            return True
        return False

    assert fn.stats_sum(()) == [0]
    assert fn.stats_sum((1, 2, 3)) == [6]
    assert fn.stats_sum((1.0e308, 1, -1.0e308)) == [1.0]
    assert fn.math_class(S.stats_sum((1.0e308, 1.0e308))) == [S.infinite]
    assert fn.stats_mean((1, 2, 3)) == [2]
    assert tuple(fn.math_ratio(S.stats_mean((1, 2))).one()) == (3, 2)
    assert fn.stats_mean((1.0e308, 1.0e308)) == [1.0e308]
    assert fn.stats_mean((1.0e308, 1, -1.0e308)) == fn.math_float(S.math_rational(1, 3))
    assert fn.stats_harmonic_mean((40, 60)) == [48]
    assert fn.stats_harmonic_mean((40.0, 60)) == [48.0]
    assert fn.stats_harmonic_mean((0, 7)) == [0]
    assert fn.stats_geometric_mean((54, 24, 36)) == [36.0]
    assert fn.stats_geometric_mean((0, 7)) == [0.0]
    assert fn.stats_geometric_mean((1.0e308, 1.0e308)) == [1.0e308]
    big = fn.pow_math(2, 2000).one()
    small = fn.math_rational(1, big)[0]
    assert fn.stats_geometric_mean((big, small)) == [1.0]

    assert fn.stats_median((9, 1, 4)) == [4]
    assert tuple(fn.math_ratio(S.stats_median((1, 2))).one()) == (3, 2)
    assert fn.stats_median((9.0, 1, 4)) == [4.0]
    assert fn.stats_quantile((0, 10), 0, S.inclusive) == [0]
    assert fn.stats_quantile((0, 10), 1, S.inclusive) == [10]
    assert tuple(fn.math_ratio(S.stats_quantile((0, 10), 0.25, S.inclusive)).one()) == (5, 2)
    assert fn.stats_quantile((0, 10), 0, S.exclusive) == [-10]
    assert fn.stats_quantile((0, 10), 1, S.exclusive) == [20]
    assert tuple(fn.stats_quantiles((0, 4, 8), 4, S.inclusive).one()) == (2, 4, 6)
    assert tuple(fn.stats_quantiles((0, 4, 8), 4, S.exclusive).one()) == (0, 4, 8)
    assert tuple(fn.stats_quantiles((7,), 4, S.exclusive).one()) == (7, 7, 7)
    assert tuple(fn.stats_quantiles((7,), 1, S.inclusive).one()) == ()
    assert fn.stats_mode((G("b"), G("a"), G("b"), G("a"), G("c"))) == [G("b"), G("a")]
    assert fn.once(S.stats_mode((G("b"), G("a"), G("b"), G("a")))) == [G("b")]
    assert list(fn.stats_mode((1, 1.0))) == [G(1), G(1.0)]
    assert len(fn.stats_mode((S["+"](1, 2), S["+"](1, 2), 9)).one()) == 3

    assert fn.stats_variance((1, 2, 3), 1) == [1]
    assert tuple(fn.math_ratio(S.stats_variance((1, 2, 3), 0)).one()) == (2, 3)
    assert fn.stats_variance((1, 2, 3), 2) == [2]
    assert fn.stats_variance((1000000000.0, 1000000001.0, 1000000002.0), 1) == [1.0]
    assert fn.stats_variance((7,), 0) == [0]
    assert fn.stats_stdev((1, 2, 3), 1) == [1.0]
    assert fn.stats_stdev((1, 3), 0) == [1.0]
    assert fn.math_class(S.stats_variance((-1.0e308, 1.0e308), 0)) == [S.infinite]
    assert fn.stats_stdev((-1.0e308, 1.0e308), 0) == [1.0e308]
    assert fn.stats_variance((-1.0e-300, 1.0e-300), 0) == [0.0]
    assert fn.stats_stdev((-1.0e-300, 1.0e-300), 0) == [1.0e-300]
    assert fn.stats_covariance((1, 2, 3), (1, 3, 5), 1) == [2]
    assert tuple(fn.math_ratio(S.stats_covariance((1, 2, 3), (1, 3, 5), 0)).one()) == (4, 3)
    assert fn.stats_correlation((-1.0e308, 1.0e308), (-1.0e308, 1.0e308)) == [1.0]
    assert fn.stats_correlation((-1.0e308, 1.0e308), (1.0e308, -1.0e308)) == [-1.0]
    assert tuple(fn.stats_ranks(()).one()) == ()
    assert tuple(fn.stats_ranks((30, 10, 20)).one()) == (3, 1, 2)
    assert tuple(fn.vector_scale(S.stats_ranks((1, 1.0, 2)), 2).one()) == (3, 3, 6)
    assert fn.stats_correlation(S.stats_ranks((1, 4, 9)), S.stats_ranks((1, 2, 3))) == [1.0]
    assert fn.stats_regression((0, 1, 2), (1, 5, 9), FALSE) == [S.linear_fit(4, 1)]
    assert fn.stats_regression((0.0, 1, 2), (1, 5, 9), FALSE) == [S.linear_fit(4.0, 1.0)]
    assert fn.stats_regression((2,), (6,), TRUE) == [S.linear_fit(3, 0)]
    assert fn.stats_regression((0, 1, 2), (7, 7, 7), FALSE) == [S.linear_fit(0, 7)]

    row = m.match(S["="](S.stats_variance(V.data, V.degrees), V.body)).one()
    recipe = S["|->"]((row.data, row.degrees), row.body)
    reconstructed = m.eval(recipe)[0]
    assert list(m.eval((reconstructed, (1, 2, 3), 1))) == [G(1)]
    row = m.match(S["="](S.stats_variance(V.data, 0), V.body)).one()
    recipe = S["|->"]((row.data,), row.body)
    specialized = m.eval(recipe)[0]
    assert list(m.eval((specialized, (1, 2, 3)))) == [fn.math_rational(2, 3)[0]]

    assert refused(S.stats_mean(()))
    assert refused(S.stats_sum((1, G("bad"))))
    assert refused(S.stats_geometric_mean(()))
    assert refused(S.stats_geometric_mean((0, -1)))
    assert refused(S.stats_harmonic_mean(()))
    assert refused(S.stats_harmonic_mean((0, -1)))
    assert refused(S.stats_median(()))
    assert refused(S.stats_quantile((1,), 2, S.inclusive))
    assert refused(S.stats_quantile((1,), 0.5, S.missing))
    assert refused(S.stats_quantiles((1,), 0, S.inclusive))
    assert refused(S.stats_quantiles((1,), 1, S.missing))
    assert refused(S.stats_mode(()))
    assert refused(S.stats_variance((1,), 1))
    assert refused(S.stats_variance((1, 2), -1))
    assert refused(S.stats_stdev((), 0))
    assert refused(S.stats_covariance((1, 2), (1,), 0))
    assert refused(S.stats_correlation((1, 1), (2, 3)))
    assert refused(S.stats_correlation((1,), (2,)))
    assert refused(S.stats_regression((1, 1), (2, 3), FALSE))
    assert refused(S.stats_regression((0,), (2,), TRUE))
    assert refused(S.stats_regression((1, 2), (3,), FALSE))
    infinity = fn.math_real(S.inf, ()).one()
    assert refused(S.stats_mean((infinity,)))


#: MEASURED: all 76 claims, including exact rational results, range-preserving
#: deviations and the complete refusal paths. The example pays 141717.
#: [measured 2026-09-12: 157714 inferences, minimum of three fresh serial processes;
#: command=python extensions/python/tools/twin_coverage.py --measure --rounds 3
#: examples/ch08-data/08-03-the-shipped-libraries/37-statistics_lib.metta;
#: fixture=lib_statistics with engine/lib QLF artifacts purged; commit=84824f5cf870f5cd7ac89d6580093d0459d91a9b].
#: RE-PINNED 2026-09-13, 157714 to 163787 (+6073), Combinatorics, Functional,
#: Pairs and Sets now derive collection operations through MeTTa equations,
#: segments and folds. This example imports the changed provider directly or
#: through its library dependencies [measured 2026-09-13: min-of-3 serial fresh
#: processes; command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=6471fbad35eced5ed6440ebf2c25a053b20221f3].
#: RE-PINNED 2026-09-13, 163787 to 165130 (+1343), The validated range
#: continuation now lives in the private support file rather than appearing as
#: a public library head. The import adds its measured loading cost without
#: changing the continuation body [measured 2026-09-13: min-of-3 serial fresh
#: processes; command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=6471fbad35eced5ed6440ebf2c25a053b20221f3].
#: RE-PINNED 2026-09-13, 165130 to 40107888 (+39942758), Math and Statistics
#: derive their recipes from MeTTa equations; Statistics consolidates finite
#: laws and adds reflective claims through Python space query and evaluation
#: doors. Their collection dependencies share the proper finite expression
#: boundary in lib/_support/collections_data.pl [measured 2026-09-13: min-of-3
#: serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=6fa571d1b7059b610f73e9feed657711414251e5].
#: RE-PINNED 2026-09-13, 40107888 to 40108091 (+203), Vector, Math and the
#: shared collection boundary declare their native effects. The engine reads
#: late provider declarations and retains definition analysis for computed
#: function heads [measured 2026-09-13: min-of-3 serial fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=1d0b78a359f58de49f2f98bed50a6480d56cd5f6].
#: RE-PINNED 2026-09-14, 40108091 to 40973899 (+865808), Functional applies
#: finished callback arguments through reduce; Statistics derives exact
#: coefficient rows and Combinatorics retires its native probability provider
#: [measured 2026-09-14: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=e1be99ea1c08f70444c1c35cada441e089777906].
#: RE-PINNED 2026-09-14, 40973899 to 40976038 (+2139), Vector derives fill,
#: random construction and normalized-dot through MeTTa equations;
#: Combinatorics supplies ranges, literal validation folds once before core
#: seeded draws, and the Vector example adds nine construction and refusal
#: claims. Native Math also imports the shared Vector kernels, so every MeTTa
#: and native consumer is renewed [measured 2026-09-14: min-of-3 serial fresh
#: processes; command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=c7bacead4feb29b9761d026b52b952e91b26b10b].
#: RE-PINNED 2026-09-21, 40976038 to 40692035 (-284003), the sixty libraries
#: derived in MeTTa landed with merge 97763e7fa eight hours after the previous
#: pin 55d451b67, so every example importing one now pays a MeTTa derivation
#: where it paid a Prolog body instead, which the 2026-09-14 ruling accepts
#: explicitly as the price of a library that survives the engine swap [measured
#: 2026-09-21: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=6e09cb25d5495c2db3283166e6ce4e07eefecfb2].
#: RE-PINNED 2026-09-24, 40692035 to 2379458 (-38312577), placed on the full-
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
#: RE-PINNED 2026-09-24, 2379458 to 2321701 (-57757), 0a81c782f loads a
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
#: RE-PINNED 2026-09-24, 2321701 to 2379633 (+57932), +57,902 at ae1cc8936,
#: where a registration batch of thirteen names or more walks the visible
#: predicate table at two inferences a predicate that asking per name spent
#: inside one C call, and a batch above forty tests each predicate with a dict
#: at one inference fewer than the AVL; +30 at b5eb39acd, whose three new
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
#: RE-PINNED 2026-09-24, 2379633 to 2379055 (-578), d4a365c16 holds the support
#: graph's visited set and the reference refresh's space sets in SWI tries
#: instead of library(nb_set): a membership check is one foreign call where
#: nb_set probed in Prolog, four inferences a step past a taken slot, from a
#: slot a library space's path-bearing name decided, and a walk over a node or
#: two pays a few inferences more for the trie's setup (-251); gate-perf's
#: d781eab8f carries an exact removal's selected head from the code that
#: selected it, so a withdrawal copies its equation once: 23 inferences fewer
#: for each equation removal the twin adopts and 4 for each it selects (-437);
#: the packages job's 90be572a9 and 4003462fe register Prolog through one
#: engine service: +22 for each library the twin imports (ten new engine
#: predicates and two user imports in the registration walk at two inferences
#: each, less the retired loaded_extension_file/2), and 146 inferences for a
#: Prolog file's origin or 220 for a text's SHA-256 on a twin that registers
#: Prolog (+110); each step read serially on its own committed tree, from gate-
#: perf's pin at c7d7244fb, and the fixed tree 4ff69551e reads what 4003462fe
#: does [measured 2026-09-24: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=4ff69551e0e226442cf7257b96af858adda957a4].
#: RE-PINNED 2026-09-24, 2379055 to 2379065 (+10), +10 at the change this re-
#: pin lands with, which groups a whole reference face's heads in one pass over
#: its sorted entries where each head searched the whole face, and whose three
#: imports into the engine module are one more predicate filereader's
#: registration walk reads above twelve names, pairs_keys/2, and three a
#: restricted space's core steps over as it enumerates that module's predicates
#: [measured 2026-09-24: the twins lane alone on the base 8d651070d and on the
#: base with this change, one after the other in battery 117's one path, every
#: component at its pin; command=sh tools/check.sh twins (twin_coverage.py
#: inside tools/bounded.sh); commit=8bda9d5525a8174a8304376e111df8da258076a9].
#: RE-PINNED 2026-09-24, 2379065 to 2379487 (+422), +422 at the change this re-
#: pin lands with, which publishes a from row by itself when rows are all a
#: space owes: its 36 predicates visible to filereader's registration walk cost
#: a batch above twelve names 72 inferences, each restricted space's core about
#: 28 a predicate, and every whole publication and face event its ledger's
#: bookkeeping [measured 2026-09-24: the twins lane alone on 8d651070d with the
#: change before this one and with this change too, one after the other in
#: battery 117's one path, every component at its pin; command=sh
#: tools/check.sh twins (twin_coverage.py inside tools/bounded.sh);
#: commit=e4b7448d1f1bd98733f1b04c3906aaa42f35ef1a].
#: RE-PINNED 2026-09-24, 2379487 to 2379454 (-33), the host switch of
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
#: RE-PINNED 2026-09-25, 2379454 to 2379465 (+11), the pragma refusal defines
#: require_metta_pragma_capability/2 in the engine module, and on the same tree
#: defining it without calling it moves this twin by the whole of the change's
#: move, so the cost is one more engine predicate and functor met through the
#: engine's walks over its predicate and functor tables, among them
#: filereader:existing_predicate_arities/2, which charges two inferences for
#: each predicate visible from the loading module at every load of a source
#: registering more than twelve names (i-arity-walk-all-predicates); the
#: change's work at a pragma write does not reach this twin [measured
#: 2026-09-25T00:48:45+10:00: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-25, 2379465 to 2379565 (+100), the py-* doors change makes
#: more predicates visible from filereader, and
#: filereader:existing_predicate_arities/2 walks every predicate visible there
#: at two inferences each whenever a source registering more than twelve names
#: loads: on one tree the change's new engine predicates alone, defined with
#: their two boot uses taken out, make eight more visible and move this twin by
#: 16 for each such load, and the whole change by 20, ten more at its loads
#: (i-arity-walk-all-predicates) [measured 2026-09-25T02:52:36+10:00: min-of-3
#: serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-25, 2379565 to 2379570 (+5), the registration refusal kind
#: makes the (vocabulary refusal-kind ...) catalog row fifteen members long
#: instead of fourteen, which moves it from storage arity 17 to 18, where the
#: Python seat's (vocabulary door-answers ...) already sits, so &metta keeps
#: one storage arity fewer and each open-tail catalog lookup,
#: metta_catalog_clause/2 visiting every arity, costs five inferences less; and
#: metta_host_signal_message//2 is one more predicate the engine module
#: defines, which every walk over the engine's predicates pays: filereader's
#: existing_predicate_arities/2 two inferences a registration of more than
#: twelve names, each restricted space's core 29, and 11-reference_rows' walk
#: 240, each reproduced exactly by one inert predicate added to the engine on
#: the base [measured 2026-09-25T06:38:29+10:00: min-of-3 serial fresh
#: processes; command=python extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-25, 2379570 to 2374355 (-5215), the host evaluation door
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
#: more than twelve names [measured 2026-09-25T06:47:57+10:00: min-of-3 serial
#: fresh processes; command=python extensions/python/tools/twin_coverage.py
#: --repin].
#: RE-PINNED 2026-09-25, 2374355 to 2374405 (+50), Runtime.reclaim(), the
#: reclamation barrier metta_py_reclaim/1, adds five predicates to user, and
#: existing_predicate_arities/2 walks every user predicate about twice per
#: large load (i-arity-walk-all-predicates) [measured
#: 2026-09-25T11:25:25+10:00: one full twins lane before this commit and one
#: with it, the two read on one battery path at the landing's HEAD;
#: command=python extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-25, 2374405 to 2374433 (+28), both specializer doors
#: prepare a specialization's predicate with
#: spaces:metta_prepare_function_predicate/3 before asserting its clauses
#: [measured 2026-09-25T11:29:10+10:00: one full twins lane before this commit
#: and one with it, the two read on one battery path at the landing's HEAD;
#: command=python extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-25, 2374433 to 2374453 (+20), retiring a library importer
#: derives the arity row again from any backing head a library home still
#: registers, journalled to the load that owns it [measured
#: 2026-09-25T11:33:06+10:00: one full twins lane before this commit and one
#: with it, the two read on one battery path at the landing's HEAD;
#: command=python extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-25, 2374453 to 2374959 (+506), every force of a waiting
#: function names the module it is made from, through fun_home_in/3, and a
#: write forces only its own space [measured 2026-09-25T16:54:32+10:00: one
#: full twins lane before this commit and one with it, the two read on one
#: battery path at the landing's HEAD; command=python
#: extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-25, 2374959 to 2359547 (-15412), lambdas are named by
#: their content and a copy restores its source's rows as a program [measured
#: 2026-09-25T17:00:15+10:00: one full twins lane before this commit and one
#: with it, the two read on one battery path at the landing's HEAD;
#: command=python extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-25, 2359547 to 2359563 (+16), engine/source_loading.pl's
#: load-error clause moved from the thread_local user:thread_message_hook/3 to
#: the global user:message_hook/3, so every thread and engine now runs the
#: check the main thread always ran: one inference per message while no load is
#: open there (clause(watching, true, _) fails) and two inside one
#: (load_failure/2 rejects the silent kind); the Python seat prints a twin's
#: library-load messages inside engines, where no clause ran before, and the
#: original's side does not move [measured 2026-09-25T18:42:59+10:00: min-of-3
#: serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-25, 2359563 to 2359568 (+5), the erase audit routes three
#: engine releases through host_transactions:try_erase/1, whose ignore/1 frame
#: costs about 1.5 inferences more per release than the bare erase/1 it
#: replaces: a forgotten specialization's clauses and an equation's token and
#: binding rows (engine/filereader.pl), a removed equation's two function-
#: metadata rows (engine/translator/analysis.pl) and a typing rule's entry
#: (engine/type_rules.pl); applying the change one engine file at a time at
#: superproject 3a6b92b40 puts the whole move on those three files [measured
#: 2026-09-25T20:40:42+10:00: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-25, 2359568 to 2359578 (+10), a sweep of a module's
#: generated predicates retires the records describing each swept predicate,
#: and a release the rest of the module's [measured 2026-09-25T23:29:52+10:00:
#: one full twins lane before this commit and one with it, the two read on one
#: battery path at the landing's HEAD; command=python
#: extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-26, 2359578 to 2359668 (+90), engine/metta/control.pl's
#: partial/3 to partial/11, the clauses that let a Prolog meta-predicate call a
#: partial function value, are nine more predicates visible from filereader,
#: and filereader:existing_predicate_arities/2's batch walk, which a load
#: registering more than twelve names runs, pays two inferences for each: 18 a
#: batch, the original and the twin alike, and nine inert facts of those
#: arities move it the same [measured 2026-09-26T01:31:12+10:00: min-of-3
#: serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-26, 2359668 to 2359768 (+100), the reference faces of a
#: strongly connected component of from rows are computed together by label-
#: setting, which moves this program's face computation by +1 inferences; the
#: other +99 inferences is the ten more predicates it makes visible from
#: metta_engine, which a control adding only ten unused predicates to
#: metta_engine reads the same [measured 2026-09-26T03:10:48+10:00: min-of-3
#: serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
BUDGET = 2359768

#: RETIRED: the former 1826-inference overrun. The 78-claim MeTTa recipe now
#: costs 40092306 and its twin 40107888, within the ordinary band.
#: [measured 2026-09-13: minimum of three fresh serial processes;
#: command=python extensions/python/tools/twin_coverage.py --measure --rounds 3
#: examples/ch08-data/08-03-the-shipped-libraries/37-statistics_lib.metta;
#: fixture=78 claims with engine/lib QLF artifacts purged; commit=6fa571d1b7059b610f73e9feed657711414251e5].
