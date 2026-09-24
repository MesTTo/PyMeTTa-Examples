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
BUDGET = 19537
