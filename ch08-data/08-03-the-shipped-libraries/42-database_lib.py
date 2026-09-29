"""Purpose: persist metagraph syntax and compose selection and reconstruction.

Guarantees: the same claims as 42-database_lib.metta.
[tested: python extensions/python/tools/twin_coverage.py examples/ch08-data/08-03-the-shipped-libraries/42-database_lib.metta; commit=24b9b7ee948564963a5c3455cd5b412d05afdd2c].
Owns resources: explicit handles close below and in finally; scoped handles
close when their answer streams end. Finally removes the temporary directory.
"""

from metta import Expression, G, S, V, lib
from metta._errors.errors import MettaError


def twin(m):
    """Match passive snapshots, join relations and reconstruct stored equations."""
    m += lib.file
    m += lib.database
    fn = m.fn
    atoms = fn.database_atoms
    add, remove = fn["database-add!"], fn["database-remove!"]
    close, scoped = fn["database-close!"], fn.with_database

    def selected(rows, pattern, template):
        """Compose Python atom bindings with substitution over an ordered snapshot."""
        if isinstance(template, tuple):
            template = Expression(template)
        return tuple(template.subs(bindings) for row in rows
                     if (bindings := pattern.unify(row)) is not None)

    def query(handle, pattern, template):
        """Read a snapshot before selecting its passive values."""
        return [selected(atoms(handle)[0], pattern, template)]

    def refused(call):
        """Observe a native refusal through the public evaluation door."""
        try:
            list(m.eval(call))
        except MettaError:
            return True
        return False

    assert fn.path_join(G("store"), G("journal.pl")) == [G("store/journal.pl")]
    work = fn["temp-dir!"](G("database-lib")).one()
    handles = []
    try:
        first_path = fn.path_join(work, G("first")).one()
        second_path = fn.path_join(work, G("second")).one()
        first = fn["database-open!"](first_path, S.none)[0]
        handles.append(first)
        second = fn["database-open!"](second_path, S.close)[0]
        handles.append(second)
        assert query(first, V.value, V.value) == [()]
        assert refused(S["database-open!"](first_path, S.flush))

        assert add(first, S.item(S.apple, 3)) == [True]
        assert add(first, S.item(S.pear, 5)) == [True]
        assert add(first, S.item(S.apple, 3)) == [True]
        assert query(first, S.item(V.name, V.price), (V.name, V.price)) == [((S.apple, 3), (S.pear, 5), (S.apple, 3))]
        assert query(first, S.item(V.name, 3), V.name) == [(S.apple, S.apple)]
        assert remove(first, S.item(S.apple, 3)) == [True]
        assert query(first, S.item(V.name, V.price), (V.name, V.price)) == [((S.pear, 5), (S.apple, 3))]
        assert remove(first, S.item(S.missing, 0)) == [False]
        assert query(first, S.missing(V.value), V.value) == [()]
        assert query(first, S.item(S.pear, V.price), V.price) == [(5,)]

        assert query(second, V.value, V.value) == [()]
        assert add(second, S.item(S.banana, 8)) == [True]
        assert query(second, S.item(V.name, V.price), (V.name, V.price)) == [((S.banana, 8),)]
        assert query(first, S.item(V.name, V.price), (V.name, V.price)) == [((S.pear, 5), (S.apple, 3))]

        assert add(first, S["+"](1, 2)) == [True]
        assert query(first, S["+"](1, V.value), V.value) == [(2,)]
        assert add(first, S.number(1)) == [True]
        assert add(first, S.number(1.0)) == [True]
        assert [S.hit for row in atoms(first)[0]
                if row == S.number(1) or row == S.number(1.0)] == [S.hit, S.hit]
        assert remove(first, S.number(1)) == [True]
        assert query(first, S.number(V.value), V.value) == [(1.0,)]
        nul_text = fn.string_from_codes((97, 0, 98)).one()
        assert fn.string_codes(nul_text) == [(97, 0, 98)]
        assert add(first, S.text(G("café"), nul_text, ())) == [True]
        assert query(first, S.text(V.left, V.right, ()), (V.left, V.right)) == [((G("café"), G("a\0b")),)]
        assert add(first, S.path(S.a, S.b, S.c)) == [True]
        path = next(row.children[1:] for row in atoms(first)[0]
                    if isinstance(row, Expression) and row[0] == S.path)
        assert [(path[:index], path[index:]) for index in range(len(path) + 1)] == [((), (S.a, S.b, S.c)), ((S.a,), (S.b, S.c)), ((S.a, S.b), (S.c,)), ((S.a, S.b, S.c), ())]
        assert add(first, ()) == [True]
        assert query(first, Expression(()), S.empty_value) == [(S.empty_value,)]
        assert add(first, S.unbound(V.value)) == [True]
        assert remove(first, S.unbound(V.renamed)) == [True]
        assert refused(S["database-add!"](first, second))

        assert add(first, S["="](S.stored_twice(V.x), V.x + V.x)) == [True]
        assert add(first, S["="](S.stored_twice(V.x), (V.x + V.x) + 1)) == [True]
        assert list(m.match(S["="](S.stored_twice(V.x), V.body))) == []
        assert add(first, S.edge(S.e1, S.alice, S.bob)) == [True]
        assert add(first, S.edge(S.e2, S.bob, S.carol)) == [True]
        assert add(first, S.supports(S.e1, S.e2)) == [True]
        graph = atoms(first)[0]
        joined = []
        for left, right in selected(graph, S.supports(V.left, V.right), (V.left, V.right)):
            for source, middle in selected(graph, S.edge(left, V.source, V.middle), (V.source, V.middle)):
                joined.extend((source, middle, target)
                              for target in selected(graph, S.edge(right, middle, V.target), V.target))
        assert joined == [(S.alice, S.bob, S.carol)]

        assert fn["database-sync!"](first) == [True]
        assert fn.file_exists(fn.path_join(first_path, G("journal.pl")).one()) == [True]
        assert refused(S["database-open!"](first_path, S.close))
        assert add(first, S.after_sync) == [True]
        assert close(first) == [True]
        assert close(first) == [True]
        assert close(second) == [True]
        assert refused(S.database_atoms(first))

        reopened = fn["database-open!"](first_path, S.flush)[0]
        handles.append(reopened)
        assert query(reopened, S.item(V.name, V.price), (V.name, V.price)) == [((S.pear, 5), (S.apple, 3))]
        assert query(reopened, S.text(V.left, V.right, ()), (V.left, V.right)) == [((G("café"), G("a\0b")),)]
        assert query(reopened, S.after_sync, S.present) == [(S.present,)]
        recipes = selected(atoms(reopened)[0], S["="](S.stored_twice(V.parameter), V.body),
                           S["|->"]((V.parameter,), V.body))
        assert [answer for recipe in recipes
                for answer in m.eval((m.eval(recipe)[0], 7))] == [14, 15]
        bodies = selected(atoms(reopened)[0], S["="](S.stored_twice(9), V.body), V.body)
        assert [answer for body in bodies for answer in m.eval(body)] == [18, 19]
        parameters = selected(atoms(reopened)[0], S["="](S.stored_twice(V.parameter), V.body), V.parameter)
        assert [bool(parameter.vars) for parameter in parameters] == [True, True]
        assert remove(reopened, S["="](S.stored_twice(V.fresh), V.fresh + V.fresh)) == [True]
        bodies = selected(atoms(reopened)[0], S["="](S.stored_twice(4), V.body), V.body)
        assert [answer for body in bodies for answer in m.eval(body)] == [9]
        assert close(reopened) == [True]

        snapshot = S["|->"]((V.store,), S.database_atoms(V.store))
        assert selected(scoped(first_path, S.flush, snapshot)[0],
                        S.item(V.name, V.price), (V.name, V.price)) == ((S.pear, 5), (S.apple, 3))
        assert list(scoped(first_path, S.none, S["|->"]((V.store,), S.superpose((S.left, S.right))))) == [S.left, S.right]
        assert list(scoped(first_path, S.none, S["|->"]((V.store,), S.superpose(())))) == []
        assert refused(S.with_database(first_path, S.none, S["|->"]((V.store,), S["database-add!"](V.store, S.bad(V.store)))))
        assert scoped(first_path, S.close, S["|->"]((V.store,), S["database-close!"](V.store))) == [True]
        assert scoped(second_path, S.close, snapshot) == [((S.item, S.banana, 8),)]
        invalid_path = fn.path_join(work, G("invalid")).one()
        assert refused(S["database-open!"](invalid_path, S.invented))
        assert fn.dir_exists(invalid_path) == [False]

        bad_path = fn.path_join(work, G("bad")).one()
        assert scoped(bad_path, S.close, S["|->"]((V.store,), S["database-add!"](V.store, S.original))) == [True]
        journal = fn.path_join(bad_path, G("journal.pl")).one()
        damaged = G("created(0).\nassert(row(original)).\ninvented(corruption).\n")
        assert fn["write-file!"](journal, damaged) == [True]
        assert refused(S["database-open!"](bad_path, S.flush))
        assert fn["read-file!"](journal) == [damaged]
    finally:
        for handle in handles:
            close(handle).one()
        assert fn["delete-tree!"](work) == [True]


#: MEASURED: all 71 claims cover snapshots, variable rules, joins and ownership.
#: The example pays 244929; both notations import File before Database.
#: [measured 2026-09-13: 226128 inferences, minimum of three fresh serial processes;
#: command=python extensions/python/tools/twin_coverage.py --measure --rounds 3
#: examples/ch08-data/08-03-the-shipped-libraries/42-database_lib.metta;
#: fixture=lib_database with engine/lib QLF artifacts purged; commit=24b9b7ee948564963a5c3455cd5b412d05afdd2c].
#: RE-PINNED 2026-09-14, 226128 to 248018 (+21890), String now derives nine
#: text recipes through MeTTa equations, with one function parameter for
#: padding and complete validation before empty construction; all import
#: consumers are measured after the provider change [measured 2026-09-14: min-
#: of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=118b805aedbee6de22be4f6131d97c3d6b9156de].
#: RE-PINNED 2026-09-21, 248018 to 518677 (+270659), the sixty libraries
#: derived in MeTTa landed with merge 97763e7fa eight hours after the previous
#: pin 55d451b67, so every example importing one now pays a MeTTa derivation
#: where it paid a Prolog body instead, which the 2026-09-14 ruling accepts
#: explicitly as the price of a library that survives the engine swap [measured
#: 2026-09-21: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=6e09cb25d5495c2db3283166e6ce4e07eefecfb2].
#: RE-PINNED 2026-09-24, 518677 to 543594 (+24917), placed on the full-
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
#: f2822e2ae: the boot host check (metta_require_patched_host, called once in
#: qlf_load_engine) adds about 10.3k inferences to every later load of a
#: library's Prolog half; measured 507,704 to 518,008 on text_lib's twin,
#: mechanism below the predicate not isolated; the commits
#: 63fc952ac..8d45268e3, which the ladder did not split; their runtime changes
#: are 31c0afd8a (the host refusal's message), 7472c4907, which marks a
#: module's reference face dirty instead of walking its forward closure, so
#: support_stabilize/3 walks the face's dependents only when the recomputed
#: value moved and an event that changes nothing recompiles no caller,
#: 7054c11f7, which carries lib 62ca61c's bisecting bit length in
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
#: RE-PINNED 2026-09-24, 543594 to 347954 (-195640), 0a81c782f loads a
#: library's Prolog half through the boot's claim (metta_load_source/2 in
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
#: RE-PINNED 2026-09-24, 347954 to 349386 (+1432), both: 2126ab6 installs the
#: library's native half through lib/_support/native_install.pl, loaded once
#: per process, and 0847c3d4c with 984eabe23 decides on its first read each
#: platform capability the twin reads, in a flag under a mutex; a792976 loads
#: process, socket and HTTP's libraries through the census and refuses per
#: call, which moves process_lib by 44 and socket_lib by -603 [measured
#: 2026-09-24: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=d832d20e8edfdad28ad52815757ba9e685ad2de3].
#: RE-PINNED 2026-09-24, 349386 to 360911 (+11525), +11,519 at ae1cc8936, where
#: a registration batch of thirteen names or more walks the visible predicate
#: table at two inferences a predicate that asking per name spent inside one C
#: call, and a batch above forty tests each predicate with a dict at one
#: inference fewer than the AVL; +6 at b5eb39acd, whose three new engine
#: exports the registration walk above twelve names reads at two inferences
#: each [measured 2026-09-24: min-of-3 serial fresh processes at HEAD in
#: battery 118 holding the committed tree alone (BATTERY_KEEP='', 11:56); each
#: step read with its parent and child in turn in battery 115 (10:42 to 11:18),
#: 117 (11:01 to 12:10) or 120 (12:04 to 12:13) from committed trees or this
#: job's patched copies of them, none from a working tree; 850d2a660's and
#: 0f6d29ba6's split from provider-carry's own pairs, aaeea643a's on the ladder
#: before 10:05; command=python extensions/python/tools/twin_coverage.py
#: --measure --rounds 3; commit=c7d7244fbe6d32d024ca8c61b336008e98b156ef].
#: RE-PINNED 2026-09-24, 360911 to 360678 (-233), d4a365c16 holds the support
#: graph's visited set and the reference refresh's space sets in SWI tries
#: instead of library(nb_set): a membership check is one foreign call where
#: nb_set probed in Prolog, four inferences a step past a taken slot, from a
#: slot a library space's path-bearing name decided, and a walk over a node or
#: two pays a few inferences more for the trie's setup (-2); gate-perf's
#: d781eab8f carries an exact removal's selected head from the code that
#: selected it, so a withdrawal copies its equation once: 23 inferences fewer
#: for each equation removal the twin adopts and 4 for each it selects (-253);
#: the packages job's 90be572a9 and 4003462fe register Prolog through one
#: engine service: +22 for each library the twin imports (ten new engine
#: predicates and two user imports in the registration walk at two inferences
#: each, less the retired loaded_extension_file/2), and 146 inferences for a
#: Prolog file's origin or 220 for a text's SHA-256 on a twin that registers
#: Prolog (+22); each step read serially on its own committed tree, from gate-
#: perf's pin at c7d7244fb, and the fixed tree 4ff69551e reads what 4003462fe
#: does [measured 2026-09-24: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=4ff69551e0e226442cf7257b96af858adda957a4].
#: RE-PINNED 2026-09-24, 360678 to 361036 (+358), +356 at the change this re-
#: pin lands with, which publishes a from row by itself when rows are all a
#: space owes: its 36 predicates visible to filereader's registration walk cost
#: a batch above twelve names 72 inferences, each restricted space's core about
#: 28 a predicate, and every whole publication and face event its ledger's
#: bookkeeping [measured 2026-09-24: the twins lane alone on 8d651070d with the
#: change before this one and with this change too, one after the other in
#: battery 117's one path, every component at its pin; command=sh
#: tools/check.sh twins (twin_coverage.py inside tools/bounded.sh);
#: commit=e4b7448d1f1bd98733f1b04c3906aaa42f35ef1a].
#: RE-PINNED 2026-09-25, 361036 to 361059 (+23), the py-* doors change makes
#: more predicates visible from filereader, and
#: filereader:existing_predicate_arities/2 walks every predicate visible there
#: at two inferences each whenever a source registering more than twelve names
#: loads: on one tree the change's new engine predicates alone, defined with
#: their two boot uses taken out, move this twin by 16 for each such load and
#: the whole change by 20, each give or take one or two inferences that move
#: with where the new names land in SWI's tables and that SWI's profiler, which
#: lists no system predicate, does not place (i-arity-walk-all-predicates)
#: [measured 2026-09-25T02:57:16+10:00: min-of-3 serial fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-25, 361059 to 355989 (-5070), the host evaluation door
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
#: more than twelve names [measured 2026-09-25T06:48:12+10:00: min-of-3 serial
#: fresh processes; command=python extensions/python/tools/twin_coverage.py
#: --repin].
#: RE-PINNED 2026-09-25, 355989 to 355999 (+10), Runtime.reclaim(), the
#: reclamation barrier metta_py_reclaim/1, adds five predicates to user, and
#: existing_predicate_arities/2 walks every user predicate about twice per
#: large load (i-arity-walk-all-predicates) [measured
#: 2026-09-25T11:25:25+10:00: one full twins lane before this commit and one
#: with it, the two read on one battery path at the landing's HEAD;
#: command=python extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-25, 355999 to 356001 (+2), both specializer doors prepare
#: a specialization's predicate with spaces:metta_prepare_function_predicate/3
#: before asserting its clauses [measured 2026-09-25T11:29:10+10:00: one full
#: twins lane before this commit and one with it, the two read on one battery
#: path at the landing's HEAD; command=python
#: extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-25, 356001 to 356005 (+4), retiring a library importer
#: derives the arity row again from any backing head a library home still
#: registers, journalled to the load that owns it [measured
#: 2026-09-25T11:33:06+10:00: one full twins lane before this commit and one
#: with it, the two read on one battery path at the landing's HEAD;
#: command=python extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-25, 356005 to 356015 (+10), lib/lib_string/lib_string.qlf
#: is now compiled by a child of its own whichever half's load reaches it first
#: (engine/qlf_boot.pl, qlf_compile_argument/0), and that compile keeps the :-
#: non_terminal directive for word_tokens//1 that a compile inside lib_csv's
#: child, where the warm-up's glob order put it, left out, since SWI's
#: non_terminal_decl/2 writes it only for a head no earlier load flagged; the
#: loader runs the directive, ten inferences, in every process that loads
#: lib_string [measured 2026-09-25T15:56:50+10:00: min-of-3 serial fresh
#: processes; command=python extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-25, 356015 to 356039 (+24), every force of a waiting
#: function names the module it is made from, through fun_home_in/3, and a
#: write forces only its own space [measured 2026-09-25T16:54:32+10:00: one
#: full twins lane before this commit and one with it, the two read on one
#: battery path at the landing's HEAD; command=python
#: extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-25, 356039 to 355855 (-184), lambdas are named by their
#: content and a copy restores its source's rows as a program [measured
#: 2026-09-25T17:00:15+10:00: one full twins lane before this commit and one
#: with it, the two read on one battery path at the landing's HEAD;
#: command=python extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-25, 355855 to 355925 (+70), engine/source_loading.pl's
#: load-error clause moved from the thread_local user:thread_message_hook/3 to
#: the global user:message_hook/3, so every thread and engine now runs the
#: check the main thread always ran: one inference per message while no load is
#: open there (clause(watching, true, _) fails) and two inside one
#: (load_failure/2 rejects the silent kind); the Python seat prints a twin's
#: library-load messages inside engines, where no clause ran before, and the
#: original's side does not move [measured 2026-09-25T18:43:14+10:00: min-of-3
#: serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-25, 355925 to 355927 (+2), a sweep of a module's generated
#: predicates retires the records describing each swept predicate, and a
#: release the rest of the module's [measured 2026-09-25T23:29:52+10:00: one
#: full twins lane before this commit and one with it, the two read on one
#: battery path at the landing's HEAD; command=python
#: extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-26, 355927 to 355945 (+18), engine/metta/control.pl's
#: partial/3 to partial/11, the clauses that let a Prolog meta-predicate call a
#: partial function value, are nine more predicates visible from filereader,
#: and filereader:existing_predicate_arities/2's batch walk, which a load
#: registering more than twelve names runs, pays two inferences for each: 18 a
#: batch, the original and the twin alike, and nine inert facts of those
#: arities move it the same [measured 2026-09-26T01:31:26+10:00: min-of-3
#: serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-26, 355945 to 355965 (+20), the reference faces of a
#: strongly connected component of from rows are computed together by label-
#: setting, which makes ten more predicates visible from metta_engine, and a
#: control adding only ten unused predicates to metta_engine reads the same, so
#: none of the move is face work; existing_predicate_arities/2 walks every
#: visible predicate at two inferences for each batch of more than twelve names
#: a load registers (i-arity-walk-all-predicates) [measured
#: 2026-09-26T03:09:18+10:00: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-26, 355965 to 355972 (+7), engine/source_loading.pl hears
#: a load's printed failures through a user:thread_message_hook/3 clause each
#: load asserts on the thread or engine running it and erases, where
#: c83b6bb1e's clause of the global user:message_hook/3 ran for every message:
#: 5 loads each call prolog_current_frame/1 once more (+5); 1 registration walk
#: over a batch of more than twelve names
#: (filereader:existing_predicate_arities/2) enumerates one more predicate than
#: the trunk's (+2), since SWI's autoImport() links prolog_current_frame/1 into
#: every module on metta_source_loading's import chain, user included, at the
#: boot's first load, where the trunk links it into user only at its first
#: library import [measured 2026-09-26T06:56:26+10:00: min-of-3 serial fresh
#: processes; command=python extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-26, 355972 to 355987 (+15), Registering a source's names
#: answers each name's Prolog arities in standard order, one msort/2 per
#: registration that adds names, where they came in the procedure table's order
#: and set the order of the arity/2 facts [measured 2026-09-26T12:30:45+10:00:
#: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-26, 355987 to 356048 (+61), A Prolog function registered
#: without its arity is claimed from its lowest arity's file through
#: aggregate_all(min(Arity, File), ...), where the scan took the first arity
#: the procedure table answered [measured 2026-09-26T13:04:06+10:00: min-of-3
#: serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-26, 356048 to 356054 (+6), The engine module defines three
#: predicates more, builtin_seat_prefixes/1, builtin_implementation_gap/2,
#: validate_builtin_implementation_gaps/2 and builtin_surface_predicate/3 in
#: and builtin_surface_predicate_name/1 out, and a program pays for each
#: predicate visible from the engine wherever it walks them:
#: existing_predicate_arities/2 two inferences a predicate for each load that
#: registers more than twelve names, and a restricted space twenty-seven a
#: predicate when it publishes the engine's core; three facts appended to
#: engine/metta/registration.pl on 07b75d16e move 14-lib_roman_pair_helpers,
#: 02-restricted_spaces and 37-statistics_lib by the same +6, +87 and +30
#: [measured 2026-09-26T14:30:17+10:00: min-of-3 serial fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-27, 356054 to 356466 (+412), the host switch to swipl-
#: patched.7 and the seat changes it needs: +26 the host switch to swipl-
#: patched.7, which delivers the heartbeat inside loops, so a held engine ticks
#: and the held goals read its ticks from the raw counter, 9 inferences a tick,
#: and whose three new system predicates ('$heartbeat'/0, '$file_hash'/2,
#: '$qlf_source_changed'/2) filereader's walk of every visible predicate
#: (existing_predicate_arities/2) meets, 2 inferences each; +12 the seat's
#: interrupt poll crossing only on its arming thread, whose hook costs 3
#: inferences a tick more and whose start goal runs on every new thread and
#: engine; +6 the poll's tick record updated in place, 3 inferences a tick more
#: than replacing it; +368 the held goals reading Used through metta_py_work/2,
#: which leaves a held engine's own ticks out and reads the tick term inside
#: its opening edge, 5 inferences a held reading [measured
#: 2026-09-27T03:41:21+10:00: one full twins lane of the trunk and one with
#: this landing, wt-merge battery 1, the trunk on swipl-patched.6 and every
#: part on .7, each through a same-shape host shim; command=python
#: extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-27, 356466 to 356471 (+5), a force of a waiting function
#: takes the typing policy and the specializer's lock before translation:
#: spaces:metta_ensure_compiled/2 stabilises the policy and takes the
#: specializer's mutex around the translation once per force, and the
#: translation's own per-pair stabilisation re-enters through
#: with_typing_policy_stable/1's first clause [measured
#: 2026-09-27T09:56:55+10:00: one full twins lane before this commit and one
#: with it, each read in one battery of the landing's HEAD after a QLF purge
#: and one warm-up; command=python extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-27, 356471 to 356531 (+60), the constructive negation's
#: engine additions, each counted in this twin's own run: 1 registration walk
#: over more than twelve names (filereader:existing_predicate_arities/2), each
#: now reading 31 more predicates at 2 inferences (+62); -2 of clause-indexing
#: layout [measured 2026-09-27T18:31:56+10:00: one full twins lane with this
#: landing, in a battery of its tree at 775d3cf35, beside one of the base in a
#: battery of 775d3cf35 from 2026-09-27T18:40:06+10:00, which reads the old
#: pin; command=python extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-28, 356531 to 356529 (-2), -2 at tsm-licence's notices
#: reader as its block lookahead amended it: engine/host_notices.pl, which
#: every boot loads, opens a component block only where its Component field
#: directly follows the line of 78 '=', the calls not traced; read on swipl-
#: patched.8, the count above on .7, which no longer runs [measured
#: 2026-09-28T12:31:49+10:00: full twins lanes in wt-merge's battery 1 on
#: swipl-patched.8 at this boundary, engine/host_notices.pl as amended against
#: the day before's as first written; command=sh tools/check.sh twins].
#: RE-PINNED 2026-09-27, 356529 to 356282 (-247), +2 at the host switch to
#: swipl-patched.8, whose swi-heartbeat-inferences-charged-to-the-program
#: leaves the interrupt poll's own inferences out of every count, so a window
#: the seat's calibrated poll correction read 1 to 3 low on .7 reads exactly;
#: -249 at interrupts B's seat change, which drops the poll's boot calibration,
#: its tick charges and its tick record: a held reading through metta_py_work/2
#: brackets 3 inferences where it bracketed 6, a registration walk over more
#: than twelve names meets 6 fewer seat predicates (12 or 14 fewer), and a
#: thread the twin joins credits it 11 where it credited 16 [measured
#: 2026-09-27T20:07:01+10:00: full twins lanes in wt-merge's battery 1, tsm-
#: licence's series and its engine reader on swipl-patched.7, the series on
#: swipl-patched.8, and the stack through janus-contract B on swipl-patched.8
#: twice; command=sh tools/check.sh twins]. With step 4's notices reader as
#: amended both counts read -2 [measured 2026-09-28T12:34:38+10:00: full twins
#: lanes in wt-merge's battery 1 on swipl-patched.8 at this boundary,
#: engine/host_notices.pl as amended against the day before's as first written;
#: command=sh tools/check.sh twins].
#: RE-PINNED 2026-09-27, 356282 to 356284 (+2), +2 at janus-contract A, whose
#: seat loader adds metta_extension_require_patches/3 and the format/3 it
#: imports to the engine module a registration walk enumerates, and reads the
#: seat's requirement into its own module where host_patch/2 used to stand
#: there, so a walk over more than twelve names meets one more predicate at 2
#: inferences [measured 2026-09-27T20:31:29+10:00: full twins lanes on swipl-
#: patched.8 in wt-merge's battery 1, two of the stack through janus-contract B
#: and two with janus-contract A; command=sh tools/check.sh twins]. With step
#: 4's notices reader as amended both counts read -2 [measured
#: 2026-09-28T12:37:38+10:00: full twins lanes in wt-merge's battery 1 on
#: swipl-patched.8 at this boundary, engine/host_notices.pl as amended against
#: the day before's as first written; command=sh tools/check.sh twins].
#: RE-PINNED 2026-09-27, 356284 to 344425 (-11859), -11,859 at walk-tax B,
#: which registers a batch's Prolog arities by asking each name, so a
#: registration walk over more than twelve names no longer reads every
#: predicate visible from the loading module at 2 inferences each [measured
#: 2026-09-27T20:38:05+10:00: full twins lanes on swipl-patched.8 in wt-merge's
#: battery 1, two with janus-contract A and two with walk-tax B; command=sh
#: tools/check.sh twins]. With step 4's notices reader as amended both counts
#: read -2 [measured 2026-09-28T12:40:25+10:00: full twins lanes in wt-merge's
#: battery 1 on swipl-patched.8 at this boundary, engine/host_notices.pl as
#: amended against the day before's as first written; command=sh tools/check.sh
#: twins].
#: RE-PINNED 2026-09-29, 344425 to 345406 (+981), this twin reads 344429 before
#: the change and 345406 with the change (+977): each definition marks its name
#: as changed and a sweep repairs only the receipts naming a marked name, where
#: it re-checked every receipt the process held: with that use this twin reads
#: 345406 where the definitions alone read 344429 (+977); it read 344429
#: against its pin 344425 before this step, a distance of +4 that is not this
#: step's (+4 the earlier steps' moves inside its tolerance) and is not
#: attributed here [measured 2026-09-29T06:43:43+10:00: min-of-3 serial fresh
#: processes; command=python extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-29, 345406 to 345594 (+188), this twin reads 345406 before
#: the change and 345594 with the change (+188): a definition that cannot move
#: its space's source map leaves the space's source reader published, so a load
#: beside a from row publishes the face once per runnable instead of once per
#: definition: with that use this twin reads 345594 where the definitions alone
#: read 345406 (+188) [measured 2026-09-29T06:51:34+10:00: min-of-3 serial
#: fresh processes; command=python extensions/python/tools/twin_coverage.py
#: --repin].
BUDGET = 345594
