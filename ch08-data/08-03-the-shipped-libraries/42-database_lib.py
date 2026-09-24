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
BUDGET = 360911
