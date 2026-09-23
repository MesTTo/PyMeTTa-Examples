"""Purpose: exchange CSV through every library head and both typed arities.

Guarantees: the twin preserves the example's field lists, duplicate answers,
live queries and numbered snapshots
[tested: python extensions/python/tools/twin_coverage.py examples/ch08-data/08-03-the-shipped-libraries/17-csv_lib.metta; commit=bd027d8b7a9ef1d96fb4cdb160c9b3eb4157d52e].
Owns resources: the temporary directory removes its CSV and writer lock;
snapshots follow the engine's ordinary space lifetime.
"""

from pathlib import Path
from tempfile import TemporaryDirectory

import metta
from metta import G, S, V, lib


def twin(m):
    """Use Python values and native space queries around the CSV functions."""
    m += lib.csv
    parse, encode = m.fn.csv_parse, m.fn.csv_encode
    records = ((G("001"), G("a,b")), (G("002"), G("9")))
    assert [list(row) for row in parse(G('001,"a,b"\r\n002,9\r\n')).one()] == [list(row) for row in records]
    assert encode(records) == [G('001,"a,b"\r\n002,9\r\n')]
    skipped = S.quote(((S.separator, G(";")), (S.skip, 1)))
    assert [list(row) for row in parse(G("id;value\n001;a\n001;a\n"), skipped).one()] == [[G("001"), G("a")], [G("001"), G("a")]]
    assert encode(((G("001"), G("a;b")),), S.quote(((S.separator, G(";")), (S.newline, G("\n"))))) == [G('001;"a;b"\n')]
    assert list(parse(G("")).one()) == []
    assert encode(()) == [G("")]
    assert [list(row) for row in parse(G('\n""\n,\n'), S.quote(((S.width, S.any),))).one()] == [[], [G("")], [G(""), G("")]]
    assert [list(row) for row in parse(G('a"b,c\n'), S.quote(((S.quote, G("")),))).one()] == [[G('a"b'), G("c")]]
    unicode_dialect = S.quote(((S.separator, G("🦊")), (S.quote, G("λ"))))
    text = encode(((G("é🦊"), G("λ\r\n")),), unicode_dialect).one()
    assert [list(row) for row in parse(G(text), unicode_dialect).one()] == [[G("é🦊"), G("λ\r\n")]]

    m += lib.file
    with TemporaryDirectory(prefix="metta-csv-") as directory:
        path = G(str(Path(directory) / "records.csv"))
        assert m.fn["csv-write!"](path, records).one() is True
        assert [list(row) for row in m.fn["csv-read!"](path)] == [list(row) for row in records]
        assert m.fn["csv-append!"](path, ((G("002"), G("9")),)).one() is True
        original = [[G("001"), G("a,b")], [G("002"), G("9")], [G("002"), G("9")]]
        assert [list(row) for row in m.fn["csv-read!"](path)] == original
        live = metta.space(m.fn.csv_space(path).one())
        assert [[row.id, row.value] for row in live[S.row(V.id, V.value)]] == original
        snapshot = metta.space(m.fn["csv-snapshot!"](path).one())
        numbered = [[1, G("001"), G("a,b")], [2, G("002"), G("9")], [3, G("002"), G("9")]]
        assert [[row.n, row.id, row.value] for row in snapshot[S.row(V.n, V.id, V.value)]] == numbered

        dialect = S.quote(((S.separator, G(";")),))
        assert m.fn["csv-write!"](path, ((G("id"), G("value")), (G("003"), G("a;b"))), dialect).one() is True
        assert m.fn["csv-append!"](path, ((G("004"), G("7")),), dialect).one() is True
        changed = [[G("003"), G("a;b")], [G("004"), G("7")]]
        assert [list(row) for row in m.fn["csv-read!"](path, skipped)] == changed
        configured = metta.space(m.fn.csv_space(path, skipped).one())
        assert [[row.id, row.value] for row in configured[S.row(V.id, V.value)]] == changed
        kept = metta.space(m.fn["csv-snapshot!"](path, skipped).one())
        assert [[row.n, row.id, row.value] for row in kept[S.row(V.n, V.id, V.value)]] == [[2, G("003"), G("a;b")], [3, G("004"), G("7")]]
        assert [[row.n, row.id, row.value] for row in snapshot[S.row(V.n, V.id, V.value)]] == numbered
        m.fn["csv-write!"](path, ((G("id"), G("value")), (G("005"), G("later"))), dialect).one()
        assert [[row.id, row.value] for row in configured[S.row(V.id, V.value)]] == [[G("005"), G("later")]]


#: CSV text, files, live views and snapshots prove all twenty-two example
#: claims through seven heads and both arities. Configuration uses the
#: language's quote barrier; stored rows retain duplicates and record numbers.
#: [measured 2026-09-11: 103630 inferences, minimum of three serial fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --measure --rounds 3
#: examples/ch08-data/08-03-the-shipped-libraries/17-csv_lib.metta
#: examples/ch08-data/08-03-the-shipped-libraries/05-json_lib.metta; commit=bd027d8b7a9ef1d96fb4cdb160c9b3eb4157d52e].
#: RE-PINNED 2026-09-11, 103630 to 163857 (+60227), String now imports its
#: complete typed native surface and checks its declared native inputs; an
#: unchanged-cut control with identical engine and MORK binaries attributes
#: these exact movements to the String provider and shared native_object/6
#: dependency argument [measured 2026-09-11: min-of-3 serial fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=3aaad3435292e4c7d5cc3a01bfda39430aacc6e8].
#: RE-PINNED 2026-09-12, 163857 to 188409 (+24552), The File library publishes
#: 56 documented heads at 60 arities where it published 32, so every direct and
#: transitive importer pays the larger generated face and the module's own
#: export list. An identical-binary control at 8eb04b55a with artifacts purged
#: measured each of these ten twins before the change (ai-tmp/ai-lib2-file-
#: importers-before.log) and attributes the whole movement to that face:
#: +22,479 on the four twins that only import it through another library,
#: +24,552 to +24,862 where the example also calls it, and +30,258 and +30,687
#: on the two whose own claims are file operations [measured 2026-09-12: min-
#: of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=e40ef941310bddd1f57074eb559e78aac8a263b0].
#: RE-PINNED 2026-09-12, 188409 to 188422 (+13), File transfers newly owned
#: streams through adopt_file_stream/2 and claims a close atomically; HTTP also
#: verifies transaction refusal before server lifecycle effects [measured
#: 2026-09-12: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=0f22b69cfca5c108e4126bdd56ab9bb2e493744d].
#: RE-PINNED 2026-09-13, 188422 to 188443 (+21), File exports its shared stream
#: borrowing and rollback operations; failed Socket and HTTP publication now
#: withdraws the registered stream before closing it [measured 2026-09-13: min-
#: of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=781ee98e188c23ea7ef9298636d6e5e6c7fdc727].
#: RE-PINNED 2026-09-13, 188443 to 188456 (+13), File privately exports its
#: existing staged publisher with callback qualification; Compression shares
#: that ownership and publication protocol [measured 2026-09-13: min-of-3
#: serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=7b42d5ee5cecb82709617b7ed08dfa2c1441f268].
#: RE-PINNED 2026-09-13, 188456 to 188987 (+531), File exports its staged
#: publisher to Compression; the shared native builder accepts the private
#: archive provider recipe. All consumers are remeasured after those dependency
#: changes [measured 2026-09-13: min-of-3 serial fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=7b42d5ee5cecb82709617b7ed08dfa2c1441f268].
#: RE-PINNED 2026-09-14, 188987 to 211951 (+22964), String now derives nine
#: text recipes through MeTTa equations, with one function parameter for
#: padding and complete validation before empty construction; all import
#: consumers are measured after the provider change [measured 2026-09-14: min-
#: of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=118b805aedbee6de22be4f6131d97c3d6b9156de].
#: RE-PINNED 2026-09-21, 211951 to 472619 (+260668), the sixty libraries
#: derived in MeTTa landed with merge 97763e7fa eight hours after the previous
#: pin 55d451b67, so every example importing one now pays a MeTTa derivation
#: where it paid a Prolog body instead, which the 2026-09-14 ruling accepts
#: explicitly as the price of a library that survives the engine swap [measured
#: 2026-09-21: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=6e09cb25d5495c2db3283166e6ce4e07eefecfb2].
#: RE-PINNED 2026-09-24, 472619 to 529418 (+56799), placed on the full-
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
BUDGET = 529418
