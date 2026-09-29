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
#: RE-PINNED 2026-09-25, 48247 to 47405 (-842), the host evaluation door
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
#: more than twelve names [measured 2026-09-25T06:47:05+10:00: min-of-3 serial
#: fresh processes; command=python extensions/python/tools/twin_coverage.py
#: --repin].
#: RE-PINNED 2026-09-25, 47405 to 47475 (+70), every force of a waiting
#: function names the module it is made from, through fun_home_in/3, and a
#: write forces only its own space [measured 2026-09-25T16:54:32+10:00: one
#: full twins lane before this commit and one with it, the two read on one
#: battery path at the landing's HEAD; command=python
#: extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-25, 47475 to 47566 (+91), lambdas are named by their
#: content and a copy restores its source's rows as a program [measured
#: 2026-09-25T17:00:15+10:00: one full twins lane before this commit and one
#: with it, the two read on one battery path at the landing's HEAD;
#: command=python extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-27, 47566 to 47706 (+140), the host switch to swipl-
#: patched.7 and the seat changes it needs: +140 the held goals reading Used
#: through metta_py_work/2, which leaves a held engine's own ticks out and
#: reads the tick term inside its opening edge, 5 inferences a held reading;
#: the trunk's lane read this twin +3 off its pin, an offset that is not this
#: landing's, so the pin moves by the landing's delta alone [measured
#: 2026-09-27T03:41:21+10:00: one full twins lane of the trunk and one with
#: this landing, wt-merge battery 1, the trunk on swipl-patched.6 and every
#: part on .7, each through a same-shape host shim; command=python
#: extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-27, 47706 to 47735 (+29), a force of a waiting function
#: takes the typing policy and the specializer's lock before translation:
#: spaces:metta_ensure_compiled/2 stabilises the policy and takes the
#: specializer's mutex around the translation once per force, and the
#: translation's own per-pair stabilisation re-enters through
#: with_typing_policy_stable/1's first clause; the lanes' tree read this twin
#: +3 off its pin before the step, an offset that is not this step's, so the
#: pin moves by the step's delta alone [measured 2026-09-27T09:56:55+10:00: one
#: full twins lane before this commit and one with it, each read in one battery
#: of the landing's HEAD after a QLF purge and one warm-up; command=python
#: extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-27, 47735 to 47747 (+12), the constructive negation's
#: engine additions, each counted in this twin's own run: 1 space module
#: prepared, each importing and exporting the three names the change emits into
#: compiled clauses, metta_case_row/3, metta_decided/2 and metta_same_term/3
#: (+9); +3 of clause-indexing layout [measured 2026-09-27T18:31:56+10:00: one
#: full twins lane with this landing, in a battery of its tree at 775d3cf35,
#: beside one of the base in a battery of 775d3cf35 from
#: 2026-09-27T18:40:06+10:00, which reads the old pin; command=python
#: extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-27, 47747 to 47672 (-75), -75 at interrupts B's seat
#: change, which drops the poll's boot calibration, its tick charges and its
#: tick record: a held reading through metta_py_work/2 brackets 3 inferences
#: where it bracketed 6, a registration walk over more than twelve names meets
#: 6 fewer seat predicates (12 or 14 fewer), and a thread the twin joins
#: credits it 11 where it credited 16 [measured 2026-09-27T20:07:01+10:00: full
#: twins lanes in wt-merge's battery 1, tsm-licence's series and its engine
#: reader on swipl-patched.7, the series on swipl-patched.8, and the stack
#: through janus-contract B on swipl-patched.8 twice; command=sh tools/check.sh
#: twins].
#: RE-PINNED 2026-09-27, 47672 to 47660 (-12), -12 at walk-tax B, which
#: registers a batch's Prolog arities by asking each name, so a registration
#: walk over more than twelve names no longer reads every predicate visible
#: from the loading module at 2 inferences each [measured
#: 2026-09-27T20:38:05+10:00: full twins lanes on swipl-patched.8 in wt-merge's
#: battery 1, two with janus-contract A and two with walk-tax B; command=sh
#: tools/check.sh twins].
#: RE-PINNED 2026-09-29, 47660 to 47680 (+20), this twin reads 47660 before the
#: change and 47680 with the change (+20): each definition through the define
#: doors asks whether its module holds a shadow-import receipt for the name,
#: holds it in flight until the write is visible when it does, and a sweep
#: leaves a receipt another live thread holds: with that use this twin reads
#: 47680 where the definitions alone read 47660 (+20) [measured
#: 2026-09-29T06:36:33+10:00: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-29, 47680 to 48171 (+491), this twin reads 47680 before
#: the change and 48171 with the change (+491): each definition marks its name
#: as changed and a sweep repairs only the receipts naming a marked name, where
#: it re-checked every receipt the process held: with that use this twin reads
#: 48171 where the definitions alone read 47680 (+491) [measured
#: 2026-09-29T06:43:15+10:00: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-29, 48171 to 48269 (+98), this twin reads 48174 before the
#: change and 48269 with the change (+95): every operation that registers a
#: name outside a load opens a registration unit, files there the repairs its
#: registrations owe, and drains them once when it finishes, so a caller
#: compiled before the name became a function is repaired: with that use this
#: twin reads 48269 where the definitions alone read 48174 (+95); it read 48174
#: against its pin 48171 before this step, a distance of +3 that is not this
#: step's (+3 the trunk's own) and is not attributed here [measured
#: 2026-09-29T20:22:57+10:00: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-29, 48269 to 48157 (-112), this twin reads 48269 before
#: the change and 48157 with the change (-112): a call site forces the function
#: it names before deciding the call's shape, so a call of a waiting function
#: builds the application protocol an eager load builds, and the protocol's
#: marker test around a value the translation already holds is decided at
#: compile time: with that use this twin reads 48157 where the definitions
#: alone read 48269 (-112) [measured 2026-09-29T20:34:55+10:00: min-of-3 serial
#: fresh processes; command=python extensions/python/tools/twin_coverage.py
#: --repin].
#: RE-PINNED 2026-09-30, 48157 to 47893 (-264), this twin reads 48157 before
#: the change and 47893 with the change (-264): a named space's prelude-tier
#: type readers look the prelude's row up before asking whether it governs
#: there, and builtin_result_type/3 asks whether a program took a builtin over
#: only for a builtin whose result is evaluated (engine/metta/types.pl,
#: engine/translator/lowering.pl), so a lookup of a name the prelude does not
#: declare costs one indexed miss and no ownership probe [measured
#: 2026-09-30T04:16:51+10:00: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
BUDGET = 47893
