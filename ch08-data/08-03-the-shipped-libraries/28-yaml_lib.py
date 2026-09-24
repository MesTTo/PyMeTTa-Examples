"""Purpose: YAML documents as values, in the shape lib_json already uses.

A mapping is a space, so `opened` is `metta.space(answers.one())` exactly as the
JSON twin's is, and the queries over a YAML document are the queries over a JSON
one. Text is `G("...")`, and the file scope takes a FUNCTION, so the read and
write pair is one `@m.define`.

Guarantees: the same claims as 28-yaml_lib.metta
[tested: python extensions/python/tools/twin_coverage.py examples/ch08-data/08-03-the-shipped-libraries/28-yaml_lib.metta; commit=672e5be181839a8301ba70bc6ead69678f3735bd].
Open Obligations:
  To Do: None
  Hacks: None
  Future Enhancements: None.
"""

import metta
from metta import G, S, ground, lib
from metta._errors.errors import MettaError

#: The document every query below reads, written once so the twin and its example
#: hold the same text. It is `ground()` data rather than a bare string, because a
#: bare string is a NAME and this is text.
CONF = ground("""name: petta
version: 1.5
tags:
  - prolog
  - metta
limits:
  depth: 3
  strict: true
  note:
  nothing: ~
""")


def twin(m):
    """Decode a document, query it, encode it back, and read and write a file."""
    m += lib.yaml

    def refused(call):
        """Whether evaluating a call raises, which is what if-error reads."""
        try:
            list(m.eval(call))
        except MettaError:
            return True
        return False

    def opened(answers):
        """The handle for the space yaml-decode or dict-space answered by name."""
        return metta.space(answers.one())

    decode, encode = m.fn.yaml_decode, m.fn.yaml_encode
    at, value_of, keys = m.fn.json_at, m.fn.get_value, m.fn.get_keys

    # A mapping becomes a SPACE of (Key Value) atoms, which is lib_json's own
    # shape, so the queries over a YAML document are the queries over a JSON one.
    conf = opened(decode(CONF))
    assert sorted(keys(conf), key=str) == [S.limits, S.name, S.tags, S.version]
    assert value_of(conf, S.name) == [G("petta")]
    assert value_of(conf, S.version) == [1.5]
    assert list(value_of(conf, S.tags).one()) == [G("prolog"), G("metta")]
    assert at(conf, (S.tags, 0)) == [G("prolog")]
    assert at(conf, (S.limits, S.depth)) == [3]
    assert at(conf, (S.limits, S.strict)) == [True]
    # A key written with NO value decodes as the empty string rather than null: the
    # host's reader does not distinguish `note:` from `note: ""`, so a document
    # that means null writes `~` or `null`. An absent key has no answer at all.
    assert at(conf, (S.limits, S.note)) == [G("")]
    assert at(conf, (S.limits, S.nothing)) == [S.Null]
    assert list(value_of(conf, S.missing)) == []

    # A sequence becomes an expression and a scalar document stays a scalar.
    assert list(decode(G("- 1\n- 2\n")).one()) == [1, 2]
    assert decode(G("just text\n")) == [G("just text")]
    assert decode(G("42\n")) == [42]
    assert decode(G("true\n")) == [True]
    assert decode(G("null\n")) == [S.Null]
    # An empty document is Null, which is what YAML says it holds.
    assert decode(G("")) == [S.Null]
    # A quoted scalar keeps its type: this is the string "no", not a boolean,
    # because YAML 1.2's core schema has only true and false.
    assert at(opened(decode(G("k: no\n"))), (S.k,)) == [G("no")]

    # Encoding inverts decoding, and the text it writes is one document ending in
    # a newline.
    assert encode(S.yaml_decode(G("a: 1\nb:\n  - x\n"))) == [G("a: 1\nb:\n- x\n")]
    assert encode((1, 2, S.Null, True)) == [G("- 1\n- 2\n- null\n- true\n")]
    assert encode(G("text")) == [G("text\n")]
    assert encode(7) == [G("7\n")]
    assert encode(S.Null) == [G("null\n")]
    # A mapping to encode is a space of pairs, which dict-space builds without any
    # text in between.
    assert encode(S.dict_space(((S.a, 1), (S.b, G("two"))))) == [G("a: 1\nb: two\n")]
    assert at(opened(decode(S.yaml_encode(S.dict_space(((S.k, 1),))))), (S.k,)) == [1]

    # The file doors are one line each over lib_file: the read is the decode of a
    # whole file and the write is an atomic replacement, so a reader never sees
    # half a document. The scope is lib_file's own, and it takes a function.
    @m.define
    def write_and_read(directory):
        # (= (write-and-read $dir) (let $path (path-join $dir "conf.yaml") ...))
        path = S.path_join(directory, "conf.yaml")
        _written = S["yaml-write!"](path, S.dict_space(((S.host, "localhost"), (S.port, 8080))))
        text = S["read-file!"](path)
        return (text, S.json_at(S["yaml-read!"](path), (S.port,)))

    written = list(m.fn["with-temp-dir"](G("yaml-lib"), S.write_and_read).one())
    assert written == [G("host: localhost\nport: 8080\n"), 8080]

    # The four refusals. A stream with more than one document is refused naming
    # the marker, because the host's reader takes one and answering the first
    # would answer less than the text says.
    assert refused(S.yaml_decode(G("a: 1\n---\nb: 2\n")))
    # A tag the host has no value for is refused naming the tag, where it would
    # otherwise answer an opaque term no MeTTa form can read.
    assert refused(S.yaml_decode(G("k: !foo 1\n")))
    # Malformed text is refused with the line the host stopped on, and a duplicate
    # key is refused rather than silently keeping one of the two.
    assert refused(S.yaml_decode(G("a: [1,\n")))
    assert refused(S.yaml_decode(G("dup: 1\ndup: 2\n")))
    assert list(m.eval(S.yaml_decode(7))) == [
        S.Error(S.yaml_decode(7), S.BadArgType(1, S.String, S.Number)),
    ]
    # A space that is not a mapping is refused naming the atom that is not a pair.
    not_a_map = metta.space(S.notamap)
    not_a_map += S.a(1, 2)
    assert refused(S.yaml_encode(not_a_map))
    # A symbol encodes as the string it spells, so an expression of symbols is a
    # sequence of strings rather than a refusal.
    assert encode((S.one, S.two)) == [G("- one\n- two\n")]


#: MEASURED on this branch rather than inherited: this twin is new, so there is
#: no earlier pin to move. The 32 claims cover both heads, the two derived file
#: doors, the mapping-as-space shape lib_json owns and the five refusals; the
#: twin costs less than the example, whose `let` chain in the scope function is one
#: compiled body here
#: [measured 2026-09-12: 179414 inferences against the example's 182395, minimum
#: of three serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --measure --rounds 3
#: examples/ch08-data/08-03-the-shipped-libraries/28-yaml_lib.metta;
#: fixture=lib_yaml at its functional commit, artifacts purged before the run;
#: commit=672e5be181839a8301ba70bc6ead69678f3735bd].
#: RE-PINNED 2026-09-12, 179414 to 179426 (+12), File transfers newly owned
#: streams through adopt_file_stream/2 and claims a close atomically; HTTP also
#: verifies transaction refusal before server lifecycle effects [measured
#: 2026-09-12: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=0f22b69cfca5c108e4126bdd56ab9bb2e493744d].
#: RE-PINNED 2026-09-13, 179426 to 179444 (+18), File exports its shared stream
#: borrowing and rollback operations; failed Socket and HTTP publication now
#: withdraws the registered stream before closing it [measured 2026-09-13: min-
#: of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=781ee98e188c23ea7ef9298636d6e5e6c7fdc727].
#: RE-PINNED 2026-09-13, 179444 to 179457 (+13), File privately exports its
#: existing staged publisher with callback qualification; Compression shares
#: that ownership and publication protocol [measured 2026-09-13: min-of-3
#: serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=7b42d5ee5cecb82709617b7ed08dfa2c1441f268].
#: RE-PINNED 2026-09-13, 179457 to 179988 (+531), File exports its staged
#: publisher to Compression; the shared native builder accepts the private
#: archive provider recipe. All consumers are remeasured after those dependency
#: changes [measured 2026-09-13: min-of-3 serial fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=7b42d5ee5cecb82709617b7ed08dfa2c1441f268].
#: RE-PINNED 2026-09-14, 179988 to 201983 (+21995), String now derives nine
#: text recipes through MeTTa equations, with one function parameter for
#: padding and complete validation before empty construction; all import
#: consumers are measured after the provider change [measured 2026-09-14: min-
#: of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=118b805aedbee6de22be4f6131d97c3d6b9156de].
#: RE-PINNED 2026-09-21, 201983 to 510171 (+308188), the sixty libraries
#: derived in MeTTa landed with merge 97763e7fa eight hours after the previous
#: pin 55d451b67, so every example importing one now pays a MeTTa derivation
#: where it paid a Prolog body instead, which the 2026-09-14 ruling accepts
#: explicitly as the price of a library that survives the engine swap [measured
#: 2026-09-21: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=6e09cb25d5495c2db3283166e6ce4e07eefecfb2].
#: RE-PINNED 2026-09-24, 510171 to 546930 (+36759), placed on the full-
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
#: RE-PINNED 2026-09-24, 546930 to 327902 (-219028), 0a81c782f loads a
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
#: RE-PINNED 2026-09-24, 327902 to 329206 (+1304), both: 2126ab6 installs the
#: library's native half through lib/_support/native_install.pl, loaded once
#: per process, and 0847c3d4c with 984eabe23 decides on its first read each
#: platform capability the twin reads, in a flag under a mutex; a792976 loads
#: process, socket and HTTP's libraries through the census and refuses per
#: call, which moves process_lib by 44 and socket_lib by -603 [measured
#: 2026-09-24: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=d832d20e8edfdad28ad52815757ba9e685ad2de3].
#: RE-PINNED 2026-09-24, 329206 to 340747 (+11541), +11,519 at ae1cc8936, where
#: a registration batch of thirteen names or more walks the visible predicate
#: table at two inferences a predicate that asking per name spent inside one C
#: call, and a batch above forty tests each predicate with a dict at one
#: inference fewer than the AVL; +15 at 850d2a660, which reads a native space's
#: lengths in ascending arity rather than functor-hash order; +6 at b5eb39acd,
#: whose three new engine exports the registration walk above twelve names
#: reads at two inferences each [measured 2026-09-24: min-of-3 serial fresh
#: processes at HEAD in battery 118 holding the committed tree alone
#: (BATTERY_KEEP='', 11:56); each step read with its parent and child in turn
#: in battery 115 (10:42 to 11:18), 117 (11:01 to 12:10) or 120 (12:04 to
#: 12:13) from committed trees or this job's patched copies of them, none from
#: a working tree; 850d2a660's and 0f6d29ba6's split from provider-carry's own
#: pairs, aaeea643a's on the ladder before 10:05; command=python
#: extensions/python/tools/twin_coverage.py --measure --rounds 3;
#: commit=c7d7244fbe6d32d024ca8c61b336008e98b156ef].
#: RE-PINNED 2026-09-24, 340747 to 340398 (-349), d4a365c16 holds the support
#: graph's visited set and the reference refresh's space sets in SWI tries
#: instead of library(nb_set): a membership check is one foreign call where
#: nb_set probed in Prolog, four inferences a step past a taken slot, from a
#: slot a library space's path-bearing name decided, and a walk over a node or
#: two pays a few inferences more for the trie's setup (-3); gate-perf's
#: d781eab8f carries an exact removal's selected head from the code that
#: selected it, so a withdrawal copies its equation once: 23 inferences fewer
#: for each equation removal the twin adopts and 4 for each it selects (-368);
#: the packages job's 90be572a9 and 4003462fe register Prolog through one
#: engine service: +22 for each library the twin imports (ten new engine
#: predicates and two user imports in the registration walk at two inferences
#: each, less the retired loaded_extension_file/2), and 146 inferences for a
#: Prolog file's origin or 220 for a text's SHA-256 on a twin that registers
#: Prolog (+22); each step read serially on its own committed tree, from gate-
#: perf's pin at c7d7244fb, and the fixed tree 4ff69551e reads what 4003462fe
#: does [measured 2026-09-24: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=4ff69551e0e226442cf7257b96af858adda957a4].
BUDGET = 340398

#: DIVERGED 2026-09-12, the example holds 1 atom the twin does not (1 =) and
#: the twin holds 1 atom the example does not (1 =): the scope function is four
#: Python statements, which compile to four nested one-binding let* forms where
#: the example writes three nested let forms; the bindings, the effects and the
#: answer are the same [measured 2026-09-12: the two stored-atom surpluses, one
#: fresh process per side; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=672e5be181839a8301ba70bc6ead69678f3735bd].
#: DIVERGED 2026-09-21, the example holds 1 atom the twin does not (1 =) and
#: the twin holds 1 atom the example does not (1 =): the sixty libraries
#: derived in MeTTa landed with merge 97763e7fa eight hours after the previous
#: pin 55d451b67, so every example importing one now pays a MeTTa derivation
#: where it paid a Prolog body instead, which the 2026-09-14 ruling accepts
#: explicitly as the price of a library that survives the engine swap [measured
#: 2026-09-21: the two stored-atom surpluses, one fresh process per side;
#: command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=6e09cb25d5495c2db3283166e6ce4e07eefecfb2].
DIVERGENCE = "8b4d30c744227b013138e72eb94d49d7763894e339225c370fe00460a902df9f"
