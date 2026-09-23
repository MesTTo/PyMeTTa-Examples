"""Purpose: route local HTTP requests through equations and owned byte streams.

Guarantees: the same 41 claims as 38-http_lib.metta.
[tested: python extensions/python/tools/twin_coverage.py examples/ch08-data/08-03-the-shipped-libraries/38-http_lib.metta; commit=0f22b69cfca5c108e4126bdd56ab9bb2e493744d].
Owns resources: finally stops the named loopback server; scoped resources close
through their library owners.
"""

from metta import TRUE, G, S, V, arrow, lib, typed
from metta._errors.errors import MettaError


def twin(m):
    """Use one request shape for methods, byte bodies, headers and streaming."""
    m += lib.http
    m += lib.encoding
    m.add(typed(S.library_http, arrow(S.Expression, S.Expression)),
          typed(S.read_http, arrow(S.Expression, S.Expression)),
          typed(S.ping_http, arrow(S.Expression, S.Expression)))
    routes = (
        (G("/"), S.http_response(200, ((G("X-Reply"), G("one")),
                                    (G("X-Reply"), G("two"))), (0, 128, 255))),
        (G("/echo"), S.http_response(201,
            ((G("Content-Type"), G("text/plain; charset=UTF-8")),
             (G("X-Method"), S.repr(V.method)), (G("X-Target"), V.target)), V.body)),
        (G("/absent"), S.http_response(404, (), ())),
        (G("/redirect"), S.http_response(307, ((G("Location"), G("/")),), ())),
        (G("/empty"), S.empty()),
        (G("/broken"), S.broken_response(7)),
    )
    m.add(*(S["="](S.library_http(S.http_request(V.method, path, V.target,
                                                  V.fields, V.body)), response)
            for path, response in routes))
    m.add(S["="](S.read_http(S.http_response(V.status, V.fields, V.handle)),
                  S["file-read-bytes!"](V.handle)),
          S["="](S.ping_http(V.server),
                  S["http-request!"](S.get, S.http_server_url(V.server), ())))

    def refused(call):
        """Read a native refusal through the evaluation boundary."""
        try:
            list(m.eval(call))
        except MettaError:
            return True
        return False

    request = m.fn["http-request!"]
    stop = m.fn["http-server-stop!"]
    close = m.fn["file-close!"]
    field = m.fn.http_header

    assert list(m.fn.http_methods().one()) == [S.delete, S.get, S.head, S.post,
                                              S.put, S.patch, S.options]
    server = m.fn["http-server-start!"](G("127.0.0.1"), 0, S.library_http,
                                          (S.workers(2),)).one()
    try:
        url = m.fn.http_server_url(server).one()
        echo = m.fn.string_join(G(""), (url, G("echo?q=one%20two"))).one()
        response = request(S.get, url, (S.timeout(5),)).one()
        assert response[1] == 200
        assert list(response[3]) == [0, 128, 255]
        assert field(response[2], G("Content-Type")) == [G("application/octet-stream")]
        assert field(response[2], G("CONTENT-LENGTH")) == [3]
        assert list(field(response[2], G("x-reply"))) == [G("one"), G("two")]
        assert list(field(response[2], G("missing"))) == []

        head = request(S.head, url, ()).one()
        assert head[1] == 200
        assert list(head[3]) == []
        assert field(head[2], G("content-length")) == [3]
        posted = request(S.post, echo,
            (S.body(G("text/plain; charset=UTF-8"), S.utf8_encode(G("aπ🙂"))),
             S.header(G("X-Input"), G("one")), S.header(G("X-Input"), G("two")))).one()
        assert posted[1] == 201
        assert m.fn.utf8_decode(posted[3]) == [G("aπ🙂")]
        assert field(posted[2], G("x-method")) == [G("post")]
        assert field(posted[2], G("x-target")) == [G("/echo?q=one%20two")]
        assert field(request(S.put, echo, ()).one()[2], G("x-method")) == [G("put")]
        assert field(request(S.patch, echo, ()).one()[2], G("x-method")) == [G("patch")]
        assert field(request(S.delete, echo, ()).one()[2], G("x-method")) == [G("delete")]
        assert field(request(S.options, echo, ()).one()[2], G("x-method")) == [G("options")]

        def at(path):
            """Append an example path through the same String operation."""
            return m.fn.string_join(G(""), (url, path)).one()

        assert request(S.get, at(G("absent")), ()).one()[1] == 404
        assert request(S.get, at(G("empty")), ()).one()[1] == 404
        assert request(S.get, at(G("broken")), ()).one()[1] == 500
        assert request(S.get, at(G("redirect")), ()).one()[1] == 307
        assert list(request(S.get, at(G("redirect")), (S.redirect(TRUE),)).one()[3]) == [0, 128, 255]

        stream = m.fn["http-open!"](S.get, url, ()).one()
        handle = stream[3]
        try:
            assert list(m.fn["file-read-bytes!"](handle, 2).one()) == [0, 128]
            assert list(m.fn["file-read-bytes!"](handle).one()) == [255]
        finally:
            assert close(handle) == [True]
        assert close(handle) == [True]
        assert list(m.fn["with-http"](S.get, url, (), S.read_http).one()) == [0, 128, 255]
        assert m.fn["with-http-server"](G("127.0.0.1"), 0, S.library_http,
                                       (S.workers(1),), S.ping_http).one()[1] == 200

        assert refused(S["http-request!"](S.invented, url, ()))
        assert refused(S["http-request!"](S.get, G("file:///etc/passwd"), ()))
        assert refused(S["http-request!"](S.get, url, (S.header(G("bad:name"), G("x")),)))
        assert refused(S["http-request!"](S.get, url, (S.header(G("X-Input"), G("a\nb")),)))
        assert refused(S["http-request!"](S.post, url,
                                          (S.body(G("application/octet-stream"), (256,)),)))
        assert refused(S["http-request!"](S.get, url, (S.timeout(1), S.timeout(2))))
        assert refused(S["http-request!"](S.get, url, (S.header(G("Content-Length"), G("3")),)))
        assert refused(S["http-server-start!"](G("127.0.0.1"), 0, S.library_http, (S.workers(0),)))
        assert refused(S.transaction(S["http-server-start!"](G("127.0.0.1"), 0, S.library_http, ())))
        assert refused(S.transaction(S["http-server-stop!"](server)))
    finally:
        assert stop(server) == [True]
    assert stop(server) == [True]


#: MEASURED: all 41 claims use loopback requests and native byte streams.
#: The example pays 328540; each shutdown owns its native acknowledgement mailbox.
#: [measured 2026-09-13: 323580 inferences, minimum of three fresh serial processes;
#: command=python extensions/python/tools/twin_coverage.py --measure --rounds 3
#: examples/ch08-data/08-03-the-shipped-libraries/38-http_lib.metta;
#: fixture=lib_http with engine/lib QLF artifacts purged; commit=0f22b69cfca5c108e4126bdd56ab9bb2e493744d].
#: RE-PINNED 2026-09-13, 323580 to 323706 (+126), File exports its shared
#: stream borrowing and rollback operations; failed Socket and HTTP publication
#: now withdraws the registered stream before closing it [measured 2026-09-13:
#: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=781ee98e188c23ea7ef9298636d6e5e6c7fdc727].
#: RE-PINNED 2026-09-13, 323706 to 323720 (+14), File privately exports its
#: existing staged publisher with callback qualification; Compression shares
#: that ownership and publication protocol [measured 2026-09-13: min-of-3
#: serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=7b42d5ee5cecb82709617b7ed08dfa2c1441f268].
#: RE-PINNED 2026-09-13, 323720 to 324253 (+533), File exports its staged
#: publisher to Compression; the shared native builder accepts the private
#: archive provider recipe. All consumers are remeasured after those dependency
#: changes [measured 2026-09-13: min-of-3 serial fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=7b42d5ee5cecb82709617b7ed08dfa2c1441f268].
#: RE-PINNED 2026-09-14, 324253 to 346140 (+21887), String now derives nine
#: text recipes through MeTTa equations, with one function parameter for
#: padding and complete validation before empty construction; all import
#: consumers are measured after the provider change [measured 2026-09-14: min-
#: of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=118b805aedbee6de22be4f6131d97c3d6b9156de].
#: RE-PINNED 2026-09-14, 346140 to 369064 (+22924), Encoding hex and UUID
#: byte/name formulas are MeTTa recipes over shared strict boundaries;
#: malformed codec classification preserves all unrelated exceptions [measured
#: 2026-09-14: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=8fe20f1bdcde1af8b3e1753c545924f978246dba].
#: RE-PINNED 2026-09-21, 369064 to 723756 (+354692), the sixty libraries
#: derived in MeTTa landed with merge 97763e7fa eight hours after the previous
#: pin 55d451b67, so every example importing one now pays a MeTTa derivation
#: where it paid a Prolog body instead, which the 2026-09-14 ruling accepts
#: explicitly as the price of a library that survives the engine swap [measured
#: 2026-09-21: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=6e09cb25d5495c2db3283166e6ce4e07eefecfb2].
#: RE-PINNED 2026-09-24, 723756 to 766462 (+42706), placed on the full-
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
#: CONVERTED to an empirical envelope 2026-09-24 under 'full-
#: lane/323/workers=32/file-search-cache-time=9223372036854775807/before-boot':
#: the re-pinned point 766462 held in 17 of 20 full-lane observations on the
#: tree it was pinned on, which read 766462 in 17, 767401 in 3, so under the
#: lane's 32-worker schedule the count takes more than one value and a point
#: budget with a 4-inference band would fail some lane runs; the envelope
#: records those 20 observations exactly. Which scheduling-dependent path adds
#: the 939 is not isolated [measured 2026-09-24: 20 full-lane observations;
#: command=python extensions/python/tools/twin_coverage.py --observe --rounds
#: 20; commit=WORKTREE].
#: POOLED 2026-09-24 under 'full-lane/323/workers=32/file-search-cache-
#: time=9223372036854775807/before-boot', 766462..767401 over 20 to
#: 766461..767401 over 21: the final whole-lane run read 766461, one inference
#: below the twenty rounds' minimum, on HEAD 49e2b250d with the engine diff
#: empty; the two commits after the observed 6a7ac233d change CHANGELOG.md, a
#: comment in tools/check.sh, the MORK seat's CHANGELOG.md and bench.sh and the
#: Node seat pointer, none on a path this twin runs, and the seat is the same
#: 7d995f762; a whole-lane run under this protocol on this runtime is an
#: observation, so the envelope is the union of the extrema and the sum of the
#: counts. Which scheduling-dependent path saves the one inference is not
#: isolated [measured 2026-09-24: 1 whole-lane run, sh
#: extensions/python/check.sh twins in battery 5; command=python
#: extensions/python/tools/twin_coverage.py; commit=WORKTREE].
#: POOLED 2026-09-24 under 'full-lane/323/workers=32/file-search-cache-
#: time=9223372036854775807/before-boot', 766461..767401 over 21 to
#: 766461..767401 over 28: the 7 whole-lane runs of this runtime the envelope
#: did not yet hold read the pin run's first lane 766462; the pin run's second
#: lane 766462; the pin run's third lane 766462; the purged lane on 49e2b250d
#: 766462; the purged lane on 26de4ddcf 766462; the purged lane after a8487162
#: 766462; the purged lane after 878b8bd9 766462. They are the pin run's own
#: lanes on the 6a7ac233d snapshot and the final lanes on 49e2b250d and
#: 26de4ddcf, whose commits touch no path this twin runs, and each reads every
#: deterministic twin exactly as a battery whose governed QLF set was compiled
#: in place does, so none carries a moved artifact's cost; the lane whose
#: battery carried a lib_import.qlf compiled in wt-merge is left out. A whole-
#: lane run under this protocol on this runtime is an observation, so the
#: envelope is the union of the extrema and the sum of the counts [measured
#: 2026-09-24: 7 whole-lane runs, sh extensions/python/check.sh twins in
#: battery 5; command=python extensions/python/tools/twin_coverage.py;
#: commit=WORKTREE].
#: RE-OBSERVED 2026-09-24 under 'full-lane/323/workers=32/file-search-cache-
#: time=9223372036854775807/before-boot', 766461..767401 to 535057..536000 over
#: 20 observations: the tree moved under this envelope: 0a81c782f loads a
#: library's Prolog half through the boot's claim, so the half and every
#: governed half it loads read the .qlf the claim's hermetic child wrote where
#: they had compiled from source in every process, and it starts that child
#: from the running home's own swipl, which the host check accepts, where the
#: stock swipl the lane's PATH finds had been refused since f2822e2ae; the
#: about 10.3k per Prolog-half load that a 2026-09-24 paragraph above charges
#: to f2822e2ae's boot host check was never the check's own cost: from
#: f2822e2ae on the check refused every compile child the stock swipl ran, so
#: no child wrote an artifact and every governed half a half loads compiled
#: from source in every process; an empirical envelope is a claim about one
#: scheduler's protocol on one tree, so these observations are this tree's own
#: and are not pooled with the earlier ones [measured 2026-09-24: 20 full-lane
#: observations; command=python extensions/python/tools/twin_coverage.py
#: --observe --rounds 20; commit=0a81c782fd6ba00984c36e58e228f73bca810dee].
#: RE-OBSERVED 2026-09-24 under 'full-lane/323/workers=32/file-search-cache-
#: time=9223372036854775807/before-boot', 535057..536000 to 543250..543251 over
#: 20 observations: the tree moved under this envelope: 0847c3d4c decides the
#: http capability, seven libraries, on its first read (+2,160), 984eabe23
#: keeps the verdict in a flag under a mutex (+40), lib 2126ab6 loads
#: native_install.pl (+629), and lib a792976 loads lib_http's platform
#: libraries through the census and refuses per call (+2,182), the four
#: measured by reverting each and together moving the twin by 8,194; an
#: empirical envelope is a claim about one scheduler's protocol on one tree, so
#: these observations are this tree's own and are not pooled with the earlier
#: ones [measured 2026-09-24: 20 full-lane observations, two runs of ten on one
#: battery tree; command=python extensions/python/tools/twin_coverage.py
#: --observe --rounds 10; commit=d832d20e8edfdad28ad52815757ba9e685ad2de3].
BUDGET = {
    "minimum": 543250,
    "maximum": 543251,
    "observations": 20,
    "protocol": "full-lane/323/workers=32/file-search-cache-time=9223372036854775807/before-boot"
}
