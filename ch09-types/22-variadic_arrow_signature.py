"""Purpose: examples/ch09-types/22-variadic_arrow_signature.metta in Python.

The declaration and equation atoms are the rung below compiled def, whose
parameter syntax does not admit a segment. S[":seg"] builds type syntax;
seg(V.args) builds the pattern's variable capture.
[tested: variadic_arrows; commit=6031c83ab3002b5703cb6fcb10e70a60a89f4ad7]
"""

from metta import Expression, S, V, arrow, equation, seg, typed


def twin(m):
    """Call the same declared run at zero through three arguments."""
    signature = arrow(S[":seg"](S.Bool), arrow())
    m += typed(S.do2, signature)
    m += equation(S.do2(seg(V.args))).to(Expression())  # rung: compiled def has no segment parameter
    for count in range(4):
        effects = [S["println!"](name) for name in (S.one, S.two, S.three)[:count]]  # rung: print() returns None before dispatch; the Bool-valued effect must run as the typed operand
        assert m.fn.do2(*effects) == [Expression()]
    assert m.type(S.do2) == signature

    m += equation(S.undeclared_do(seg(V.args))).to(S.got(V.args))  # rung: as above
    assert m.fn.undeclared_do(S.a, S.b) == [S.got(Expression(S.a, S.b))]
    assert m.fn.undeclared_do() == [S.got(Expression())]


#: The initial 16,386-inference price includes
#: once-per-arity segment compilation and positional type diagnostics; the no-
#: work compiled-call matrix matches fixed callees and no allowance is widened
#: [measured 2026-09-09: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=6031c83ab3002b5703cb6fcb10e70a60a89f4ad7].
#: RE-PINNED 2026-09-09, 16386 to 16435 (+49), The fixed diagnostic reader now
#: consumes parameter and argument spines together, and segment families
#: compile once per shape. Fixed-arrow presentation and warmed single-run
#: callees keep their controls. Fused syntax admission adds 44 inferences for a
#: cold prepare/admit type shape versus the old annotation scan and eight per
#: source-preflight declaration; repeated shapes reuse the analysis. The
#: authoring control moves by -16 once, with its per-definition slope
#: unchanged. Cold family generation is included. See
#: docs/journal/2026-09-09-the-splice-in-an-arrow.md [measured 2026-09-09: min-
#: of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=6031c83ab3002b5703cb6fcb10e70a60a89f4ad7].
#: RE-PINNED 2026-09-11, 16435 to 16651 (+216), end-of-wave re-pin on the
#: merged tree after FROM's reference rows and four engine units, the closed-
#: set derivations and two host services, BINDING's one native evaluation entry
#: and boot import, W-OBSERVE's observer guard, PERF's receipts batching and
#: cursor retirement, and the three REDS repairs (derived runtime resources and
#: the shared loader, the tool-lane repairs, the corpus example); serial
#: minimum of three fresh processes through the lane's run_twin with
#: file_search_cache_time=9223372036854775807 set before child boot [measured
#: 2026-09-11: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=57f84148ba2684015f052d533f3197eca07b1f7b].
#: RE-PINNED 2026-09-18, 16435 to 17208 (+773), the branch's landings since the
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
#: RE-PINNED 2026-09-18, 17208 to 16760 (-448), the trunk merged (f97c4b0a3,
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
#: RE-PINNED 2026-09-21, 16760 to 16778 (+18), the sixty libraries derived in
#: MeTTa landed with merge 97763e7fa eight hours after the previous pin
#: 55d451b67, so every example importing one now pays a MeTTa derivation where
#: it paid a Prolog body instead, which the 2026-09-14 ruling accepts
#: explicitly as the price of a library that survives the engine swap [measured
#: 2026-09-21: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=6e09cb25d5495c2db3283166e6ce4e07eefecfb2].
#: RE-PINNED 2026-09-25, 16778 to 16395 (-383), the host evaluation door
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
#: more than twelve names [measured 2026-09-25T06:49:07+10:00: min-of-3 serial
#: fresh processes; command=python extensions/python/tools/twin_coverage.py
#: --repin].
#: RE-PINNED 2026-09-25, 16395 to 16425 (+30), both specializer doors prepare a
#: specialization's predicate with spaces:metta_prepare_function_predicate/3
#: before asserting its clauses [measured 2026-09-25T11:29:10+10:00: one full
#: twins lane before this commit and one with it, the two read on one battery
#: path at the landing's HEAD; command=python
#: extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-25, 16425 to 16426 (+1), every force of a waiting function
#: names the module it is made from, through fun_home_in/3, and a write forces
#: only its own space [measured 2026-09-25T16:54:32+10:00: one full twins lane
#: before this commit and one with it, the two read on one battery path at the
#: landing's HEAD; command=python extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-27, 16426 to 16456 (+30), the host switch to swipl-
#: patched.7 and the seat changes it needs: +30 the held goals reading Used
#: through metta_py_work/2, which leaves a held engine's own ticks out and
#: reads the tick term inside its opening edge, 5 inferences a held reading
#: [measured 2026-09-27T03:41:21+10:00: one full twins lane of the trunk and
#: one with this landing, wt-merge battery 1, the trunk on swipl-patched.6 and
#: every part on .7, each through a same-shape host shim; command=python
#: extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-27, 16456 to 16438 (-18), -18 at interrupts B's seat
#: change, which drops the poll's boot calibration, its tick charges and its
#: tick record: a held reading through metta_py_work/2 brackets 3 inferences
#: where it bracketed 6, a registration walk over more than twelve names meets
#: 6 fewer seat predicates (12 or 14 fewer), and a thread the twin joins
#: credits it 11 where it credited 16 [measured 2026-09-27T20:07:01+10:00: full
#: twins lanes in wt-merge's battery 1, tsm-licence's series and its engine
#: reader on swipl-patched.7, the series on swipl-patched.8, and the stack
#: through janus-contract B on swipl-patched.8 twice; command=sh tools/check.sh
#: twins].
#: RE-PINNED 2026-09-29, 16438 to 16461 (+23), this twin reads 16438 before the
#: change and 16461 with the change (+23): each definition through the define
#: doors asks whether its module holds a shadow-import receipt for the name,
#: holds it in flight until the write is visible when it does, and a sweep
#: leaves a receipt another live thread holds: with that use this twin reads
#: 16461 where the definitions alone read 16438 (+23) [measured
#: 2026-09-29T06:37:01+10:00: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-29, 16461 to 16578 (+117), this twin reads 16461 before
#: the change and 16578 with the change (+117): each definition marks its name
#: as changed and a sweep repairs only the receipts naming a marked name, where
#: it re-checked every receipt the process held: with that use this twin reads
#: 16578 where the definitions alone read 16461 (+117) [measured
#: 2026-09-29T06:44:05+10:00: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-29, 16578 to 16696 (+118), this twin reads 16578 before
#: the change and 16696 with the change (+118): every operation that registers
#: a name outside a load opens a registration unit, files there the repairs its
#: registrations owe, and drains them once when it finishes, so a caller
#: compiled before the name became a function is repaired: with that use this
#: twin reads 16696 where the definitions alone read 16578 (+118) [measured
#: 2026-09-29T20:24:03+10:00: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-29, 16696 to 16678 (-18), this twin reads 16696 before the
#: change and 16678 with the change (-18): a call site forces the function it
#: names before deciding the call's shape, so a call of a waiting function
#: builds the application protocol an eager load builds, and the protocol's
#: marker test around a value the translation already holds is decided at
#: compile time: with that use this twin reads 16678 where the definitions
#: alone read 16696 (-18) [measured 2026-09-29T20:35:59+10:00: min-of-3 serial
#: fresh processes; command=python extensions/python/tools/twin_coverage.py
#: --repin].
#: RE-PINNED 2026-09-30, 16678 to 16582 (-96), this twin reads 16678 before the
#: change and 16582 with the change (-96): a named space's prelude-tier type
#: readers look the prelude's row up before asking whether it governs there,
#: and builtin_result_type/3 asks whether a program took a builtin over only
#: for a builtin whose result is evaluated (engine/metta/types.pl,
#: engine/translator/lowering.pl), so a lookup of a name the prelude does not
#: declare costs one indexed miss and no ownership probe [measured
#: 2026-09-30T04:18:01+10:00: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-30, 16582 to 16589 (+7), the twins lane reads this twin at
#: 16582 before this change and at 16589 with it (+7): a module takes a name
#: over only when the name's equations compile to a predicate of that name
#: (engine/metta/registration.pl, fun_overrides_in/2), so each reader that
#: asked fun_in/2 whether a module took a name over now also asks
#: compiled_function_name/2 when the module registers the name, one call per
#: such lookup of a module's own name [measured 2026-09-30T04:29:11+10:00: min-
#: of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
BUDGET = 16589
