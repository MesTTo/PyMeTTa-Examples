"""Purpose: use every String head through Python values and the typed library.

Guarantees: this twin preserves every example claim and both optional forms
[tested: python extensions/python/tools/twin_coverage.py examples/ch08-data/08-03-the-shipped-libraries/18-string_lib.metta; commit=118b805aedbee6de22be4f6131d97c3d6b9156de].
"""

from metta import G, S, V, lib


def twin(m):
    """Combine text recipes and native boundaries through their typed face."""
    m += lib.string
    fn = m.fn
    assert fn.string_length(G("a🦊é")).one() == 3
    assert fn.string_slice(G("a🦊é"), 1, 99) == [G("🦊é")]
    assert list(fn.string_split(G(",;"), G("a,b;;c")).one()) == [G("a"), G("b"), G(""), G("c")]
    assert list(fn.string_split_exact(G("::"), G("::a::::")).one()) == [G(""), G("a"), G(""), G("")]
    assert fn.string_join(G(" / "), (G("a"), G("b"))) == [G("a / b")]
    assert fn.string_trim(G(" \ta\r\n")) == [G("a")]
    assert fn.string_upper(S.hello) == [G("HELLO")]
    assert fn.string_lower(G("HELLO")) == [G("hello")]
    assert fn.string_starts_with(G("a🦊é"), G("a🦊")).one() is True
    assert fn.string_ends_with(G("a🦊é"), G("é")).one() is True
    assert fn.string_contains(G("a🦊é"), G("🦊")).one() is True
    assert fn.string_index_of(G("banana"), G("ana")).one() == 1
    assert fn.string_last_index_of(G("banana"), G("ana")).one() == 3
    assert fn.string_count(G("aaaaa"), G("aa")).one() == 2
    assert fn.string_count(G("aaaaa"), G("aa"), True).one() == 4  # noqa: FBT003 -- MeTTa calls take positional arguments.
    assert fn.string_replace(G("aaaaa"), G("aa"), G("X")) == [G("XXa")]
    assert fn.string_replace(G("abc"), G(""), G("X")) == [G("abc")]
    assert fn.string_last_index_of(G("a🦊"), G("")).one() == 2
    assert fn.string_count(G("a🦊"), G("")).one() == 3

    assert list(fn.string_chars(G("a🦊")).one()) == [G("a"), G("🦊")]
    assert fn.string_from_chars((G("ab"), S.c, 42)) == [G("abc42")]
    assert list(fn.string_codes(G("a🦊")).one()) == [97, 129418]
    assert fn.string_from_codes((97, 129418)) == [G("a🦊")]
    text = fn.string_from_codes((97, 0, 129418)).one()
    assert list(fn.string_codes(G(text)).one()) == [97, 0, 129418]
    assert fn.string_repeat(G("ab"), 3) == [G("ababab")]
    assert fn.string_pad_left(G("x"), 4, G("ab")) == [G("abax")]
    assert fn.string_pad_right(G("x"), 4, G("ab")) == [G("xaba")]
    assert fn.string_center(G("x"), 6, G("ab")) == [G("abxaba")]

    assert list(fn.string_lines(G("a\n\nb\n")).one()) == [G("a"), G(""), G("b")]
    assert fn.string_unlines((G("a"), G(""), G("b"))) == [G("a\n\nb\n")]
    assert fn.string_dedent(G("  a\n  b\n")) == [G("a\nb\n")]
    assert fn.string_indent(G("> "), G("a\n \nb\n")) == [G("> a\n \n> b\n")]
    assert fn.string_wrap(G("one two three"), 7) == [G("one two\nthree")]
    assert fn.string_wrap(G("a b c d"), 4, S.justify) == [G("a  b\nc d")]
    values = S.quote(((S.Name, G("Ada")), (S.Value, (S.age, 3))))
    assert fn.string_template(G("Dear {Name}: {Value}. {Missing,none}"), values) == [G("Dear Ada: (age 3). none")]

    assert fn.string_edit_distance(G("kitten"), G("sitting")).one() == 3
    assert fn.string_similarity(G("ab"), G("ac")).one() == 0.5
    assert fn.string_isub(G("language"), G("language")).one() == 1.0
    options = ((S.normalize, True), (S.zero_to_one, True), (S.substring_threshold, 0))
    assert fn.string_isub(G("A.B"), G("ab"), options).one() == 1.0
    assert fn.parse_number(G("0x10")).one() == 16
    assert fn.number_to_string(42) == [G("42")]
    assert list(fn.parse_number(G("not a number"))) == []

    assert fn.string_repeat(42, 2) == [G("4242")]
    assert fn.string_repeat(G(""), 10**24) == [G("")]
    assert fn.string_center(12, 7, 3) == [G("3312333")]
    assert fn.string_center(G("x"), 10**24, G("")) == [G("x")]
    assert fn.string_ends_with(G("ab"), G("abc")).one() is False
    assert fn.if_error(S.catch(S.string_repeat(G(""), 1.5)), True, False).one() is True  # noqa: FBT003 -- MeTTa calls take positional arguments.
    assert fn.string_repeat(G("x"), S.superpose((0, 2))) == [G(""), G("xx")]
    row = m.match(S["="](S.string_repeat(V.value, V.n), V.body)).one()
    recipe = m.eval(S["|->"]((row.value, row.n), row.body))[0]
    assert m.eval((recipe, G("ab"), 2)) == [G("abab")]


#: All thirty-four String heads and thirty-seven typed arities preserve the
#: example's fifty claims through values, function calls and reflected equations.
#: [measured 2026-09-11: 126928 inferences, minimum of three serial fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --measure --rounds 3
#: examples/ch08-data/08-03-the-shipped-libraries/18-string_lib.metta;
#: fixture=String library and warm native provider; commit=3aaad3435292e4c7d5cc3a01bfda39430aacc6e8].
#: RE-PINNED 2026-09-13, 126928 to 127459 (+531), File exports its staged
#: publisher to Compression; the shared native builder accepts the private
#: archive provider recipe. All consumers are remeasured after those dependency
#: changes [measured 2026-09-13: min-of-3 serial fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=7b42d5ee5cecb82709617b7ed08dfa2c1441f268].
#: RE-PINNED 2026-09-14, 127459 to 329461 (+202002), String now derives nine
#: text recipes through MeTTa equations, with one function parameter for
#: padding and complete validation before empty construction; all import
#: consumers are measured after the provider change [measured 2026-09-14: min-
#: of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=118b805aedbee6de22be4f6131d97c3d6b9156de].
#: RE-PINNED 2026-09-21, 329461 to 393161 (+63700), the sixty libraries derived
#: in MeTTa landed with merge 97763e7fa eight hours after the previous pin
#: 55d451b67, so every example importing one now pays a MeTTa derivation where
#: it paid a Prolog body instead, which the 2026-09-14 ruling accepts
#: explicitly as the price of a library that survives the engine swap [measured
#: 2026-09-21: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=6e09cb25d5495c2db3283166e6ce4e07eefecfb2].
#: RE-PINNED 2026-09-24, 393161 to 411716 (+18555), placed on the full-
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
#: RE-PINNED 2026-09-24, 411716 to 367981 (-43735), 0a81c782f loads a library's
#: Prolog half through the boot's claim (metta_load_source/2 in
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
#: RE-PINNED 2026-09-24, 367981 to 368610 (+629), 2126ab6 installs every
#: library's native half through lib/_support/native_install.pl, which tests
#: for a statically linked host and loads library(shlib) only where there is
#: none, where each half used to load shlib itself, so a process importing a
#: library with a native half now loads that module once [measured 2026-09-24:
#: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=d832d20e8edfdad28ad52815757ba9e685ad2de3].
#: RE-PINNED 2026-09-24, 368610 to 380135 (+11525), +11,519 at ae1cc8936, where
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
#: RE-PINNED 2026-09-24, 380135 to 380017 (-118), d4a365c16 holds the support
#: graph's visited set and the reference refresh's space sets in SWI tries
#: instead of library(nb_set): a membership check is one foreign call where
#: nb_set probed in Prolog, four inferences a step past a taken slot, from a
#: slot a library space's path-bearing name decided, and a walk over a node or
#: two pays a few inferences more for the trie's setup (-2); gate-perf's
#: d781eab8f carries an exact removal's selected head from the code that
#: selected it, so a withdrawal copies its equation once: 23 inferences fewer
#: for each equation removal the twin adopts and 4 for each it selects (-138);
#: the packages job's 90be572a9 and 4003462fe register Prolog through one
#: engine service: +22 for each library the twin imports (ten new engine
#: predicates and two user imports in the registration walk at two inferences
#: each, less the retired loaded_extension_file/2), and 146 inferences for a
#: Prolog file's origin or 220 for a text's SHA-256 on a twin that registers
#: Prolog (+22); each step read serially on its own committed tree, from gate-
#: perf's pin at c7d7244fb, and the fixed tree 4ff69551e reads what 4003462fe
#: does [measured 2026-09-24: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=4ff69551e0e226442cf7257b96af858adda957a4].
#: RE-PINNED 2026-09-24, 380017 to 380180 (+163), +161 at the change this re-
#: pin lands with, which publishes a from row by itself when rows are all a
#: space owes: its 36 predicates visible to filereader's registration walk cost
#: a batch above twelve names 72 inferences, each restricted space's core about
#: 28 a predicate, and every whole publication and face event its ledger's
#: bookkeeping [measured 2026-09-24: the twins lane alone on 8d651070d with the
#: change before this one and with this change too, one after the other in
#: battery 117's one path, every component at its pin; command=sh
#: tools/check.sh twins (twin_coverage.py inside tools/bounded.sh);
#: commit=e4b7448d1f1bd98733f1b04c3906aaa42f35ef1a].
#: RE-PINNED 2026-09-25, 380180 to 380202 (+22), the py-* doors change makes
#: more predicates visible from filereader, and
#: filereader:existing_predicate_arities/2 walks every predicate visible there
#: at two inferences each whenever a source registering more than twelve names
#: loads: on one tree the change's new engine predicates alone, defined with
#: their two boot uses taken out, make eight more visible and move this twin by
#: 16 for each such load, and the whole change by 20, ten more at its loads
#: (i-arity-walk-all-predicates) [measured 2026-09-25T02:51:16+10:00: min-of-3
#: serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-25, 380202 to 377072 (-3130), the host evaluation door
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
#: more than twelve names [measured 2026-09-25T06:46:59+10:00: min-of-3 serial
#: fresh processes; command=python extensions/python/tools/twin_coverage.py
#: --repin].
#: RE-PINNED 2026-09-25, 377072 to 377082 (+10), Runtime.reclaim(), the
#: reclamation barrier metta_py_reclaim/1, adds five predicates to user, and
#: existing_predicate_arities/2 walks every user predicate about twice per
#: large load (i-arity-walk-all-predicates) [measured
#: 2026-09-25T11:25:25+10:00: one full twins lane before this commit and one
#: with it, the two read on one battery path at the landing's HEAD;
#: command=python extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-25, 377082 to 377102 (+20), both specializer doors prepare
#: a specialization's predicate with spaces:metta_prepare_function_predicate/3
#: before asserting its clauses [measured 2026-09-25T11:29:10+10:00: one full
#: twins lane before this commit and one with it, the two read on one battery
#: path at the landing's HEAD; command=python
#: extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-25, 377102 to 377106 (+4), retiring a library importer
#: derives the arity row again from any backing head a library home still
#: registers, journalled to the load that owns it [measured
#: 2026-09-25T11:33:06+10:00: one full twins lane before this commit and one
#: with it, the two read on one battery path at the landing's HEAD;
#: command=python extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-25, 377106 to 377116 (+10), lib/lib_string/lib_string.qlf
#: is now compiled by a child of its own whichever half's load reaches it first
#: (engine/qlf_boot.pl, qlf_compile_argument/0), and that compile keeps the :-
#: non_terminal directive for word_tokens//1 that a compile inside lib_csv's
#: child, where the warm-up's glob order put it, left out, since SWI's
#: non_terminal_decl/2 writes it only for a head no earlier load flagged; the
#: loader runs the directive, ten inferences, in every process that loads
#: lib_string [measured 2026-09-25T15:55:13+10:00: min-of-3 serial fresh
#: processes; command=python extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-25, 377116 to 377271 (+155), every force of a waiting
#: function names the module it is made from, through fun_home_in/3, and a
#: write forces only its own space [measured 2026-09-25T16:54:32+10:00: one
#: full twins lane before this commit and one with it, the two read on one
#: battery path at the landing's HEAD; command=python
#: extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-25, 377271 to 378159 (+888), lambdas are named by their
#: content and a copy restores its source's rows as a program [measured
#: 2026-09-25T17:00:15+10:00: one full twins lane before this commit and one
#: with it, the two read on one battery path at the landing's HEAD;
#: command=python extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-25, 378159 to 378211 (+52), engine/source_loading.pl's
#: load-error clause moved from the thread_local user:thread_message_hook/3 to
#: the global user:message_hook/3, so every thread and engine now runs the
#: check the main thread always ran: one inference per message while no load is
#: open there (clause(watching, true, _) fails) and two inside one
#: (load_failure/2 rejects the silent kind); the Python seat prints a twin's
#: library-load messages inside engines, where no clause ran before, and the
#: original's side does not move [measured 2026-09-25T18:41:57+10:00: min-of-3
#: serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-25, 378211 to 378213 (+2), a sweep of a module's generated
#: predicates retires the records describing each swept predicate, and a
#: release the rest of the module's [measured 2026-09-25T23:29:52+10:00: one
#: full twins lane before this commit and one with it, the two read on one
#: battery path at the landing's HEAD; command=python
#: extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-26, 378213 to 378231 (+18), engine/metta/control.pl's
#: partial/3 to partial/11, the clauses that let a Prolog meta-predicate call a
#: partial function value, are nine more predicates visible from filereader,
#: and filereader:existing_predicate_arities/2's batch walk, which a load
#: registering more than twelve names runs, pays two inferences for each: 18 a
#: batch, the original and the twin alike, and nine inert facts of those
#: arities move it the same [measured 2026-09-26T01:30:26+10:00: min-of-3
#: serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-26, 378231 to 378251 (+20), the reference faces of a
#: strongly connected component of from rows are computed together by label-
#: setting, which makes ten more predicates visible from metta_engine, and a
#: control adding only ten unused predicates to metta_engine reads the same, so
#: none of the move is face work; existing_predicate_arities/2 walks every
#: visible predicate at two inferences for each batch of more than twelve names
#: a load registers (i-arity-walk-all-predicates) [measured
#: 2026-09-26T03:08:26+10:00: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-26, 378251 to 378246 (-5), engine/source_loading.pl hears
#: a load's printed failures through a user:thread_message_hook/3 clause each
#: load asserts on the thread or engine running it and erases, where
#: c83b6bb1e's clause of the global user:message_hook/3 ran for every message:
#: 3 loads each call prolog_current_frame/1 once more (+3); 1 registration walk
#: over a batch of more than twelve names
#: (filereader:existing_predicate_arities/2) enumerates one more predicate than
#: the trunk's (+2), since SWI's autoImport() links prolog_current_frame/1 into
#: every module on metta_source_loading's import chain, user included, at the
#: boot's first load, where the trunk links it into user only at its first
#: library import; 10 messages this twin's count reads, printed outside a load,
#: no longer run the loader's clause (-10) [measured 2026-09-26T06:55:06+10:00:
#: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-26, 378246 to 378260 (+14), Registering a source's names
#: answers each name's Prolog arities in standard order, one msort/2 per
#: registration that adds names, where they came in the procedure table's order
#: and set the order of the arity/2 facts [measured 2026-09-26T12:29:46+10:00:
#: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-26, 378260 to 378321 (+61), A Prolog function registered
#: without its arity is claimed from its lowest arity's file through
#: aggregate_all(min(Arity, File), ...), where the scan took the first arity
#: the procedure table answered [measured 2026-09-26T13:02:54+10:00: min-of-3
#: serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-26, 378321 to 378327 (+6), The engine module defines three
#: predicates more, builtin_seat_prefixes/1, builtin_implementation_gap/2,
#: validate_builtin_implementation_gaps/2 and builtin_surface_predicate/3 in
#: and builtin_surface_predicate_name/1 out, and a program pays for each
#: predicate visible from the engine wherever it walks them:
#: existing_predicate_arities/2 two inferences a predicate for each load that
#: registers more than twelve names, and a restricted space twenty-seven a
#: predicate when it publishes the engine's core; three facts appended to
#: engine/metta/registration.pl on 07b75d16e move 14-lib_roman_pair_helpers,
#: 02-restricted_spaces and 37-statistics_lib by the same +6, +87 and +30
#: [measured 2026-09-26T14:28:51+10:00: min-of-3 serial fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-26, 378327 to 378411 (+84), the specializer substitutes
#: only ground bindings into a specialization's stored row: it tests each
#: binding with ground/1, which SWI calls as a builtin where nonvar/1 compiled
#: inline, and leaves a binding with variables as the row's own parameter
#: instead of substituting it into the body [measured
#: 2026-09-26T18:25:19+10:00: one full twins lane before this commit and one
#: with it, each read in one battery of the landing's HEAD after a QLF purge
#: and one warm-up; command=python extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-27, 378411 to 378683 (+272), the host switch to swipl-
#: patched.7 and the seat changes it needs: +17 the host switch to swipl-
#: patched.7, which delivers the heartbeat inside loops, so a held engine ticks
#: and the held goals read its ticks from the raw counter, 9 inferences a tick,
#: and whose three new system predicates ('$heartbeat'/0, '$file_hash'/2,
#: '$qlf_source_changed'/2) filereader's walk of every visible predicate
#: (existing_predicate_arities/2) meets, 2 inferences each; +9 the seat's
#: interrupt poll crossing only on its arming thread, whose hook costs 3
#: inferences a tick more and whose start goal runs on every new thread and
#: engine; +3 the poll's tick record updated in place, 3 inferences a tick more
#: than replacing it; +243 the held goals reading Used through metta_py_work/2,
#: which leaves a held engine's own ticks out and reads the tick term inside
#: its opening edge, 5 inferences a held reading [measured
#: 2026-09-27T03:41:21+10:00: one full twins lane of the trunk and one with
#: this landing, wt-merge battery 1, the trunk on swipl-patched.6 and every
#: part on .7, each through a same-shape host shim; command=python
#: extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-27, 378683 to 378744 (+61), a force of a waiting function
#: takes the typing policy and the specializer's lock before translation:
#: spaces:metta_ensure_compiled/2 stabilises the policy and takes the
#: specializer's mutex around the translation once per force, and the
#: translation's own per-pair stabilisation re-enters through
#: with_typing_policy_stable/1's first clause [measured
#: 2026-09-27T09:56:55+10:00: one full twins lane before this commit and one
#: with it, each read in one battery of the landing's HEAD after a QLF purge
#: and one warm-up; command=python extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-27, 378744 to 378807 (+63), the constructive negation's
#: engine additions, each counted in this twin's own run: 1 registration walk
#: over more than twelve names (filereader:existing_predicate_arities/2), each
#: now reading 31 more predicates at 2 inferences (+62); 1 == or != on compound
#: terms that differ, each now decided by metta_same_term/3 (+2); -1 of clause-
#: indexing layout [measured 2026-09-27T18:31:56+10:00: one full twins lane
#: with this landing, in a battery of its tree at 775d3cf35, beside one of the
#: base in a battery of 775d3cf35 from 2026-09-27T18:40:06+10:00, which reads
#: the old pin; command=python extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-28, 378807 to 378805 (-2), -2 at tsm-licence's notices
#: reader as its block lookahead amended it: engine/host_notices.pl, which
#: every boot loads, opens a component block only where its Component field
#: directly follows the line of 78 '=', the calls not traced; read on swipl-
#: patched.8, the count above on .7, which no longer runs [measured
#: 2026-09-28T12:31:49+10:00: full twins lanes in wt-merge's battery 1 on
#: swipl-patched.8 at this boundary, engine/host_notices.pl as amended against
#: the day before's as first written; command=sh tools/check.sh twins].
#: RE-PINNED 2026-09-27, 378805 to 378642 (-163), +2 at the host switch to
#: swipl-patched.8, whose swi-heartbeat-inferences-charged-to-the-program
#: leaves the interrupt poll's own inferences out of every count, so a window
#: the seat's calibrated poll correction read 1 to 3 low on .7 reads exactly;
#: -165 at interrupts B's seat change, which drops the poll's boot calibration,
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
#: RE-PINNED 2026-09-27, 378642 to 378644 (+2), +2 at janus-contract A, whose
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
#: RE-PINNED 2026-09-27, 378644 to 366789 (-11855), -11,855 at walk-tax B,
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
#: RE-PINNED 2026-09-29, 366789 to 366833 (+44), this twin reads 366789 before
#: the change and 366833 with the change (+44): each definition through the
#: define doors asks whether its module holds a shadow-import receipt for the
#: name, holds it in flight until the write is visible when it does, and a
#: sweep leaves a receipt another live thread holds: with that use this twin
#: reads 366833 where the definitions alone read 366789 (+44) [measured
#: 2026-09-29T06:36:32+10:00: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-29, 366833 to 367859 (+1026), this twin reads 366833
#: before the change and 367859 with the change (+1026): each definition marks
#: its name as changed and a sweep repairs only the receipts naming a marked
#: name, where it re-checked every receipt the process held: with that use this
#: twin reads 367859 where the definitions alone read 366833 (+1026) [measured
#: 2026-09-29T06:43:13+10:00: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-29, 367859 to 367917 (+58), this twin reads 367859 before
#: the change and 367917 with the change (+58): a definition that cannot move
#: its space's source map leaves the space's source reader published, so a load
#: beside a from row publishes the face once per runnable instead of once per
#: definition: with that use this twin reads 367917 where the definitions alone
#: read 367859 (+58) [measured 2026-09-29T06:51:16+10:00: min-of-3 serial fresh
#: processes; command=python extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-29, 367917 to 368072 (+155), this twin reads 367917 before
#: the change and 368072 with the change (+155): a mark names the module its
#: definition changed in, and a sweep repairs only the receipts held by that
#: module and its declared descendants: with that use this twin reads 368072
#: where the definitions alone read 367917 (+155) [measured
#: 2026-09-29T06:56:24+10:00: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-29, 368072 to 368656 (+584), this twin reads 368072 before
#: the change and 368656 with the change (+584): every operation that registers
#: a name outside a load opens a registration unit, files there the repairs its
#: registrations owe, and drains them once when it finishes, so a caller
#: compiled before the name became a function is repaired: with that use this
#: twin reads 368656 where the definitions alone read 368072 (+584) [measured
#: 2026-09-29T20:22:55+10:00: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-29, 368656 to 368286 (-370), this twin reads 368656 before
#: the change and 368286 with the change (-370): a call site forces the
#: function it names before deciding the call's shape, so a call of a waiting
#: function builds the application protocol an eager load builds, and the
#: protocol's marker test around a value the translation already holds is
#: decided at compile time: with that use this twin reads 368286 where the
#: definitions alone read 368656 (-370) [measured 2026-09-29T20:34:42+10:00:
#: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-30, 368286 to 365950 (-2336), this twin reads 368286
#: before the change and 365950 with the change (-2336): a named space's
#: prelude-tier type readers look the prelude's row up before asking whether it
#: governs there, and builtin_result_type/3 asks whether a program took a
#: builtin over only for a builtin whose result is evaluated
#: (engine/metta/types.pl, engine/translator/lowering.pl), so a lookup of a
#: name the prelude does not declare costs one indexed miss and no ownership
#: probe [measured 2026-09-30T04:16:53+10:00: min-of-3 serial fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-30, 365950 to 366233 (+283), the twins lane reads this
#: twin at 365954 before this change and at 366233 with it (+279): every import
#: request that succeeds, a load or a receipt still current, now records who
#: asked for the source (engine/metta/interop.pl, record_import_request/2
#: writing import_request/3), so unimport! of a package can leave a file
#: another live requester still asks for; it read 365954 against its pin 365950
#: before this change, +4 from an earlier commit of this landing, the takeover
#: read through a module's compiled predicate, inside the allowance [measured
#: 2026-09-30T04:34:03+10:00: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
BUDGET = 366233
