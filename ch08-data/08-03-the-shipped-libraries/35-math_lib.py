"""Purpose: exact number operations and native floating functions.

Guarantees: the same 74 claims as 35-math_lib.metta.
[tested: python extensions/python/tools/twin_coverage.py examples/ch08-data/08-03-the-shipped-libraries/35-math_lib.metta; commit=6fa571d1b7059b610f73e9feed657711414251e5].
"""

from metta import G, S, lib
from metta._errors.errors import MettaError


def twin(m):
    """Compute exact numbers, stream factors and apply native floating functions."""
    m += lib.math

    def refused(call):
        """Read a native refusal through the evaluation boundary."""
        try:
            list(m.eval(call))
        except MettaError:
            return True
        return False

    gcd, lcm = m.fn.math_gcd, m.fn.math_lcm
    ratio, rationalize = m.fn.math_ratio, m.fn.math_rationalize
    root, power = m.fn.math_integer_root, m.fn.math_power_mod
    classify, real = m.fn.math_class, m.fn.math_real

    assert m.fn.factorial(20) == [2432902008176640000]
    assert m.fn.binomial(52, 5) == [2598960]
    assert gcd(()) == [0]
    assert gcd((0, 0)) == [0]
    assert gcd((-18, 24, 30)) == [6]
    assert gcd((18446744073709551616, 36893488147419103232)) == [18446744073709551616]
    assert lcm(()) == [1]
    assert lcm((-6, 8, 15)) == [120]
    assert lcm((0, 5)) == [0]

    assert m.fn.mul(S.math_rational(1, 3), 3) == [1]
    assert tuple(ratio(S.math_rational(10, -20)).one()) == (-1, 2)
    assert classify(S.math_rational(6, 3)) == [S.integer]
    assert classify(S.math_rational(1, 3)) == [S.rational]
    assert tuple(ratio(0.1).one()) == (3602879701896397, 36028797018963968)
    assert tuple(ratio(S.math_rational(0.1)).one()) == (3602879701896397, 36028797018963968)
    assert tuple(ratio(-0.0).one()) == (0, 1)
    assert tuple(ratio(S.math_rationalize(0.1)).one()) == (1, 10)
    assert rationalize(42) == [42]
    assert tuple(ratio(S.math_rationalize(S.math_rational(2, 3))).one()) == (2, 3)

    assert tuple(root(2, 101).one()) == (10, 1)
    assert tuple(root(3, -28).one()) == (-3, -1)
    assert tuple(root(1, -42).one()) == (-42, 0)
    assert tuple(root(2, 340282366920938463463374607431768211456).one()) == (18446744073709551616, 0)
    assert power(2, 100, 1000) == [376]
    assert power(-2, 3, 5) == [2]
    assert power(42, 0, 1) == [0]
    assert [tuple(pair) for pair in m.fn.math_factor_pairs(1)] == [(1, 1)]
    assert [tuple(pair) for pair in m.fn.math_factor_pairs(36)] == [(1, 36), (2, 18), (3, 12), (4, 9), (6, 6)]
    assert tuple(m.fn.once(S.math_factor_pairs(36)).one()) == (1, 36)

    assert m.fn.math_sqrt(4) == [2.0]
    assert m.fn.math_sqrt(S.bit_shift_left(1, 2000)) == m.fn.math_float(S.bit_shift_left(1, 1000))
    assert m.fn.math_sqrt(S.math_rational(1, S.bit_shift_left(1, 2000))) == m.fn.math_float(
        S.math_rational(1, S.bit_shift_left(1, 1000)))
    assert real(S.copysign, (1.0, S.math_sqrt(-0.0))) == [-1.0]
    assert refused(S.math_sqrt(-1))
    assert refused(S.math_sqrt(S.math_real(S.inf, ())))

    assert m.fn.math_float(S.math_rational(1, 10)) == [0.1]
    assert classify(S.math_float(1)) == [S.normal]
    assert classify(S.math_float(-0.0)) == [S.zero]
    assert real(S.copysign, (1.0, S.math_float(-0.0))) == [-1.0]
    assert classify(S.math_float(S.math_rational(18014398509481985, S.bit_shift_left(1, 1129)))) == [S.subnormal]
    assert classify(S.math_float(S.bit_shift_left(1, 2000))) == [S.infinite]

    assert len(m.fn.math_real_functions().one()) == 20
    assert real(S.sinh, (0,)) == [0.0]
    assert real(S.cosh, (0,)) == [1.0]
    assert real(S.tanh, (0,)) == [0.0]
    assert real(S.asinh, (0,)) == [0.0]
    assert real(S.acosh, (1,)) == [0.0]
    assert real(S.atanh, (0,)) == [0.0]
    assert real(S.log10, (100,)) == [2.0]
    assert real(S.erf, (0,)) == [0.0]
    assert real(S.erfc, (0,)) == [1.0]
    assert real(S.lgamma, (1,)) == [0.0]
    assert real(S.atan2, (1, 1)).one() == m.fn.truediv(S.math_real(S.pi, ()), 4).one()
    assert real(S.nexttoward, (1.0, 2.0)) == [1.0000000000000002]
    assert real(S["float_integer_part"], (-1.75,)) == [-1.0]
    assert real(S["float_fractional_part"], (-1.75,)) == [-0.75]
    assert real(S.e, ()).one() > 2.7
    assert real(S.epsilon, ()) == [2.220446049250313e-16]
    assert classify(S.math_real(S.inf, ())) == [S.infinite]
    assert classify(S.math_real(S.nan, ())) == [S.nan]

    assert refused(S.math_gcd((1, 2.5)))
    assert refused(S.math_lcm((0, 2.5)))
    assert refused(S.math_rational(1, 0))
    assert refused(S.math_ratio(S.math_real(S.inf, ())))
    assert refused(S.math_rationalize(S.math_real(S.nan, ())))
    assert refused(S.math_integer_root(0, 5))
    assert refused(S.math_integer_root(2, -1))
    assert refused(S.math_power_mod(2, -1, 5))
    assert refused(S.math_power_mod(2, 3, 0))
    assert refused(S.math_factor_pairs(0))
    assert refused(S.math_real(S.missing, (1,)))
    assert refused(S.math_real(S.atan2, (1,)))
    assert refused(S.math_real(S.erf, (G("x"),)))
    assert refused(S.math_real(S.acosh, (0,)))


#: MEASURED: all 67 claims, including exact arithmetic, streamed factors,
#: native floating dispatch and refusals. The example pays 118980 inferences.
#: [measured 2026-09-12: 121592 inferences, minimum of three fresh serial processes;
#: command=python extensions/python/tools/twin_coverage.py --measure --rounds 3
#: examples/ch08-data/08-03-the-shipped-libraries/35-math_lib.metta;
#: fixture=lib_math at its functional commit with engine/lib QLF artifacts purged;
#: commit=4d17f1af15fe125e3b8cd488502ba1e0e688fb3e].
#: RE-PINNED 2026-09-12, 121592 to 121599 (+7), Vector now exports its existing
#: fraction_sqrt native service; the additional module export moves each
#: measured library import by seven inferences while the numerical
#: implementations and MeTTa heads stay unchanged [measured 2026-09-12: min-
#: of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=84824f5cf870f5cd7ac89d6580093d0459d91a9b].
#: RE-PINNED 2026-09-13, 121599 to 192956 (+71357), Combinatorics, Functional,
#: Pairs and Sets now derive collection operations through MeTTa equations,
#: segments and folds. This example imports the changed provider directly or
#: through its library dependencies [measured 2026-09-13: min-of-3 serial fresh
#: processes; command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=6471fbad35eced5ed6440ebf2c25a053b20221f3].
#: RE-PINNED 2026-09-13, 192956 to 194299 (+1343), The validated range
#: continuation now lives in the private support file rather than appearing as
#: a public library head. The import adds its measured loading cost without
#: changing the continuation body [measured 2026-09-13: min-of-3 serial fresh
#: processes; command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=6471fbad35eced5ed6440ebf2c25a053b20221f3].
#: RE-PINNED 2026-09-13, 194299 to 361166 (+166867), Math and Statistics derive
#: their recipes from MeTTa equations; Statistics consolidates finite laws and
#: adds reflective claims. Their collection dependencies share the proper
#: finite expression boundary in lib/_support/collections_data.pl [measured
#: 2026-09-13: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=6fa571d1b7059b610f73e9feed657711414251e5].
#: RE-PINNED 2026-09-13, 361166 to 361369 (+203), Vector, Math and the shared
#: collection boundary declare their native effects. The engine reads late
#: provider declarations and retains definition analysis for computed function
#: heads [measured 2026-09-13: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=1d0b78a359f58de49f2f98bed50a6480d56cd5f6].
#: RE-PINNED 2026-09-14, 361369 to 357368 (-4001), Functional applies finished
#: callback arguments through reduce; Statistics derives exact coefficient rows
#: and Combinatorics retires its native probability provider [measured
#: 2026-09-14: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=e1be99ea1c08f70444c1c35cada441e089777906].
#: RE-PINNED 2026-09-14, 357368 to 359493 (+2125), Vector derives fill, random
#: construction and normalized-dot through MeTTa equations; Combinatorics
#: supplies ranges, literal validation folds once before core seeded draws, and
#: the Vector example adds nine construction and refusal claims. Native Math
#: also imports the shared Vector kernels, so every MeTTa and native consumer
#: is renewed [measured 2026-09-14: min-of-3 serial fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=c7bacead4feb29b9761d026b52b952e91b26b10b].
#: RE-PINNED 2026-09-21, 359493 to 439898 (+80405), the sixty libraries derived
#: in MeTTa landed with merge 97763e7fa eight hours after the previous pin
#: 55d451b67, so every example importing one now pays a MeTTa derivation where
#: it paid a Prolog body instead, which the 2026-09-14 ruling accepts
#: explicitly as the price of a library that survives the engine swap [measured
#: 2026-09-21: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=6e09cb25d5495c2db3283166e6ce4e07eefecfb2].
#: RE-PINNED 2026-09-24, 439898 to 456262 (+16364), placed on the full-
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
#: RE-PINNED 2026-09-24, 456262 to 398505 (-57757), 0a81c782f loads a library's
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
#: RE-PINNED 2026-09-24, 398505 to 410030 (+11525), +11,519 at ae1cc8936, where
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
#: RE-PINNED 2026-09-24, 410030 to 409820 (-210), d4a365c16 holds the support
#: graph's visited set and the reference refresh's space sets in SWI tries
#: instead of library(nb_set): a membership check is one foreign call where
#: nb_set probed in Prolog, four inferences a step past a taken slot, from a
#: slot a library space's path-bearing name decided, and a walk over a node or
#: two pays a few inferences more for the trie's setup (-2); gate-perf's
#: d781eab8f carries an exact removal's selected head from the code that
#: selected it, so a withdrawal copies its equation once: 23 inferences fewer
#: for each equation removal the twin adopts and 4 for each it selects (-230);
#: the packages job's 90be572a9 and 4003462fe register Prolog through one
#: engine service: +22 for each library the twin imports (ten new engine
#: predicates and two user imports in the registration walk at two inferences
#: each, less the retired loaded_extension_file/2), and 146 inferences for a
#: Prolog file's origin or 220 for a text's SHA-256 on a twin that registers
#: Prolog (+22); each step read serially on its own committed tree, from gate-
#: perf's pin at c7d7244fb, and the fixed tree 4ff69551e reads what 4003462fe
#: does [measured 2026-09-24: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=4ff69551e0e226442cf7257b96af858adda957a4].
#: RE-PINNED 2026-09-24, 409820 to 409956 (+136), +134 at the change this re-
#: pin lands with, which publishes a from row by itself when rows are all a
#: space owes: its 36 predicates visible to filereader's registration walk cost
#: a batch above twelve names 72 inferences, each restricted space's core about
#: 28 a predicate, and every whole publication and face event its ledger's
#: bookkeeping [measured 2026-09-24: the twins lane alone on 8d651070d with the
#: change before this one and with this change too, one after the other in
#: battery 117's one path, every component at its pin; command=sh
#: tools/check.sh twins (twin_coverage.py inside tools/bounded.sh);
#: commit=e4b7448d1f1bd98733f1b04c3906aaa42f35ef1a].
#: RE-PINNED 2026-09-24, 409956 to 409940 (-16), the host switch of
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
BUDGET = 409940
