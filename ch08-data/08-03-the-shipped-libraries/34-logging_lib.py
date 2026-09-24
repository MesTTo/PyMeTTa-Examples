"""Purpose: structured messages, topic controls and explicit capture handlers.

Guarantees: the same 28 claims as 34-logging_lib.metta.
[tested: python extensions/python/tools/twin_coverage.py examples/ch08-data/08-03-the-shipped-libraries/34-logging_lib.metta; commit=cf6b111ffad74477d9fa7169b215379dcabe721c].
"""

import metta
from metta import FALSE, TRUE, Expression, G, S, V, fn, lib
from metta._errors.errors import MettaError


def twin(m):
    """Capture structured events, preserve payload syntax and route by topic."""
    m += lib.logging
    records = metta.space(S.log_records)

    @m.define
    def record_log(label: str, event: Expression) -> bool:
        return fn.add_atom(records, S.captured(label, event))

    def refused(call):
        """Read a native refusal through the evaluation boundary."""
        try:
            list(m.eval(call))
        except MettaError:
            return True
        return False

    enabled, topic = m.fn.log_enabled, m.fn["log-topic!"]
    log, log_to = m.fn["log!"], m.fn["log-to!"]
    name = G("library-example")
    payload = S["+"](1, 2)
    consume = S["|->"]((V.event,), TRUE)

    assert list(m.fn.log_levels().one()) == [S.debug, S.informational, S.warning, S.error]
    assert enabled(name) == [False]
    assert list(m.fn.log_topics().one()) == []
    assert list(log_to(S.missing_handler, name, S.error, payload).one()) == []
    assert m.fn.log_format(name, S.debug, payload) == [G("library-example [debug] (+ 1 2)")]
    assert list(topic(name, TRUE).one()) == []
    assert enabled(name) == [True]
    assert [tuple(row) for row in m.fn.log_topics().one()] == [(S.log_topic, name, True)]

    assert list(log(name, S.informational, G("hello")).one()) == []
    assert list(log_to(S.record_log(G("first")), name, S.debug, payload).one()) == []
    pattern = S.captured(G("first"), S.log_event(V.topic, V.level, V.payload))
    captured = records[pattern].one()
    assert len(captured.payload) == 3
    assert captured.payload == payload
    assert list(log_to(S.record_log(G("second")), name, S.informational,
                       S.loaded(G("data.csv"))).one()) == []
    assert list(log_to(consume, name, S.warning, S.retry(2)).one()) == []
    assert list(log_to(consume, name, S.error, S.failed(G("input"))).one()) == []
    assert len(records) == 2
    assert list(log_to(S["|->"]((V.event,), FALSE), name, S.informational, G("visible")).one()) == []

    assert refused(S["log-to!"](S["|->"]((V.event,), 7), name, S.debug, S.x))
    assert refused(S["log-to!"](S["|->"]((V.event,), S.empty()), name, S.debug, S.x))
    assert refused(S["log-to!"](S.missing_handler, name, S.debug, S.x))
    assert refused(S["log!"](name, S.fatal, S.x))
    assert refused(S.log_format(name, S.fatal, S.x))
    assert list(topic(name, FALSE).one()) == []
    assert enabled(name) == [False]
    assert list(log_to(S.missing_handler, name, S.error, S.x).one()) == []
    assert [tuple(row) for row in m.fn.log_topics().one()] == [(S.log_topic, name, False)]
    assert refused(S["log!"](name, S.fatal, S.x))
    assert enabled(G("library-example.child")) == [False]


#: MEASURED: all 28 claims, including the compiled capture handler and both
#: native printing and explicit capture. The example pays 53732 inferences.
#: [measured 2026-09-12: 54976 inferences, minimum of three fresh serial processes;
#: command=python extensions/python/tools/twin_coverage.py --measure --rounds 3
#: examples/ch08-data/08-03-the-shipped-libraries/34-logging_lib.metta;
#: fixture=lib_logging at its functional commit with engine/lib QLF artifacts purged;
#: commit=cf6b111ffad74477d9fa7169b215379dcabe721c].
#: RE-PINNED 2026-09-21, 54976 to 75076 (+20100), the sixty libraries derived
#: in MeTTa landed with merge 97763e7fa eight hours after the previous pin
#: 55d451b67, so every example importing one now pays a MeTTa derivation where
#: it paid a Prolog body instead, which the 2026-09-14 ruling accepts
#: explicitly as the price of a library that survives the engine swap [measured
#: 2026-09-21: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=6e09cb25d5495c2db3283166e6ce4e07eefecfb2].
#: RE-PINNED 2026-09-24, 75076 to 79466 (+4390), placed on the full-
#: configuration first-parent ladder from the pin commit 6e09cb25d: the 120
#: commits 43e964002..c09dc4868, where the per-commit probe sweep puts each
#: step at one commit: 5b4e7e53d reads a translator rule's declared type where
#: the rule lives; aea2e5e03 and 6922f54c9 carry the csv and lib_file refusal
#: vocabulary; d27805154 carries lib 19a231b, whose regenerated faces declare
#: six libraries' inputs %Undefined%, so their calls stop paying a declared-
#: type check (vector_lib -7278, statistics_lib -6453); 33219ffa0 resolves a
#: bare library name to its pkg.metta; 0cd329450 adds the platform refusal
#: kind, one metta_refusal_declaration/4 row that metta_catalog_preset/1 turns
#: into one more (refusal ...) catalog row and one more refusal-kind vocabulary
#: member, measured at +10 to +15 on most twins; and d8231f103 refuses a
#: library spec that walks out of the library root; a7955cd07 carried lib
#: 629c86c, the library split, which moved every library's surface out of its
#: pkg.metta manifest into lib.metta beside it, so an import reads the manifest
#: and then imports the library's own source as a second file; 54784fded reads
#: the builtin type surface from every .metta in lib_builtin_types' directory,
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
#: the commits 63fc952ac..8d45268e3, which the ladder did not split; their
#: runtime changes are 31c0afd8a (the host refusal's message), 7472c4907, which
#: marks a module's reference face dirty instead of walking its forward
#: closure, so support_stabilize/3 walks the face's dependents only when the
#: recomputed value moved and an event that changes nothing recompiles no
#: caller, 7054c11f7, which carries lib 62ca61c's bisecting bit length in
#: _support/statistics.metta, and the Python-seat pointers; da91bc244 confines
#: an exact removal's selection to its own atom: native_retract_one/2 now
#: records the selected clause's head, a clause/3 lookup per exact removal, and
#: checks each removal made while the selector is live against it, a few
#: inferences per removal (+8 on most twins, +24 to +192 on the library twins
#: that withdraw package rows); where a twin's move exceeds these steps, the
#: remainder is drift that stayed inside its band (four inferences, or its own
#: declared allowance) on every other interval [measured 2026-09-24: min-of-3
#: serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=WORKTREE].
#: RE-PINNED 2026-09-24, 79466 to 69387 (-10079), 0a81c782f loads a library's
#: Prolog half through the boot's claim (metta_load_source/2 in
#: package_load_native/2), so the half, and every governed half or support file
#: it loads in turn, reads the .qlf the claim's hermetic child wrote where it
#: had compiled from source in every process; the same commit starts that child
#: from the running home's own swipl, where it had been the stock swipl the
#: lane's PATH finds, which the host check has refused since f2822e2ae, so no
#: child had written an artifact and lib/_support/native_build.pl compiled in
#: every process that loaded a library with a native half, the +10.3k that
#: f2822e2ae's paragraph charges to the boot host check [measured 2026-09-24:
#: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=0a81c782fd6ba00984c36e58e228f73bca810dee].
#: RE-PINNED 2026-09-24, 69387 to 69321 (-66), d4a365c16 holds the support
#: graph's visited set and the reference refresh's space sets in SWI tries
#: instead of library(nb_set): a membership check is one foreign call where
#: nb_set probed in Prolog, four inferences a step past a taken slot, from a
#: slot a library space's path-bearing name decided, and a walk over a node or
#: two pays a few inferences more for the trie's setup (+3); gate-perf's
#: d781eab8f carries an exact removal's selected head from the code that
#: selected it, so a withdrawal copies its equation once: 23 inferences fewer
#: for each equation removal the twin adopts and 4 for each it selects (-69);
#: each step read serially on its own committed tree, from gate-perf's pin at
#: c7d7244fb, and the fixed tree 4ff69551e reads what 4003462fe does [measured
#: 2026-09-24: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=4ff69551e0e226442cf7257b96af858adda957a4].
#: RE-PINNED 2026-09-24, 69321 to 69344 (+23), +23 at the change this re-pin
#: lands with, which publishes a from row by itself when rows are all a space
#: owes: its 36 predicates visible to filereader's registration walk cost a
#: batch above twelve names 72 inferences, each restricted space's core about
#: 28 a predicate, and every whole publication and face event its ledger's
#: bookkeeping [measured 2026-09-24: the twins lane alone on 8d651070d with the
#: change before this one and with this change too, one after the other in
#: battery 117's one path, every component at its pin; command=sh
#: tools/check.sh twins (twin_coverage.py inside tools/bounded.sh);
#: commit=e4b7448d1f1bd98733f1b04c3906aaa42f35ef1a].
#: RE-PINNED 2026-09-25, 69344 to 69324 (-20), the registration refusal kind
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
#: the base [measured 2026-09-25T06:29:11+10:00: min-of-3 serial fresh
#: processes; command=python extensions/python/tools/twin_coverage.py --repin].
BUDGET = 69324
