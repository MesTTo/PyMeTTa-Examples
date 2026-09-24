"""Purpose: examples/ch17-concurrency-and-the-loop/13-class_decorators.metta in Python.

The decorators and special methods of a class are rows the engine already
has: a property is an accessor equation, a class method takes the class
symbol, a static method has no receiver, `functools.total_ordering` derives
the comparisons it wrote from the root and equality, `__add__`, `__len__`,
`__iter__` and `__call__` are the words add, len, iter and call, and an
abstract method is an arrow with no equation. The example writes those rows
by hand; this twin declares the classes and proves the same claims.
"""

import functools
from abc import ABC, abstractmethod
from dataclasses import dataclass

from metta import S, V


def twin(m):
    """Declare the decorated classes and prove the example's twelve claims."""
    @m.define
    @dataclass(frozen=True)
    class Circle:
        r: int

        @property
        def area(self) -> int:
            return 3 * (self.r * self.r)

        @classmethod
        def unit(cls) -> "Circle":
            return Circle(1)

        @staticmethod
        def grow(r: int, by: int) -> int:
            return r + by

    @m.define
    @functools.total_ordering
    @dataclass(frozen=True)
    class Money:
        cents: int

        def __eq__(self, other: "Money") -> bool:
            return self.cents == other.cents

        def __lt__(self, other: "Money") -> bool:
            return self.cents < other.cents

    @m.define
    @dataclass(frozen=True)
    class Vector:
        x: int
        y: int

        def __add__(self, other: "Vector") -> "Vector":
            return Vector(self.x + other.x, self.y + other.y)

    @m.define
    @dataclass(frozen=True)
    class Stack:
        items: tuple[int, ...]

        def __len__(self) -> int:
            return len(self.items)

        def __iter__(self):
            for item in self.items:  # noqa: UP028 -- each yield is one answer, the generator lowering
                yield item

    @m.define
    @dataclass(frozen=True)
    class Adder:
        n: int

        def __call__(self, x: int) -> int:
            return self.n + x

    @m.define
    class Shape(ABC):
        @abstractmethod
        def area(self) -> int: ...

    @m.define
    @dataclass(frozen=True)
    class Square(Shape):
        s: int

        def area(self) -> int:
            return self.s * self.s

    # !(test (Circle-area (Circle 2)) 12)
    assert Circle(2).area == 12
    # !(test (Circle-unit Circle) (Circle 1))
    assert Circle.unit() == Circle(1)
    # !(test (Circle-grow 2 3) 5)
    assert Circle.grow(2, 3) == 5
    # !(test (Money-le (Money 5) (Money 5)) True)
    assert Money(5) <= Money(5)
    # !(test (Money-gt (Money 7) (Money 5)) True)
    assert Money(7) > Money(5)
    # !(test (Money-gt (Money 5) (Money 5)) False)
    assert not Money(5) > Money(5)
    # !(test (Vector-add (Vector 1 2) (Vector 3 4)) (Vector 4 6))
    assert Vector(1, 2) + Vector(3, 4) == Vector(4, 6)
    # !(test (Stack-len (Stack (1 2 3))) 3)
    assert len(Stack((1, 2, 3))) == 3
    # !(test (collapse (Stack-iter (Stack (1 2 3)))) (1 2 3))
    assert list(Stack((1, 2, 3))) == [1, 2, 3]
    # !(test (Adder-call (Adder 10) 4) 14)
    assert Adder(10)(4) == 14
    # !(test (Square-area (Square 3)) 9)
    assert Square(3).area() == 9
    # !(test (collapse (match &Shape (: Shape-area $arrow) $arrow)) ((-> Shape Number)))
    assert [row.arrow for row in m.metta.space(S.Shape)[S[":"](S.Shape_area, V.arrow)]] == [S["->"](S.Shape, S.Number)]


#: The twin declares its classes, whose grains, accessors, method equations,
#: dispatch rows, call contracts and Python proxies the declaration derives,
#: and then proves the example's claims through them; the native example
#: writes only the rows its claims read. The difference is that declaration
#: and crossing work, the OVERRUN declared below.
#: [measured: 13979257 twin and 249305 native inferences; command=python
#: extensions/python/tools/twin_coverage.py --measure
#: examples/ch17-concurrency-and-the-loop/13-class_decorators.metta; fixture=min of three
#: serial fresh processes in a provisioned battery worktree with the .qlf set
#: warm; commit=a8cfae1f5c0be628bc40eb7c18b07749d995e9a0].
#: RE-PINNED 2026-09-18, 13979257 to 13952303 (-26954), the branch's landings
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
#: RE-PINNED 2026-09-18, 13952303 to 13950837 (-1466), 49478d67a landed the
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
#: RE-PINNED 2026-09-18, 13950837 to 13877188 (-73649), the trunk merged
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
#: RE-PINNED 2026-09-19, 13877188 to 13879438 (+2250), cost follows the answer:
#: a block is charged for its own thread's work and for the workers whose
#: answers it used, so a race's losers, the branches par-any and par-forall
#: stopped, and a cancelled future or timer are joined through the engine's
#: discarding door (metta_join_measured/3) and their partial spend, which only
#: the schedule sized, is taken out; lib_thread's join no longer polls on the
#: host patched for swi-thread-join-detach-window, and the seat's counter doors
#: read the discarded tally outside the window they bracket (metta_py_stats/2,
#: metta_py_work/2) [measured 2026-09-19: min-of-3 serial fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=32335687084e4d8ad43cf8800f2dedce707fa137].
#: ENVELOPED 2026-09-19: the point 13879438 becomes the envelope
#: 13879438..13900770 over 12: under the lane's own protocol (full-
#: lane/294/workers=32, ten rounds) the counter reads 13879438 every time, and
#: under the gate's concurrent lanes (three runs) it reads 13900245, 13900770,
#: each reading exact on its run; the extra mode is the same program's work
#: done on a different thread under load, a loader flight or a settle step the
#: foreground runs itself when the worker is late, which the join accounting
#: does not reach; an envelope states what was observed and the point was a lie
#: under the gate [measured 2026-09-19: the twins lane alone on the final tree
#: and under the gate's concurrent lanes, wt-battery-2 ai-full-
#: gate-10da82e4a.log, ai-full-gate-19fdb0b86.log, ai-lanes-exports-back.log;
#: commit=1ccbb142315d16a719807cd2c9754e4a2fcefdf1].
#: RE-OBSERVED 2026-09-21 under 'full-lane/323/workers=32/file-search-cache-
#: time=9223372036854775807/before-boot', 13879438..13900770 to
#: 11379374..11379374 over 10 observations: the corpus grew from 294 examples
#: to 323 with the merge that derived sixty libraries in MeTTa (97763e7fa), and
#: an empirical envelope is a claim about ONE scheduler's protocol, so the
#: earlier observations could not license this one; these ten are this tree's
#: own and are not pooled with that run [measured 2026-09-21: ten full-lane
#: observations; command=python extensions/python/tools/twin_coverage.py
#: --observe --rounds 10; commit=8d2e8bb94da53a1a35c79d440cc09ef56f46153e].
#: RE-OBSERVED 2026-09-21 under 'full-lane/323/workers=32/file-search-cache-
#: time=9223372036854775807/before-boot', 11379374..11379374 to
#: 11379374..11379374 over 20 observations: ten observations did not cover the
#: tail of an example whose count varies: 01-mutex_and_transaction read 23659
#: against the 23661..23666 those ten recorded, and twenty put its 23657..23669
#: around that reading. The protocol records observed extrema exactly and
#: refuses an invented allowance, so the only lawful way to cover a tail is to
#: observe it [measured 2026-09-21: twenty full-lane observations;
#: command=python extensions/python/tools/twin_coverage.py --observe --rounds
#: 10; commit=43e964002671a680825823b7ab4c1020de20f651].
#: RE-OBSERVED 2026-09-24 under 'full-lane/323/workers=32/file-search-cache-
#: time=9223372036854775807/before-boot', 11379374..11379374 to
#: 10872695..10872695 over 20 observations: the tree under these envelopes
#: moved after their last observation at 43e964002: the package-model changes
#: a7955cd07 (lib 629c86c's library split), 54784fded, 63b910f4f, d6e09995c and
#: 6167a0fb2, 814b99468's self-call dependencies, f2822e2ae's boot host check
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
#: time=9223372036854775807/before-boot', 10872695..10872695 over 20 to
#: 10872695..10872697 over 28: the 8 whole-lane runs of this runtime the
#: envelope did not yet hold read the pin run's first lane 10872695; the pin
#: run's second lane 10872695; the pin run's third lane 10872695; the first
#: final lane 10872695; the purged lane on 49e2b250d 10872695; the purged lane
#: on 26de4ddcf 10872695; the purged lane after a8487162 10872695; the purged
#: lane after 878b8bd9 10872697. They are the pin run's own lanes on the
#: 6a7ac233d snapshot and the final lanes on 49e2b250d and 26de4ddcf, whose
#: commits touch no path this twin runs, and each reads every deterministic
#: twin exactly as a battery whose governed QLF set was compiled in place does,
#: so none carries a moved artifact's cost; the lane whose battery carried a
#: lib_import.qlf compiled in wt-merge is left out. A whole-lane run under this
#: protocol on this runtime is an observation, so the envelope is the union of
#: the extrema and the sum of the counts [measured 2026-09-24: 8 whole-lane
#: runs, sh extensions/python/check.sh twins in battery 5; command=python
#: extensions/python/tools/twin_coverage.py; commit=WORKTREE].
#: RE-OBSERVED 2026-09-24 under 'full-lane/323/workers=32/file-search-cache-
#: time=9223372036854775807/before-boot', 10872695..10872697 to
#: 10563157..10563941 over 20 observations: the tree moved under this envelope:
#: 0a81c782f loads a library's Prolog half through the boot's claim, so
#: lib_thread's half reads the .qlf the claim's hermetic child wrote, started
#: from the running home's own swipl, where it had compiled from source in
#: every process, about 292k inferences on each of the six class twins; before
#: that commit the six already read about 8k under their 28-observation
#: envelopes on the parent tree, with the Channel and Debugger reaping
#: (44e52aae1) and the host-patch split (5c32234cf) each reverted, and
#: class_grains read 6,455,023, 6,460,447, 6,455,063 and 6,453,264 in four
#: purged or gate lanes between 00:57 and 05:41 on 2026-09-24, so that drift
#: follows the battery rather than a commit; the about 10.3k per Prolog-half
#: load that a 2026-09-24 paragraph above charges to f2822e2ae's boot host
#: check was never the check's own cost: from f2822e2ae on the check refused
#: every compile child the stock swipl ran, so no child wrote an artifact and
#: every governed half a half loads compiled from source in every process; an
#: empirical envelope is a claim about one scheduler's protocol on one tree, so
#: these observations are this tree's own and are not pooled with the earlier
#: ones [measured 2026-09-24: 20 full-lane observations; command=python
#: extensions/python/tools/twin_coverage.py --observe --rounds 20;
#: commit=0a81c782fd6ba00984c36e58e228f73bca810dee].
#: RE-OBSERVED 2026-09-24 under 'full-lane/323/workers=32/file-search-cache-
#: time=9223372036854775807/before-boot', 10563157..10563941 to
#: 9529033..9529033 over 21 observations: the tree moved under this envelope
#: after its observation at 0a81c782f: read serially, one fresh process a side,
#: on each first-parent rung from 0a81c782f to the fixed tree 4ff69551e in one
#: battery, its twin went from 10,560,787 to 9,529,033 (at 0a81c782f the serial
#: protocol read 2,370 under the full lane's 10,563,157..10,563,941, and on the
#: fixed tree the two agree, so that difference is part of the band's move and
#: falls on no rung); the WebAssembly job's 0847c3d4c decides a platform
#: capability on its first read (+5,528); its 984eabe23 keeps the verdict in a
#: flag decided under a mutex (+6,143); provider-carry's aaeea643a carries a
#: provider's stored term back as the engine gave it (-6,143); 4890e870d gives
#: the governed QLF set one producer (+5,969); gate-perf's b7e3d3bcb keeps each
#: reference head's last bind in its own row, so a from row rebinds only the
#: heads it brings (-401,159); gate-perf's ae1cc8936 walks the visible
#: predicate table once for a batch of 13 to 40 registered names, two
#: inferences a visible predicate, about 11,500 for each library import that
#: registers such a batch (+8,253); provider-carry's 850d2a660 reads a native
#: space's lengths in ascending order (-6,065); provider-carry's 1748f6a06 asks
#: early-exit questions by key or in ascending arity (+114); the packages job's
#: b5eb39acd names get-property's and setup!'s subject by a from source's rule
#: (-3,173); d4a365c16 holds the support graph's visited set and the reference
#: refresh's space sets in tries instead of library(nb_set) (-629,428); gate-
#: perf's d781eab8f copies a withdrawn equation once (-12,911); the packages
#: job's registration service, 90be572a9 in the engine with 4003462fe in the
#: seat, net (+1,118); until d4a365c16 this count followed library(nb_set)'s
#: probing, which starts from a slot the variant hash of each space's name
#: decides, so a step before it carries a change in the names the run's spaces
#: hold as well as the work its commit adds, and d4a365c16's own step is that
#: probing's cost in this battery's path, less the few inferences a trie's
#: setup costs a walk; an empirical envelope is a claim about one scheduler's
#: protocol on one tree, so these observations are this tree's own and are not
#: pooled with the earlier ones [measured 2026-09-24: 21 full-lane observations
#: on the fixed tree, the twenty rounds of --observe and one run of the lane
#: itself; command=python extensions/python/tools/twin_coverage.py --observe
#: --rounds 20; commit=4ff69551e0e226442cf7257b96af858adda957a4].
#: RE-OBSERVED 2026-09-24 under 'full-lane/323/workers=32/file-search-cache-
#: time=9223372036854775807/before-boot', 9529033..9529033 to 9259305..9259305
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
#: time=9223372036854775807/before-boot', 9259305..9259305 to 9031352..9031352
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
#: POOLED 2026-09-24 under 'full-lane/323/workers=32/file-search-cache-
#: time=9223372036854775807/before-boot', 9031352..9031352 over 20 to
#: 9031352..9031358 over 24: the four whole-lane runs of this runtime the
#: rounds did not hold, the twins lane alone, read 9,031,352 in battery 117's
#: pass over the base and both changes and in two runs with the delta
#: publication's twins in battery 119, and 9,031,358 on the committed tree
#: e4b7448d1 in battery 117; the twin's serial minimum of three reads 9,031,352
#: on the committed tree 44f21cf1a and on the tree the rounds observed alike,
#: in one battery path, so the six belong to that whole-lane run and not to a
#: runtime the envelope misses, and a whole-lane run under this protocol on
#: this runtime is an observation, so the envelope is the union of the extrema
#: and the sum of the counts [measured 2026-09-24: sh tools/check.sh twins
#: alone, on 8d651070d with the delta publication and the change before it in
#: batteries 117 and 119 and on the committed tree e4b7448d1 in battery 117;
#: command=python extensions/python/tools/twin_coverage.py;
#: commit=e4b7448d1f1bd98733f1b04c3906aaa42f35ef1a].
#: RE-OBSERVED 2026-09-24 under 'full-lane/323/workers=32/file-search-cache-
#: time=9223372036854775807/before-boot', 9031352..9031358 to 9027178..9027178
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
#: time=9223372036854775807/before-boot', 9027178..9027178 to 9020757..9020760
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
#: RE-OBSERVED 2026-09-25 under 'full-lane/323/workers=32/file-search-cache-
#: time=9223372036854775807/before-boot', 9020757..9020760 to 9021612..9021612
#: over 20 observations: the pragma refusal defines
#: require_metta_pragma_capability/2 in the engine module, and on the same tree
#: defining it without calling it moves this twin by the whole of the change's
#: move, so the cost is one more engine predicate and functor, whose place in
#: the engine's predicate and functor tables these twins' walks follow; which
#: walk carries it here is not profiled, and the change's work at a pragma
#: write does not reach this twin [measured 2026-09-25T00:50:00+10:00: 20 full-
#: lane observations; command=python extensions/python/tools/twin_coverage.py
#: --observe --rounds 20].
BUDGET = {
    "minimum": 9021612,
    "maximum": 9021612,
    "observations": 20,
    "protocol": "full-lane/323/workers=32/file-search-cache-time=9223372036854775807/before-boot"
}
OVERRUN = 13729952

#: DIVERGED 2026-09-18, the example holds 0 atoms the twin does not (none) and
#: the twin holds 113 atoms the example does not (100 :, 13 @doc): The twin's
#: @m.define derives the class's arrows, application and binding contracts and
#: documentation rows into the class space beside the equations the example
#: writes by hand, so the referenced content differs by exactly those derived
#: rows [measured 2026-09-18: the two stored-atom surpluses, one fresh process
#: per side; command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=a8cfae1f5c0be628bc40eb7c18b07749d995e9a0].
DIVERGENCE = "c7ef13de8b97b32596745a6f10048a9c9662d7c32af16a8f3eb96ab6d52f46f2"
