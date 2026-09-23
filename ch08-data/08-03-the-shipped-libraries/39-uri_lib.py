"""Purpose: compose URI components, resolve references and encode query relations.

Guarantees: the same 55 claims as 39-uri_lib.metta.
[tested: python extensions/python/tools/twin_coverage.py examples/ch08-data/08-03-the-shipped-libraries/39-uri_lib.metta; commit=24b96f8ec8468bc97cec35e1d71ce689ede7fdcf].
"""

from metta import G, S, lib
from metta._errors.errors import MettaError


def twin(m):
    """Preserve URI structure and move Unicode through percent-encoded pairs."""
    m += lib.uri
    m += lib.pairs
    m += lib.encoding

    def refused(call):
        """Read a native refusal through the evaluation boundary."""
        try:
            list(m.eval(call))
        except MettaError:
            return True
        return False

    parts, build = m.fn.uri_parts, m.fn.uri_build
    normalize, resolve = m.fn.uri_normalize, m.fn.uri_resolve
    encode, decode = m.fn.uri_encode, m.fn.uri_decode
    parse_query, build_query = m.fn.uri_query_parse, m.fn.uri_query_build

    assert parts(G("")) == [((G("path"), G("")),)]
    assert parts(G("?#")) == [((G("path"), G("")), (G("query"), G("")), (G("fragment"), G("")))]
    assert parts(G("https://User:Pass@[::1]:0012/a%2Fb?q=1#F")) == [(
        (G("scheme"), G("https")), (G("authority"), G("User:Pass@[::1]:0012")),
        (G("path"), G("/a%2Fb")), (G("query"), G("q=1")), (G("fragment"), G("F")),
    )]
    assert parts(G("urn:Example:ABC")) == [((G("scheme"), G("urn")), (G("path"), G("Example:ABC")))]
    assert build(()) == [G("")]
    assert build(((G("query"), G("")), (G("fragment"), G("")))) == [G("?#")]
    assert build(((G("path"), G("/x")), (G("authority"), G("host:")), (G("scheme"), G("http")))) == [G("http://host:/x")]
    assert build(S.uri_parts(G("a:b?x#"))) == [G("a:b?x#")]

    assert normalize(G("HTTP://User:Pass@HOST/a/%2e%2e/b?x=%7e#F")) == [G("http://User:Pass@host/b?x=~#F")]
    assert normalize(G("urn:Example:ABC")) == [G("urn:Example:ABC")]
    assert normalize(G("http://HOST/%ff/%c0%af/%2f?#")) == [G("http://host/%FF/%C0%AF/%2F?#")]
    assert normalize(G("../a/./b")) == [G("../a/./b")]
    assert normalize(G("foo:/a/..//b")) == [G("foo:/.//b")]

    assert resolve(G("g"), G("http://a")) == [G("http://a/g")]
    assert resolve(G("../g"), G("http://a/b/c/d;p?q")) == [G("http://a/b/g")]
    assert resolve(G("?"), G("http://a/b?old#f")) == [G("http://a/b?")]
    assert resolve(G("#"), G("http://a/b?old#f")) == [G("http://a/b?old#")]
    assert resolve(G(""), G("http://a/b?old#f")) == [G("http://a/b?old")]
    assert resolve(G("//other/x"), G("http://a/b")) == [G("http://other/x")]
    assert resolve(G("http:g"), G("http://a/b")) == [G("http:g")]
    assert resolve(G("urn:Example:ABC"), G("http://a/b")) == [G("urn:Example:ABC")]
    assert resolve(G("g?y/../x"), G("http://a/b/c/d;p?q")) == [G("http://a/b/c/g?y/../x")]
    assert resolve(G("%2e%2e/g"), G("http://a/b/")) == [G("http://a/b/%2e%2e/g")]

    assert tuple(m.fn.uri_contexts().one()) == (S.path, S.segment, S.query_value, S.fragment)
    assert encode(S.path, G("a b/c?d")) == [G("a%20b/c%3Fd")]
    assert encode(S.segment, G("a b/c?d")) == [G("a%20b%2Fc%3Fd")]
    assert encode(S.query_value, G("a+b&c=d")) == [G("a%2Bb%26c%3Dd")]
    assert encode(S.fragment, G("a+b&c=d/x?y")) == [G("a+b&c=d/x?y")]
    assert encode(S.segment, G("π🙂")) == [G("%CF%80%F0%9F%99%82")]
    assert encode(S.segment, S.utf8_decode((97, 0, 98))) == [G("a%00b")]
    assert decode(G("%CF%80%F0%9F%99%82")) == [G("π🙂")]
    assert decode(G("%252F+a")) == [G("%2F+a")]
    assert tuple(m.fn.utf8_encode(S.uri_decode(G("%00x"))).one()) == (0, 120)

    assert parse_query(S.uri, G("a+b=c+d&&a=2&bare&empty=&")) == [(
        (G("a+b"), G("c+d")), (G("a"), G("2")), (G("bare"), G("")), (G("empty"), G("")),
    )]
    assert parse_query(S.form, G("a+b=c+d&&a=2&bare&empty=&")) == [(
        (G("a b"), G("c d")), (G("a"), G("2")), (G("bare"), G("")), (G("empty"), G("")),
    )]
    assert parse_query(S.uri, G("a=1;b=2&=x")) == [((G("a"), G("1;b=2")), (G(""), G("x")))]
    assert tuple(parse_query(S.form, G("")).one()) == ()
    pairs = ((G("a b"), G("c+d")), (G("a b"), G("")), (G(""), G("π🙂")))
    assert build_query(S.uri, pairs) == [G("a%20b=c%2Bd&a%20b=&=%CF%80%F0%9F%99%82")]
    assert build_query(S.form, pairs) == [G("a+b=c%2Bd&a+b=&=%CF%80%F0%9F%99%82")]
    assert build_query(S.form, ()) == [G("")]
    assert m.fn.pairs_lookup(S.uri_query_parse(S.uri, G("a=1&a=2&b=3")), G("a")) == [G("1"), G("2")]
    assert build_query(S.form, S.uri_query_parse(S.form, G("%2B=%00&x=a/b?c"))) == [G("%2B=%00&x=a/b?c")]

    assert refused(S.uri_parts(G("a b")))
    assert refused(S.uri_parts(S.utf8_decode((97, 0, 98))))
    assert refused(S.uri_parts(G("x%ZZ")))
    assert refused(S.uri_build(((G("path"), G("a")), (G("authority"), G("host")))))
    assert refused(S.uri_build(((G("path"), G("a")), (G("path"), G("b")))))
    assert refused(S.uri_build(((G("missing"), G("x")),)))
    assert refused(S.uri_resolve(G("x"), G("relative")))
    assert refused(S.uri_encode(S.missing, G("x")))
    assert refused(S.uri_decode(G("%")))
    assert refused(S.uri_decode(G("%FF")))
    assert refused(S.uri_decode(G("%C0%AF")))
    assert refused(S.uri_query_parse(S.form, G("x=%ED%A0%80")))
    assert refused(S.uri_query_build(S.missing, ()))


#: MEASURED: all 55 claims, including encoded components, RFC resolution,
#: strict decoding, query relations and refusals. The example pays 125852.
#: [measured 2026-09-13: 118602 inferences, minimum of three fresh serial processes;
#: command=python extensions/python/tools/twin_coverage.py --measure --rounds 3
#: examples/ch08-data/08-03-the-shipped-libraries/39-uri_lib.metta;
#: fixture=lib_uri with engine/lib QLF artifacts purged;
#: commit=24b96f8ec8468bc97cec35e1d71ce689ede7fdcf].
#: RE-PINNED 2026-09-13, 118602 to 180593 (+61991), Combinatorics, Functional,
#: Pairs and Sets now derive collection operations through MeTTa equations,
#: segments and folds. This example imports the changed provider directly or
#: through its library dependencies [measured 2026-09-13: min-of-3 serial fresh
#: processes; command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=6471fbad35eced5ed6440ebf2c25a053b20221f3].
#: RE-PINNED 2026-09-13, 180593 to 181936 (+1343), The validated range
#: continuation now lives in the private support file rather than appearing as
#: a public library head. The import adds its measured loading cost without
#: changing the continuation body [measured 2026-09-13: min-of-3 serial fresh
#: processes; command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=6471fbad35eced5ed6440ebf2c25a053b20221f3].
#: RE-PINNED 2026-09-13, 181936 to 185656 (+3720), Math and Statistics derive
#: their recipes from MeTTa equations; Statistics consolidates finite laws and
#: adds reflective claims. Their collection dependencies share the proper
#: finite expression boundary in lib/_support/collections_data.pl [measured
#: 2026-09-13: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=6fa571d1b7059b610f73e9feed657711414251e5].
#: RE-PINNED 2026-09-13, 185656 to 185678 (+22), Vector, Math and the shared
#: collection boundary declare their native effects. The engine reads late
#: provider declarations and retains definition analysis for computed function
#: heads [measured 2026-09-13: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=1d0b78a359f58de49f2f98bed50a6480d56cd5f6].
#: RE-PINNED 2026-09-14, 185678 to 181677 (-4001), Functional applies finished
#: callback arguments through reduce; Statistics derives exact coefficient rows
#: and Combinatorics retires its native probability provider [measured
#: 2026-09-14: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=e1be99ea1c08f70444c1c35cada441e089777906].
#: RE-PINNED 2026-09-14, 181677 to 262887 (+81210), Encoding hex and UUID
#: byte/name formulas are MeTTa recipes over shared strict boundaries;
#: malformed codec classification preserves all unrelated exceptions [measured
#: 2026-09-14: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=8fe20f1bdcde1af8b3e1753c545924f978246dba].
#: RE-PINNED 2026-09-21, 262887 to 393740 (+130853), the sixty libraries
#: derived in MeTTa landed with merge 97763e7fa eight hours after the previous
#: pin 55d451b67, so every example importing one now pays a MeTTa derivation
#: where it paid a Prolog body instead, which the 2026-09-14 ruling accepts
#: explicitly as the price of a library that survives the engine swap [measured
#: 2026-09-21: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=6e09cb25d5495c2db3283166e6ce4e07eefecfb2].
#: RE-PINNED 2026-09-24, 393740 to 444092 (+50352), placed on the full-
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
BUDGET = 444092
