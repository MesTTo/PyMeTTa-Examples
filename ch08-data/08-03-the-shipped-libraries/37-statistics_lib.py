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
BUDGET = 2379055

#: RETIRED: the former 1826-inference overrun. The 78-claim MeTTa recipe now
#: costs 40092306 and its twin 40107888, within the ordinary band.
#: [measured 2026-09-13: minimum of three fresh serial processes;
#: command=python extensions/python/tools/twin_coverage.py --measure --rounds 3
#: examples/ch08-data/08-03-the-shipped-libraries/37-statistics_lib.metta;
#: fixture=78 claims with engine/lib QLF artifacts purged; commit=6fa571d1b7059b610f73e9feed657711414251e5].
