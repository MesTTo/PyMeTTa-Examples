"""Purpose: UUID generations, namespaces, complete names and byte round trips.

Guarantees: the same 49 claims as 33-uuid_lib.metta.
[tested: python extensions/python/tools/twin_coverage.py examples/ch08-data/08-03-the-shipped-libraries/33-uuid_lib.metta; commit=8fe20f1bdcde1af8b3e1753c545924f978246dba].
"""

from metta import G, S, V, lib
from metta._errors.errors import MettaError


def twin(m):
    """Generate identifiers, preserve names and bytes, and check malformed input."""
    m += lib.crypto
    m += lib.uuid
    m += lib.encoding
    m += lib.string

    def refused(call):
        """Read a native or assertion refusal through the evaluation boundary."""
        try:
            list(m.eval(call))
        except MettaError:
            return True
        return False

    version, variant, valid = m.fn.uuid_version, m.fn.uuid_variant, m.fn.uuid_is
    name, timestamp = m.fn.uuid_name, m.fn.uuid_timestamp
    to_bytes, of_bytes = m.fn.uuid_bytes, m.fn.uuid_of_bytes

    assert len(m.fn.crypto_random_bytes(16).one()) == 16
    assert version(S["uuid-random!"]()) == [4]
    assert variant(S["uuid-random!"]()) == [S.rfc]
    assert valid(S["uuid-random!"]()) == [True]
    assert m.fn["uuid-random!"]().one() != m.fn["uuid-random!"]().one()
    assert version(S["uuid-time!"]()) == [1]
    assert variant(S["uuid-time!"]()) == [S.rfc]
    assert timestamp(S["uuid-time!"]()).one() > 0

    assert list(m.fn.uuid_namespaces().one()) == [S.dns, S.url, S.oid, S.x500]
    assert name(3, S.dns, G("example.com")) == [G("9073926b-929f-31c2-abc9-fad77ae3e8eb")]
    assert name(5, S.dns, G("example.com")) == [G("cfbff0d1-9375-5685-968c-48ce8b15ae17")]
    assert name(5, G("6ba7b810-9dad-11d1-80b4-00c04fd430c8"), G("example.com")).one() == name(
        5, S.dns, G("example.com"),
    ).one()
    assert name(3, S.url, G("http://example.com")) == [G("d632b50c-7913-3137-ae9a-2d93f56e70d5")]
    assert name(5, S.oid, G("1.3.6.1.4.1")) == [G("106dd502-8b3e-50db-80ed-1134f5c18eae")]
    assert name(5, S.x500, G("cn=Test")) == [G("1a09ab7e-5f76-53b6-b866-3b565a53dc51")]
    assert name(5, S.dns, G("")) == [G("4ebd0208-8328-5d69-8c44-ec50939c0967")]
    assert name(5, S.dns, G("é")) == [G("ebfe0af8-3997-5ade-b634-ba92cf69f557")]
    assert name(3, S.dns, G("漢")) == [G("1f9d873c-79c5-37f3-a181-6bab16c1f1c9")]
    assert name(5, S.dns, S.string_from_codes((97, 0, 98))) == [
        G("0a63f66b-e02f-5d2d-9fd4-aad819cf5352"),
    ]

    assert m.fn.uuid_nil() == [G("00000000-0000-0000-0000-000000000000")]
    assert valid(S.uuid_nil()) == [True]
    assert version(S.uuid_nil()) == [0]
    assert variant(S.uuid_nil()) == [S.ncs]
    assert variant(G("00000000-0000-0000-c000-000000000000")) == [S.microsoft]
    assert variant(G("ffffffff-ffff-ffff-ffff-ffffffffffff")) == [S.future]
    assert timestamp(G("13814000-1dd2-11b2-8000-000000000000")) == [0.0]
    assert list(timestamp(S["uuid-random!"]())) == []
    assert list(timestamp(S.uuid_nil())) == []

    assert valid(G("CFBFF0D1-9375-5685-968C-48CE8B15AE17")) == [True]
    assert m.fn.hex_encode(S.uuid_bytes(G("cfbff0d1-9375-5685-968c-48ce8b15ae17"))) == [
        G("cfbff0d193755685968c48ce8b15ae17"),
    ]
    assert of_bytes(S.uuid_bytes(G("CFBFF0D1-9375-5685-968C-48CE8B15AE17"))) == [
        G("cfbff0d1-9375-5685-968c-48ce8b15ae17"),
    ]
    assert list(to_bytes(S.uuid_nil()).one()) == [0] * 16
    assert of_bytes(S.hex_decode(G("ffffffffffffffffffffffffffffffff"))) == [
        G("ffffffff-ffff-ffff-ffff-ffffffffffff"),
    ]

    assert valid(G("------------------------------------")) == [False]
    assert valid(S.string_replace(S.uuid_nil(), G("-"), S.string_from_codes((0,)))) == [False]
    assert valid(G("cfbff0d193755685968c48ce8b15ae17")) == [False]
    assert valid(G("zfbff0d1-9375-5685-968c-48ce8b15ae17")) == [False]
    assert valid(3) == [False]
    assert refused(S.uuid_version(G("broken")))
    assert refused(S.uuid_timestamp(G("broken")))
    assert refused(S.uuid_of_bytes((1, 2)))
    assert refused(S.uuid_of_bytes((0,) * 15 + (256,)))
    assert refused(S.uuid_name(2, S.dns, G("name")))
    assert refused(S.uuid_name(5, S.missing, G("name")))
    assert refused(S.uuid_name(5, G("broken"), G("name")))

    row = m.match(S["="](S.uuid_version(V.id), V.body)).one()
    inspector = m.eval(S["|->"]((row.id,), row.body))[0]
    assert m.eval((inspector, S.uuid_nil())) == [0]
    row = m.match(S["="](S.uuid_name(V.version, V.namespace, V.name), V.body)).one()
    derive = m.eval(S["|->"]((row.version, row.namespace, row.name), row.body))[0]
    assert m.eval((derive, 5, S.dns, G("example.com"))) == [G("cfbff0d1-9375-5685-968c-48ce8b15ae17")]
    assert list(version(S.superpose((
        G("00000000-0000-0000-0000-000000000000"), G("ffffffff-ffff-ffff-ffff-ffffffffffff"),
    )))) == [0, 15]
    assert name(3, S.dns, S.string_from_codes((97, 0, 98))) == [
        G("002a0ada-f547-375a-bab5-896a11d1927e"),
    ]


#: MEASURED: all 45 claims, including full names, literal UUID separators and
#: the explicit crypto import that demonstrates secure bytes beside identifiers.
#: At this original measurement, field inspection used native digit validation.
#: [measured 2026-09-12: 188846 inferences against the example's 190880, minimum
#: of three fresh serial processes; command=python
#: extensions/python/tools/twin_coverage.py --measure --rounds 3
#: examples/ch08-data/08-03-the-shipped-libraries/33-uuid_lib.metta;
#: fixture=lib_uuid at its functional commit with engine/lib QLF artifacts purged;
#: commit=d5de00cc183b4b395b552f3aae7fca87752ef38c].
#: RE-PINNED 2026-09-13, 188846 to 189377 (+531), File exports its staged
#: publisher to Compression; the shared native builder accepts the private
#: archive provider recipe. All consumers are remeasured after those dependency
#: changes [measured 2026-09-13: min-of-3 serial fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=7b42d5ee5cecb82709617b7ed08dfa2c1441f268].
#: RE-PINNED 2026-09-14, 189377 to 211352 (+21975), String now derives nine
#: text recipes through MeTTa equations, with one function parameter for
#: padding and complete validation before empty construction; all import
#: consumers are measured after the provider change [measured 2026-09-14: min-
#: of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=118b805aedbee6de22be4f6131d97c3d6b9156de].
#: RE-PINNED 2026-09-14, 211352 to 1291086 (+1079734), Encoding hex and UUID
#: byte/name formulas are MeTTa recipes over shared strict boundaries;
#: malformed codec classification preserves all unrelated exceptions [measured
#: 2026-09-14: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=8fe20f1bdcde1af8b3e1753c545924f978246dba].
#: RE-PINNED 2026-09-21, 1291086 to 1398748 (+107662), the sixty libraries
#: derived in MeTTa landed with merge 97763e7fa eight hours after the previous
#: pin 55d451b67, so every example importing one now pays a MeTTa derivation
#: where it paid a Prolog body instead, which the 2026-09-14 ruling accepts
#: explicitly as the price of a library that survives the engine swap [measured
#: 2026-09-21: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=6e09cb25d5495c2db3283166e6ce4e07eefecfb2].
#: RE-PINNED 2026-09-24, 1398748 to 1452741 (+53993), placed on the full-
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
#: RE-PINNED 2026-09-24, 1452741 to 1371681 (-81060), 0a81c782f loads a
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
#: RE-PINNED 2026-09-24, 1371681 to 1372452 (+771), both: 2126ab6 installs the
#: library's native half through lib/_support/native_install.pl, loaded once
#: per process, and 0847c3d4c with 984eabe23 decides on its first read each
#: platform capability the twin reads, in a flag under a mutex; a792976 loads
#: process, socket and HTTP's libraries through the census and refuses per
#: call, which moves process_lib by 44 and socket_lib by -603 [measured
#: 2026-09-24: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=d832d20e8edfdad28ad52815757ba9e685ad2de3].
#: RE-PINNED 2026-09-24, 1372452 to 1395667 (+23215), +23,199 at ae1cc8936,
#: where a registration batch of thirteen names or more walks the visible
#: predicate table at two inferences a predicate that asking per name spent
#: inside one C call, and a batch above forty tests each predicate with a dict
#: at one inference fewer than the AVL; +12 at b5eb39acd, whose three new
#: engine exports the registration walk above twelve names reads at two
#: inferences each [measured 2026-09-24: min-of-3 serial fresh processes at
#: HEAD in battery 118 holding the committed tree alone (BATTERY_KEEP='',
#: 11:56); each step read with its parent and child in turn in battery 115
#: (10:42 to 11:18), 117 (11:01 to 12:10) or 120 (12:04 to 12:13) from
#: committed trees or this job's patched copies of them, none from a working
#: tree; 850d2a660's and 0f6d29ba6's split from provider-carry's own pairs,
#: aaeea643a's on the ladder before 10:05; command=python
#: extensions/python/tools/twin_coverage.py --measure --rounds 3;
#: commit=c7d7244fbe6d32d024ca8c61b336008e98b156ef].
#: RE-PINNED 2026-09-24, 1395667 to 1395178 (-489), d4a365c16 holds the support
#: graph's visited set and the reference refresh's space sets in SWI tries
#: instead of library(nb_set): a membership check is one foreign call where
#: nb_set probed in Prolog, four inferences a step past a taken slot, from a
#: slot a library space's path-bearing name decided, and a walk over a node or
#: two pays a few inferences more for the trie's setup (-4); gate-perf's
#: d781eab8f carries an exact removal's selected head from the code that
#: selected it, so a withdrawal copies its equation once: 23 inferences fewer
#: for each equation removal the twin adopts and 4 for each it selects (-529);
#: the packages job's 90be572a9 and 4003462fe register Prolog through one
#: engine service: +22 for each library the twin imports (ten new engine
#: predicates and two user imports in the registration walk at two inferences
#: each, less the retired loaded_extension_file/2), and 146 inferences for a
#: Prolog file's origin or 220 for a text's SHA-256 on a twin that registers
#: Prolog (+44); each step read serially on its own committed tree, from gate-
#: perf's pin at c7d7244fb, and the fixed tree 4ff69551e reads what 4003462fe
#: does [measured 2026-09-24: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=4ff69551e0e226442cf7257b96af858adda957a4].
#: RE-PINNED 2026-09-24, 1395178 to 1395483 (+305), +301 at the change this re-
#: pin lands with, which publishes a from row by itself when rows are all a
#: space owes: its 36 predicates visible to filereader's registration walk cost
#: a batch above twelve names 72 inferences, each restricted space's core about
#: 28 a predicate, and every whole publication and face event its ledger's
#: bookkeeping [measured 2026-09-24: the twins lane alone on 8d651070d with the
#: change before this one and with this change too, one after the other in
#: battery 117's one path, every component at its pin; command=sh
#: tools/check.sh twins (twin_coverage.py inside tools/bounded.sh);
#: commit=e4b7448d1f1bd98733f1b04c3906aaa42f35ef1a].
#: RE-PINNED 2026-09-24, 1395483 to 1395475 (-8), the host switch of
#: swipl-patched from .2 to .5, the native host of build 9's 36
#: patches, measured .2 against .5 through two environment shims of one shape
#: on one tree. Its channel here is library/prolog_wrap.qlf: .2's, written
#: 2026-09-17 a minute after swi-wrapper-roundtrip-merges-closures changed
#: prolog_wrap.pl, compiles I < Arity in body_closure_args/6 as a call to
#: system:(<)/2, and .5's, recompiled by the build's QLF step, evaluates it
#: inline, so each argument that predicate walks costs one inference fewer.
#: That channel is measured on engine-bench's translate and evaluate cases,
#: whose port profiles on the two hosts differ in system:(<)/2 alone; on this
#: twin it is read from the move's shape, a multiple of 8 to within the lane's
#: deterministic allowance of 4, not profiled [measured 2026-09-24: min-of-3
#: serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=622e425d40c126681c04c7f7f81d92618ab83d0d].
#: RE-PINNED 2026-09-25, 1395475 to 1395519 (+44), the py-* doors change makes
#: more predicates visible from filereader, and
#: filereader:existing_predicate_arities/2 walks every predicate visible there
#: at two inferences each whenever a source registering more than twelve names
#: loads: on one tree the change's new engine predicates alone, defined with
#: their two boot uses taken out, make eight more visible and move this twin by
#: 16 for each such load, and the whole change by 20, ten more at its loads
#: (i-arity-walk-all-predicates) [measured 2026-09-25T02:52:20+10:00: min-of-3
#: serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-25, 1395519 to 1392383 (-3136), the host evaluation door
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
#: more than twelve names [measured 2026-09-25T06:47:46+10:00: min-of-3 serial
#: fresh processes; command=python extensions/python/tools/twin_coverage.py
#: --repin].
#: RE-PINNED 2026-09-25, 1392383 to 1392399 (+16), Runtime.reclaim(), the
#: reclamation barrier metta_py_reclaim/1, adds five predicates to user, and
#: existing_predicate_arities/2 walks every user predicate about twice per
#: large load (i-arity-walk-all-predicates) [measured
#: 2026-09-25T11:25:25+10:00: one full twins lane before this commit and one
#: with it, the two read on one battery path at the landing's HEAD;
#: command=python extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-25, 1392399 to 1392403 (+4), both specializer doors
#: prepare a specialization's predicate with
#: spaces:metta_prepare_function_predicate/3 before asserting its clauses
#: [measured 2026-09-25T11:29:10+10:00: one full twins lane before this commit
#: and one with it, the two read on one battery path at the landing's HEAD;
#: command=python extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-25, 1392403 to 1392411 (+8), retiring a library importer
#: derives the arity row again from any backing head a library home still
#: registers, journalled to the load that owns it [measured
#: 2026-09-25T11:33:06+10:00: one full twins lane before this commit and one
#: with it, the two read on one battery path at the landing's HEAD;
#: command=python extensions/python/tools/twin_coverage.py].
BUDGET = 1392411
