"""Purpose: examples/ch22-a-reasoner-you-can-serve/22-01-logic-programs/08-guarded_rules.metta in Python: a rule's side condition and a tabled answer's witnesses.

The same scored facts, the threshold as a MeTTa equation and then as a Python
callable passed as `where=`, asked on both routes. `why()` on a tabled answer
asks the engine for its witnesses, the sources each derivation uses, so the
fixpoint route explains itself too.
"""

import metta
from metta import S, V


def twin(m):
    """The guard admits a and drops b, and the answer shows its witness."""
    m.add_tagged_fact(0.6, S.score(S.a))
    m.add_tagged_fact(0.3, S.score(S.b))
    m.add(S["="](S.above_half(V.s), S[">"](V.s, 0.5)))
    stored = m.add_tagged_rule(1, S.trusted(V.x), S.score(V.x), where=S.above_half)
    assert stored.children[4] == S.where(S.above_half)

    # Only a clears the bar, on the derived route and on the fixpoint.
    for derivations in (True, False):
        rows = list(m.match(S.trusted(V.x), under=metta.prob, derivations=derivations))
        assert [row.value for row in rows] == [S.trusted(S.a)]
        assert abs(rows[0].annotation - 0.6) < 1e-9

    # A Python guard registers under its own name, like a callable tag.
    def strong(score):
        return score > 0.5

    guarded = m.add_tagged_rule(1, S.vouched(V.x), S.score(V.x), where=strong)
    assert guarded.children[4] == S.where(S.rule_strong)
    assert [row.value for row in m.match(S.vouched(V.x), under=metta.prob)] == [S.vouched(S.a)]

    # The derived route shows the guard that held; the tabled route asks the
    # engine for the witness: one derivation through the fact and the rule.
    assert "where (above-half 0.6) held" in str(m.match(S.trusted(S.a), under=metta.prob).one().why())
    tabled = m.match(S.trusted(S.a), under=metta.prob, derivations=False).one()
    witnesses = tabled.why().alternatives
    assert len(witnesses) == 1
    assert sorted(child.is_rule for child in witnesses[0].children) == [False, True]


#: The twin's own program, priced when it was written; the lane compares it
#: with the example's cost and this pin [measured 2026-09-18: min-of-3 serial
#: fresh processes; command=python extensions/python/tools/twin_coverage.py
#: --measure; commit=49478d67a10793a114d27d01a51f09a685d5136a].
#: RE-PINNED 2026-09-18, 23621 to 23658 (+37), the trunk merged (f97c4b0a3,
#: petta's 61 commits since c75181adc) with the definition batch's load pushed
#: as the running load (2da1155e3): every example moved with the engine, 279 of
#: 294 cheaper (median -0.78%), through the compiled runnable envelope
#: executing each runnable form's fixed answer, name and fuel envelope from
#: compiled clauses, the trunk's trailed scopes and compiled context readers (a
#: b_getval/2 read per recorded assertion in place of the branch's thread-local
#: rows), the host listener door and the receipts loop probing the owner once
#: per set; serial minimum of three fresh processes through the lane's run_twin
#: [measured 2026-09-18: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=55d451b670949c2dc9d2ab7bc678f33f21094bd2].
#: RE-PINNED 2026-09-19, 23658 to 23676 (+18), cost follows the answer: a block
#: is charged for its own thread's work and for the workers whose answers it
#: used, so a race's losers, the branches par-any and par-forall stopped, and a
#: cancelled future or timer are joined through the engine's discarding door
#: (metta_join_measured/3) and their partial spend, which only the schedule
#: sized, is taken out; lib_thread's join no longer polls on the host patched
#: for swi-thread-join-detach-window, and the seat's counter doors read the
#: discarded tally outside the window they bracket (metta_py_stats/2,
#: metta_py_work/2) [measured 2026-09-19: min-of-3 serial fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=32335687084e4d8ad43cf8800f2dedce707fa137].
#: RE-PINNED 2026-09-21, 23676 to 23572 (-104), the sixty libraries derived in
#: MeTTa landed with merge 97763e7fa eight hours after the previous pin
#: 55d451b67, so every example importing one now pays a MeTTa derivation where
#: it paid a Prolog body instead, which the 2026-09-14 ruling accepts
#: explicitly as the price of a library that survives the engine swap [measured
#: 2026-09-21: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=6e09cb25d5495c2db3283166e6ce4e07eefecfb2].
#: RE-PINNED 2026-09-24, 23572 to 23687 (+115), placed on the full-
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
#: dropped; 6167a0fb2 makes import currency transitive: each nested load
#: records an import_nested_source/3 edge to every import still in flight above
#: it, and a cached import answers current only when every nested receipt does;
#: the 20 commits 6167a0fb2..864c4bac0, where the sweep puts the probes' only
#: step at e1acacad2, which clears a space's import bookkeeping from the module
#: that owns it; the commits 63fc952ac..8d45268e3, which the ladder did not
#: split; their runtime changes are 31c0afd8a (the host refusal's message),
#: 7472c4907, which marks a module's reference face dirty instead of walking
#: its forward closure, so support_stabilize/3 walks the face's dependents only
#: when the recomputed value moved and an event that changes nothing recompiles
#: no caller, 7054c11f7, which carries lib 62ca61c's bisecting bit length in
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
#: RE-PINNED 2026-09-24, 23687 to 23571 (-116), 5c32234cf, the host-patch
#: split, rewrote engine/host_check.pl, which every boot loads from source:
#: c4054cea8 made metta_require_patched_host/0 a findall over the engine's
#: requirement handed to the new metta_require_host_patches/2, and the Python
#: bridge now runs that check a second time over janus's patches; with the
#: rewritten file, the requirement list and the bridge's check all reverted
#: this twin reads its previous pin exactly, while reverting the requirement
#: list alone or the bridge's check alone leaves the move, so it is the
#: rewritten file's boot content, below which no single predicate was isolated
#: [measured 2026-09-24: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=0a81c782fd6ba00984c36e58e228f73bca810dee].
BUDGET = 23571

#: OVERRUN 2026-09-18, 538: the twin costs 23621 against the example's 18397
#: and a ceiling of 23083 (the band plus 2846 to author one compiled
#: definition); the distance is this twin's own program, the callable guard
#: registered as a second rule and the two why() asks, the tabled one running
#: the program again under (product prob polynomial), which the example has
#: no spelling for [measured 2026-09-18: one fresh process per side through the
#: lane's run_example and run_twin; command=python
#: extensions/python/tools/twin_coverage.py --measure; commit=49478d67a10793a114d27d01a51f09a685d5136a].
#: OVERRUN 2026-09-18, 538 to 3385 (+2847): the twin costs 23621 against the
#: example's 18397 and a ceiling of 20775 with the earlier declaration; a
#: minimal twin of this example costs 18461, inside the 20237 the band alone
#: allows, so the distance is this twin's own program. the declaration of 538
#: was priced while the twin authored one compiled definition, 2846 of
#: allowance the lane grants for authoring; the twin since mirrors the
#: example's guard as the MeTTa equation and registers its Python guard as a
#: grounded operation, which the lane does not price as authoring, so the whole
#: distance above the band is the twin's own program: the second rule with the
#: callable guard, both routes asked for it, the witness rendered and the
#: answer re-asked under another carrier, none of which the example does
#: [measured 2026-09-18: one fresh process per side through the lane's
#: run_example and run_twin, the floor from a minimal twin built by the probe;
#: command=python extensions/python/benchmarks/probes/twin_floor.py;
#: commit=bf5f100591493a91324b1d7552b5ad2731601691].
#: OVERRUN 2026-09-19, 3385 to 3515 (+130): the twin costs 23676 against the
#: example's 18329 and a ceiling of 23546 with the earlier declaration; a
#: minimal twin of this example costs 18312, inside the 20162 the band alone
#: allows, so the distance is this twin's own program. the trunk's cost per
#: recorded write (the trailed publication context read, the owner pin and the
#: listener door on every assertion, f97c4b0a3) on the writes this twin makes
#: beyond the one compiled definition the allowance prices, its declarations,
#: documentation and reflection rows, so the twin sits past its example by that
#: residue [measured 2026-09-19: one fresh process per side through the lane's
#: run_example and run_twin, the floor from a minimal twin built by the probe;
#: command=python extensions/python/benchmarks/probes/twin_floor.py;
#: commit=32335687084e4d8ad43cf8800f2dedce707fa137].
OVERRUN = 3515

#: DIVERGED 2026-09-18, the example holds 0 atoms the twin does not (none) and
#: the twin holds 4 atoms the example does not (1 :, 2 annotation, 1 rule): the
#: twin adds a second rule whose guard is a Python callable registered as the
#: function rule-strong, so its type row, its two annotation rows and the rule
#: row naming (where rule-strong) are the twin's alone; the example's guard is
#: the MeTTa function above-half, which the twin mirrors first [measured
#: 2026-09-18: the two stored-atom surpluses, one fresh process per side;
#: command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=bf5f100591493a91324b1d7552b5ad2731601691].
DIVERGENCE = "bdb3f2dcbafa7ac4abb5860bb62b1676e66d0d354482f067629aa25cf4cf836e"
