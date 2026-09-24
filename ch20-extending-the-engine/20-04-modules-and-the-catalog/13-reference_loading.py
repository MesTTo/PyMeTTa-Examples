"""Purpose: reference_loading.metta in Python with the same admission policy.

The load pragma belongs to the receiver. A lazy call compiles its body and
a background call waits for the defining home.
[tested: examples/ch20-extending-the-engine/20-04-modules-and-the-catalog/13-reference_loading.metta; commit=90ba93eb8f6e98ebfefc55416859bf13de6a8427].
"""

from metta import MettaError, S

MAPS = S["./examples/ch20-extending-the-engine/20-04-modules-and-the-catalog/_fixtures/references/maps"]
BACKGROUND = S["./examples/ch20-extending-the-engine/20-04-modules-and-the-catalog/_fixtures/references/background"]
EFFECTFUL = S["./examples/ch20-extending-the-engine/20-04-modules-and-the-catalog/_fixtures/references/effectful"]


def twin(m):
    """Call deferred homes and refuse the initializer under both policies."""
    m.fn["pragma!"](S.load, S.lazy)
    m.from_(MAPS, S.prefix(S["lazy."]))
    assert m.fn["lazy.map-value"](41) == [42]
    assert m.fn["lazy.map-label"]() == [S.label]
    m.fn["pragma!"](S.load, S.background)
    m.from_(BACKGROUND)
    assert m.fn.background_value(41) == [42]
    for policy in (S.background, S.lazy):
        m.fn["pragma!"](S.load, policy)
        refused = False
        try:
            m.from_(EFFECTFUL)
        except MettaError as error:
            refused = True
            assert "println!" in str(error)
            assert "eager" in str(error)
        assert refused
    m.fn["pragma!"](S.load, S.eager)


#: Background loading joins a worker. Its counter includes work whose timing
#: depends on the complete lane, so this declaration records that protocol's
#: observed extrema. The ten samples were 332588, 329737, 332267, 330250,
#: 332432, 332041, 330564, 330886, 332217 and 330653, with no missing costs.
#: [measured 2026-09-10: 329737..332588 inferences over 10 observations;
#: command=python extensions/python/tools/twin_coverage.py --observe --rounds 10;
#: fixture=full-lane/280/workers=32; commit=90ba93eb8f6e98ebfefc55416859bf13de6a8427].
#: RE-ENVELOPED 2026-09-11 under 'full-lane/282/workers=32/file-search-cache-
#: time=9223372036854775807/before-boot': the lane grew from 277 to 282 twinned
#: examples (the REDS corpus example and the wave's own), and the merged tree
#: carries FROM's reference rows, BINDING's one native evaluation entry,
#: W-OBSERVE's observer guard, PERF's receipts batching and cursor retirement,
#: and the REDS shared loader; ten fresh full-lane observations read
#: 331616..335619 (spread 4003, samples [332379, 331616, 331616, 332366,
#: 333938, 333850, 335619, 332636, 332382, 334097]) where the 10 under 'full-
#: lane/280/workers=32' read 329737..332588. A run outside this envelope is a
#: real finding, and a new mode discovered later extends it with its
#: observation count rather than widening blind [measured 2026-09-11: exact
#: extrema over 10 observations; command=python
#: extensions/python/tools/twin_coverage.py --observe --rounds 10;
#: fixture=full-lane/282/workers=32/file-search-cache-
#: time=9223372036854775807/before-boot; commit=57f84148ba2684015f052d533f3197eca07b1f7b].
#: POOLED 2026-09-11: a second ten-round population under the same protocol,
#: taken on the tree that carries engine/metta/limits.pl and the re-pinned
#: twins, read 331563..334090 (samples [334088, 334090, 331563, 333121,
#: 332181, 332417, 333893, 331564, 333812, 332657]); pooled with the 10 above
#: at 331616..335619, 331563..335619 over 20 observations [measured
#: 2026-09-11: exact extrema over 10 observations; command=python
#: extensions/python/tools/twin_coverage.py --observe --rounds 10;
#: fixture=full-lane/282/workers=32/file-search-cache-time=9223372036854775807/before-boot;
#: commit=23ed2559a7c9b5712e1f6f4710ed02f8d5c6a23d].
#: RE-OBSERVED 2026-09-18 under 'full-lane/293/workers=32', 329737..332588 over
#: 10 under 'full-lane/280/workers=32' to 370077..373706 over 10: the branch's
#: tip f06186a96 after the landings the point re-pin names (the compiled call
#: law, the one codec at the grounded call, the runnable cache's dependency
#: index written by the producer, the host patches of 09-17, the class units)
#: and a corpus of 293 twinned examples under the lane's 32-worker pool, so the
#: scheduler this counter answers to is a new one and the observations are this
#: tree's own rather than pooled with the earlier protocol's [measured
#: 2026-09-18: python extensions/python/tools/twin_coverage.py --observe
#: --rounds 10, wt-battery-6 ai-tmp/ai-observe-f06186a96.log; commit=6944d06ce96fdbcd1faefb640f15dbfa0cf286dd].
#: POOLED 2026-09-18: the lane's own reading on the same tree, 369745, sits
#: under the ten rounds' floor of 370077 by 332, so it joins them under the
#: same protocol, 369745..373706 over 11, as the 2026-09-08 entry pools two
#: runs [measured 2026-09-18: python extensions/python/tools/twin_coverage.py,
#: wt-battery-4 ai-tmp/ai-twins-lane-residuals.log; commit=6944d06ce96fdbcd1faefb640f15dbfa0cf286dd].
#: RE-OBSERVED 2026-09-18 under 'full-lane/294/workers=32', 369745..373706 over
#: 11 under 'full-lane/293/workers=32' to 369880..373517 over 10: the corpus
#: grew from 293 to 294 twinned examples when 08-guarded_rules joined it
#: (49478d67a), and a full-lane protocol names the corpus width because the
#: scheduler this counter answers to is the whole corpus under the lane's
#: 32-worker pool, so the observations are this tree's own rather than pooled
#: with the earlier protocol's [measured 2026-09-18: python
#: extensions/python/tools/twin_coverage.py --observe --rounds 10, wt-battery-5
#: ai-tmp/ai-observe-558f40c9c.log; commit=bf5f100591493a91324b1d7552b5ad2731601691].
#: RE-OBSERVED 2026-09-18 under 'full-lane/294/workers=32', 369880..373517 over
#: 10 under 'full-lane/294/workers=32' to 369880..373517 over 23: every full-
#: lane run under one protocol is an observation, so the envelope pools the two
#: ten-round observations on this tree with the three full-lane runs that
#: measured it (the K5 tip's lane, the assembled tree before its envelopes and
#: after), the union of the extrema over the sum of the counts, as the
#: 2026-09-08 entry pools two runs [measured 2026-09-18: python
#: extensions/python/tools/twin_coverage.py --observe --rounds 10 twice and
#: GATE_ONLY=1 sh check.sh twins three times, ai-observe-558f40c9c.log, ai-
#: observe-c6448858b.log, ai-twins-K5.log, ai-twins-K6-interim.log, ai-
#: twins-K6-final.log; commit=bf5f100591493a91324b1d7552b5ad2731601691].
#: RE-OBSERVED 2026-09-18 under 'full-lane/294/workers=32', 369880..373517 over
#: 23 under 'full-lane/294/workers=32' to 369880..373736 over 24: every full-
#: lane run under one protocol is an observation, so the envelope pools the two
#: ten-round observations on this tree with the four full-lane runs that
#: measured it (the K5 tip's lane, the assembled tree before its envelopes,
#: after them, and after the first pooling), the union of the extrema over the
#: sum of the counts, as the 2026-09-08 entry pools two runs [measured
#: 2026-09-18: python extensions/python/tools/twin_coverage.py --observe
#: --rounds 10 twice and GATE_ONLY=1 sh check.sh twins four times, ai-
#: observe-558f40c9c.log, ai-observe-c6448858b.log, ai-twins-K5.log, ai-
#: twins-K6-interim.log, ai-twins-K6-final.log, ai-twins-K6-final-2.log;
#: commit=bf5f100591493a91324b1d7552b5ad2731601691].
#: RE-OBSERVED 2026-09-18 under 'full-lane/294/workers=32', 369880..373736 over
#: 24 under 'full-lane/294/workers=32' to 369880..373736 over 25: every full-
#: lane run under one protocol is an observation, so the envelope pools the two
#: ten-round observations on this tree with the five full-lane runs that
#: measured it (the K5 tip's lane, the assembled tree before its envelopes,
#: after them, after the first pooling, and the tip e28c4f2f5 beside a second
#: battery), the union of the extrema over the sum of the counts, as the
#: 2026-09-08 entry pools two runs [measured 2026-09-18: python
#: extensions/python/tools/twin_coverage.py --observe --rounds 10 twice and
#: GATE_ONLY=1 sh check.sh twins five times, ai-observe-558f40c9c.log, ai-
#: observe-c6448858b.log, ai-twins-K5.log, ai-twins-K6-interim.log, ai-
#: twins-K6-final.log, ai-twins-K6-final-2.log, ai-twins-tip-e28c4f2f5.log;
#: commit=0e767924501d8b25d1994f128d96c503d867e408].
#: RE-OBSERVED 2026-09-19 under 'full-lane/294/workers=32', 369880..373736 over
#: 25 under 'full-lane/294/workers=32' to 369521..372889 over 10: the trunk
#: merged (f97c4b0a3, petta's 61 commits since c75181adc) with the definition
#: batch's load pushed as the running load (2da1155e3): the engine moved under
#: every twin, 263 of the 276 re-pinned twins cheaper and 13 dearer (median
#: -1.25%), through the compiled runnable envelope, the trunk's trailed scopes
#: and compiled context readers, the host listener door and the receipts loop
#: probing the owner once per set, so the envelope is this tree's own
#: observation under the same 294-wide protocol [measured 2026-09-19: python
#: extensions/python/tools/twin_coverage.py --observe --rounds 10, ai-
#: observe-4c0533704.log; commit=55d451b670949c2dc9d2ab7bc678f33f21094bd2].
#: RE-OBSERVED 2026-09-19 under 'full-lane/294/workers=32', 369521..372889 over
#: 10 under 'full-lane/294/workers=32' to 372287..376159 over 10: cost follows
#: the answer: a block is charged for its own thread's work and for the workers
#: whose answers it used, a race's losers, the branches par-any and par-forall
#: stopped and a cancelled future or timer being joined through the engine's
#: discarding door (metta_join_measured/3) and their partial spend taken out,
#: lib_thread's join no longer polls on the host patched for swi-thread-join-
#: detach-window, and the seat's counter doors read the discarded tally outside
#: the window they bracket; the spread that remains is this twin's own
#: schedule-bound work under the same 294-wide protocol [measured 2026-09-19:
#: python extensions/python/tools/twin_coverage.py --observe --rounds 10, ai-
#: observe-remedy.log; commit=32335687084e4d8ad43cf8800f2dedce707fa137].
#: ENVELOPED 2026-09-19: the envelope 372287..376159 over 10 becomes the
#: envelope 372287..376423 over 11: under the lane's own protocol (full-
#: lane/294/workers=32, ten rounds) the counter reads 372287 every time, and
#: with the lane alone on the final tree (one run) it reads 376423, each
#: reading exact on its run; the extra mode is the same program's work done on
#: a different thread under load, a loader flight or a settle step the
#: foreground runs itself when the worker is late, which the join accounting
#: does not reach; an envelope states what was observed and the point was a lie
#: under the gate [measured 2026-09-19: the twins lane alone on the final tree
#: and under the gate's concurrent lanes, wt-battery-2 ai-full-
#: gate-10da82e4a.log, ai-full-gate-19fdb0b86.log, ai-lanes-exports-back.log;
#: commit=1ccbb142315d16a719807cd2c9754e4a2fcefdf1].
#: RE-OBSERVED 2026-09-21 under 'full-lane/323/workers=32/file-search-cache-
#: time=9223372036854775807/before-boot', 372287..376423 to 372888..374816 over
#: 10 observations: the corpus grew from 294 examples to 323 with the merge
#: that derived sixty libraries in MeTTa (97763e7fa), and an empirical envelope
#: is a claim about ONE scheduler's protocol, so the earlier observations could
#: not license this one; these ten are this tree's own and are not pooled with
#: that run [measured 2026-09-21: ten full-lane observations; command=python
#: extensions/python/tools/twin_coverage.py --observe --rounds 10;
#: commit=8d2e8bb94da53a1a35c79d440cc09ef56f46153e].
#: RE-OBSERVED 2026-09-21 under 'full-lane/323/workers=32/file-search-cache-
#: time=9223372036854775807/before-boot', 372888..374816 to 372888..377113 over
#: 20 observations: ten observations did not cover the tail of an example whose
#: count varies: 01-mutex_and_transaction read 23659 against the 23661..23666
#: those ten recorded, and twenty put its 23657..23669 around that reading. The
#: protocol records observed extrema exactly and refuses an invented allowance,
#: so the only lawful way to cover a tail is to observe it [measured
#: 2026-09-21: twenty full-lane observations; command=python
#: extensions/python/tools/twin_coverage.py --observe --rounds 10;
#: commit=43e964002671a680825823b7ab4c1020de20f651].
#: RE-OBSERVED 2026-09-24 under 'full-lane/323/workers=32/file-search-cache-
#: time=9223372036854775807/before-boot', 372888..377113 to 375124..377622 over
#: 20 observations: the tree under these envelopes moved after their last
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
#: time=9223372036854775807/before-boot', 375124..377622 over 20 to
#: 375124..378281 over 21: the whole-lane run on HEAD 26de4ddcf, its engine
#: diff empty and its battery's governed QLF set purged so that every artifact
#: was compiled where it sits, read 378281, 659 above the twenty rounds'
#: maximum; the commits after the observed 6a7ac233d touch no path this twin
#: runs; a whole-lane run under this protocol on this runtime is an
#: observation, so the envelope is the union of the extrema and the sum of the
#: counts. The spread is the reference loads' worker order, the schedule-bound
#: work docs/journal/2026-09-18-schedule-independent-counters.md names for this
#: twin [measured 2026-09-24: 1 whole-lane run, sh extensions/python/check.sh
#: twins in battery 5 after metta_qlf_boot:purge_all_qlf; command=python
#: extensions/python/tools/twin_coverage.py; commit=WORKTREE].
#: POOLED 2026-09-24 under 'full-lane/323/workers=32/file-search-cache-
#: time=9223372036854775807/before-boot', 375124..378281 over 21 to
#: 375124..379456 over 28: the 7 whole-lane runs of this runtime the envelope
#: did not yet hold read the pin run's first lane 378138; the pin run's second
#: lane 376402; the pin run's third lane 376613; the first final lane 375295;
#: the purged lane on 49e2b250d 375295; the purged lane after a8487162 375295;
#: the purged lane after 878b8bd9 379456. They are the pin run's own lanes on
#: the 6a7ac233d snapshot and the final lanes on 49e2b250d and 26de4ddcf, whose
#: commits touch no path this twin runs, and each reads every deterministic
#: twin exactly as a battery whose governed QLF set was compiled in place does,
#: so none carries a moved artifact's cost; the lane whose battery carried a
#: lib_import.qlf compiled in wt-merge is left out. A whole-lane run under this
#: protocol on this runtime is an observation, so the envelope is the union of
#: the extrema and the sum of the counts [measured 2026-09-24: 7 whole-lane
#: runs, sh extensions/python/check.sh twins in battery 5; command=python
#: extensions/python/tools/twin_coverage.py; commit=WORKTREE].
#: RE-OBSERVED 2026-09-24 under 'full-lane/323/workers=32/file-search-cache-
#: time=9223372036854775807/before-boot', 375124..379456 to 81040..87216 over
#: 20 observations: the tree moved under this envelope: 0a81c782f loads a
#: library's Prolog half through the boot's claim, so the half and every
#: governed half it loads read the .qlf the claim's hermetic child wrote where
#: they had compiled from source in every process, and it starts that child
#: from the running home's own swipl, which the host check accepts, where the
#: stock swipl the lane's PATH finds had been refused since f2822e2ae; the
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
#: time=9223372036854775807/before-boot', 81040..87216 to 69864..73777 over 21
#: observations: the tree moved under this envelope after its observation at
#: 0a81c782f: read serially, one fresh process a side, on each first-parent
#: rung from 0a81c782f to the fixed tree 4ff69551e in one battery, its twin
#: went from 81,040 to 73,988; gate-perf's b7e3d3bcb keeps each reference
#: head's last bind in its own row, so a from row rebinds only the heads it
#: brings (-7,194); d4a365c16 holds the support graph's visited set and the
#: reference refresh's space sets in tries instead of library(nb_set) (-6,627;
#: three same-tree A/Bs of the tries change read -8,007, -2,040 and -3,177);
#: the other 41 rungs that moved it net +6,769, the largest single step 3,588,
#: inside the 3,913 this reading scatters by on one tree (its full-lane
#: observations on the fixed tree spread 3,913), and the band's midpoint moved
#: -12,308; an empirical envelope is a claim about one scheduler's protocol on
#: one tree, so these observations are this tree's own and are not pooled with
#: the earlier ones [measured 2026-09-24: 21 full-lane observations on the
#: fixed tree, the twenty rounds of --observe and one run of the lane itself;
#: command=python extensions/python/tools/twin_coverage.py --observe --rounds
#: 20; commit=4ff69551e0e226442cf7257b96af858adda957a4].
BUDGET = {
    "minimum": 69864,
    "maximum": 73777,
    "observations": 21,
    "protocol": "full-lane/323/workers=32/file-search-cache-time=9223372036854775807/before-boot"
}

#: DIVERGED 2026-09-24, the example holds 2 atoms the twin does not (2 from)
#: and the twin holds 2 atoms the example does not (2 from): the twin names its
#: fixtures by their root-relative path, ./examples/ch20-extending-the-
#: engine/20-04-modules-and-the-catalog/_fixtures/references/<name>, where the
#: example names the same files relative to itself as
#: ./_fixtures/references/<name>; a from row is stored as written, so the two
#: spaces hold the same rows under two spellings of one file (twins commit
#: aa891a0d, after d8231f103 refused the library-root walk-out and 754d6c010
#: read ./ and ../ as paths) [measured 2026-09-24: the two stored-atom
#: surpluses, one fresh process per side; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=WORKTREE].
DIVERGENCE = "dc6887a5e38833a7ee4e011e007a884f3d4bfb3469d6903f88acae6eb23bf975"
