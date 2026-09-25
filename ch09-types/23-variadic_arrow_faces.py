"""Purpose: examples/ch09-types/23-variadic_arrow_faces.metta in Python.

Declaration/equation atoms are the rung below compiled def for segment heads.
The raw answer door keeps Error atoms as values for the refusal cells.
[tested: variadic_arrows; commit=6031c83ab3002b5703cb6fcb10e70a60a89f4ad7]
"""

from metta import Expression, S, V, arrow, equation, seg, typed


def twin(m):
    """Exercise expansion, element positions, holding and the fixed control."""
    m += typed(S.vsum, arrow(S[":seg"](S.Number), S.Number))
    m += equation(S.vsum(seg(V.ns))).to(S.foldl_atom(V.ns, 0, S["+"]))  # rung: compiled def has no segment parameter
    for count in range(4):
        assert m.fn.vsum(*range(1, count + 1)) == [sum(range(1, count + 1))]
    m += typed(S.vflag, S.Bool)
    for position in range(3):
        arguments = [1, 2, 3]
        arguments[position] = S.vflag
        call = S.vsum(*arguments)
        assert m.answers(call) == [S.Error(call, S.BadArgType(position + 1, S.Number, S.Bool))]

    signature = arrow(S[":seg"](S.Atom), S.Atom)
    m += typed(S.vheld, signature)
    m += equation(S.vheld(seg(V.es))).to(V.es)  # rung: as above
    assert m.fn.vheld() == [Expression()]
    assert m.fn.vheld(S["+"](1, 1), S["+"](2, 2)) == [Expression(S["+"](1, 1), S["+"](2, 2))]
    assert m.type(S.vheld) == signature

    m += typed(S.mixed, arrow(S.Number, S[":seg"](S.Atom), S.Atom))
    m += equation(S.mixed(V.n, seg(V.xs))).to(S.kept(V.n, V.xs))  # rung: as above
    assert m.fn.mixed(S["+"](1, 1), S["+"](2, 2), S["+"](3, 3)) == [S.kept(2, Expression(S["+"](2, 2), S["+"](3, 3)))]
    assert m.fn.mixed(2) == [S.kept(2, Expression())]

    @m.define
    def fixed2(a: int, b: int) -> int:
        return a + b

    assert fixed2(1, 2) == [3]
    assert m.answers(S.repr(S.catch(S.fixed2(1, 2, 3)))) == [
        "(Error (domain_error (function_input_arities fixed2 (2)) 3) none)"
    ]


#: The initial 36,561-inference price includes once-per-arity segment
#: compilation and positional type diagnostics;
#: the no-work compiled-call matrix matches fixed callees and no allowance is
#: widened [measured 2026-09-09: min-of-3 serial fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=6031c83ab3002b5703cb6fcb10e70a60a89f4ad7].
#: RE-PINNED 2026-09-09, 36561 to 36514 (-47), The fixed diagnostic reader now
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
#: RE-PINNED 2026-09-11, 36514 to 35759 (-755), end-of-wave re-pin on the
#: merged tree after FROM's reference rows and four engine units, the closed-
#: set derivations and two host services, BINDING's one native evaluation entry
#: and boot import, W-OBSERVE's observer guard, PERF's receipts batching and
#: cursor retirement, and the three REDS repairs (derived runtime resources and
#: the shared loader, the tool-lane repairs, the corpus example); serial
#: minimum of three fresh processes through the lane's run_twin with
#: file_search_cache_time=9223372036854775807 set before child boot [measured
#: 2026-09-11: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=57f84148ba2684015f052d533f3197eca07b1f7b].
#: RE-PINNED 2026-09-18, 36514 to 37477 (+963), the branch's landings since the
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
#: RE-PINNED 2026-09-18, 37477 to 36276 (-1201), the trunk merged (f97c4b0a3,
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
#: RE-PINNED 2026-09-21, 36276 to 36317 (+41), the sixty libraries derived in
#: MeTTa landed with merge 97763e7fa eight hours after the previous pin
#: 55d451b67, so every example importing one now pays a MeTTa derivation where
#: it paid a Prolog body instead, which the 2026-09-14 ruling accepts
#: explicitly as the price of a library that survives the engine swap [measured
#: 2026-09-21: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=6e09cb25d5495c2db3283166e6ce4e07eefecfb2].
#: RE-PINNED 2026-09-24, 36317 to 36323 (+6), placed on the full-configuration
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
#: library spec that walks out of the library root; where a twin's move exceeds
#: these steps, the remainder is drift that stayed inside its band (four
#: inferences, or its own declared allowance) on every other interval [measured
#: 2026-09-24: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=WORKTREE].
#: RE-PINNED 2026-09-25, 36323 to 36313 (-10), the registration refusal kind
#: makes the (vocabulary refusal-kind ...) catalog row fifteen members long
#: instead of fourteen, which moves it from storage arity 17 to 18, where the
#: Python seat's (vocabulary door-answers ...) already sits, so &metta keeps
#: one storage arity fewer and each open-tail catalog lookup,
#: metta_catalog_clause/2 visiting every arity, costs five inferences less; and
#: metta_host_signal_message//2 is one more predicate the engine module
#: defines, which every walk over the engine's predicates pays: filereader's
#: existing_predicate_arities/2 two inferences a registration of more than
#: twelve names, each restricted space's core 29, and 11-reference_rows' walk
#: 240, each reproduced exactly by one inert predicate added to the engine on
#: the base [measured 2026-09-25T06:29:44+10:00: min-of-3 serial fresh
#: processes; command=python extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-25, 36313 to 35479 (-834), the host evaluation door
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
#: more than twelve names [measured 2026-09-25T06:49:10+10:00: min-of-3 serial
#: fresh processes; command=python extensions/python/tools/twin_coverage.py
#: --repin].
#: RE-PINNED 2026-09-25, 35479 to 35521 (+42), both specializer doors prepare a
#: specialization's predicate with spaces:metta_prepare_function_predicate/3
#: before asserting its clauses [measured 2026-09-25T11:29:10+10:00: one full
#: twins lane before this commit and one with it, the two read on one battery
#: path at the landing's HEAD; command=python
#: extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-25, 35521 to 35522 (+1), every force of a waiting function
#: names the module it is made from, through fun_home_in/3, and a write forces
#: only its own space [measured 2026-09-25T16:54:32+10:00: one full twins lane
#: before this commit and one with it, the two read on one battery path at the
#: landing's HEAD; command=python extensions/python/tools/twin_coverage.py].
BUDGET = 35522
