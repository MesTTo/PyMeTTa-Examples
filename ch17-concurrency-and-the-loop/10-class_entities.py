"""Purpose: examples/ch17-concurrency-and-the-loop/10-class_entities.metta in Python.

An ordinary dataclass is an entity: `@m.define` mints a token handle for each
instance and keeps its fields as facts in the class space, a field write is
the derived writer inside the caller's transaction, a method that raises
leaves nothing half-written, and the population is one query. The example
writes those rows by hand; this twin declares the class and proves the same
claims.
"""

from dataclasses import dataclass

from metta import MettaError, S, Symbol, V


def twin(m):
    """Declare the entity class and prove the example's six claims."""
    @m.define
    @dataclass
    class Account:
        owner: Symbol
        balance: int

        def deposit(self, amount: int) -> bool:
            self.balance = self.balance + amount
            return True

        def withdraw(self, amount: int) -> bool:
            if self.balance < amount:
                msg = "overdraft"
                raise ValueError(msg)
            self.balance = self.balance - amount
            return True

    alice, bob = Account(S.alice, 40), Account(S.bob, 80)
    # !(test (Account-deposit &alice 25) True)
    assert alice.deposit(25) is True
    # !(test (Account-balance &alice) 65)
    assert alice.balance == 65
    # !(test (if-error (transaction (Account-withdraw &alice 500)) refused unexpected) refused)
    try:
        m.transaction(lambda: alice.withdraw(500))
    except MettaError:
        refused = True
    else:
        refused = False
    assert refused
    # !(test (Account-balance &alice) 65)
    assert alice.balance == 65
    # !(test (Account-withdraw &bob 30) True)
    assert bob.withdraw(30) is True
    # !(test (msort (collapse (match &Account (_field-balance $account $n) $n))) (50 65))
    accounts = m.metta.space(S.Account)
    assert sorted(row.n.value for row in accounts[S["_field-balance"](V.account, V.n)]) == [50, 65]


#: The twin declares its classes, whose grains, accessors, method equations,
#: dispatch rows, call contracts and Python proxies the declaration derives,
#: and then proves the example's claims through them; the native example
#: writes only the rows its claims read. The difference is that declaration
#: and crossing work, the OVERRUN declared below.
#: [measured: 5161225 twin and 83143 native inferences; command=python
#: extensions/python/tools/twin_coverage.py --measure
#: examples/ch17-concurrency-and-the-loop/10-class_entities.metta; fixture=min of three
#: serial fresh processes in a provisioned battery worktree with the .qlf set
#: warm; commit=a8cfae1f5c0be628bc40eb7c18b07749d995e9a0].
#: RE-PINNED 2026-09-18, 5161225 to 5161376 (+151), The classes package's
#: special-method and decorator rows: the twin declares its classes and the
#: declaration derives the arrows, dispatch and binding contracts and
#: documentation rows beside the equations the example writes by hand [measured
#: 2026-09-18: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=a8cfae1f5c0be628bc40eb7c18b07749d995e9a0].
#: RE-PINNED 2026-09-18, 5161376 to 5144705 (-16671), the branch's landings
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
#: RE-PINNED 2026-09-18, 5144705 to 5147546 (+2841), 49478d67a landed the
#: polynomial carrier, whose preset row and variable claim every catalog scan
#: reads, the product carriers and the guard read in the fixpoint door, and the
#: binding's five-element rule read: the examples that scan the catalog moved
#: with their twins (restricted_spaces +522, the three pln twins +63 each, the
#: two tabling twins +20 and +10, reflect_lib +6) and the twins that cross the
#: seat's declaration and query paths moved with their examples unmoved (the
#: class twins between -4212 and +2841, the reference twins +208 and +317, the
#: tagged fixpoint twin +610, the documentation twins -22 and -50, types_nondet
#: +5) [measured 2026-09-18: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=bf5f100591493a91324b1d7552b5ad2731601691].
#: RE-PINNED 2026-09-18, 5147546 to 5157029 (+9483), the trunk merged
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
#: RE-PINNED 2026-09-19, 5157029 to 5157302 (+273), cost follows the answer: a
#: block is charged for its own thread's work and for the workers whose answers
#: it used, so a race's losers, the branches par-any and par-forall stopped,
#: and a cancelled future or timer are joined through the engine's discarding
#: door (metta_join_measured/3) and their partial spend, which only the
#: schedule sized, is taken out; lib_thread's join no longer polls on the host
#: patched for swi-thread-join-detach-window, and the seat's counter doors read
#: the discarded tally outside the window they bracket (metta_py_stats/2,
#: metta_py_work/2) [measured 2026-09-19: min-of-3 serial fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=32335687084e4d8ad43cf8800f2dedce707fa137].
#: ENVELOPED 2026-09-19: the point 5157302 becomes the envelope
#: 5157302..5178578 over 11: under the lane's own protocol (full-
#: lane/294/workers=32, ten rounds) the counter reads 5157302 every time, and
#: under the gate's concurrent lanes (three runs) it reads 5178578, each
#: reading exact on its run; the extra mode is the same program's work done on
#: a different thread under load, a loader flight or a settle step the
#: foreground runs itself when the worker is late, which the join accounting
#: does not reach; an envelope states what was observed and the point was a lie
#: under the gate [measured 2026-09-19: the twins lane alone on the final tree
#: and under the gate's concurrent lanes, wt-battery-2 ai-full-
#: gate-10da82e4a.log, ai-full-gate-19fdb0b86.log, ai-lanes-exports-back.log;
#: commit=1ccbb142315d16a719807cd2c9754e4a2fcefdf1].
#: RE-OBSERVED 2026-09-21 under 'full-lane/323/workers=32/file-search-cache-
#: time=9223372036854775807/before-boot', 5157302..5178578 to 3808780..3808780
#: over 10 observations: the corpus grew from 294 examples to 323 with the
#: merge that derived sixty libraries in MeTTa (97763e7fa), and an empirical
#: envelope is a claim about ONE scheduler's protocol, so the earlier
#: observations could not license this one; these ten are this tree's own and
#: are not pooled with that run [measured 2026-09-21: ten full-lane
#: observations; command=python extensions/python/tools/twin_coverage.py
#: --observe --rounds 10; commit=8d2e8bb94da53a1a35c79d440cc09ef56f46153e].
#: RE-OBSERVED 2026-09-21 under 'full-lane/323/workers=32/file-search-cache-
#: time=9223372036854775807/before-boot', 3808780..3808780 to 3808780..3808780
#: over 20 observations: ten observations did not cover the tail of an example
#: whose count varies: 01-mutex_and_transaction read 23659 against the
#: 23661..23666 those ten recorded, and twenty put its 23657..23669 around that
#: reading. The protocol records observed extrema exactly and refuses an
#: invented allowance, so the only lawful way to cover a tail is to observe it
#: [measured 2026-09-21: twenty full-lane observations; command=python
#: extensions/python/tools/twin_coverage.py --observe --rounds 10;
#: commit=43e964002671a680825823b7ab4c1020de20f651].
#: RE-OBSERVED 2026-09-24 under 'full-lane/323/workers=32/file-search-cache-
#: time=9223372036854775807/before-boot', 3808780..3808780 to 3492135..3492135
#: over 20 observations: the tree under these envelopes moved after their last
#: observation at 43e964002: the package-model changes a7955cd07 (lib 629c86c's
#: library split), 54784fded, 63b910f4f, d6e09995c and 6167a0fb2, 814b99468's
#: self-call dependencies, f2822e2ae's boot host check
#: (metta_require_patched_host, called once in qlf_load_engine, which adds
#: about 10.3k inferences to every later load of a library's Prolog half,
#: mechanism below the predicate not isolated) and 7472c4907's reference faces
#: marked rather than walked, each placed on the full-configuration first-
#: parent ladder; an empirical envelope is a claim about one scheduler's
#: protocol on one tree, so these twenty observations are this tree's own and
#: are not pooled with the earlier ones [measured 2026-09-24: 20 full-lane
#: observations; command=python extensions/python/tools/twin_coverage.py
#: --observe --rounds 20; commit=WORKTREE].
#: POOLED 2026-09-24 under 'full-lane/323/workers=32/file-search-cache-
#: time=9223372036854775807/before-boot', 3492135..3492135 over 20 to
#: 3492135..3492135 over 28: the 8 whole-lane runs of this runtime the envelope
#: did not yet hold read the pin run's first lane 3492135; the pin run's second
#: lane 3492135; the pin run's third lane 3492135; the first final lane
#: 3492135; the purged lane on 49e2b250d 3492135; the purged lane on 26de4ddcf
#: 3492135; the purged lane after a8487162 3492135; the purged lane after
#: 878b8bd9 3492135. They are the pin run's own lanes on the 6a7ac233d snapshot
#: and the final lanes on 49e2b250d and 26de4ddcf, whose commits touch no path
#: this twin runs, and each reads every deterministic twin exactly as a battery
#: whose governed QLF set was compiled in place does, so none carries a moved
#: artifact's cost; the lane whose battery carried a lib_import.qlf compiled in
#: wt-merge is left out. A whole-lane run under this protocol on this runtime
#: is an observation, so the envelope is the union of the extrema and the sum
#: of the counts [measured 2026-09-24: 8 whole-lane runs, sh
#: extensions/python/check.sh twins in battery 5; command=python
#: extensions/python/tools/twin_coverage.py; commit=WORKTREE].
#: RE-OBSERVED 2026-09-24 under 'full-lane/323/workers=32/file-search-cache-
#: time=9223372036854775807/before-boot', 3492135..3492135 to 3189481..3189717
#: over 20 observations: the tree moved under this envelope: 0a81c782f loads a
#: library's Prolog half through the boot's claim, so lib_thread's half reads
#: the .qlf the claim's hermetic child wrote, started from the running home's
#: own swipl, where it had compiled from source in every process, about 292k
#: inferences on each of the six class twins; before that commit the six
#: already read about 8k under their 28-observation envelopes on the parent
#: tree, with the Channel and Debugger reaping (44e52aae1) and the host-patch
#: split (5c32234cf) each reverted, and class_grains read 6,455,023, 6,460,447,
#: 6,455,063 and 6,453,264 in four purged or gate lanes between 00:57 and 05:41
#: on 2026-09-24, so that drift follows the battery rather than a commit; the
#: about 10.3k per Prolog-half load that a 2026-09-24 paragraph above charges
#: to f2822e2ae's boot host check was never the check's own cost: from
#: f2822e2ae on the check refused every compile child the stock swipl ran, so
#: no child wrote an artifact and every governed half a half loads compiled
#: from source in every process; an empirical envelope is a claim about one
#: scheduler's protocol on one tree, so these observations are this tree's own
#: and are not pooled with the earlier ones [measured 2026-09-24: 20 full-lane
#: observations; command=python extensions/python/tools/twin_coverage.py
#: --observe --rounds 20; commit=0a81c782fd6ba00984c36e58e228f73bca810dee].
#: RE-OBSERVED 2026-09-24 under 'full-lane/323/workers=32/file-search-cache-
#: time=9223372036854775807/before-boot', 3189481..3189717 to 2977239..2977239
#: over 21 observations: the tree moved under this envelope after its
#: observation at 0a81c782f: read serially, one fresh process a side, on each
#: first-parent rung from 0a81c782f to the fixed tree 4ff69551e in one battery,
#: its twin went from 3,191,359 to 2,977,239 (at 0a81c782f the serial protocol
#: read 1,642 over the full lane's 3,189,481..3,189,717, and on the fixed tree
#: the two agree, so that difference is part of the band's move and falls on no
#: rung); the WebAssembly job's 0847c3d4c decides a platform capability on its
#: first read (+1,752); its 984eabe23 keeps the verdict in a flag decided under
#: a mutex (-1,045); provider-carry's aaeea643a carries a provider's stored
#: term back as the engine gave it (+1,045); 4890e870d gives the governed QLF
#: set one producer (-2,335); gate-perf's b7e3d3bcb keeps each reference head's
#: last bind in its own row, so a from row rebinds only the heads it brings
#: (-26,757); gate-perf's ae1cc8936 walks the visible predicate table once for
#: a batch of 13 to 40 registered names, two inferences a visible predicate,
#: about 11,500 for each library import that registers such a batch (+12,607);
#: provider-carry's 850d2a660 reads a native space's lengths in ascending order
#: (-1,295); provider-carry's 1748f6a06 asks early-exit questions by key or in
#: ascending arity (+24); the packages job's b5eb39acd names get-property's and
#: setup!'s subject by a from source's rule (-2,329); d4a365c16 holds the
#: support graph's visited set and the reference refresh's space sets in tries
#: instead of library(nb_set) (-193,227); gate-perf's d781eab8f copies a
#: withdrawn equation once (-487); the packages job's registration service,
#: 90be572a9 in the engine with 4003462fe in the seat, net (-2,073); until
#: d4a365c16 this count followed library(nb_set)'s probing, which starts from a
#: slot the variant hash of each space's name decides, so a step before it
#: carries a change in the names the run's spaces hold as well as the work its
#: commit adds, and d4a365c16's own step is that probing's cost in this
#: battery's path, less the few inferences a trie's setup costs a walk; an
#: empirical envelope is a claim about one scheduler's protocol on one tree, so
#: these observations are this tree's own and are not pooled with the earlier
#: ones [measured 2026-09-24: 21 full-lane observations on the fixed tree, the
#: twenty rounds of --observe and one run of the lane itself; command=python
#: extensions/python/tools/twin_coverage.py --observe --rounds 20;
#: commit=4ff69551e0e226442cf7257b96af858adda957a4].
#: RE-OBSERVED 2026-09-24 under 'full-lane/323/workers=32/file-search-cache-
#: time=9223372036854775807/before-boot', 2977239..2977239 to 2836578..2836578
#: over 20 observations: the tree moved under this envelope by the change this
#: observation lands with, which publishes a whole reference face's heads from
#: one pass over its sorted entries where each head searched the whole face for
#: its roots, a findall over every entry per head: a whole publication over a
#: face of many heads stops paying heads times entries steps, one over a face
#: of one to three entries pays the grouping's fixed cost of about eight calls,
#: and the change's pairs_keys/2 import is one more predicate filereader's
#: registration walk reads, 2 inferences for each registration batch above
#: twelve names; these observations are the tree's own and are not pooled with
#: the earlier ones [measured 2026-09-24: 20 full-lane observations;
#: command=python extensions/python/tools/twin_coverage.py --observe --rounds
#: 20; commit=8bda9d5525a8174a8304376e111df8da258076a9].
#: RE-OBSERVED 2026-09-24 under 'full-lane/323/workers=32/file-search-cache-
#: time=9223372036854775807/before-boot', 2836578..2836578 to 2838586..2838586
#: over 20 observations: the tree moved under this envelope by the change this
#: observation lands with, which publishes a space's from rows by themselves
#: when rows are all it owes, where each new row republished every row before
#: it: of the drain decisions while each example loads, class_decorators goes
#: by rows in 12 of 21, reference_maps in 14 of 23, class_dispatch in 5 of 38,
#: class_grains in 4 of 181, class_prototypes in 2 of 30, reference_loading in
#: 2 of 19, and class_values and class_entities in none of 3 and 14; every
#: publication now runs the ledger's decision, a stored plan and a settle,
#: about 25 to 30 inferences, every face event writes its space's ledger fact,
#: about three, and each registration batch above twelve names pays 72
#: inferences for the 36 predicates filereader's walk now sees; these
#: observations are the tree's own and are not pooled with the earlier ones
#: [measured 2026-09-24: 20 full-lane observations; command=python
#: extensions/python/tools/twin_coverage.py --observe --rounds 20;
#: commit=e4b7448d1f1bd98733f1b04c3906aaa42f35ef1a].
#: RE-OBSERVED 2026-09-24 under 'full-lane/323/workers=32/file-search-cache-
#: time=9223372036854775807/before-boot', 2838586..2838586 to 2839396..2839396
#: over 20 observations: the tree moved under this envelope by the verdict
#: rename, and by an atom-table layout effect rather than any work the rename
#: adds: its metta_hook_invalid_verdict/5 in engine/metta/space_hooks.pl, which
#: no class twin reaches, names metta_hook_handler_arity, one atom more
#: interned at load, and something the class twins run visits terms in atom-
#: handle order, so its call count follows the table; HEAD with a never-taken
#: branch in that clause naming a fresh atom moves 08-class_grains +2,036,
#: 10-class_entities +810, 11-class_dispatch +2,694, 12-class_prototypes +3,930
#: and 13-class_decorators -4,174, exactly as the rename does, while the same
#: branch built from atoms the engine already holds moves none [measured
#: 2026-09-24: min-of-3 serial fresh processes, each branch in its own battery;
#: command=python extensions/python/tools/twin_coverage.py --measure --rounds
#: 3; fixture=the branch added to metta_hook_invalid_verdict/5 on the committed
#: tree; commit=961379005df28d1ac8d2f4d794035b98965b4a26]; these observations
#: are the tree's own and are not pooled with the earlier ones [measured
#: 2026-09-24: 20 full-lane observations; command=python
#: extensions/python/tools/twin_coverage.py --observe --rounds 20;
#: commit=5bae989dfe8735448d575856e72f735bb2043e24].
#: RE-OBSERVED 2026-09-24 under 'full-lane/323/workers=32/file-search-cache-
#: time=9223372036854775807/before-boot', 2839396..2839396 to 2837434..2837434
#: over 20 observations: the host switch of /home/user/Dev/swipl-patched from
#: .2 to .5, the native host of build 9's 36 patches, moved this twin out of
#: its envelope, measured .2 against .5 through two environment shims of one
#: shape on one tree; two channels are suspected and neither is measured on
#: this twin: the functor table's layout, which .5's added builtin atom
#: shared_table (swi-shared-table-waits-for-owner-beneath, src/ATOMS) shifts
#: and whose hash order engine/spaces/tokens.pl's metta_native_pair/4 reads
#: storage arities in, the order the class envelopes follow (a never-taken
#: branch building a new functor from existing atoms moves them, one naming a
#: fresh atom moves nothing); and the host's library QLFs, of which janus.qlf,
#: prolog_wrap.qlf and ugraphs.qlf are compiled differently on .2 and .5,
#: janus.qlf by 574 bytes from a byte-identical janus.pl [measured 2026-09-24:
#: 20 full-lane observations; command=python
#: extensions/python/tools/twin_coverage.py --observe --rounds 20;
#: commit=622e425d40c126681c04c7f7f81d92618ab83d0d].
BUDGET = {
    "minimum": 2837434,
    "maximum": 2837434,
    "observations": 20,
    "protocol": "full-lane/323/workers=32/file-search-cache-time=9223372036854775807/before-boot"
}
#: OVERRUN 2026-09-19, 5078082 to 5085304 (+7222): the twin costs 5178578
#: against the example's 83025 and a ceiling of 5171356 with the earlier
#: declaration; a minimal twin of this example costs 89193, inside the 91328
#: the band alone allows, so the distance is this twin's own program. the
#: twin's second exact mode under the gate's concurrent lanes (4,677,080 and
#: 5,178,578 against 4,655,324 and 5,157,302 under the lane's own protocol),
#: the same class work done on a different thread under load, a loader flight
#: or settle step the foreground runs itself when the worker is late, which the
#: join accounting does not reach; the budget is an envelope over both modes
#: (the ENVELOPED paragraph) and this overrun prices the parity band at the
#: loaded mode [measured 2026-09-19: one fresh process per side through the
#: lane's run_example and run_twin, the floor from a minimal twin built by the
#: probe; command=python extensions/python/benchmarks/probes/twin_floor.py;
#: commit=e1bc448fdf30906af83fb62c5ecc5feb8bd67ce3].
OVERRUN = 5085304

#: DIVERGED 2026-09-18, the example holds 0 atoms the twin does not (none) and
#: the twin holds 29 atoms the example does not (28 :, 1 @doc): The twin's
#: @m.define derives the class's arrows, application and binding contracts and
#: documentation rows into the class space beside the equations the example
#: writes by hand, so the referenced content differs by exactly those derived
#: rows [measured 2026-09-18: the two stored-atom surpluses, one fresh process
#: per side; command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=a8cfae1f5c0be628bc40eb7c18b07749d995e9a0].
DIVERGENCE = "faeeea409059c7d1cb1f46057cca72ff0ef555ba95b034f0038ef40a16102f41"
