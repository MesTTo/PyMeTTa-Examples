"""Purpose: observe an editable native equation through the one-answer door.

A failed alternative leaves one answer. Completed values stay held, and a
native equation replacement changes the next call [tested:
python extensions/python/tools/twin_coverage.py examples/ch05-equations-and-evaluation/05-01-an-equation-is-a-rewrite/11-single_answer.metta;
commit=eec241dcf822db6c4c1d1ecdb6092a6a9f3c7851].
"""

from metta import Expression, S


def twin(m):
    """Count answers, retain data and observe a rewritten native equation."""
    first = S["="](S.unique_value(), 11)
    m += first
    m += S["="](S.unique_value(), S.superpose(()))

    assert m.eval(S.eval_one(S["+"](1, 2))) == [3]
    assert m.eval(S.eval_one(S.unique_value())) == [11]
    held = S["+"](2, 3)
    assert m.eval(S.eval_one(S.noeval(held))) == [held]
    assert m.eval(S.eval_one(S.noeval(()))) == [Expression()]

    m -= first
    m += S["="](S.unique_value(), 22)
    assert m.eval(S.eval_one(S.unique_value())) == [22]


#: Five fresh processes retain the same two native equations and agree on
#: 9060 twin inferences and 8991 native inferences [measured: 9060 inferences;
#: command=python extensions/python/tools/twin_coverage.py examples/ch05-equations-and-evaluation/05-01-an-equation-is-a-rewrite/11-single_answer.metta;
#: fixture=SWI-Prolog 10.1.13, five assertions, empty source space; commit=eec241dcf822db6c4c1d1ecdb6092a6a9f3c7851].
#: RE-PINNED 2026-09-18, 9060 to 7098 (-1962), the branch's landings since the
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
#: RE-PINNED 2026-09-18, 7098 to 6951 (-147), the trunk merged (f97c4b0a3,
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
#: RE-PINNED 2026-09-21, 6951 to 6987 (+36), the sixty libraries derived in
#: MeTTa landed with merge 97763e7fa eight hours after the previous pin
#: 55d451b67, so every example importing one now pays a MeTTa derivation where
#: it paid a Prolog body instead, which the 2026-09-14 ruling accepts
#: explicitly as the price of a library that survives the engine swap [measured
#: 2026-09-21: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=6e09cb25d5495c2db3283166e6ce4e07eefecfb2].
#: RE-PINNED 2026-09-24, 6987 to 6925 (-62), d4a365c16 holds the support
#: graph's visited set and the reference refresh's space sets in SWI tries
#: instead of library(nb_set): a membership check is one foreign call where
#: nb_set probed in Prolog, four inferences a step past a taken slot, from a
#: slot a library space's path-bearing name decided, and a walk over a node or
#: two pays a few inferences more for the trie's setup (-58); gate-perf's
#: d781eab8f carries an exact removal's selected head from the code that
#: selected it, so a withdrawal copies its equation once: 23 inferences fewer
#: for each equation removal the twin adopts and 4 for each it selects (-4);
#: each step read serially on its own committed tree, from gate-perf's pin at
#: c7d7244fb, and the fixed tree 4ff69551e reads what 4003462fe does [measured
#: 2026-09-24: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=4ff69551e0e226442cf7257b96af858adda957a4].
#: RE-PINNED 2026-09-25, 6925 to 6687 (-238), the host evaluation door replaces
#: the Python binding's own evaluation, and its moves are these, each measured
#: on the superproject's dd36742f5 against the registration change beneath it:
#: every answer reads its well-founded residue through call_delays/2, three
#: inferences an answer; a flat call of a compiled function is translated the
#: first time it is asked, a translation-cache miss the binding's direct call
#: skipped; the gate that direct call ran on every ask, a type-declaration
#: match through the space's storage, the foreign-space hook and the MORK
#: ownership question, is gone; and in a seat process filereader's
#: existing_predicate_arities/2 walks thirteen more predicates, the door, its
#: questions and the host services the binding now calls less the binding
#: predicates the door retired, two inferences each a registration of more than
#: twelve names [measured 2026-09-25T06:41:10+10:00: min-of-3 serial fresh
#: processes; command=python extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-25, 6687 to 6688 (+1), every force of a waiting function
#: names the module it is made from, through fun_home_in/3, and a write forces
#: only its own space [measured 2026-09-25T16:54:32+10:00: one full twins lane
#: before this commit and one with it, the two read on one battery path at the
#: landing's HEAD; command=python extensions/python/tools/twin_coverage.py].
BUDGET = 6688
