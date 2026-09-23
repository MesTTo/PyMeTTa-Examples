"""Purpose: exchange TCP bytes and IPv6 datagrams through owned File handles.

Guarantees: the same 53 claims as 40-socket_lib.metta.
[tested: python extensions/python/tools/twin_coverage.py examples/ch08-data/08-03-the-shipped-libraries/40-socket_lib.metta; commit=781ee98e188c23ea7ef9298636d6e5e6c7fdc727].
Owns resources: finally closes remaining loopback handles if an assertion fails;
with-socket owns each scoped acquisition through its answer stream.
"""

from metta import G, S, V, arrow, lib, typed
from metta._errors.errors import MettaError


def twin(m):
    """Share File ownership, query actual endpoints and preserve UDP packets."""
    m += lib.file
    m += lib.socket
    m.add(typed(S.socket_answers, arrow(S.Number, S.Number)),
          S["="](S.socket_answers(V.handle), S.superpose((1, 2))))
    fn = m.fn
    close = fn["file-close!"]
    owned = []

    def refused(call):
        """Read an operation refusal at the public evaluation boundary."""
        try:
            list(m.eval(call))
        except MettaError:
            return True
        return False

    assert fn.path_join(G("one"), G("two")) == [G("one/two")]
    assert list(fn["socket-wait!"]((), S.infinite).one()) == []
    listener = fn["tcp-listen!"](S.endpoint(S.ipv4, G("127.0.0.1"), 0), 8).one()
    owned.append(listener)
    try:
        address = fn.socket_endpoint(listener, S.local).one()
        assert fn.socket_kind(listener) == [S.listener]
        assert address[1] == S.ipv4
        assert address[2] == G("127.0.0.1")
        assert address[3] > 0
        assert list(fn["socket-wait!"]((listener,), 0).one()) == []
        client = fn["tcp-connect!"](address).one()
        owned.append(client)
        assert list(fn["socket-wait!"]((listener,), S.infinite).one()) == [listener]
        accepted = fn["tcp-accept!"](listener).one()
        owned.append(accepted)
        assert fn.socket_kind(client) == [S.tcp]
        assert fn.socket_kind(accepted) == [S.tcp]
        assert fn.socket_endpoint(accepted, S.local) == [address]
        assert fn.socket_endpoint(client, S.peer) == [address]
        assert fn.socket_endpoint(accepted, S.peer) == fn.socket_endpoint(client, S.local)

        assert fn["file-write-bytes!"](client, (0, 128, 255, 10)) == [True]
        assert list(fn["socket-wait!"]((accepted, accepted), S.infinite).one()) == [accepted, accepted]
        assert list(fn["file-read-bytes!"](accepted, 2).one()) == [0, 128]
        assert list(fn["file-read-bytes!"](accepted, 2).one()) == [255, 10]
        assert fn["socket-shutdown!"](client, S.write) == [True]
        assert list(fn["file-read-bytes!"](accepted).one()) == []
        assert fn["file-write-bytes!"](accepted, (42,)) == [True]
        assert list(fn["file-read-bytes!"](client, 1).one()) == [42]
        assert fn["socket-shutdown!"](accepted, S.both) == [True]
        assert close(listener) == [True]
        owned.remove(listener)
        assert close(client) == [True]
        owned.remove(client)
        assert close(accepted) == [True]
        owned.remove(accepted)
        assert close(accepted) == [True]

        udp = fn["udp-bind!"](S.endpoint(S.ipv6, G("::1"), 0)).one()
        owned.append(udp)
        udp_address = fn.socket_endpoint(udp, S.local).one()
        assert fn.socket_kind(udp) == [S.udp]
        assert udp_address[1] == S.ipv6
        assert udp_address[2] == G("::1")
        assert list(fn["socket-wait!"]((udp,), 0).one()) == []
        assert fn["udp-send!"](udp, udp_address, (0, 255, 1)) == [True]
        assert fn["udp-send!"](udp, udp_address, ()) == [True]
        assert list(fn["socket-wait!"]((udp,), S.infinite).one()) == [udp]
        assert fn["udp-receive!"](udp) == [S.datagram(udp_address, (0, 255, 1))]
        assert fn["udp-receive!"](udp) == [S.datagram(udp_address, ())]
        assert refused(S["udp-send!"](udp, udp_address, (256,)))
        assert list(fn["socket-wait!"]((udp,), 0).one()) == []
        assert refused(S["udp-send!"](udp, S.endpoint(S.ipv4, G("127.0.0.1"), 1), ()))
        assert refused(S.socket_endpoint(udp, S.peer))
        assert refused(S["tcp-accept!"](udp))
        assert refused(S["socket-shutdown!"](udp, S.write))
        assert close(udp) == [True]
        owned.remove(udp)
        assert refused(S.socket_kind(udp))
        assert refused(S["udp-bind!"](S.endpoint(S.unknown, G("127.0.0.1"), 0)))
        assert refused(S["udp-bind!"](S.endpoint(S.ipv4, G(""), 0)))
        assert refused(S["udp-bind!"](S.endpoint(S.ipv4, G("127.0.0.1"), 65536)))
        assert refused(S["tcp-connect!"](S.endpoint(S.ipv4, G("127.0.0.1"), 0)))
        assert refused(S["tcp-listen!"](S.endpoint(S.ipv4, G("127.0.0.1"), 0), -1))
        assert refused(S["socket-wait!"]((), -1))
        assert refused(S.transaction(S["udp-bind!"](S.endpoint(S.ipv4, G("127.0.0.1"), 0))))

        acquire = S["udp-bind!"](S.endpoint(S.ipv4, G("127.0.0.1"), 0))
        assert list(fn["with-socket"](acquire, S.socket_answers)) == [1, 2]
        assert fn["with-socket"](acquire, S.socket_kind) == [S.udp]
        closed = fn["with-socket"](acquire, S["lambda"](V.handle, V.handle)).one()
        assert refused(S.socket_kind(closed))
    finally:
        for handle in owned:
            close(handle).one()


#: MEASURED: all 53 claims cross TCP, IPv6 UDP and owned socket scopes.
#: The example pays 189530; both notations import File before Socket.
#: [measured 2026-09-13: 178533 inferences, minimum of three fresh serial processes;
#: command=python extensions/python/tools/twin_coverage.py --measure --rounds 3
#: examples/ch08-data/08-03-the-shipped-libraries/40-socket_lib.metta;
#: fixture=lib_socket with engine/lib QLF artifacts purged; commit=781ee98e188c23ea7ef9298636d6e5e6c7fdc727].
#: RE-PINNED 2026-09-13, 178533 to 178547 (+14), File privately exports its
#: existing staged publisher with callback qualification; Compression shares
#: that ownership and publication protocol [measured 2026-09-13: min-of-3
#: serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=7b42d5ee5cecb82709617b7ed08dfa2c1441f268].
#: RE-PINNED 2026-09-13, 178547 to 179079 (+532), File exports its staged
#: publisher to Compression; the shared native builder accepts the private
#: archive provider recipe. All consumers are remeasured after those dependency
#: changes [measured 2026-09-13: min-of-3 serial fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=7b42d5ee5cecb82709617b7ed08dfa2c1441f268].
#: RE-PINNED 2026-09-14, 179079 to 200969 (+21890), String now derives nine
#: text recipes through MeTTa equations, with one function parameter for
#: padding and complete validation before empty construction; all import
#: consumers are measured after the provider change [measured 2026-09-14: min-
#: of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=118b805aedbee6de22be4f6131d97c3d6b9156de].
#: RE-PINNED 2026-09-21, 200969 to 486335 (+285366), the sixty libraries
#: derived in MeTTa landed with merge 97763e7fa eight hours after the previous
#: pin 55d451b67, so every example importing one now pays a MeTTa derivation
#: where it paid a Prolog body instead, which the 2026-09-14 ruling accepts
#: explicitly as the price of a library that survives the engine swap [measured
#: 2026-09-21: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=6e09cb25d5495c2db3283166e6ce4e07eefecfb2].
#: RE-PINNED 2026-09-24, 486335 to 511014 (+24679), placed on the full-
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
#: RE-PINNED 2026-09-24, 511014 to 310272 (-200742), 0a81c782f loads a
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
BUDGET = 310272
