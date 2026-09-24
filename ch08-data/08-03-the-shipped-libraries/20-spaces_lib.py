"""Purpose: every lib_spaces operation over whole spaces, from Python.

A space is a handle, so the bulk operations take handles and the patterns are
built terms. Each one answers once per atom it touched, and a list of those
answers is the count of work it did.

Guarantees: the same claims as 20-spaces_lib.metta
[tested: python extensions/python/tools/twin_coverage.py examples/ch08-data/08-03-the-shipped-libraries/20-spaces_lib.metta; commit=a8b4bab6eb0bf1b42eb441e9145144cf91befa7d].
Open Obligations:
  To Do: None
  Hacks: None
  Future Enhancements: None.
"""

import metta
from metta import G, S, V, lib


def twin(m):
    """Count, find, copy, move, drain, snapshot, subtract and clear."""
    m += lib.spaces

    ledger = metta.space(S.ledger)
    ledger += S.entry(S.rent, 1200)
    ledger += S.entry(S.food, 300)
    ledger += S.note(G("checked"))

    count, find = m.fn["match-count"], m.fn.find
    copy, move = m.fn["space-copy"], m.fn["move-atoms"]
    drain, snapshot = m.fn["space-drain"], m.fn["space-snapshot"]
    subtract, clear = m.fn["space-subtract"], m.fn["remove-all-atoms"]
    entry = S.entry(V.what, V.amount)

    # match-count folds over a match that answers 1 per solution, so nothing is
    # materialised and a pattern nothing matches counts 0.
    assert count(ledger, entry) == [2]
    assert count(ledger, S.invoice(V.n)) == [0]

    # find is a match reduced to a Bool, and succeedsPredicate asks the same of
    # a Prolog-shaped call.
    assert find(ledger, S.entry(S.rent, V.amount)) == [True]
    assert find(ledger, S.entry(S.car, V.amount)) == [False]
    assert m.fn.succeedsPredicate((ledger, S.entry, S.rent, V.amount)) == [True]

    # space-copy leaves the source alone; a bare variable pattern copies
    # everything, which is how one space merges into another.
    audit = metta.space(S.audit)
    assert sorted(copy(ledger, audit, entry)) == [True, True]
    assert count(audit, entry) == [2]
    assert count(ledger, entry) == [2]
    everything = metta.space(S.everything)
    assert sorted(copy(ledger, everything, V.any)) == [True, True, True]
    assert len(everything) == 3

    # space-snapshot mints the destination itself, so what a space holds now
    # survives later writes to it.
    before = metta.space(snapshot(ledger).one())
    assert len(before) == 3
    ledger += S.entry(S.travel, 90)
    assert len(before) == 3
    assert len(ledger) == 4

    # move-atoms is what migrateAtoms' NAME promises.
    archive = metta.space(S.archive)
    assert move(ledger, archive, S.entry(S.travel, V.amount)) == [True]
    assert [(row.what, row.amount) for row in archive[entry]] == [(S.travel, 90)]
    assert count(ledger, S.entry(S.travel, V.amount)) == [0]

    # migrateAtoms keeps upstream's own equation, which names the source on both
    # sides: it drains, and the destination stays empty. The behaviour rather
    # than the name is what a program relies on.
    nowhere = metta.space(S.nowhere)
    assert [tuple(answer) for answer in m.fn.migrateAtoms(
        ledger, nowhere, S.entry(S.food, V.amount)
    )] == [(True, True)]
    assert list(nowhere) == []
    assert count(ledger, S.entry(S.food, V.amount)) == [0]

    # space-drain answers the atoms it removed.
    assert list(drain(ledger, S.note(V.text))) == [S.note(G("checked"))]
    assert list(ledger) == [S.entry(S.rent, 1200)]

    # space-subtract removes every atom another space holds; an atom the space
    # does not hold answers the removal's ordinary verdict.
    assert sorted(subtract(everything, audit)) == [True, True]
    assert list(everything) == [S.note(G("checked"))]
    assert sorted(subtract(everything, audit)) == [True, True]

    # remove-all-atoms clears a space. Its own body is a collapse over every
    # atom's removal, so one call answers one expression of verdicts.
    assert [tuple(answer) for answer in clear(everything)] == [(True,)]
    assert list(everything) == []
    assert [tuple(answer) for answer in clear(everything)] == [()]


#: MEASURED on this branch rather than inherited: this twin is new, so there is
#: no earlier pin to move. The 27 claims cover all nine lib_spaces heads; the
#: example pays 45,668 inferences for the same work
#: [measured 2026-09-12: 43720 inferences, minimum of three serial fresh
#: processes; command=python extensions/python/tools/twin_coverage.py --measure
#: --rounds 3 examples/ch08-data/08-03-the-shipped-libraries/20-spaces_lib.metta;
#: fixture=lib_spaces at its functional commit, artifacts purged before the run;
#: commit=a8b4bab6eb0bf1b42eb441e9145144cf91befa7d].
#: RE-PINNED 2026-09-21, 43720 to 44083 (+363), the sixty libraries derived in
#: MeTTa landed with merge 97763e7fa eight hours after the previous pin
#: 55d451b67, so every example importing one now pays a MeTTa derivation where
#: it paid a Prolog body instead, which the 2026-09-14 ruling accepts
#: explicitly as the price of a library that survives the engine swap [measured
#: 2026-09-21: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=6e09cb25d5495c2db3283166e6ce4e07eefecfb2].
#: RE-PINNED 2026-09-24, 44083 to 48014 (+3931), placed on the full-
#: configuration first-parent ladder from the pin commit 6e09cb25d: a7955cd07
#: carried lib 629c86c, the library split, which moved every library's surface
#: out of its pkg.metta manifest into lib.metta beside it, so an import reads
#: the manifest and then imports the library's own source as a second file;
#: 54784fded reads the builtin type surface from every .metta in
#: lib_builtin_types' directory, which restored the 195 builtin cost rows the
#: split's manifest-only read had dropped; 63b910f4f added a clause to
#: metta_reference_internal/2 that asks the specializer's ho_specialization/3
#: registry, so every reference grade a load computes pays that lookup, which
#: is how defined-name, documented and undocumented stopped reporting
#: specializer residues; 814b99468 retains a self-call's function_view
#: dependency, so a recursive body is rebuilt as a caller of its own function
#: whenever an arriving equation changes that view (fib's rebuilds 1 to 2 and
#: newtons_method's energy 2 to 4, each reached from spaces:add_function_atom/7
#: through lib_memo's automatic reconcile), the fix that took lib_statistics
#: and lib_random to green; d6e09995c retires a load's package rows from every
#: space but its library home after package_load/3, withdrawing each through
#: metta_remove_atom_reference/1, which uncompiles the row's equation, so every
#: import into an importing space pays that withdrawal; 6167a0fb2 makes import
#: currency transitive: each nested load records an import_nested_source/3 edge
#: to every import still in flight above it, and a cached import answers
#: current only when every nested receipt does; da91bc244 confines an exact
#: removal's selection to its own atom: native_retract_one/2 now records the
#: selected clause's head, a clause/3 lookup per exact removal, and checks each
#: removal made while the selector is live against it, a few inferences per
#: removal (+8 on most twins, +24 to +192 on the library twins that withdraw
#: package rows); where a twin's move exceeds these steps, the remainder is
#: drift that stayed inside its band (four inferences, or its own declared
#: allowance) on every other interval [measured 2026-09-24: min-of-3 serial
#: fresh processes; command=python extensions/python/tools/twin_coverage.py
#: --repin; commit=WORKTREE].
#: RE-PINNED 2026-09-24, 48014 to 48275 (+261), +262 at 850d2a660, which reads
#: a native space's lengths in ascending arity rather than functor-hash order;
#: -1 at 0f6d29ba6, the seat's early-exit questions asked by key or in
#: ascending arity [measured 2026-09-24: min-of-3 serial fresh processes at
#: HEAD in battery 118 holding the committed tree alone (BATTERY_KEEP='',
#: 11:56); each step read with its parent and child in turn in battery 115
#: (10:42 to 11:18), 117 (11:01 to 12:10) or 120 (12:04 to 12:13) from
#: committed trees or this job's patched copies of them, none from a working
#: tree; 850d2a660's and 0f6d29ba6's split from provider-carry's own pairs,
#: aaeea643a's on the ladder before 10:05; command=python
#: extensions/python/tools/twin_coverage.py --measure --rounds 3;
#: commit=c7d7244fbe6d32d024ca8c61b336008e98b156ef].
#: RE-PINNED 2026-09-24, 48275 to 48252 (-23), gate-perf's d781eab8f carries an
#: exact removal's selected head from the code that selected it, so a
#: withdrawal copies its equation once: 23 inferences fewer for each equation
#: removal the twin adopts and 4 for each it selects (-23); each step read
#: serially on its own committed tree, from gate-perf's pin at c7d7244fb, and
#: the fixed tree 4ff69551e reads what 4003462fe does [measured 2026-09-24:
#: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=4ff69551e0e226442cf7257b96af858adda957a4].
#: RE-PINNED 2026-09-25, 48252 to 48247 (-5), the registration refusal kind
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
#: the base [measured 2026-09-25T06:28:55+10:00: min-of-3 serial fresh
#: processes; command=python extensions/python/tools/twin_coverage.py --repin].
BUDGET = 48247
