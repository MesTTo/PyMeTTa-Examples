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
#: RE-PINNED 2026-09-24, 340398 to 340784 (+386), +384 at the change this re-
#: pin lands with, which publishes a from row by itself when rows are all a
#: space owes: its 36 predicates visible to filereader's registration walk cost
#: a batch above twelve names 72 inferences, each restricted space's core about
#: 28 a predicate, and every whole publication and face event its ledger's
#: bookkeeping [measured 2026-09-24: the twins lane alone on 8d651070d with the
#: change before this one and with this change too, one after the other in
#: battery 117's one path, every component at its pin; command=sh
#: tools/check.sh twins (twin_coverage.py inside tools/bounded.sh);
#: commit=e4b7448d1f1bd98733f1b04c3906aaa42f35ef1a].
#: RE-PINNED 2026-09-25, 340784 to 340807 (+23), the py-* doors change makes
#: more predicates visible from filereader, and
#: filereader:existing_predicate_arities/2 walks every predicate visible there
#: at two inferences each whenever a source registering more than twelve names
#: loads: on one tree the change's new engine predicates alone, defined with
#: their two boot uses taken out, move this twin by 16 for each such load and
#: the whole change by 20, each give or take one or two inferences that move
#: with where the new names land in SWI's tables and that SWI's profiler, which
#: lists no system predicate, does not place (i-arity-walk-all-predicates)
#: [measured 2026-09-25T02:56:44+10:00: min-of-3 serial fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-25, 340807 to 340794 (-13), the registration refusal kind
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
#: the base [measured 2026-09-25T06:29:05+10:00: min-of-3 serial fresh
#: processes; command=python extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-25, 340794 to 338407 (-2387), the host evaluation door
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
#: more than twelve names [measured 2026-09-25T06:47:32+10:00: min-of-3 serial
#: fresh processes; command=python extensions/python/tools/twin_coverage.py
#: --repin].
#: RE-PINNED 2026-09-25, 338407 to 338418 (+11), Runtime.reclaim(), the
#: reclamation barrier metta_py_reclaim/1, adds five predicates to user, and
#: existing_predicate_arities/2 walks every user predicate about twice per
#: large load (i-arity-walk-all-predicates) [measured
#: 2026-09-25T11:25:25+10:00: one full twins lane before this commit and one
#: with it, the two read on one battery path at the landing's HEAD;
#: command=python extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-25, 338418 to 338420 (+2), both specializer doors prepare
#: a specialization's predicate with spaces:metta_prepare_function_predicate/3
#: before asserting its clauses [measured 2026-09-25T11:29:10+10:00: one full
#: twins lane before this commit and one with it, the two read on one battery
#: path at the landing's HEAD; command=python
#: extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-25, 338420 to 338424 (+4), retiring a library importer
#: derives the arity row again from any backing head a library home still
#: registers, journalled to the load that owns it [measured
#: 2026-09-25T11:33:06+10:00: one full twins lane before this commit and one
#: with it, the two read on one battery path at the landing's HEAD;
#: command=python extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-25, 338424 to 338433 (+9), lib/lib_string/lib_string.qlf
#: is now compiled by a child of its own whichever half's load reaches it first
#: (engine/qlf_boot.pl, qlf_compile_argument/0), and that compile keeps the :-
#: non_terminal directive for word_tokens//1 that a compile inside lib_csv's
#: child, where the warm-up's glob order put it, left out, since SWI's
#: non_terminal_decl/2 writes it only for a head no earlier load flagged; the
#: loader runs the directive, ten inferences, in every process that loads
#: lib_string; the move also holds the -1 this twin read against its pin
#: without the change, inside its allowance, where the reference loader's
#: change to when a background load is published as finished left it
#: (superproject 2fea1b292) [measured 2026-09-25T15:19:48+10:00: the twin read
#: 338424 with engine/metta/reference_loading.pl as e806af707 has it and 338423
#: as 2fea1b292 has it, min of three serial fresh processes each from a cold
#: set, one after the other in one battery] [measured
#: 2026-09-25T15:55:47+10:00: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-25, 338433 to 338471 (+38), every force of a waiting
#: function names the module it is made from, through fun_home_in/3, and a
#: write forces only its own space [measured 2026-09-25T16:54:32+10:00: one
#: full twins lane before this commit and one with it, the two read on one
#: battery path at the landing's HEAD; command=python
#: extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-25, 338471 to 338486 (+15), lambdas are named by their
#: content and a copy restores its source's rows as a program [measured
#: 2026-09-25T17:00:15+10:00: one full twins lane before this commit and one
#: with it, the two read on one battery path at the landing's HEAD;
#: command=python extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-25, 338486 to 338546 (+60), engine/source_loading.pl's
#: load-error clause moved from the thread_local user:thread_message_hook/3 to
#: the global user:message_hook/3, so every thread and engine now runs the
#: check the main thread always ran: one inference per message while no load is
#: open there (clause(watching, true, _) fails) and two inside one
#: (load_failure/2 rejects the silent kind); the Python seat prints a twin's
#: library-load messages inside engines, where no clause ran before, and the
#: original's side does not move [measured 2026-09-25T18:42:31+10:00: min-of-3
#: serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-25, 338546 to 338548 (+2), a sweep of a module's generated
#: predicates retires the records describing each swept predicate, and a
#: release the rest of the module's [measured 2026-09-25T23:29:52+10:00: one
#: full twins lane before this commit and one with it, the two read on one
#: battery path at the landing's HEAD; command=python
#: extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-26, 338548 to 338566 (+18), engine/metta/control.pl's
#: partial/3 to partial/11, the clauses that let a Prolog meta-predicate call a
#: partial function value, are nine more predicates visible from filereader,
#: and filereader:existing_predicate_arities/2's batch walk, which a load
#: registering more than twelve names runs, pays two inferences for each: 18 a
#: batch, the original and the twin alike, and nine inert facts of those
#: arities move it the same [measured 2026-09-26T01:30:53+10:00: min-of-3
#: serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-26, 338566 to 338586 (+20), the reference faces of a
#: strongly connected component of from rows are computed together by label-
#: setting, which makes ten more predicates visible from metta_engine, and a
#: control adding only ten unused predicates to metta_engine reads the same, so
#: none of the move is face work; existing_predicate_arities/2 walks every
#: visible predicate at two inferences for each batch of more than twelve names
#: a load registers (i-arity-walk-all-predicates) [measured
#: 2026-09-26T03:08:57+10:00: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-26, 338586 to 338591 (+5), engine/source_loading.pl hears
#: a load's printed failures through a user:thread_message_hook/3 clause each
#: load asserts on the thread or engine running it and erases, where
#: c83b6bb1e's clause of the global user:message_hook/3 ran for every message:
#: 6 loads each call prolog_current_frame/1 once more (+6); 1 registration walk
#: over a batch of more than twelve names
#: (filereader:existing_predicate_arities/2) enumerates one more predicate than
#: the trunk's (+2), since SWI's autoImport() links prolog_current_frame/1 into
#: every module on metta_source_loading's import chain, user included, at the
#: boot's first load, where the trunk links it into user only at its first
#: library import; 3 messages this twin's count reads, printed outside a load,
#: no longer run the loader's clause (-3) [measured 2026-09-26T06:55:21+10:00:
#: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-26, 338591 to 338596 (+5), this twin reads 338592 at the
#: base and 338596 with the change (+4): the change adds
#: metta_reference_enroll/1 and metta_reference_source_bound/5 to the
#: metta_engine module (engine/metta/reference_refresh.pl and
#: reference_sources.pl), and on a tree that defines them and never calls them
#: this twin reads 338596 (+4), which only a walk over SWI's predicate or atom
#: tables can move, by visiting more entries or visiting them in another order;
#: it read 338592 against its pin 338591 at the base, so +1 of the distance is
#: the trunk's own and is not attributed here [measured
#: 2026-09-26T11:18:06+10:00: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-26, 338596 to 338607 (+11), Registering a source's names
#: answers each name's Prolog arities in standard order, one msort/2 per
#: registration that adds names, where they came in the procedure table's order
#: and set the order of the arity/2 facts [measured 2026-09-26T12:30:16+10:00:
#: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-26, 338607 to 338668 (+61), A Prolog function registered
#: without its arity is claimed from its lowest arity's file through
#: aggregate_all(min(Arity, File), ...), where the scan took the first arity
#: the procedure table answered [measured 2026-09-26T13:03:26+10:00: min-of-3
#: serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-26, 338668 to 338674 (+6), The engine module defines three
#: predicates more, builtin_seat_prefixes/1, builtin_implementation_gap/2,
#: validate_builtin_implementation_gaps/2 and builtin_surface_predicate/3 in
#: and builtin_surface_predicate_name/1 out, and a program pays for each
#: predicate visible from the engine wherever it walks them:
#: existing_predicate_arities/2 two inferences a predicate for each load that
#: registers more than twelve names, and a restricted space twenty-seven a
#: predicate when it publishes the engine's core; three facts appended to
#: engine/metta/registration.pl on 07b75d16e move 14-lib_roman_pair_helpers,
#: 02-restricted_spaces and 37-statistics_lib by the same +6, +87 and +30
#: [measured 2026-09-26T14:29:36+10:00: min-of-3 serial fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-27, 338674 to 338857 (+183), the host switch to swipl-
#: patched.7 and the seat changes it needs: +26 the host switch to swipl-
#: patched.7, which delivers the heartbeat inside loops, so a held engine ticks
#: and the held goals read its ticks from the raw counter, 9 inferences a tick,
#: and whose three new system predicates ('$heartbeat'/0, '$file_hash'/2,
#: '$qlf_source_changed'/2) filereader's walk of every visible predicate
#: (existing_predicate_arities/2) meets, 2 inferences each; +12 the seat's
#: interrupt poll crossing only on its arming thread, whose hook costs 3
#: inferences a tick more and whose start goal runs on every new thread and
#: engine; +6 the poll's tick record updated in place, 3 inferences a tick more
#: than replacing it; +139 the held goals reading Used through metta_py_work/2,
#: which leaves a held engine's own ticks out and reads the tick term inside
#: its opening edge, 5 inferences a held reading [measured
#: 2026-09-27T03:41:21+10:00: one full twins lane of the trunk and one with
#: this landing, wt-merge battery 1, the trunk on swipl-patched.6 and every
#: part on .7, each through a same-shape host shim; command=python
#: extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-27, 338857 to 338868 (+11), a force of a waiting function
#: takes the typing policy and the specializer's lock before translation:
#: spaces:metta_ensure_compiled/2 stabilises the policy and takes the
#: specializer's mutex around the translation once per force, and the
#: translation's own per-pair stabilisation re-enters through
#: with_typing_policy_stable/1's first clause [measured
#: 2026-09-27T09:56:55+10:00: one full twins lane before this commit and one
#: with it, each read in one battery of the landing's HEAD after a QLF purge
#: and one warm-up; command=python extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-27, 338868 to 338928 (+60), the constructive negation's
#: engine additions, each counted in this twin's own run: 1 registration walk
#: over more than twelve names (filereader:existing_predicate_arities/2), each
#: now reading 31 more predicates at 2 inferences (+62); -2 of clause-indexing
#: layout [measured 2026-09-27T18:31:56+10:00: one full twins lane with this
#: landing, in a battery of its tree at 775d3cf35, beside one of the base in a
#: battery of 775d3cf35 from 2026-09-27T18:40:06+10:00, which reads the old
#: pin; command=python extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-28, 338928 to 338927 (-1), -1 at tsm-licence's notices
#: reader as its block lookahead amended it: engine/host_notices.pl, which
#: every boot loads, opens a component block only where its Component field
#: directly follows the line of 78 '=', the calls not traced; read on swipl-
#: patched.8, the count above on .7, which no longer runs [measured
#: 2026-09-28T12:31:49+10:00: full twins lanes in wt-merge's battery 1 on
#: swipl-patched.8 at this boundary, engine/host_notices.pl as amended against
#: the day before's as first written; command=sh tools/check.sh twins].
#: RE-PINNED 2026-09-27, 338927 to 338820 (-107), +1 at the host switch to
#: swipl-patched.8, whose swi-heartbeat-inferences-charged-to-the-program
#: leaves the interrupt poll's own inferences out of every count, so a window
#: the seat's calibrated poll correction read 1 to 3 low on .7 reads exactly;
#: -107 at interrupts B's seat change, which drops the poll's boot calibration,
#: its tick charges and its tick record: a held reading through metta_py_work/2
#: brackets 3 inferences where it bracketed 6, a registration walk over more
#: than twelve names meets 6 fewer seat predicates (12 or 14 fewer), and a
#: thread the twin joins credits it 11 where it credited 16 [measured
#: 2026-09-27T20:07:01+10:00: full twins lanes in wt-merge's battery 1, tsm-
#: licence's series and its engine reader on swipl-patched.7, the series on
#: swipl-patched.8, and the stack through janus-contract B on swipl-patched.8
#: twice; command=sh tools/check.sh twins]. With step 4's notices reader as
#: amended the counts read -1 before the step and -2 after it, so the step
#: moves the twin -107 where it moved it -106 [measured
#: 2026-09-28T12:34:38+10:00: full twins lanes in wt-merge's battery 1 on
#: swipl-patched.8 at this boundary, engine/host_notices.pl as amended against
#: the day before's as first written; command=sh tools/check.sh twins].
#: RE-PINNED 2026-09-27, 338820 to 338822 (+2), +1 at janus-contract A, whose
#: seat loader adds metta_extension_require_patches/3 and the format/3 it
#: imports to the engine module a registration walk enumerates, and reads the
#: seat's requirement into its own module where host_patch/2 used to stand
#: there, so a walk over more than twelve names meets one more predicate at 2
#: inferences [measured 2026-09-27T20:31:29+10:00: full twins lanes on swipl-
#: patched.8 in wt-merge's battery 1, two of the stack through janus-contract B
#: and two with janus-contract A; command=sh tools/check.sh twins]. With step
#: 4's notices reader as amended the counts read -2 before the step and -1
#: after it, so the step moves the twin +2 where it moved it +1 [measured
#: 2026-09-28T12:37:38+10:00: full twins lanes in wt-merge's battery 1 on
#: swipl-patched.8 at this boundary, engine/host_notices.pl as amended against
#: the day before's as first written; command=sh tools/check.sh twins].
#: RE-PINNED 2026-09-27, 338822 to 326962 (-11860), -11,859 at walk-tax B,
#: which registers a batch's Prolog arities by asking each name, so a
#: registration walk over more than twelve names no longer reads every
#: predicate visible from the loading module at 2 inferences each [measured
#: 2026-09-27T20:38:05+10:00: full twins lanes on swipl-patched.8 in wt-merge's
#: battery 1, two with janus-contract A and two with walk-tax B; command=sh
#: tools/check.sh twins]. With step 4's notices reader as amended the counts
#: read -1 before the step and -2 after it, so the step moves the twin -11860
#: where it moved it -11859 [measured 2026-09-28T12:40:25+10:00: full twins
#: lanes in wt-merge's battery 1 on swipl-patched.8 at this boundary,
#: engine/host_notices.pl as amended against the day before's as first written;
#: command=sh tools/check.sh twins].
BUDGET = 326962

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
