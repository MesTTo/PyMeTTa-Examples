"""Purpose: examples/ch17-concurrency-and-the-loop/11-class_dispatch.metta in Python.

Inheritance is a head pattern: a base method is one equation over `self`, a
subclass that redefines the name adds an equation over its own constructor,
`super().describe()` is the base's qualified spelling, and `get-type` with the
`:<` edges is what `isinstance` means. The example writes those rows by
hand; this twin declares the classes and proves the same claims.
"""

from dataclasses import dataclass

from metta import S, V


def twin(m):
    """Declare the shape hierarchy and prove the example's six claims."""
    @m.define
    @dataclass(frozen=True)
    class Shape:
        def area(self) -> int:
            return 0

        def describe(self):
            return S.area_of(self.area())

    @m.define
    @dataclass(frozen=True)
    class Circle(Shape):
        r: int

        def area(self) -> int:
            return 3 * (self.r * self.r)

        def describe(self):
            return S.circle(super().describe())

    @m.define
    @dataclass(frozen=True)
    class Square(Shape):
        s: int

        def area(self) -> int:
            return self.s * self.s

    # !(test (area (Circle 2)) 12)
    assert Circle(2).area() == 12
    # !(test (area (Square 3)) 9)
    assert Square(3).area() == 9
    # !(test (describe (Square 3)) (area-of 9))
    assert Square(3).describe() == S.area_of(9)
    # !(test (describe (Circle 2)) (circle (area-of 12)))
    assert Circle(2).describe() == S.circle(S.area_of(12))
    # !(test (collapse (get-type (Circle 2))) (quote (Circle Shape)))
    assert m.eval(S.get_type(Circle(2))) == [S.Circle, S.Shape]
    # !(test (collapse (match &Circle (:< Circle $base) $base)) (Shape))
    assert [row.base for row in m.metta.space(S.Circle)[S[":<"](S.Circle, V.base)]] == [S.Shape]


#: The twin declares its classes, whose grains, accessors, method equations,
#: dispatch rows, call contracts and Python proxies the declaration derives,
#: and then proves the example's claims through them; the native example
#: writes only the rows its claims read. The difference is that declaration
#: and crossing work, the OVERRUN declared below.
#: [measured: 10770478 twin and 311841 native inferences; command=python
#: extensions/python/tools/twin_coverage.py --measure
#: examples/ch17-concurrency-and-the-loop/11-class_dispatch.metta; fixture=min of three
#: serial fresh processes in a provisioned battery worktree with the .qlf set
#: warm; commit=a8cfae1f5c0be628bc40eb7c18b07749d995e9a0].
#: RE-PINNED 2026-09-18, 10770478 to 10757553 (-12925), the branch's landings
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
#: RE-PINNED 2026-09-18, 10757553 to 10759060 (+1507), 49478d67a landed the
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
#: RE-PINNED 2026-09-18, 10759060 to 10740502 (-18558), the trunk merged
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
#: RE-PINNED 2026-09-19, 10740502 to 10736403 (-4099), cost follows the answer:
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
#: ENVELOPED 2026-09-19: the point 10736403 becomes the envelope
#: 10736403..10760531 over 12: under the lane's own protocol (full-
#: lane/294/workers=32, ten rounds) the counter reads 10736403 every time, and
#: under the gate's concurrent lanes (three runs) it reads 10758251, 10760531,
#: each reading exact on its run; the extra mode is the same program's work
#: done on a different thread under load, a loader flight or a settle step the
#: foreground runs itself when the worker is late, which the join accounting
#: does not reach; an envelope states what was observed and the point was a lie
#: under the gate [measured 2026-09-19: the twins lane alone on the final tree
#: and under the gate's concurrent lanes, wt-battery-2 ai-full-
#: gate-10da82e4a.log, ai-full-gate-19fdb0b86.log, ai-lanes-exports-back.log;
#: commit=1ccbb142315d16a719807cd2c9754e4a2fcefdf1].
#: RE-OBSERVED 2026-09-21 under 'full-lane/323/workers=32/file-search-cache-
#: time=9223372036854775807/before-boot', 10736403..10760531 to
#: 7935515..7935515 over 10 observations: the corpus grew from 294 examples to
#: 323 with the merge that derived sixty libraries in MeTTa (97763e7fa), and an
#: empirical envelope is a claim about ONE scheduler's protocol, so the earlier
#: observations could not license this one; these ten are this tree's own and
#: are not pooled with that run [measured 2026-09-21: ten full-lane
#: observations; command=python extensions/python/tools/twin_coverage.py
#: --observe --rounds 10; commit=8d2e8bb94da53a1a35c79d440cc09ef56f46153e].
#: RE-OBSERVED 2026-09-21 under 'full-lane/323/workers=32/file-search-cache-
#: time=9223372036854775807/before-boot', 7935515..7935515 to 7935515..7935515
#: over 20 observations: ten observations did not cover the tail of an example
#: whose count varies: 01-mutex_and_transaction read 23659 against the
#: 23661..23666 those ten recorded, and twenty put its 23657..23669 around that
#: reading. The protocol records observed extrema exactly and refuses an
#: invented allowance, so the only lawful way to cover a tail is to observe it
#: [measured 2026-09-21: twenty full-lane observations; command=python
#: extensions/python/tools/twin_coverage.py --observe --rounds 10;
#: commit=43e964002671a680825823b7ab4c1020de20f651].
#: RE-OBSERVED 2026-09-24 under 'full-lane/323/workers=32/file-search-cache-
#: time=9223372036854775807/before-boot', 7935515..7935515 to 7337926..7337926
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
#: time=9223372036854775807/before-boot', 7337926..7337926 over 20 to
#: 7337926..7337926 over 28: the 8 whole-lane runs of this runtime the envelope
#: did not yet hold read the pin run's first lane 7337926; the pin run's second
#: lane 7337926; the pin run's third lane 7337926; the first final lane
#: 7337926; the purged lane on 49e2b250d 7337926; the purged lane on 26de4ddcf
#: 7337926; the purged lane after a8487162 7337926; the purged lane after
#: 878b8bd9 7337926. They are the pin run's own lanes on the 6a7ac233d snapshot
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
#: time=9223372036854775807/before-boot', 7337926..7337926 to 7029424..7029964
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
#: time=9223372036854775807/before-boot', 7029424..7029964 to 6410731..6410731
#: over 21 observations: the tree moved under this envelope after its
#: observation at 0a81c782f: read serially, one fresh process a side, on each
#: first-parent rung from 0a81c782f to the fixed tree 4ff69551e in one battery,
#: its twin went from 7,025,749 to 6,410,731 (at 0a81c782f the serial protocol
#: read 3,675 under the full lane's 7,029,424..7,029,964, and on the fixed tree
#: the two agree, so that difference is part of the band's move and falls on no
#: rung); the WebAssembly job's 0847c3d4c decides a platform capability on its
#: first read (-5,539); its 984eabe23 keeps the verdict in a flag decided under
#: a mutex (+8,612); provider-carry's aaeea643a carries a provider's stored
#: term back as the engine gave it (-8,612); 4890e870d gives the governed QLF
#: set one producer (+6,367); gate-perf's b7e3d3bcb keeps each reference head's
#: last bind in its own row, so a from row rebinds only the heads it brings
#: (-59,490); gate-perf's ae1cc8936 walks the visible predicate table once for
#: a batch of 13 to 40 registered names, two inferences a visible predicate,
#: about 11,500 for each library import that registers such a batch (+14,029);
#: provider-carry's 850d2a660 reads a native space's lengths in ascending order
#: (-2,367); provider-carry's 1748f6a06 asks early-exit questions by key or in
#: ascending arity (+40); the packages job's b5eb39acd names get-property's and
#: setup!'s subject by a from source's rule (-4,419); d4a365c16 holds the
#: support graph's visited set and the reference refresh's space sets in tries
#: instead of library(nb_set) (-572,865); gate-perf's d781eab8f copies a
#: withdrawn equation once (+976); the packages job's registration service,
#: 90be572a9 in the engine with 4003462fe in the seat, net (+8,250); until
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
BUDGET = {
    "minimum": 6410731,
    "maximum": 6410731,
    "observations": 21,
    "protocol": "full-lane/323/workers=32/file-search-cache-time=9223372036854775807/before-boot"
}
OVERRUN = 10458637

#: DIVERGED 2026-09-18, the example holds 0 atoms the twin does not (none) and
#: the twin holds 70 atoms the example does not (67 :, 3 @doc): The twin's
#: @m.define derives the class's arrows, application and binding contracts and
#: documentation rows into the class space beside the equations the example
#: writes by hand, so the referenced content differs by exactly those derived
#: rows [measured 2026-09-18: the two stored-atom surpluses, one fresh process
#: per side; command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=a8cfae1f5c0be628bc40eb7c18b07749d995e9a0].
DIVERGENCE = "23cfb7805396602395cdd90b0e1bac4fcf32796361eb120f9fb55f7e53b7d98f"
