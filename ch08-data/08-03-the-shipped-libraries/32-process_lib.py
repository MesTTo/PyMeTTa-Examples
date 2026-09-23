"""Purpose: running a program with an argument vector, and watching a started one.

A program name and an argument are `G("...")` text, because they are text; a run
answers a `(process-result Code Output Error)` expression, read as a tuple. The two
started processes are Python names holding the identifiers, as the example's `bind!`
forms are.

Guarantees: the same claims as 32-process_lib.metta
[tested: python extensions/python/tools/twin_coverage.py examples/ch08-data/08-03-the-shipped-libraries/32-process_lib.metta; commit=623a2848ef49a936cd82b07adfbed2999d8548a4].
Open Obligations:
  To Do: None
  Hacks: None
  Future Enhancements: None.
"""

from metta import G, S, lib
from metta._errors.errors import MettaError


def twin(m):
    """Run, capture, feed, start, poll, signal and wait."""
    m += lib.process

    def refused(call):
        """Whether evaluating a call raises, which is what if-error reads."""
        try:
            list(m.eval(call))
        except MettaError:
            return True
        return False

    def result(answers):
        """One run's (process-result Code Output Error) expression, as a tuple."""
        return tuple(answers.one())

    run, feed = m.fn["process-run!"], m.fn["process-run-input!"]
    start, wait = m.fn["process-start!"], m.fn["process-wait!"]
    status, signal = m.fn.process_status, m.fn["process-signal!"]

    # A run answers (process-result Code Output Error): the exit code as a Number and
    # both streams as Strings. The program is named and the arguments are a
    # COLLECTION, so nothing in them can become a second command.
    assert result(run(G("echo"), (G("hi"),))) == (S.process_result, 0, G("hi\n"), G(""))
    assert result(run(G("echo"), (G("one"), G("two")))) == (
        S.process_result, 0, G("one two\n"), G(""),
    )
    assert result(run(G("true"), ())) == (S.process_result, 0, G(""), G(""))

    # A nonzero exit is a STATUS and not an error.
    assert result(run(G("false"), ())) == (S.process_result, 1, G(""), G(""))
    assert m.fn.index_atom(S["process-run!"](G("sh"), (G("-c"), G("exit 7"))), 1) == [7]

    # Both streams are captured separately.
    assert result(run(G("sh"), (G("-c"), G("echo out; echo err 1>&2; exit 3")))) == (
        S.process_result, 3, G("out\n"), G("err\n"),
    )

    # An argument is never parsed: this file name would be two commands to a shell,
    # and here it is one argument.
    assert result(run(G("echo"), (G("; echo hacked"),))) == (
        S.process_result, 0, G("; echo hacked\n"), G(""),
    )
    # Running a shell is the caller's own choice, and it says so in the program's name.
    assert result(run(G("sh"), (G("-c"), G("echo shell")))) == (
        S.process_result, 0, G("shell\n"), G(""),
    )

    # A program that reads its input is fed without a temporary file.
    assert result(feed(G("cat"), (), G("fed"))) == (S.process_result, 0, G("fed"), G(""))
    assert result(feed(G("wc"), (G("-c"),), G("1234"))) == (
        S.process_result, 0, G("4\n"), G(""),
    )

    # A program that could not be launched is a refusal naming it.
    assert refused(S["process-run!"](G("no_such_program_anywhere"), ()))
    assert refused(S["process-run!"](G("/no/such/binary"), ()))

    # A started process is the caller's: it answers an identifier, process-status asks
    # without waiting, and process-wait! answers the code.
    quick = start(G("true"), ()).one()
    assert quick > 0
    assert wait(quick) == [0]
    # Waiting twice is a refusal, because the host has already forgotten the process.
    assert refused(S["process-wait!"](quick))

    # A process that outlives the call is signalled, and a signalled program answers
    # the negative of its signal number.
    sleeper = start(G("sleep"), (G("30"),)).one()
    assert status(sleeper) == [S.running]
    assert signal(sleeper, S.term) == [True]
    assert wait(sleeper) == [-15]

    # Every signal the library sends is data, and one it does not know is refused.
    assert list(m.fn.process_signals().one()) == [S.term, S.kill, S.int, S.hup]
    assert refused(S["process-signal!"](1, S.nosuch))

    # The refusals for what is not a program, not a vector and not a process. The
    # face declares these inputs %Undefined%, so each wrong value reaches the
    # Prolog body and its type_error is the refusal, which the example's if-error
    # over catch reads the same way it would read a declared BadArgType.
    assert refused(S["process-run!"](G("echo"), G("not a collection")))
    assert refused(S["process-run!"](G("echo"), (S.nested(),)))
    assert refused(S["process-run!"](7, ()))
    assert refused(S["process-wait!"](G("not a process")))


#: MEASURED on this branch rather than inherited: this twin is new, so there is
#: no earlier pin to move. The 24 claims cover the seven heads, the exit code as a
#: status, the signalled process's negative code and the refusals. A run's cost is
#: mostly the host's: the child does the work, so both sides here are well under the
#: other libraries' examples [measured 2026-09-12: 47068 inferences against the
#: example's 50892, minimum of three serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --measure --rounds 3
#: examples/ch08-data/08-03-the-shipped-libraries/32-process_lib.metta;
#: fixture=lib_process at its functional commit, artifacts purged before the run;
#: commit=623a2848ef49a936cd82b07adfbed2999d8548a4].
#: RE-PINNED 2026-09-21, 47068 to 75573 (+28505), the sixty libraries derived
#: in MeTTa landed with merge 97763e7fa eight hours after the previous pin
#: 55d451b67, so every example importing one now pays a MeTTa derivation where
#: it paid a Prolog body instead, which the 2026-09-14 ruling accepts
#: explicitly as the price of a library that survives the engine swap [measured
#: 2026-09-21: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=6e09cb25d5495c2db3283166e6ce4e07eefecfb2].
#: RE-PINNED 2026-09-24, 75573 to 76966 (+1393), placed on the full-
#: configuration first-parent ladder from the pin commit 6e09cb25d: d27805154
#: carried lib 19a231b, which regenerated the six drifted Prolog faces from
#: their Prolog halves' export modes and declares this twin's refused inputs
#: %Undefined%, so each wrong value reaches the Prolog body, and the twin
#: asserts those refusals with refused(...) since twins commit aa891a0d; the
#: old assertions cannot run after d27805154 and the new ones cannot run before
#: it, so the face and the twin's own change are one step; the 77 commits
#: d27805154..c09dc4868, where the sweep puts the probes' steps at 33219ffa0 (a
#: bare library name resolves to its pkg.metta), 0cd329450 (the platform
#: refusal kind's catalog row and vocabulary member) and d8231f103 (a library
#: spec may not walk out of the library root); a7955cd07 carried lib 629c86c,
#: the library split, which moved every library's surface out of its pkg.metta
#: manifest into lib.metta beside it, so an import reads the manifest and then
#: imports the library's own source as a second file; 54784fded reads the
#: builtin type surface from every .metta in lib_builtin_types' directory,
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
#: 7472c4907 marks a module's reference face dirty instead of walking its
#: forward closure when the face's value carries the event, so
#: support_stabilize/3 walks the face's dependents only when the recomputed
#: value moved and an event that changes nothing recompiles no caller;
#: da91bc244 confines an exact removal's selection to its own atom:
#: native_retract_one/2 now records the selected clause's head, a clause/3
#: lookup per exact removal, and checks each removal made while the selector is
#: live against it, a few inferences per removal (+8 on most twins, +24 to +192
#: on the library twins that withdraw package rows) [measured 2026-09-24: min-
#: of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=WORKTREE].
BUDGET = 76966
