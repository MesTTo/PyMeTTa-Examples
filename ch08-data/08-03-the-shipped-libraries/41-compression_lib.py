"""Purpose: compress complete bytes and publish validated archive contents.

Guarantees: the same 54 claims as 41-compression_lib.metta.
[tested: python extensions/python/tools/twin_coverage.py examples/ch08-data/08-03-the-shipped-libraries/41-compression_lib.metta; commit=7b42d5ee5cecb82709617b7ed08dfa2c1441f268].
Owns resources: finally removes the temporary directory; native operations
close their streams and remove unpublished staging on each exit.
"""

from metta import G, S, lib
from metta._errors.errors import MettaError


def twin(m):
    """Use one envelope parameter for bytes, files and archive validation."""
    m += lib.file
    m += lib.compression
    fn = m.fn

    def refused(call):
        """Observe an operation refusal through the public evaluation door."""
        try:
            list(m.eval(call))
        except MettaError:
            return True
        return False

    assert list(fn.compression_formats().one()) == [S.gzip, S.zlib]
    assert fn.path_join(G("one"), G("two")) == [G("one/two")]
    data = (0, 128, 255, 10)
    gzip_bytes = fn.compress_bytes(S.gzip, 6, data).one()
    zlib_bytes = fn.compress_bytes(S.zlib, 6, data).one()
    assert gzip_bytes[0] == 31
    assert gzip_bytes[1] == 139
    assert list(fn.decompress_bytes(S.gzip, gzip_bytes).one()) == list(data)
    assert list(fn.decompress_bytes(S.zlib, zlib_bytes).one()) == list(data)
    assert list(fn.decompress_bytes(S.gzip, fn.compress_bytes(S.gzip, 0, ()).one()).one()) == []
    assert list(fn.decompress_bytes(S.zlib, fn.compress_bytes(S.zlib, 9, ()).one()).one()) == []
    assert list(fn.decompress_bytes(S.gzip, fn.compress_bytes(S.gzip, 9, (1, 1, 1, 1, 1)).one()).one()) == [1, 1, 1, 1, 1]
    assert list(fn.decompress_bytes(S.zlib, fn.compress_bytes(S.zlib, 0, (1, 2, 3)).one()).one()) == [1, 2, 3]
    assert refused(S.compress_bytes(S.invented, 6, data))
    assert refused(S.compress_bytes(S.gzip, -1, data))
    assert refused(S.compress_bytes(S.gzip, 10, data))
    assert refused(S.compress_bytes(S.gzip, 6, (256,)))
    assert refused(S.compress_bytes(S.gzip, 6, (-1,)))
    assert refused(S.decompress_bytes(S.gzip, ()))
    assert refused(S.decompress_bytes(S.gzip, (31, 139)))
    assert refused(S.decompress_bytes(S.zlib, gzip_bytes))
    assert refused(S.decompress_bytes(S.gzip, zlib_bytes))

    work = fn["temp-dir!"](G("compression-lib")).one()
    try:
        source = fn.path_join(work, G("source")).one()
        packed = fn.path_join(work, G("packed.gz")).one()
        restored = fn.path_join(work, G("restored")).one()
        assert fn["write-bytes!"](source, data) == [True]
        assert fn["compress-file!"](S.gzip, 6, source, packed) == [True]
        assert list(fn.decompress_bytes(S.gzip, fn["read-bytes!"](packed).one()).one()) == list(data)
        assert fn["decompress-file!"](S.gzip, packed, restored) == [True]
        assert list(fn["read-bytes!"](restored).one()) == list(data)
        assert fn["compress-file!"](S.zlib, 0, source, source) == [True]
        assert fn["decompress-file!"](S.zlib, source, source) == [True]
        assert list(fn["read-bytes!"](source).one()) == list(data)
        assert fn["write-bytes!"](packed, (31, 139)) == [True]
        assert refused(S["decompress-file!"](S.gzip, packed, restored))
        assert list(fn["read-bytes!"](restored).one()) == list(data)

        fixtures = G("examples/ch08-data/08-03-the-shipped-libraries/_fixtures")
        fixture = fn.path_join(fixtures, G("compression-data.zip")).one()
        entries = fn["archive-entries!"](fixture).one()
        assert len(entries) == 4
        assert (entries[0][1], entries[0][2]) == (0, G("./"))
        assert list(fn["archive-read!"](fixture, 2).one()) == list(data)
        assert list(fn["archive-read!"](fixture, 3).one()) == []
        assert refused(S["archive-read!"](fixture, 0))
        assert refused(S["archive-read!"](fixture, 4))
        extracted = fn.path_join(work, G("extracted")).one()
        assert fn["archive-extract!"](fixture, extracted) == [True]
        assert list(fn["read-bytes!"](fn.path_join(extracted, G("sub/bytes.bin")).one()).one()) == list(data)
        assert list(fn["read-bytes!"](fn.path_join(extracted, G("empty")).one()).one()) == []
        assert refused(S["archive-extract!"](fixture, extracted))
        assert list(fn["read-bytes!"](fn.path_join(extracted, G("sub/bytes.bin")).one()).one()) == list(data)
        assert fn["compress-file!"](S.gzip, 6, fixture, packed) == [True]
        assert fn["archive-entries!"](packed) == [entries]
        assert list(fn["archive-read!"](packed, 2).one()) == list(data)
        second = fn.path_join(work, G("second")).one()
        assert fn["archive-extract!"](packed, second) == [True]
        assert list(fn["read-bytes!"](fn.path_join(second, G("sub/bytes.bin")).one()).one()) == list(data)

        assert fn["archive-entries!"](fn.path_join(fixtures, G("compression-unicode.zip")).one()).one()[0][2] == G("café/π🙂")
        assert fn["archive-entries!"](fn.path_join(fixtures, G("compression-legacy.zip")).one()).one()[0][2] == G("café")
        assert fn["archive-entries!"](fn.path_join(fixtures, G("compression-unicode-extra.zip")).one()).one()[0][2] == G("café/π🙂")

        unsafe = fn.path_join(fixtures, G("compression-unsafe.zip")).one()
        refused_path = fn.path_join(work, G("refused")).one()
        assert list(fn["archive-read!"](unsafe, 0).one()) == [42]
        assert refused(S["archive-extract!"](unsafe, refused_path))
        assert fn.dir_exists(refused_path) == [False]
        assert fn.file_exists(fn.path_join(work, G("escape")).one()) == [False]
    finally:
        assert fn["delete-tree!"](work) == [True]


#: MEASURED: all 54 claims cover envelopes, publication, extraction and ZIP names.
#: The example pays 229506; both notations import File before Compression.
#: [measured 2026-09-13: 204351 inferences, minimum of three fresh serial processes;
#: command=python extensions/python/tools/twin_coverage.py --measure --rounds 3
#: examples/ch08-data/08-03-the-shipped-libraries/41-compression_lib.metta;
#: fixture=lib_compression with engine/lib QLF artifacts purged; commit=7b42d5ee5cecb82709617b7ed08dfa2c1441f268].
#: RE-PINNED 2026-09-14, 204351 to 226243 (+21892), String now derives nine
#: text recipes through MeTTa equations, with one function parameter for
#: padding and complete validation before empty construction; all import
#: consumers are measured after the provider change [measured 2026-09-14: min-
#: of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=118b805aedbee6de22be4f6131d97c3d6b9156de].
#: RE-PINNED 2026-09-21, 226243 to 513946 (+287703), the sixty libraries
#: derived in MeTTa landed with merge 97763e7fa eight hours after the previous
#: pin 55d451b67, so every example importing one now pays a MeTTa derivation
#: where it paid a Prolog body instead, which the 2026-09-14 ruling accepts
#: explicitly as the price of a library that survives the engine swap [measured
#: 2026-09-21: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=6e09cb25d5495c2db3283166e6ce4e07eefecfb2].
#: RE-PINNED 2026-09-24, 513946 to 538861 (+24915), placed on the full-
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
BUDGET = 538861
