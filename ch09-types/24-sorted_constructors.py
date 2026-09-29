"""Purpose: examples/ch09-types/24-sorted_constructors.metta in Python.

The example exposes sorted operations and equations themselves. Their atom
builders preserve that exact declaration surface, including its untyped control.
[tested: translator_constructors; commit=2398951d3272ad02b2c2d7b1e2b610c8e332c1f5]
"""

from metta import S, V, arrow, equation, ground, typed


def twin(m):
    """Build the same declarations and compare all three reductions."""
    m += typed(S.SortedPoint, arrow(S.Number, S.Number, S.SortedPoint))
    # rung: these head patterns teach the arrow/equation layer directly.
    m += equation(S.sorted_x(S.SortedPoint(V.x, V.y))).to(V.x)
    m += equation(S.plain_x(S.PlainPoint(V.x, V.y))).to(V.x)
    m += equation(S.make_sorted_point(V.x, V.y)).to(S.SortedPoint(V.x, V.y))
    m += equation(S.sorted_norm(S.SortedPoint(V.x, V.y))).to(
        S.sqrt_math(S["+"](S["*"](V.x, V.x), S["*"](V.y, V.y)))
    )
    assert m.type(S.SortedPoint(3, 4)) == S.SortedPoint
    assert m.fn.sorted_x(S.SortedPoint(3, 4)) == [3]
    assert m.fn.sorted_norm(S.SortedPoint(3, 4)) == [5.0]
    assert m.fn.make_sorted_point(ground("bad"), 4) == [
        S.Error(S.SortedPoint(ground("bad"), 4), S.BadArgType(1, S.Number, S.String))
    ]

    projections = {
        S.constructor_control: 3,
        S.constructor_sorted: S.sorted_x(S.SortedPoint(3, 4)),
        S.constructor_plain: S.plain_x(S.PlainPoint(3, 4)),
    }
    for head, projection in projections.items():
        # rung: one equation template keeps the three measured loops identical
        # apart from the projection whose cost the example compares.
        m += equation(head(V.n, V.sum)).to(
            S["if"](
                S["=="](V.n, 0), V.sum,
                S.let(V.x, projection, head(S["-"](V.n, 1), S["+"](V.sum, V.x))),
            )
        )
    assert m.fn.constructor_control(20, 0) == [60]
    assert m.fn.constructor_sorted(20, 0) == [60]
    assert m.fn.constructor_plain(20, 0) == [60]


#: Construction proofs remove the repeated strict check, and the retained
#: sorted field projection removes its call. Declaration publication and
#: invalidation remain inside this complete-example count.
#: [measured: 19782 inferences; command=python
#: extensions/python/tools/twin_coverage.py --measure
#: examples/ch09-types/24-sorted_constructors.metta; fixture=min of three
#: serial fresh processes with native engine artifacts; commit=2398951d3272ad02b2c2d7b1e2b610c8e332c1f5].
#: RE-PINNED 2026-09-18, 19782 to 19852 (+70), the branch's landings since the
#: 09-10 pins, re-taken on the tip f06186a96: the compiled call law (e59104ace:
#: an Atom argument enters as written, a Python object crosses as a value, a
#: positional call of a bound callee is the plain application and a compiled
#: lambda is bare where it is applied), the one codec at the grounded call
#: (fd0af38f7, whose read of a call site's written keyword tail costs about six
#: inferences per translated site, read once since 7cc8fb863), the runnable
#: cache's dependency index written by the producer (a9e2c06d3, which takes
#: back the walk of the generated code 5416e741d charged at every miss), the
#: host patches of 09-17 and the class units of 09-13 to 09-16 the ladder in
#: docs/journal/2026-09-14-runnable-artifact-dependencies.md places; serial
#: minimum of three fresh processes through the lane's run_twin with
#: file_search_cache_time=9223372036854775807 set before child boot [measured
#: 2026-09-18: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=6944d06ce96fdbcd1faefb640f15dbfa0cf286dd].
#: RE-PINNED 2026-09-18, 19852 to 19392 (-460), the trunk merged (f97c4b0a3,
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
#: RE-PINNED 2026-09-21, 19392 to 19550 (+158), the sixty libraries derived in
#: MeTTa landed with merge 97763e7fa eight hours after the previous pin
#: 55d451b67, so every example importing one now pays a MeTTa derivation where
#: it paid a Prolog body instead, which the 2026-09-14 ruling accepts
#: explicitly as the price of a library that survives the engine swap [measured
#: 2026-09-21: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=6e09cb25d5495c2db3283166e6ce4e07eefecfb2].
#: RE-PINNED 2026-09-24, 19550 to 19537 (-13), the host switch of
#: swipl-patched from .2 to .5, the native host of build 9's 36
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
#: RE-PINNED 2026-09-25, 19537 to 20619 (+1082), the host evaluation door
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
#: more than twelve names [measured 2026-09-25T06:49:12+10:00: min-of-3 serial
#: fresh processes; command=python extensions/python/tools/twin_coverage.py
#: --repin].
#: RE-PINNED 2026-09-25, 20619 to 20620 (+1), every force of a waiting function
#: names the module it is made from, through fun_home_in/3, and a write forces
#: only its own space [measured 2026-09-25T16:54:32+10:00: one full twins lane
#: before this commit and one with it, the two read on one battery path at the
#: landing's HEAD; command=python extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-27, 20620 to 20650 (+30), the host switch to swipl-
#: patched.7 and the seat changes it needs: +30 the held goals reading Used
#: through metta_py_work/2, which leaves a held engine's own ticks out and
#: reads the tick term inside its opening edge, 5 inferences a held reading;
#: the trunk's lane read this twin -1 off its pin, an offset that is not this
#: landing's, so the pin moves by the landing's delta alone [measured
#: 2026-09-27T03:41:21+10:00: one full twins lane of the trunk and one with
#: this landing, wt-merge battery 1, the trunk on swipl-patched.6 and every
#: part on .7, each through a same-shape host shim; command=python
#: extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-27, 20650 to 20631 (-19), -18 at interrupts B's seat
#: change, which drops the poll's boot calibration, its tick charges and its
#: tick record: a held reading through metta_py_work/2 brackets 3 inferences
#: where it bracketed 6, a registration walk over more than twelve names meets
#: 6 fewer seat predicates (12 or 14 fewer), and a thread the twin joins
#: credits it 11 where it credited 16; the base read 20,649 where the pin stood
#: at 20,650, a gap of +1 this re-pin takes out [measured
#: 2026-09-27T20:07:01+10:00: full twins lanes in wt-merge's battery 1, tsm-
#: licence's series and its engine reader on swipl-patched.7, the series on
#: swipl-patched.8, and the stack through janus-contract B on swipl-patched.8
#: twice; command=sh tools/check.sh twins].
#: RE-PINNED 2026-09-29, 20631 to 20659 (+28), this twin reads 20631 before the
#: change and 20659 with the change (+28): each definition through the define
#: doors asks whether its module holds a shadow-import receipt for the name,
#: holds it in flight until the write is visible when it does, and a sweep
#: leaves a receipt another live thread holds: with that use this twin reads
#: 20659 where the definitions alone read 20631 (+28) [measured
#: 2026-09-29T06:37:05+10:00: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-29, 20659 to 21046 (+387), this twin reads 20659 before
#: the change and 21046 with the change (+387): each definition marks its name
#: as changed and a sweep repairs only the receipts naming a marked name, where
#: it re-checked every receipt the process held: with that use this twin reads
#: 21046 where the definitions alone read 20659 (+387) [measured
#: 2026-09-29T06:44:12+10:00: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-29, 21046 to 21138 (+92), this twin reads 21046 before the
#: change and 21138 with the change (+92): every operation that registers a
#: name outside a load opens a registration unit, files there the repairs its
#: registrations owe, and drains them once when it finishes, so a caller
#: compiled before the name became a function is repaired: with that use this
#: twin reads 21138 where the definitions alone read 21046 (+92) [measured
#: 2026-09-29T20:24:04+10:00: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-29, 21138 to 21111 (-27), this twin reads 21138 before the
#: change and 21111 with the change (-27): a call site forces the function it
#: names before deciding the call's shape, so a call of a waiting function
#: builds the application protocol an eager load builds, and the protocol's
#: marker test around a value the translation already holds is decided at
#: compile time: with that use this twin reads 21111 where the definitions
#: alone read 21138 (-27) [measured 2026-09-29T20:36:02+10:00: min-of-3 serial
#: fresh processes; command=python extensions/python/tools/twin_coverage.py
#: --repin].
#: RE-PINNED 2026-09-30, 21111 to 20996 (-115), this twin reads 21111 before
#: the change and 20996 with the change (-115): a named space's prelude-tier
#: type readers look the prelude's row up before asking whether it governs
#: there, and builtin_result_type/3 asks whether a program took a builtin over
#: only for a builtin whose result is evaluated (engine/metta/types.pl,
#: engine/translator/lowering.pl), so a lookup of a name the prelude does not
#: declare costs one indexed miss and no ownership probe [measured
#: 2026-09-30T04:18:10+10:00: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
BUDGET = 20996
