"""Purpose: prove exact additive conditioning and inspect its MeTTa recipe.

Guarantees: the example's exact masses, marginals, literal identities and
alternative rows have matching answers and stored content [tested: twin;
commit=e1be99ea1c08f70444c1c35cada441e089777906].
"""

from metta import S, V, lib


def twin(m):
    """Use Statistics for exact laws and ordinary matching for their recipes."""
    m += lib.statistics
    mass = m.fn.weighted_subset_mass_independent
    posterior = m.fn.weighted_subset_posterior_independent

    assert posterior((S.candidate(S.pump_a, 2, S.ratio(1, 2)),
                      S.candidate(S.pump_b, 3, S.ratio(1, 4))), 2) == [
        S.subset_posterior(S.ratio(3, 8),
                          (S.candidate_posterior(S.pump_a, S.ratio(1, 1)),
                           S.candidate_posterior(S.pump_b, S.ratio(0, 1))))]
    assert posterior((S.candidate(S.left, 1, S.ratio(1, 2)),
                      S.candidate(S.right, 1, S.ratio(1, 2))), 1) == [
        S.subset_posterior(S.ratio(1, 2),
                          (S.candidate_posterior(S.left, S.ratio(1, 2)),
                           S.candidate_posterior(S.right, S.ratio(1, 2))))]
    assert posterior((S.candidate(S.metadata_flag, 0, S.ratio(1, 3)),
                      S.candidate(S.failing_part, 2, S.ratio(1, 2))), 2) == [
        S.subset_posterior(S.ratio(1, 2),
                          (S.candidate_posterior(S.metadata_flag, S.ratio(1, 3)),
                           S.candidate_posterior(S.failing_part, S.ratio(1, 1))))]
    assert mass((S.candidate(S.absent, 5, S.ratio(0, 1)),), 5) == [S.ratio(0, 1)]
    assert mass((S.candidate(S.scaled_loss, 125, S.ratio(2, 5)),), 125) == [S.ratio(2, 5)]
    assert posterior((), 0) == [S.subset_posterior(S.ratio(1, 1), ())]
    assert posterior((S.candidate(1, 0, S.ratio(1, 2)),
                      S.candidate(1.0, 0, S.ratio(1, 3))), 0) == [
        S.subset_posterior(S.ratio(1, 1),
                          (S.candidate_posterior(1, S.ratio(1, 2)),
                           S.candidate_posterior(1.0, S.ratio(1, 3))))]
    assert posterior((S.candidate(S["+"](1, 2), 0, S.ratio(1, 2)),
                      S.candidate(S.Error(S.a, S.b), 0, S.ratio(1, 3))), 0) == [
        S.subset_posterior(S.ratio(1, 1),
                          (S.candidate_posterior(S["+"](1, 2), S.ratio(1, 2)),
                           S.candidate_posterior(S.Error(S.a, S.b), S.ratio(1, 3))))]
    laws = ((S.candidate(S.a, 1, S.ratio(1, 2)),),
            (S.candidate(S.a, 1, S.ratio(1, 2)),),
            (S.candidate(S.b, 1, S.ratio(1, 3)),))
    assert [answer for rows in laws for answer in mass(rows, 1)] == [
        S.ratio(1, 2), S.ratio(1, 2), S.ratio(1, 3)]

    row = m.match(S["="](S.weighted_subset_mass_independent(V.rows, V.target), V.body)).one()
    recipe = m.eval(S["|->"]((row.rows, row.target), row.body))[0]
    assert m.eval((recipe, S.quote((S.candidate(S.a, 1, S.ratio(1, 3)),)), 1)) == [S.ratio(1, 3)]

    m += S.subset_event(S.from_space, 2, S.ratio(1, 3))
    m += S.subset_event(S.other, 3, S.ratio(1, 4))
    rows = tuple(S.candidate(row.id, row.loss, row.prior)
                 for row in m.match(S.subset_event(V.id, V.loss, V.prior)))
    assert mass(rows, 2) == [S.ratio(1, 4)]


#: The eleven claims exercise exact masses, inclusion marginals, literal IDs,
#: alternative candidate rows and reconstruction of a stored MeTTa equation.
#: [measured: 1755787 inferences against example1749167, minimum of three
#: serial fresh processes; command=python extensions/python/tools/twin_coverage.py
#: --measure --rounds 3 examples/ch22-a-reasoner-you-can-serve/22-02-weighted-answers/11-weighted_subset_posterior.metta;
#: fixture=Statistics MeTTa coefficient rows, QLFs purged before measurement;
#: commit=e1be99ea1c08f70444c1c35cada441e089777906].
#: RE-PINNED 2026-09-14, 1755787 to 1757926 (+2139), Vector derives fill,
#: random construction and normalized-dot through MeTTa equations;
#: Combinatorics supplies ranges, literal validation folds once before core
#: seeded draws, and the Vector example adds nine construction and refusal
#: claims. Native Math also imports the shared Vector kernels, so every MeTTa
#: and native consumer is renewed [measured 2026-09-14: min-of-3 serial fresh
#: processes; command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=c7bacead4feb29b9761d026b52b952e91b26b10b].
#: RE-PINNED 2026-09-21, 1757926 to 1832370 (+74444), the sixty libraries
#: derived in MeTTa landed with merge 97763e7fa eight hours after the previous
#: pin 55d451b67, so every example importing one now pays a MeTTa derivation
#: where it paid a Prolog body instead, which the 2026-09-14 ruling accepts
#: explicitly as the price of a library that survives the engine swap [measured
#: 2026-09-21: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=6e09cb25d5495c2db3283166e6ce4e07eefecfb2].
#: RE-PINNED 2026-09-24, 1832370 to 1867451 (+35081), placed on the full-
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
#: RE-PINNED 2026-09-24, 1867451 to 1809694 (-57757), 0a81c782f loads a
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
#: RE-PINNED 2026-09-24, 1809694 to 1867626 (+57932), +57,902 at ae1cc8936,
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
#: RE-PINNED 2026-09-24, 1867626 to 1867238 (-388), d4a365c16 holds the support
#: graph's visited set and the reference refresh's space sets in SWI tries
#: instead of library(nb_set): a membership check is one foreign call where
#: nb_set probed in Prolog, four inferences a step past a taken slot, from a
#: slot a library space's path-bearing name decided, and a walk over a node or
#: two pays a few inferences more for the trie's setup (-61); gate-perf's
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
#: RE-PINNED 2026-09-24, 1867238 to 1867248 (+10), +10 at the change this re-
#: pin lands with, which groups a whole reference face's heads in one pass over
#: its sorted entries where each head searched the whole face, and whose three
#: imports into the engine module are one more predicate filereader's
#: registration walk reads above twelve names, pairs_keys/2, and three a
#: restricted space's core steps over as it enumerates that module's predicates
#: [measured 2026-09-24: the twins lane alone on the base 8d651070d and on the
#: base with this change, one after the other in battery 117's one path, every
#: component at its pin; command=sh tools/check.sh twins (twin_coverage.py
#: inside tools/bounded.sh); commit=8bda9d5525a8174a8304376e111df8da258076a9].
#: RE-PINNED 2026-09-24, 1867248 to 1867670 (+422), +422 at the change this re-
#: pin lands with, which publishes a from row by itself when rows are all a
#: space owes: its 36 predicates visible to filereader's registration walk cost
#: a batch above twelve names 72 inferences, each restricted space's core about
#: 28 a predicate, and every whole publication and face event its ledger's
#: bookkeeping [measured 2026-09-24: the twins lane alone on 8d651070d with the
#: change before this one and with this change too, one after the other in
#: battery 117's one path, every component at its pin; command=sh
#: tools/check.sh twins (twin_coverage.py inside tools/bounded.sh);
#: commit=e4b7448d1f1bd98733f1b04c3906aaa42f35ef1a].
#: RE-PINNED 2026-09-24, 1867670 to 1867653 (-17), the host switch of
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
#: RE-PINNED 2026-09-25, 1867653 to 1867664 (+11), the pragma refusal defines
#: require_metta_pragma_capability/2 in the engine module, and on the same tree
#: defining it without calling it moves this twin by the whole of the change's
#: move, so the cost is one more engine predicate and functor met through the
#: engine's walks over its predicate and functor tables, among them
#: filereader:existing_predicate_arities/2, which charges two inferences for
#: each predicate visible from the loading module at every load of a source
#: registering more than twelve names (i-arity-walk-all-predicates); the
#: change's work at a pragma write does not reach this twin [measured
#: 2026-09-25T00:49:10+10:00: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
BUDGET = 1867664
