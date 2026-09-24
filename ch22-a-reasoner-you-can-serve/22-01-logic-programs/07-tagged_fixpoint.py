"""Purpose: examples/ch22-a-reasoner-you-can-serve/22-01-logic-programs/07-tagged_fixpoint.metta in Python: a tagged program's fixpoint under several carriers.

The same graph with a cycle, written through the tagged doors, asked with
`match(..., under=carrier)`. The engine takes the fixpoint route for the
cyclic rules under a carrier whose combine is idempotent, and `derivations=False`
asks for it on the acyclic graph too. `formula` then `.under(prob)` is the
MeTTa `(formula prob)`: the exact probability, shared edges counted once.
"""

import metta
from metta import S, V


def _graph(space, edges):
    for start, end, weight in edges:
        space.add_tagged_fact(weight, S.edge(start, end))
    space.add_tagged_rule(1, S.path(V.x, V.y), S.edge(V.x, V.y))
    space.add_tagged_rule(1, S.path(V.x, V.z), S.edge(V.x, V.y), S.path(V.y, V.z))


def twin(m):
    """The strongest, the cheapest, the exact and the counted path."""
    _graph(m, ((S.a, S.b, 0.6), (S.b, S.a, 0.5), (S.a, S.c, 0.2), (S.b, S.c, 0.3)))
    query = S.path(S.a, S.c)

    # bool is max of products: the direct 0.2 beats 0.6 * 0.3, the cycle adds nothing.
    assert abs(m.match(query, under=metta.bool).one().annotation - 0.2) < 1e-9
    # tropical is min of sums, each rule adding its own tag 1.
    assert abs(m.match(query, under=metta.tropical).one().annotation - 1.2) < 1e-9
    # Every pair the cycle reaches from a, once each.
    assert len(list(m.match(S.path(S.a, V.y), under=metta.set))) == 3
    # The exact probability: the formula read back under prob.
    exact = m.match(query, under=metta.formula).one().under(metta.prob).annotation
    assert abs(exact - (1 - (1 - 0.2) * (1 - 0.6 * 0.3))) < 1e-6

    # On an acyclic graph every carrier is exact on the fixpoint route.
    dag = metta.space()
    _graph(dag, ((S.a, S.b, 0.6), (S.b, S.c, 0.5), (S.a, S.c, 0.2)))
    assert dag.match(query, under=metta.counting).one().annotation == 2
    assert abs(dag.match(query, under=metta.prob, derivations=False).one().annotation - 0.5) < 1e-9


#: MEASURED on this branch rather than inherited: this twin is new, so there is
#: no earlier pin to move. Its first reading was 757958 inferences, 24.5x the
#: example's, every `match(under=)` reading the whole catalog into Python to
#: find one annotations row; the catalog reads became pattern matches and the
#: twin dropped to below the original [measured 2026-09-18: 26374 inferences,
#: 0.8538x the example's 30891, min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --measure --rounds 3
#: examples/ch22-a-reasoner-you-can-serve/22-01-logic-programs/07-tagged_fixpoint.metta;
#: commit=12609a929638e7a2b08d3ff8f517abc1a399e7a9].
#: RE-PINNED 2026-09-18, 26374 to 26984 (+610), 49478d67a landed the polynomial
#: carrier, whose preset row and variable claim every catalog scan reads, the
#: product carriers and the guard read in the fixpoint door, and the binding's
#: five-element rule read: the examples that scan the catalog moved with their
#: twins (restricted_spaces +522, the three pln twins +63 each, the two tabling
#: twins +20 and +10, reflect_lib +6) and the twins that cross the seat's
#: declaration and query paths moved with their examples unmoved (the class
#: twins between -4212 and +2841, the reference twins +208 and +317, the tagged
#: fixpoint twin +610, the documentation twins -22 and -50, types_nondet +5)
#: [measured 2026-09-18: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=bf5f100591493a91324b1d7552b5ad2731601691].
#: RE-PINNED 2026-09-18, 26984 to 27071 (+87), the trunk merged (f97c4b0a3,
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
#: RE-PINNED 2026-09-19, 27071 to 27131 (+60), cost follows the answer: a block
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
#: RE-PINNED 2026-09-21, 27131 to 27049 (-82), the sixty libraries derived in
#: MeTTa landed with merge 97763e7fa eight hours after the previous pin
#: 55d451b67, so every example importing one now pays a MeTTa derivation where
#: it paid a Prolog body instead, which the 2026-09-14 ruling accepts
#: explicitly as the price of a library that survives the engine swap [measured
#: 2026-09-21: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=6e09cb25d5495c2db3283166e6ce4e07eefecfb2].
#: RE-PINNED 2026-09-24, 27049 to 27137 (+88), placed on the full-configuration
#: first-parent ladder from the pin commit 6e09cb25d: the 120 commits
#: 43e964002..c09dc4868, where the per-commit probe sweep puts each step at one
#: commit: 5b4e7e53d reads a translator rule's declared type where the rule
#: lives; aea2e5e03 and 6922f54c9 carry the csv and lib_file refusal
#: vocabulary; d27805154 carries lib 19a231b, whose regenerated faces declare
#: six libraries' inputs %Undefined%, so their calls stop paying a declared-
#: type check (vector_lib -7278, statistics_lib -6453); 33219ffa0 resolves a
#: bare library name to its pkg.metta; 0cd329450 adds the platform refusal
#: kind, one metta_refusal_declaration/4 row that metta_catalog_preset/1 turns
#: into one more (refusal ...) catalog row and one more refusal-kind vocabulary
#: member, measured at +10 to +15 on most twins; and d8231f103 refuses a
#: library spec that walks out of the library root; 6167a0fb2 makes import
#: currency transitive: each nested load records an import_nested_source/3 edge
#: to every import still in flight above it, and a cached import answers
#: current only when every nested receipt does; the 20 commits
#: 6167a0fb2..864c4bac0, where the sweep puts the probes' only step at
#: e1acacad2, which clears a space's import bookkeeping from the module that
#: owns it [measured 2026-09-24: min-of-3 serial fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=WORKTREE].
#: RE-PINNED 2026-09-24, 27137 to 27049 (-88), 5c32234cf, the host-patch split,
#: rewrote engine/host_check.pl, which every boot loads from source: c4054cea8
#: made metta_require_patched_host/0 a findall over the engine's requirement
#: handed to the new metta_require_host_patches/2, and the Python bridge now
#: runs that check a second time over janus's patches; with the rewritten file,
#: the requirement list and the bridge's check all reverted this twin reads its
#: previous pin exactly, while reverting the requirement list alone or the
#: bridge's check alone leaves the move, so it is the rewritten file's boot
#: content, below which no single predicate was isolated [measured 2026-09-24:
#: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=0a81c782fd6ba00984c36e58e228f73bca810dee].
#: RE-PINNED 2026-09-24, 27049 to 27137 (+88), 0847c3d4c decides a platform
#: capability the first time anything reads it, by whether every library its
#: census row names resolves, where only a failed load used to record anything,
#: and 984eabe23 keeps each verdict in a flag decided under a mutex so two
#: threads' first reads agree; the count moves by what the twin's reads now
#: decide, about 660 inferences for a one-library capability and 1,964 for
#: markup's three, and by a few where it reads the census without deciding
#: [measured 2026-09-24: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=d832d20e8edfdad28ad52815757ba9e685ad2de3].
#: RE-PINNED 2026-09-24, 27137 to 27272 (+135), +313 at 850d2a660, which reads
#: a native space's lengths in ascending arity rather than functor-hash order;
#: -178 at 0f6d29ba6, the seat's early-exit questions asked by key or in
#: ascending arity [measured 2026-09-24: min-of-3 serial fresh processes at
#: HEAD in battery 118 holding the committed tree alone (BATTERY_KEEP='',
#: 11:56); each step read with its parent and child in turn in battery 115
#: (10:42 to 11:18), 117 (11:01 to 12:10) or 120 (12:04 to 12:13) from
#: committed trees or this job's patched copies of them, none from a working
#: tree; 850d2a660's and 0f6d29ba6's split from provider-carry's own pairs,
#: aaeea643a's on the ladder before 10:05; command=python
#: extensions/python/tools/twin_coverage.py --measure --rounds 3;
#: commit=c7d7244fbe6d32d024ca8c61b336008e98b156ef].
BUDGET = 27272
