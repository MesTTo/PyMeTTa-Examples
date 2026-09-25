"""Purpose: examples/ch22-a-reasoner-you-can-serve/22-03-search/02-tilepuzzle.metta in Python: the eight-tile state graph.

Twenty-four move equations say where the blank may go from each of the nine
positions, and a breadth-first loop walks the reachable states, refusing a
duplicate, until the queue empties. The claim is the count it reaches, 181440,
the 9!/2 boards reachable from the start, each dequeued once because the start
enters the duplicate store before the loop, as every other board does when the
loop first reaches it. Upstream PeTTa's copy seeds the store through
`add-unique-item-or-empty`, which nothing defines, so its start is dequeued a
second time and it answers 181441; the example says why it differs.

The moves are one shape repeated, so a pair of loops writes them: the blank's
position and the direction are the loop variables, and the row is the eight
placeholders with the blank swapped into place. The example writes all
twenty-four out; here the shape is stated once and `@m.rules` lands the
twenty-four equations the loops supply, which is the door for a head that
destructures a nine-cell board.

The search is a `@m.rules` bundle and two compiled functions. `bfs_loop` is
the example's TWO coexisting clauses. Folding them into one `if`/`else` raised
StackOverflow at 16,665 states when this twin was written (friction, P14.4),
and the folded search has completed since the tail-context work retired that
row on 2026-09-05 [source: docs/journal/2026-09-05-case-duals-and-tail-contexts.md;
residue.json's retired P14.4 row for this example]. The example inlines a
`let*` under the `collapse`, and the twin NAMES that intermediate as
`fresh-neighbour` instead, which is a compiled function whose statements ARE
that let*.

Three names carry a genuine underscore, `bfs_loop`, `bfs_all` and `$_1`. The
factory attribute door maps every underscore to a hyphen, so the variables take
the bracket and the two heads are given explicitly with `name=`: the implicit
name would install `bfs-loop`, a different head from the one the example makes
matchable.
"""

import metta
from metta import S, V, equation, if_, lib

#: The search head, whose MeTTa name carries a genuine underscore, so the
#: attribute door cannot say it: rung 4's map would make it `bfs-loop`.
BFS_LOOP = S["bfs_loop"]

#: The blank, and one variable per board position.
BLANK = S["___"]
SLOTS = (V["_1"], V["_2"], V["_3"], V["_4"], V["_5"],
         V["_6"], V["_7"], V["_8"], V["_9"])

#: Source order is up, left, right, down wherever the move is legal.
DIRECTIONS = ((S.U, -3), (S.L, -1), (S.R, 1), (S.D, 3))


def _legal(blank, direction):
    """Whether ``direction`` stays on the three-by-three board from ``blank``."""
    row, column = divmod(blank, 3)
    return not (
        (direction == S.U and row == 0)
        or (direction == S.D and row == 2)
        or (direction == S.L and column == 0)
        or (direction == S.R and column == 2)
    )


def _moves():
    """Yield the source's twenty-four structured move equations in source order."""
    for blank in range(9):
        for direction, shift in DIRECTIONS:
            if not _legal(blank, direction):
                continue
            before = list(SLOTS)
            before[blank] = BLANK
            after = before.copy()
            destination = blank + shift
            after[blank], after[destination] = after[destination], after[blank]
            yield equation(S.move(tuple(before), direction)).to(tuple(after))


def twin(m):
    """State the moves and queue laws, then exhaust the reachable state graph."""

    @m.rules
    def board():
        """Twenty-four move equations, the example's own shape written once.

        (= (move (___ $_2 $_3 $_4 $_5 $_6 $_7 $_8 $_9) R)
           ($_2 ___ $_3 $_4 $_5 $_6 $_7 $_8 $_9)), and twenty-three more.
        """
        yield from _moves()

    # !(import! &self (library lib_datastructures))
    m += lib.datastructures

    # The duplicate store is an ordinary space, and the Python variable IS its
    # binding, so it needs no name: the handle crosses a term position as
    # itself, which is what `add-unique-or-fail` receives.
    duplicates = metta.space()

    @m.define
    def fresh_neighbour(state):
        """One unseen state per legal move; the example inlines this let*."""
        moved = S.move(state, V._)
        _receipt = S.add_unique_or_fail(duplicates, moved)
        return moved

    @m.rules
    def search(queue, seen, state, rest, neighbours, grown):  # noqa: PLR0917  -- a bundle's parameters ARE its equations' variables, not a call signature
        """The two coexisting clauses: stop on an empty queue, or take one."""
        # `empty-queue` is a function, so the base case tests the queue against
        # what it produces rather than writing the call in the head, which
        # would be a pattern matched structurally.
        # (= (bfs_loop $Q $N0) (if (== $Q (empty-queue)) $N0 (empty)))
        yield equation(BFS_LOOP(queue, seen)).to(
            if_(S.eq(queue, S.empty_queue()), seen, S.empty())
        )
        # (= (bfs_loop $Q $N0)
        #    (let* (($Q1 (once (dequeue $S $Q)))
        #           ($Ln (collapse (let* (($Snew (move $S $_)) ...) $Snew)))
        #           ($Q2 (foldl enqueue $Ln $Q1))
        #           ($N1 (+ $N0 1)))
        #          (bfs_loop $Q2 $N1)))
        yield equation(BFS_LOOP(queue, seen)).to(
            S["let*"](  # rung: a stored let* whose bindings are queue calls, and whose TAIL is the recursion this search needs (P14.4)
                (
                    (rest, S.once(S.dequeue(state, queue))),
                    (neighbours, S.collapse(S.fresh_neighbour(state))),  # rung: `collapse` is list() (P14.4)
                    (grown, S.foldl(S.enqueue, neighbours, rest)),
                ),
                BFS_LOOP(grown, seen + 1),
            )
        )

    @m.define(name="bfs_all")
    def bfs_all(start):
        """Seed the duplicate store and the queue, then run the loop."""
        # (= (bfs_all $Start)
        #    (let* (($Pt (add-unique-or-fail &dup $Start))
        #           ($Q1 (enqueue $Start (empty-queue))))
        #         (bfs_loop $Q1 0)))
        _receipt = S.add_unique_or_fail(duplicates, start)
        queue = S.enqueue(start, S.empty_queue())
        return S["bfs_loop"](queue, 0)

    # !(test (let $x (bfs_all (___ 1 2 3 4 5 6 7 8)) $x) 181440)
    assert bfs_all((BLANK, 1, 2, 3, 4, 5, 6, 7, 8)) == [181440]


#: Inferences this twin spends, its own tripwire. A PLACEHOLDER: the wave's
#: integrator prices all 218 budgets in one pass on the merged tree, so no
#: figure measured in a single agent's worktree is pinned here. THIS TWIN'S
#: PREVIOUS PIN WAS AN EMPIRICAL ENVELOPE, minimum 55047786, maximum 55047980
#: over 28 observations under `full-lane/218/workers=32`, so the re-pin owes
#: it an envelope rather than a point
#: [assumed: 1 is a placeholder rather than a measurement; commit=6a3e8b959229afa7adce172704045d1456a40df6].
#: PRICED 2026-08-25 by the corpus pricing pass: tools/twin_coverage.py --measure min-of-3 on p14-integration at the store-wave merge, pinned exactly under the suite's two-sided +-4 deterministic allowance.
#: RE-PINNED 2026-08-25, 197554387 to 197554425, at the flat-door
#: typed-dispatch gate and the library import door landing
#: together: every flat call prices one declaration read through
#: type_declaration_in/3, a declared head's flat call routes
#: through the same call-site typed dispatch the engine's own
#: form runs (metta_py_typed_dispatch_applies/2, the P14.9
#: residue retirement), and an import-bearing twin now spells
#: its import as `m += lib.x` on the write door [measured
#: 2026-08-25 through tools/twin_coverage.py --measure min-of-3
#: on the tree carrying both].
#: RE-PINNED 2026-08-25, 197554425 to 197554239, on the QLF-boot final
#: tree: the engine now boots through engine/qlf_boot.pl, and any
#: boot-content change moves twin counts a few tens through SWI's
#: clause-indexing shape (qlf_boot.pl's header carries the A/B),
#: so the corpus re-pins once on the exact shipping tree
#: [measured 2026-08-25 through tools/twin_coverage.py --measure
#: min-of-3 on the final tree].
#: RE-PINNED 2026-08-25, 197554239 to 197554208, on the release tree:
#: the typed-dispatch question moved engine-side
#: (metta_typed_dispatch_applies/2, one extra frame per direct
#: call), the conformance kit gained the family, source and
#: round-trip laws, extensions gained the spaces([...]) readying
#: moment, and any boot-content change also moves counts a few
#: tens through SWI's clause-indexing shape (qlf_boot.pl's header
#: carries the A/B), so the corpus re-pins once on the exact
#: shipping tree [measured 2026-08-25 through
#: tools/twin_coverage.py --measure min-of-3 after a canonical
#: single-boot QLF regeneration].
#: RE-PINNED 2026-08-25, 197554208 to 197554165, at the release cut: the
#: identity-wire merge (numeric ownership seams, exact-primitive
#: wire, Python operator dispatch), the rules-body staging split
#: (ground folds, op-call staging), and the door-combinations
#: example growing the corpus each move counts through SWI's
#: clause-indexing shape (qlf_boot.pl's header carries the A/B),
#: so the whole corpus re-pins once on the exact release tree
#: [measured 2026-08-25 through tools/twin_coverage.py --measure
#: min-of-3 after a canonical single-boot QLF regeneration].
#: RE-PINNED 2026-08-26, 197554165 to 197556044 (+1879), by the open-tail-index
#: pricing pass, one sweep over the whole corpus after four attributed
#: engine movements: the writable-specialization merge 5c731b03 prices
#: each lazily translated match-bearing equation (~+1,500, first-call
#: probe 2,208 to 3,724 across that merge alone;
#: ai-brief-p14-specializer-translation-tax names the follow-up), the
#: relational-candidate rows of 6917bef7, and the open-tail head-index
#: and deprecation apply-seam fixes recovering their shares; the
#: remainder is compiled-image layout, the class this file's own chain
#: documents [measured: min-of-3 serial fresh processes; command=python extensions/python/tools/twin_coverage.py --measure --rounds 3; fixture=p14-integration open-tail-index pricing tree with engine/reader.so; commit=5ca9ef775933e349f8dc3ec64ec3cb85273a5a00].
#: RE-PINNED 2026-08-26, 197556044 to 197555920 (-124), on the composed
#: async-scheduler tree: a live operation call pays the six-inference
#: admission probe the baseline's p14_async_scheduler_comment prices,
#: and the scheduler, context-callback and exact-memo lifecycle clauses
#: move compiled-image layout by tens, the class this file's chain
#: documents [measured: min-of-3 serial fresh processes; command=python extensions/python/tools/twin_coverage.py --measure --rounds 3; fixture=merged p14-audit-async composed tree with engine/reader.so; commit=5059173b1767600ce4df0f6b7841d88116ee62d3].
#: RE-PINNED 2026-08-26, 197555920 to 197555874 (-46), at the tabling-seam
#: merge: compiled-image layout from the library's dispatch and
#: reflection clauses, the tens-scale class this file's chain documents
#: [measured: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --measure --rounds 3;
#: fixture=tabling-seam merged tree with engine/reader.so;
#: commit=694c12f70da25a28ffe22f9209f1d75d56921f93].
#: RE-PINNED 2026-08-26, 197555874 to 197554482 (-1392), by the
#: specializer argument-walk fix this file's own chain named as the
#: follow-up. Planning a specialization grafts a call argument onto the
#: equation's head pattern one position at a time, and that walk
#: metacalled a yall lambda per position, so each fresh process paid
#: '>>'/4's one-time resolution wherever its first binding plan landed
#: and 13 further inferences at every later position. The walk is
#: first-order now, at 4.0 inferences per position against 17.0.
#: [measured: two independent full-lane rounds on this tree agreeing exactly, against one on the unchanged tree and one on the same tree plus an inert never-called clause; command=python extensions/python/tools/twin_coverage.py; fixture=p14-specializer-tax off 694c12f7 with engine/reader.so and the MORK backend; commit=7e7cac85fee08c117032b2efa5a58a40f3b21365].
#: RE-PINNED 2026-09-01, 197554482 to 30041145 (-167513337), one corpus pricing
#: pass on the merged tree for the 2026-08-27..09-01 engine span
#: (8e75816d..f0744f86), whose four mechanisms are decomposed per lane in
#: benchmarks/baseline.json and ai-parametricity-audit.md passes 10-16: the
#: seam-offer routing and its one-wrap fold (net +8 inferences per evaluation),
#: the strict-scope removal leaving the eval path, the doubling cursor chunk
#: (~3 engine-side inferences per answer replacing per-answer crossings; drains
#: halve on CPU), and the aligned-path work; thirteen twins additionally carry
#: the idiom sweep's local deltas tabulated in the twin-idioms notes, none
#: above 347 [measured 2026-09-01: min-of-3 serial fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=51b792423cec5787614d1488c0793b8a50eaa6fc].
#: RE-PINNED 2026-09-01, 30041145 to 30041072 (-73), the subtract-atom
#: primitive and Counter's grain for -=: a new engine head shifts every twin's
#: load structure, the removal doors changed meaning where a twin spells one,
#: and the quad twin stopped being a different program [measured 2026-09-01:
#: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=c6a40460b1db341198a6150e3600f502831a6e83].
#: RE-PINNED 2026-09-01, 30041072 to 30041081 (+9), generic Python operators
#: now dispatch through live protocols while source twins explicitly name
#: relational engine heads [measured 2026-09-01: min-of-3 serial fresh
#: processes; command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=e3787593132a7ece2d300397045f7415709847c9].
#: RE-PINNED 2026-09-02, 30041081 to 30042317 (+1236), static contract
#: discharge and policy-stable recompilation [measured 2026-09-02: min-of-3
#: serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=c00341f0ff9d83d1b9338ca86ad51708eaf07ebd].
#: RE-PINNED 2026-09-02, 30042317 to 30042393 (+76), static contract discharge
#: with policy checks confined to invalidated contracts [measured 2026-09-02:
#: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=c00341f0ff9d83d1b9338ca86ad51708eaf07ebd].
#: RE-PINNED 2026-09-02, 30042393 to 30042435 (+42), P43 protects both
#: generated policy-check fallbacks from space-local capture [measured
#: 2026-09-02: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=c00341f0ff9d83d1b9338ca86ad51708eaf07ebd].
#: RE-PINNED 2026-09-06, 30042435 to 30041563 (-872), the one pricing pass at
#: the 0.8.0 release cut, and trunk's own movement rather than any mechanism in
#: this twin: each pin was taken on the base its own branch had, and the
#: September merge wave has moved the engine's clause layout, the evaluation
#: path and the library's write doors since [measured 2026-09-06: min-of-3
#: serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=b96e1a15260b7538a8e42be613bcc5dd0dddd136].
#: RE-PINNED 2026-09-07, 30041563 to 30225504 (+183941), trunk's own movement
#: since each twin's pin was taken on the base its own branch had: twenty-two
#: first-parent steps between the 0.8.0 release re-pin and this tree, the
#: prelude's move into Prolog the largest of them at +39 to +115 a twin and
#: -65,806 on the error algebra, the live-views merge -45 on every twin that
#: writes, the catalog and get-type repairs +169 on the types chapter, and the
#: rest SWI clause-indexing layout as the boot image grew; this tree also
#: stores the compiled default space operand as &self rather than a (context-
#: space) call [measured 2026-09-07: min-of-3 serial fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=9010a79b01c9b2a66b96a3952fa378fb3e939dc3].
#: RE-PINNED 2026-09-08, 30225504 to 30225543 (+39), the merges between this
#: lane's burn-down base (dfd5003f) and the tree that merged it, placed by a
#: first-parent ladder through the lane's own driver over ten twins at
#: f8c4b672, 4af59757, 90c08119, ad762ee7, 72f9cdf2 and 249389cb (ai-
#: tmp/integrator-849a9e/mergeTW-twin-ladder.log): the catalog-types merge
#: (1a3579fa) moves every twin by a lookup-and-layout step of about +5 for a
#: twin that makes no typed call and about +35 for one that does, plus about +6
#: per compiled definition through the argument-delivery check at the write
#: (the authoring fit re-measured 1370+1307 to 1406+1309), and +1411 for the
#: catalog twin that enumerates the 280 new rows; the two-sided-fragments merge
#: (4af59757) moves the sequence-variable twins by what their fixed rows now
#: compute (+2604 for the two-sided fragments, -217 for the fence, +19 for
#: restricted spaces); the every-atom merge (90c08119) re-authored the reading-
#: forms twin into the sread half (+3017) and added forty-six twins pinned on
#: its own base 31d54e19, which the merges since moved by the same clusters;
#: the gate-hygiene merge (ad762ee7) makes the tabling twins cheaper by the wfs
#: library no longer loading eagerly. Every twin here re-reads its budget on
#: the merged tree, minimum of three fresh processes [measured 2026-09-08: min-
#: of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=08f6f4df19a283bb84ba5f679c83944b42685b2e].
#: RE-PINNED 2026-09-08, 30225543 to 30223531 (-2012), metta_substitute_self/3
#: probes the term for the text &self before walking it, one C write and one C
#: substring probe, where the twins-lane merge's one-equation door (08f6f4df)
#: walked every natively added equation in a named space unconditionally, so
#: every twin that adds or defines an equation in a named space drops by about
#: that equation's size in inferences; the same probe now guards the reader's
#: per-form door (record_translated_from/4), the deferred door's fallback
#: (stored_equation_source/4), a batch's arriving equations
#: (mark_or_translate_equation/5) and the removal probe (remove_equation/6),
#: where the walk is new and skipped for a term that never says &self, and a
#: twin that only removes or re-adds such equations pays the two-inference
#: probe per door crossing instead. Every twin here re-reads its budget on this
#: tree, minimum of three fresh processes [measured 2026-09-08: min-of-3 serial
#: fresh processes; command=python extensions/python/tools/twin_coverage.py
#: --repin; commit=856434d7c1d381b3f3d7cbbd008f46c0d41b61aa].
#: RE-PINNED 2026-09-08, 30223531 to 30223525 (-6), the evaluation-fuel scope
#: marker is a trailed write (fix/every-intermittent-root-caused, f6e05ca9):
#: `$metta_fuel_scope` is written open with b_setval/2 at scope open and read
#: with b_getval/2 where nb_current/2 used to answer, so an abandoned scope
#: closes itself when an exception unwinds the trail and the cleanup is the
#: fast ordinary exit, and every runnable form pays fewer inferences per scope;
#: a twin drops by about the count of its runnables, and the engine bench reads
#: evaluate and translate 1642 lower each on the same tree. Every twin here re-
#: reads its budget on the merged tree, minimum of three fresh processes
#: [measured 2026-09-08: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=3fc65f02ce807c359f1a52026f950f345da2a9af].
#: RE-PINNED 2026-09-08, 30223525 to 30223546 (+21), boot content moved: the
#: refusal table and the typing point are modules this package did not have,
#: three convert doors became one, per-library faces are projections, and the
#: engine gained a catalog watch point, and SWI clause-indexing shape shifts a
#: twin count by tens whenever boot content moves, the mechanism every earlier
#: entry in these chains names. The watch point itself is one inference per
#: &metta write, which a twin that defines a function pays three of (2239
#: against 2236 on ch03 01-comments with the two announcement clauses taken
#: out), and the (limit ...) rows it exists for cost nothing at all: 2239
#: either way with every row-backed bound removed, because boot seeds the
#: mirror those bounds are read from [measured 2026-09-08: min-of-3 serial
#: fresh processes; command=python extensions/python/tools/twin_coverage.py
#: --repin; commit=c26b6a4d28ef8fb50742440feed2c0578ebb0f58].
#: RE-PINNED 2026-09-08, 30223525 to 30223847 (+322), The engine and library
#: predicates now resolve through their owning modules and the explicit engine
#: facade; compiled program lookup crosses the added metta_engine tier
#: [measured 2026-09-08: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=ede2ac57e213a0d4502c6bbbca6227f97015b720].
#: RE-PINNED 2026-09-08, 30223847 to 30223859 (+12), The engine and library
#: module boundaries retain explicit lookup owners, including host registration
#: and returned callback goals [measured 2026-09-08: min-of-3 serial fresh
#: processes; command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=ede2ac57e213a0d4502c6bbbca6227f97015b720].
#: RE-PINNED 2026-09-08, 30223859 to 30223852 (-7), the module boundary merged
#: with trunk's later packages (refactor/engine-and-libraries-as-modules at
#: b64291369): every space now resolves through one more chain link, prelude ->
#: metta_engine -> user, the engine's measured export list is imported into the
#: host tier at boot, the closed-sets watch point costs one inference per
#: &metta write, and a cursor opened by a host pays one transaction check at
#: its door; the branch pinned its budgets on its cut, trunk re-pinned the same
#: twins for the packages that landed after that cut, and only the merged tree
#: carries both, so this entry is where the two chains meet [measured
#: 2026-09-08: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=f1038acdcaf5230b6431c112f38a719d3dc9ef19].
#: RE-PINNED 2026-09-08, 30223546 to 30223601 (+55), The typed host door
#: catalog is published before user code. Its declarations change catalog
#: lookup indexes; generated public names bind directly to their existing
#: bodies [measured 2026-09-08: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=b615b5a33b43252ef9826e5387da7c9bd7f6b543].
#: RE-PINNED 2026-09-09, 30223601 to 30223892 (+291), the door table landed
#: (feat/space-as-a-projection-of-door-rows merged at 6471faa37, its
#: reconciliation fixes at 58bf75947): every Space door is a generated alias
#: over its body, the catalog publishes the door contracts at boot as typed
#: atoms, and the seam's listeners publish on every registration, so boot
#: content and clause layout moved, which shifts a twin count by tens; measured
#: on the merged tree [measured 2026-09-09: min-of-3 serial fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=aeb46b14152274db84f6415c8a3dd8c98a9c9eb1].
#: RE-PINNED 2026-09-09, 30223892 to 30223968 (+76), structured concurrency
#: landed (feat/structured-concurrency merged at f80cc416d): every space mint
#: records its allocation in the library's lifetime rows, every write and run
#: pays the ownership hook and every drop asks the library whether a scope owns
#: the name, measured on a pristine control as 32 per mint, 2 per write and 44
#: per drop with none per read; measured on the merged tree [measured
#: 2026-09-09: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=0f53926c2fd9f28e188814c84253ad82e13258f7].
#: RE-PINNED 2026-09-08, 30223852 to 31314836 (+1090984), Trailing occurrence
#: arguments, token allocation in native writes, exact source withdrawal and
#: transaction-safe shared-table guards change the engine work priced by this
#: twin; answer bags retain the upstream law [measured 2026-09-08: min-of-3
#: serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=7f00ac7932fefa6f380fc8d14ec583ea0c58eff4].
#: RE-PINNED 2026-09-08, 31314836 to 31314776 (-60), Sharing the fast-image
#: hexadecimal validator changes the engine predicate layout. The identity twin
#: moves below its declared band while the seven engine work counters move only
#: at boot; the native add and read slopes remain unchanged. Token storage and
#: source ownership retain their earlier measured costs and answer bags
#: [measured 2026-09-08: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=7f00ac7932fefa6f380fc8d14ec583ea0c58eff4].
#: RE-PINNED 2026-09-09, 31314776 to 31314937 (+161), tokens as storage landed
#: (feat/tokens-as-storage merged): every native occurrence carries a (t actor
#: generation) token as the trailing argument of its storage clause, minted
#: through flag/3 at the write funnel, and every clause read decodes it,
#: measured on a pristine control of trunk cbf7a958d as 8 more inferences per
#: add, 31 more per remove, 4 more per atom saved and 54 more per atom loaded
#: from a fast image, none per match, plus the merged tree's own lib_thread
#: repairs; measured on the merged tree [measured 2026-09-09: min-of-3 serial
#: fresh processes; command=python extensions/python/tools/twin_coverage.py
#: --repin; commit=50e34286f66c938d89d5d367c6370ad44164c97f].
#: RE-PINNED 2026-09-08, 30223852 to 30223905 (+53), Compiled shipped typing
#: decisions and initial vocabulary facts remove repeated interpretation;
#: indexed vocabulary membership replaces member-list scans; catalog reference
#: checks now respect transaction-local erasure. Paired controls and cut counts
#: are recorded in docs/journal/2026-09-08-what-the-waivers-were-paying-for.md
#: extensions/python/tools/twin_coverage.py --repin; commit=32650f9ff4d1c4aa0749d8eb8b153e5bb448ee5c].
#: RE-PINNED 2026-09-09, 30223905 to 30231867 (+7962), Compile shipped typing
#: decisions and initial vocabulary facts, index vocabulary membership, and
#: reuse the first Python variable binding before indexing additional names;
#: retain type, transaction and variable-identity checks [measured 2026-09-09:
#: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=32650f9ff4d1c4aa0749d8eb8b153e5bb448ee5c].
#: RE-PINNED 2026-09-09, 30231867 to 31322857 (+1090990), the compiled
#: vocabulary seed, the membership index, base-module type lookups and the
#: singleton decoder landed (perf/cross-engine-waivers merged): boot publishes
#: the initial vocabulary types from a compiled payload through the tokenized
#: funnel, a warm membership read touches only its own clauses, a base-module
#: type lookup skips the prelude, and a Python decode with one named variable
#: builds no index; per-operation costs of a mint, write, read, drop, run, save
#: and load are unchanged against the trunk in fresh processes; measured on the
#: merged tree, +7920 against the trunk's own pin of 31314937 at da0e5755d; the
#: previous number is the branch's cut-time price, and the remaining +1083070
#: is what landed on the trunk between the cut f0d33dcad and da0e5755d, tokens
#: as storage above all [measured 2026-09-09: min-of-3 serial fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=b4341ae382c48ef225f4a52e566af6a9a71757c4].
#: RE-PINNED 2026-09-09, 31322857 to 31322916 (+59), a library's Prolog half
#: compiles beside itself on its first import and loads from the artifact after
#: (metta_load_source/2, seam:compiled_source/1): a twin whose example imports
#: a library with a Prolog half pays the artifact load where both sides paid
#: the source consult and its compile-time expansion in every process,
#: lib_thread's import 278,309 to 5,925 inferences; every import now resolves
#: its spec and asks the boot's claim, about 180 inferences an import, and the
#: boot's content moved (the door, the seam and the three library imports the
#: tokens, receipts and seed units gained), which shifts clause layout by tens;
#: measured on this tree with the artifacts warm [measured 2026-09-09: min-of-3
#: serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=f26de01fbf3e0e3c64bb691c66a59fa959fee7f3].
#: RE-PINNED 2026-09-09, 31322916 to 31322926 (+10), engine/qlf_boot.pl gained
#: the hermetic child that writes the engine's own artifact set and every
#: library half's (qlf_child/2, qlf_regenerate_aside/1, qlf_child_boot/0,
#: qlf_shell_words/2), so no process's flags, initialisation file or packs
#: shape an artifact the tree shares; the boot file's added predicates move the
#: first definition's warm-up by ten, the load-structure movement its header
#: records for any boot-content change, and the lane's authoring constant moves
#: with it (warmup 1482); a twin importing a half pays the claim's freshness
#: check besides; measured on this tree with the artifacts warm, against the
#: pins of f26de01fb [measured 2026-09-09: min-of-3 serial fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=5f8a823d23fbed5c7395912a89ba32760e2df4b1].
#: RE-PINNED 2026-09-09, 31322926 to 31141449 (-181477), Public add-atom calls
#: metta_add_atom/4 directly and the native bulk loop calls add_sexp_in/5
#: directly, removing one forwarding inference per accepted atom while keeping
#: the atomic token clock, hooks and errors. Open native enumeration uses the
#: shared native_storage_functor/2 mapping, including parametric scalar
#: storage. Receipt scopes retain the nearest unnested transaction and post no
#: cleanup when no reservation exists. Full-lane ten-round observations on the
#: repaired tree place this point below the published budget; the provisioned
#: cut is 3e5855a35d7b206c847845f12467551ea4c54a59. See the 2026-09-09 entries in
#: docs/journal/2026-09-07-every-fact-has-a-token.md. Autoload-only excursions
#: are excluded from this point selection and keep their pins [measured
#: 2026-09-09: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=8ca8a387fc61d0918484b19a1a3baf85b6523043].
#: RE-PINNED 2026-09-13, 31141449 to 31583779 (+442330), Immutable maps and
#: priority queues are MeTTa equations over the shared collection libraries,
#: replacing the native tree adaptation [measured 2026-09-13: min-of-3 serial
#: fresh processes; command=python extensions/python/tools/twin_coverage.py
#: --repin; commit=9c9e60542491416e2c5e431a2672bb20f04264fa].
#: RE-PINNED 2026-09-14, 31583779 to 31579777 (-4002), Functional applies
#: finished callback arguments through reduce; Statistics derives exact
#: coefficient rows and Combinatorics retires its native probability provider
#: [measured 2026-09-14: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=e1be99ea1c08f70444c1c35cada441e089777906].
#: RE-PINNED 2026-09-14, 31579777 to 31579783 (+6), Closure publishes the
#: shared rendering and IEEE services, refreshes the callable projection and
#: annotates native protocol domains; every direct and transitive library
#: consumer is measured again [measured 2026-09-14: min-of-3 serial fresh
#: processes; command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=b7866b4d874879ff0cb212eb1c6af60dddaa39c6].
#: RE-PINNED 2026-09-11, 31141449 to 31140482 (-967), end-of-wave re-pin on the
#: merged tree after FROM's reference rows and four engine units, the closed-
#: set derivations and two host services, BINDING's one native evaluation entry
#: and boot import, W-OBSERVE's observer guard, PERF's receipts batching and
#: cursor retirement, and the three REDS repairs (derived runtime resources and
#: the shared loader, the tool-lane repairs, the corpus example); serial
#: minimum of three fresh processes through the lane's run_twin with
#: file_search_cache_time=9223372036854775807 set before child boot [measured
#: 2026-09-11: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=57f84148ba2684015f052d533f3197eca07b1f7b].
#: RE-PINNED 2026-09-18, 31141449 to 31498393 (+356944), the branch's landings
#: since the 09-10 pins, re-taken on the tip f06186a96: the compiled call law
#: (e59104ace: an Atom argument enters as written, a Python object crosses as a
#: value, a positional call of a bound callee is the plain application and a
#: compiled lambda is bare where it is applied), the one codec at the grounded
#: call (fd0af38f7, whose read of a call site's written keyword tail costs
#: about six inferences per translated site, read once since 7cc8fb863), the
#: runnable cache's dependency index written by the producer (a9e2c06d3, which
#: takes back the walk of the generated code 5416e741d charged at every miss),
#: the host patches of 09-17 and the class units of 09-13 to 09-16 the ladder
#: in docs/journal/2026-09-14-runnable-artifact-dependencies.md places; serial
#: minimum of three fresh processes through the lane's run_twin with
#: file_search_cache_time=9223372036854775807 set before child boot [measured
#: 2026-09-18: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=6944d06ce96fdbcd1faefb640f15dbfa0cf286dd].
#: RE-PINNED 2026-09-18, 31498393 to 31497684 (-709), the trunk merged
#: (f97c4b0a3, petta's 61 commits since c75181adc) with the definition batch's
#: load pushed as the running load (2da1155e3): every example moved with the
#: engine, 279 of 294 cheaper (median -0.78%), through the compiled runnable
#: envelope executing each runnable form's fixed answer, name and fuel envelope
#: from compiled clauses, the trunk's trailed scopes and compiled context
#: readers (a b_getval/2 read per recorded assertion in place of the branch's
#: thread-local rows), the host listener door and the receipts loop probing the
#: owner once per set; serial minimum of three fresh processes through the
#: lane's run_twin [measured 2026-09-18: min-of-3 serial fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=55d451b670949c2dc9d2ab7bc678f33f21094bd2].
#: RE-PINNED 2026-09-21, 31497684 to 31950845 (+453161), the sixty libraries
#: derived in MeTTa landed with merge 97763e7fa eight hours after the previous
#: pin 55d451b67, so every example importing one now pays a MeTTa derivation
#: where it paid a Prolog body instead, which the 2026-09-14 ruling accepts
#: explicitly as the price of a library that survives the engine swap [measured
#: 2026-09-21: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=6e09cb25d5495c2db3283166e6ce4e07eefecfb2].
#: RE-PINNED 2026-09-24, 31950845 to 31964566 (+13721), placed on the full-
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
#: the 20 commits 6167a0fb2..864c4bac0, where the sweep puts the probes' only
#: step at e1acacad2, which clears a space's import bookkeeping from the module
#: that owns it; da91bc244 confines an exact removal's selection to its own
#: atom: native_retract_one/2 now records the selected clause's head, a
#: clause/3 lookup per exact removal, and checks each removal made while the
#: selector is live against it, a few inferences per removal (+8 on most twins,
#: +24 to +192 on the library twins that withdraw package rows); where a twin's
#: move exceeds these steps, the remainder is drift that stayed inside its band
#: (four inferences, or its own declared allowance) on every other interval
#: [measured 2026-09-24: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=WORKTREE].
#: RE-PINNED 2026-09-24, 31964566 to 31962770 (-1796), 0a81c782f loads a
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
#: RE-PINNED 2026-09-24, 31962770 to 31962803 (+33), 0847c3d4c decides a
#: platform capability the first time anything reads it, by whether every
#: library its census row names resolves, where only a failed load used to
#: record anything, and 984eabe23 keeps each verdict in a flag decided under a
#: mutex so two threads' first reads agree; the count moves by what the twin's
#: reads now decide, about 660 inferences for a one-library capability and
#: 1,964 for markup's three, and by a few where it reads the census without
#: deciding [measured 2026-09-24: min-of-3 serial fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=d832d20e8edfdad28ad52815757ba9e685ad2de3].
#: RE-PINNED 2026-09-24, 31962803 to 31980112 (+17309), +36 at aaeea643a, whose
#: seat 5b0b92274 adds twelve predicates to module user that filereader's
#: registration walk above forty names reads at three inferences each; +9 at
#: b7e3d3bcb, whose three new metta_engine predicates that walk reads at three
#: inferences each; +17,246 at ae1cc8936, where a registration batch of
#: thirteen names or more walks the visible predicate table at two inferences a
#: predicate that asking per name spent inside one C call, and a batch above
#: forty tests each predicate with a dict at one inference fewer than the AVL;
#: +18 at b5eb39acd, whose three new engine exports the registration walk above
#: twelve names reads at two inferences each [measured 2026-09-24: min-of-3
#: serial fresh processes at HEAD in battery 118 holding the committed tree
#: alone (BATTERY_KEEP='', 11:56); each step read with its parent and child in
#: turn in battery 115 (10:42 to 11:18), 117 (11:01 to 12:10) or 120 (12:04 to
#: 12:13) from committed trees or this job's patched copies of them, none from
#: a working tree; 850d2a660's and 0f6d29ba6's split from provider-carry's own
#: pairs, aaeea643a's on the ladder before 10:05; command=python
#: extensions/python/tools/twin_coverage.py --measure --rounds 3;
#: commit=c7d7244fbe6d32d024ca8c61b336008e98b156ef].
#: RE-PINNED 2026-09-24, 31980112 to 31979518 (-594), d4a365c16 holds the
#: support graph's visited set and the reference refresh's space sets in SWI
#: tries instead of library(nb_set): a membership check is one foreign call
#: where nb_set probed in Prolog, four inferences a step past a taken slot,
#: from a slot a library space's path-bearing name decided, and a walk over a
#: node or two pays a few inferences more for the trie's setup (-476); gate-
#: perf's d781eab8f carries an exact removal's selected head from the code that
#: selected it, so a withdrawal copies its equation once: 23 inferences fewer
#: for each equation removal the twin adopts and 4 for each it selects (-184);
#: the packages job's 90be572a9 and 4003462fe register Prolog through one
#: engine service: +22 for each library the twin imports (ten new engine
#: predicates and two user imports in the registration walk at two inferences
#: each, less the retired loaded_extension_file/2), and 146 inferences for a
#: Prolog file's origin or 220 for a text's SHA-256 on a twin that registers
#: Prolog (+66); each step read serially on its own committed tree, from gate-
#: perf's pin at c7d7244fb, and the fixed tree 4ff69551e reads what 4003462fe
#: does [measured 2026-09-24: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=4ff69551e0e226442cf7257b96af858adda957a4].
#: RE-PINNED 2026-09-24, 31979518 to 31979524 (+6), +6 at the change this re-
#: pin lands with, which groups a whole reference face's heads in one pass over
#: its sorted entries where each head searched the whole face, and whose three
#: imports into the engine module are one more predicate filereader's
#: registration walk reads above twelve names, pairs_keys/2, and three a
#: restricted space's core steps over as it enumerates that module's predicates
#: [measured 2026-09-24: the twins lane alone on the base 8d651070d and on the
#: base with this change, one after the other in battery 117's one path, every
#: component at its pin; command=sh tools/check.sh twins (twin_coverage.py
#: inside tools/bounded.sh); commit=8bda9d5525a8174a8304376e111df8da258076a9].
#: RE-PINNED 2026-09-24, 31979524 to 31979745 (+221), +221 at the change this
#: re-pin lands with, which publishes a from row by itself when rows are all a
#: space owes: its 36 predicates visible to filereader's registration walk cost
#: a batch above twelve names 72 inferences, each restricted space's core about
#: 28 a predicate, and every whole publication and face event its ledger's
#: bookkeeping [measured 2026-09-24: the twins lane alone on 8d651070d with the
#: change before this one and with this change too, one after the other in
#: battery 117's one path, every component at its pin; command=sh
#: tools/check.sh twins (twin_coverage.py inside tools/bounded.sh);
#: commit=e4b7448d1f1bd98733f1b04c3906aaa42f35ef1a].
#: RE-PINNED 2026-09-24, 31979745 to 31979930 (+185), bfs_all seeds the
#: duplicate store with add-unique-or-fail, as the example now does where it
#: called the undefined add-unique-item-or-empty, so the start board is
#: dequeued once and the search answers 181,440: one add-unique-or-fail call
#: more, and one dequeue with its two neighbour checks fewer [measured
#: 2026-09-24: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=3488b97533f948baeb380863c79629a968f08989].
#: RE-PINNED 2026-09-25, 31979930 to 31979936 (+6), the pragma refusal defines
#: require_metta_pragma_capability/2 in the engine module, and on the same tree
#: defining it without calling it moves this twin by the whole of the change's
#: move, so the cost is one more engine predicate and functor met through the
#: engine's walks over its predicate and functor tables, among them
#: filereader:existing_predicate_arities/2, which charges two inferences for
#: each predicate visible from the loading module at every load of a source
#: registering more than twelve names (i-arity-walk-all-predicates); the
#: change's work at a pragma write does not reach this twin [measured
#: 2026-09-25T00:49:18+10:00: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-25, 31979936 to 31979996 (+60), the py-* doors change
#: makes more predicates visible from filereader, and
#: filereader:existing_predicate_arities/2 walks every predicate visible there
#: at two inferences each whenever a source registering more than twelve names
#: loads: on one tree the change's new engine predicates alone, defined with
#: their two boot uses taken out, make eight more visible and move this twin by
#: 16 for each such load, and the whole change by 20, ten more at its loads
#: (i-arity-walk-all-predicates) [measured 2026-09-25T02:55:55+10:00: min-of-3
#: serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-25, 31979996 to 31979982 (-14), the registration refusal
#: kind makes the (vocabulary refusal-kind ...) catalog row fifteen members
#: long instead of fourteen, which moves it from storage arity 17 to 18, where
#: the Python seat's (vocabulary door-answers ...) already sits, so &metta
#: keeps one storage arity fewer and each open-tail catalog lookup,
#: metta_catalog_clause/2 visiting every arity, costs five inferences less; and
#: metta_host_signal_message//2 is one more predicate the engine module
#: defines, which every walk over the engine's predicates pays: filereader's
#: existing_predicate_arities/2 two inferences a registration of more than
#: twelve names, each restricted space's core 29, and 11-reference_rows' walk
#: 240, each reproduced exactly by one inert predicate added to the engine on
#: the base [measured 2026-09-25T06:37:23+10:00: min-of-3 serial fresh
#: processes; command=python extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-25, 31979982 to 31979954 (-28), the host evaluation door
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
#: more than twelve names [measured 2026-09-25T07:01:32+10:00: min-of-3 serial
#: fresh processes; command=python extensions/python/tools/twin_coverage.py
#: --repin].
#: RE-PINNED 2026-09-25, 31979954 to 31979984 (+30), Runtime.reclaim(), the
#: reclamation barrier metta_py_reclaim/1, adds five predicates to user, and
#: existing_predicate_arities/2 walks every user predicate about twice per
#: large load (i-arity-walk-all-predicates) [measured
#: 2026-09-25T11:25:25+10:00: one full twins lane before this commit and one
#: with it, the two read on one battery path at the landing's HEAD;
#: command=python extensions/python/tools/twin_coverage.py].
BUDGET = 31979984

#: DIVERGED 2026-09-07, the example holds 2 atoms the twin does not (2 =) and
#: the twin holds 5 the example does not (3 =, 2 @doc): the twin is an ordinary
#: Python program and its body lowers to the engine's own forms: a match
#: statement is ONE equation whose body is a case tower where the example
#: writes one clause per arm, a named intermediate is a let* the original does
#: not have, a Python truth test wraps its condition in py-truthy, and the
#: annotations and docstrings that come with it are stored beside them
#: [measured 2026-09-07: the two stored-atom surpluses, one fresh process per
#: side; command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=9010a79b01c9b2a66b96a3952fa378fb3e939dc3].
#: DIVERGED 2026-09-24, the example holds 2 atoms the twin does not (2 =) and
#: the twin holds 5 atoms the example does not (3 =, 2 @doc): both bfs_all
#: equations now seed the duplicate store before the search, the example's
#: through (add-unique-or-fail &dup $Start) and the twin's through its own
#: space, so each side's stored bfs_all atom changed and the census is the one
#: before [measured 2026-09-24: the two stored-atom surpluses, one fresh
#: process per side; command=python extensions/python/tools/twin_coverage.py
#: --repin; commit=3488b97533f948baeb380863c79629a968f08989].
DIVERGENCE = "cbd575ab625831a7a68a80886d4df6be6aa903a295dad6907164eb1861bcd56b"
