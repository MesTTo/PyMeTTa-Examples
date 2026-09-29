"""Purpose: the Unicode database and the standard transformations over text.

Text is a `G("...")` grounded string, because a bare Python string is a name and
these operations are about TEXT; a form, a property name, a flag and a class are
symbols, so they come from `S`. The normalizations that answer the same string in
a different form are compared by their code points, which is the only way the
difference is visible at all.

Guarantees: the same claims as 26-unicode_lib.metta
[tested: python extensions/python/tools/twin_coverage.py examples/ch08-data/08-03-the-shipped-libraries/26-unicode_lib.metta; commit=a30e0a59e8e16d15705dc0258d7e0a004ae63e4b].
Open Obligations:
  To Do: None
  Hacks: None
  Future Enhancements: None.
"""

from metta import G, S, lib
from metta._errors.errors import MettaError


def twin(m):
    """Normalize, fold, map, ask the database, classify, split and validate."""
    m += lib.unicode
    # lib_string is beside it here because the two answer different questions
    # about the same text: string-codes and string-chars count code points,
    # unicode-graphemes counts what a person calls a character, and string-lower
    # is a lowercasing where unicode-casefold is not.
    m += lib.string

    def refused(call):
        """Whether evaluating a call raises, which is what if-error reads."""
        try:
            list(m.eval(call))
        except MettaError:
            return True
        return False

    def codes(text):
        """The code points of a string, as a list."""
        return list(m.fn.string_codes(text).one())

    normalize, casefold, unimap = m.fn.unicode_normalize, m.fn.unicode_casefold, m.fn.unicode_map
    prop, is_class = m.fn.unicode_property, m.fn.unicode_is
    graphemes, valid = m.fn.unicode_graphemes, m.fn.unicode_codepoint_valid

    # Every answer here comes from the host's own database, and its version is a
    # head because a normalization is reproducible only beside the version that
    # made it.
    assert m.fn.unicode_version() == [G("16.0.0")]

    # The five normalization forms. "é" can be one code point or two, and nfc and
    # nfd are what move between them; string-codes shows which one a string holds.
    assert codes(normalize(S.nfd, G("é")).one()) == [101, 769]
    assert codes(normalize(S.nfc, G("é")).one()) == [233]
    assert normalize(S.nfc, normalize(S.nfd, G("é")).one()) == [G("é")]
    # The compatibility forms also replace presentation characters: the ffi
    # ligature becomes three letters and the superscript two becomes a two.
    assert normalize(S.nfkc, G("ﬃ")) == [G("ffi")]
    assert normalize(S.nfkd, G("2²")) == [G("22")]
    assert normalize(S.nfc, G("2²")) == [G("2²")]
    # nfkc-casefold is the caseless identifier form of UAX#31: compatibility, then
    # composition, then case folding, in one pass.
    assert normalize(S.nfkc_casefold, G("Straße")) == [G("strasse")]
    assert refused(S.unicode_normalize(S.nfx, G("a")))

    # Case folding is NOT lowercasing: it answers what compares equal regardless
    # of case, so sharp s becomes two letters and the answer is longer.
    assert casefold(G("Straße")) == [G("strasse")]
    assert m.fn.string_lower(G("Straße")) == [G("straße")]
    assert casefold(G("HELLO")).one() == casefold(G("hello")).one()

    # unicode-map is the general operation the forms above are compositions of,
    # and it does the transformations that have no standard name: stripping the
    # accents off text is composing it and stripping the marks.
    assert unimap(G("café"), (S.compose, S.stripmark)) == [G("cafe")]
    # lump folds typographic variants onto their ASCII equivalents, which is what
    # a search index wants. Double quotes are not in the host's table, which is
    # why this claim uses the apostrophe.
    # The apostrophe and the dash are the typographic ones, written as their code
    # points so the difference from the ASCII answer is visible in the source.
    assert unimap(G("it\u2019s a\u2013b"), (S.lump,)) == [G("it's a-b")]
    assert unimap(G("Hello"), (S.casefold,)) == [G("hello")]
    assert refused(S.unicode_map(G("a"), (S.nosuchflag,)))
    # Two combinations are refused rather than passed to the host, which answers a
    # bare domain error for both.
    assert refused(S.unicode_map(G("a"), (S.compose, S.decompose)))
    assert refused(S.unicode_map(G("a"), (S.stripmark,)))

    # The database, one character at a time. A character is a one-character string
    # or the number of a code point, whichever the program has in hand.
    assert prop(G("A"), S.category) == [S.Lu]
    assert prop(65, S.category) == [S.Lu]
    assert prop(G("1"), S.category) == [S.Nd]
    assert prop(G(" "), S.category) == [S.Zs]
    assert prop(G("A"), S.lowercase) == [97]
    assert prop(G("a"), S.uppercase) == [65]
    assert prop(G("A"), S.width) == [1]
    assert prop(G("漢"), S.width) == [2]
    # A property the character has no value for has NO answer, which is data about
    # the character; an unknown property NAME is refused, which is a mistake.
    assert list(prop(G("A"), S.uppercase)) == []
    assert list(prop(G("a"), S.decomp_type)) == []
    assert refused(S.unicode_property(G("a"), S.colour))
    assert refused(S.unicode_property(G("ab"), S.category))

    # The classification a lexer asks per character, as a Bool so it composes.
    # Every class is a general category of the database or a group of them, so
    # the answers do not move with the process locale.
    assert is_class(G("a"), S.letter) == [True]
    assert is_class(G("1"), S.letter) == [False]
    assert is_class(G("1"), S.digit) == [True]
    assert is_class(G("Ⅲ"), S.number) == [True]
    assert is_class(G(" "), S.white_space) == [True]
    assert is_class(G("é"), S.letter) == [True]
    assert is_class(G("é"), S.ascii) == [False]
    assert is_class(G("漢"), S.letter) == [True]
    assert is_class(65, S.upper) == [True]
    assert is_class(G(","), S.punctuation) == [True]
    assert is_class(1114111, S.assigned) == [False]
    assert refused(S.unicode_is(G("a"), S.vowel))

    # Graphemes are the characters a PERSON counts: a base character with its
    # combining marks is one, where string-chars answers each code point.
    decomposed = normalize(S.nfd, G("éx")).one()
    assert len(m.fn.string_chars(decomposed).one()) == 3
    assert len(graphemes(decomposed).one()) == 2
    # The first grapheme holds BOTH code points, which is what grouping means, and
    # the codes are what makes it visible: the two strings print the same.
    assert codes(m.fn.car_atom(graphemes(decomposed)).one()) == [101, 769]
    assert list(graphemes(G("abc")).one()) == [G("a"), G("b"), G("c")]
    assert list(graphemes(G("")).one()) == []

    # A code point is valid when the database ASSIGNS it a character, which is
    # stricter than being in range: a surrogate half, an unassigned number and a
    # noncharacter all answer False, and a private-use code point answers True.
    assert valid(97) == [True]
    assert valid(55296) == [False]
    assert valid(1114112) == [False]
    assert valid(1114111) == [False]
    assert valid(57344) == [True]
    assert prop(57344, S.category) == [S.Co]
    assert list(prop(1114111, S.category)) == []


#: MEASURED on this branch rather than inherited: this twin is new, so there is
#: no earlier pin to move. The 54 claims cover the eight heads, the five forms,
#: fourteen classes and the refusals, and the twin costs LESS than the example,
#: whose two library imports it shares: the example's `collapse` and
#: `string-codes` round trips are `list()` and one `codes` helper here
#: [measured 2026-09-12: 129667 inferences against the example's 139207,
#: minimum of three serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --measure --rounds 3
#: examples/ch08-data/08-03-the-shipped-libraries/26-unicode_lib.metta;
#: fixture=lib_unicode at its functional commit, artifacts purged before the
#: run; commit=a30e0a59e8e16d15705dc0258d7e0a004ae63e4b].
#: RE-PINNED 2026-09-13, 129667 to 130198 (+531), File exports its staged
#: publisher to Compression; the shared native builder accepts the private
#: archive provider recipe. All consumers are remeasured after those dependency
#: changes [measured 2026-09-13: min-of-3 serial fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=7b42d5ee5cecb82709617b7ed08dfa2c1441f268].
#: RE-PINNED 2026-09-14, 130198 to 152171 (+21973), String now derives nine
#: text recipes through MeTTa equations, with one function parameter for
#: padding and complete validation before empty construction; all import
#: consumers are measured after the provider change [measured 2026-09-14: min-
#: of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=118b805aedbee6de22be4f6131d97c3d6b9156de].
#: RE-PINNED 2026-09-21, 152171 to 235201 (+83030), the sixty libraries derived
#: in MeTTa landed with merge 97763e7fa eight hours after the previous pin
#: 55d451b67, so every example importing one now pays a MeTTa derivation where
#: it paid a Prolog body instead, which the 2026-09-14 ruling accepts
#: explicitly as the price of a library that survives the engine swap [measured
#: 2026-09-21: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=6e09cb25d5495c2db3283166e6ce4e07eefecfb2].
#: RE-PINNED 2026-09-24, 235201 to 256623 (+21422), placed on the full-
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
#: RE-PINNED 2026-09-24, 256623 to 193873 (-62750), 0a81c782f loads a library's
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
#: RE-PINNED 2026-09-24, 193873 to 195177 (+1304), both: 2126ab6 installs the
#: library's native half through lib/_support/native_install.pl, loaded once
#: per process, and 0847c3d4c with 984eabe23 decides on its first read each
#: platform capability the twin reads, in a flag under a mutex; a792976 loads
#: process, socket and HTTP's libraries through the census and refuses per
#: call, which moves process_lib by 44 and socket_lib by -603 [measured
#: 2026-09-24: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=d832d20e8edfdad28ad52815757ba9e685ad2de3].
#: RE-PINNED 2026-09-24, 195177 to 206786 (+11609), +11,603 at ae1cc8936, where
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
#: RE-PINNED 2026-09-24, 206786 to 206622 (-164), d4a365c16 holds the support
#: graph's visited set and the reference refresh's space sets in SWI tries
#: instead of library(nb_set): a membership check is one foreign call where
#: nb_set probed in Prolog, four inferences a step past a taken slot, from a
#: slot a library space's path-bearing name decided, and a walk over a node or
#: two pays a few inferences more for the trie's setup (-2); gate-perf's
#: d781eab8f carries an exact removal's selected head from the code that
#: selected it, so a withdrawal copies its equation once: 23 inferences fewer
#: for each equation removal the twin adopts and 4 for each it selects (-184);
#: the packages job's 90be572a9 and 4003462fe register Prolog through one
#: engine service: +22 for each library the twin imports (ten new engine
#: predicates and two user imports in the registration walk at two inferences
#: each, less the retired loaded_extension_file/2), and 146 inferences for a
#: Prolog file's origin or 220 for a text's SHA-256 on a twin that registers
#: Prolog (+22); each step read serially on its own committed tree, from gate-
#: perf's pin at c7d7244fb, and the fixed tree 4ff69551e reads what 4003462fe
#: does [measured 2026-09-24: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=4ff69551e0e226442cf7257b96af858adda957a4].
#: RE-PINNED 2026-09-24, 206622 to 206809 (+187), +185 at the change this re-
#: pin lands with, which publishes a from row by itself when rows are all a
#: space owes: its 36 predicates visible to filereader's registration walk cost
#: a batch above twelve names 72 inferences, each restricted space's core about
#: 28 a predicate, and every whole publication and face event its ledger's
#: bookkeeping [measured 2026-09-24: the twins lane alone on 8d651070d with the
#: change before this one and with this change too, one after the other in
#: battery 117's one path, every component at its pin; command=sh
#: tools/check.sh twins (twin_coverage.py inside tools/bounded.sh);
#: commit=e4b7448d1f1bd98733f1b04c3906aaa42f35ef1a].
#: RE-PINNED 2026-09-25, 206809 to 206832 (+23), the py-* doors change makes
#: more predicates visible from filereader, and
#: filereader:existing_predicate_arities/2 walks every predicate visible there
#: at two inferences each whenever a source registering more than twelve names
#: loads: on one tree the change's new engine predicates alone, defined with
#: their two boot uses taken out, move this twin by 16 for each such load and
#: the whole change by 20, each give or take one or two inferences that move
#: with where the new names land in SWI's tables and that SWI's profiler, which
#: lists no system predicate, does not place (i-arity-walk-all-predicates)
#: [measured 2026-09-25T02:56:27+10:00: min-of-3 serial fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-25, 206832 to 202757 (-4075), the host evaluation door
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
#: more than twelve names [measured 2026-09-25T06:47:25+10:00: min-of-3 serial
#: fresh processes; command=python extensions/python/tools/twin_coverage.py
#: --repin].
#: RE-PINNED 2026-09-25, 202757 to 202767 (+10), Runtime.reclaim(), the
#: reclamation barrier metta_py_reclaim/1, adds five predicates to user, and
#: existing_predicate_arities/2 walks every user predicate about twice per
#: large load (i-arity-walk-all-predicates) [measured
#: 2026-09-25T11:25:25+10:00: one full twins lane before this commit and one
#: with it, the two read on one battery path at the landing's HEAD;
#: command=python extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-25, 202767 to 202769 (+2), both specializer doors prepare
#: a specialization's predicate with spaces:metta_prepare_function_predicate/3
#: before asserting its clauses [measured 2026-09-25T11:29:10+10:00: one full
#: twins lane before this commit and one with it, the two read on one battery
#: path at the landing's HEAD; command=python
#: extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-25, 202769 to 202773 (+4), retiring a library importer
#: derives the arity row again from any backing head a library home still
#: registers, journalled to the load that owns it [measured
#: 2026-09-25T11:33:06+10:00: one full twins lane before this commit and one
#: with it, the two read on one battery path at the landing's HEAD;
#: command=python extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-25, 202773 to 202783 (+10), lib/lib_string/lib_string.qlf
#: is now compiled by a child of its own whichever half's load reaches it first
#: (engine/qlf_boot.pl, qlf_compile_argument/0), and that compile keeps the :-
#: non_terminal directive for word_tokens//1 that a compile inside lib_csv's
#: child, where the warm-up's glob order put it, left out, since SWI's
#: non_terminal_decl/2 writes it only for a head no earlier load flagged; the
#: loader runs the directive, ten inferences, in every process that loads
#: lib_string [measured 2026-09-25T15:55:29+10:00: min-of-3 serial fresh
#: processes; command=python extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-25, 202783 to 202807 (+24), every force of a waiting
#: function names the module it is made from, through fun_home_in/3, and a
#: write forces only its own space [measured 2026-09-25T16:54:32+10:00: one
#: full twins lane before this commit and one with it, the two read on one
#: battery path at the landing's HEAD; command=python
#: extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-25, 202807 to 202821 (+14), lambdas are named by their
#: content and a copy restores its source's rows as a program [measured
#: 2026-09-25T17:00:15+10:00: one full twins lane before this commit and one
#: with it, the two read on one battery path at the landing's HEAD;
#: command=python extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-25, 202821 to 202871 (+50), engine/source_loading.pl's
#: load-error clause moved from the thread_local user:thread_message_hook/3 to
#: the global user:message_hook/3, so every thread and engine now runs the
#: check the main thread always ran: one inference per message while no load is
#: open there (clause(watching, true, _) fails) and two inside one
#: (load_failure/2 rejects the silent kind); the Python seat prints a twin's
#: library-load messages inside engines, where no clause ran before, and the
#: original's side does not move [measured 2026-09-25T18:42:22+10:00: min-of-3
#: serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-25, 202871 to 202873 (+2), a sweep of a module's generated
#: predicates retires the records describing each swept predicate, and a
#: release the rest of the module's [measured 2026-09-25T23:29:52+10:00: one
#: full twins lane before this commit and one with it, the two read on one
#: battery path at the landing's HEAD; command=python
#: extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-26, 202873 to 202891 (+18), engine/metta/control.pl's
#: partial/3 to partial/11, the clauses that let a Prolog meta-predicate call a
#: partial function value, are nine more predicates visible from filereader,
#: and filereader:existing_predicate_arities/2's batch walk, which a load
#: registering more than twelve names runs, pays two inferences for each: 18 a
#: batch, the original and the twin alike, and nine inert facts of those
#: arities move it the same [measured 2026-09-26T01:30:50+10:00: min-of-3
#: serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-26, 202891 to 202911 (+20), the reference faces of a
#: strongly connected component of from rows are computed together by label-
#: setting, which makes ten more predicates visible from metta_engine, and a
#: control adding only ten unused predicates to metta_engine reads the same, so
#: none of the move is face work; existing_predicate_arities/2 walks every
#: visible predicate at two inferences for each batch of more than twelve names
#: a load registers (i-arity-walk-all-predicates) [measured
#: 2026-09-26T03:08:50+10:00: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-26, 202911 to 202919 (+8), this twin reads 202915 at the
#: base and 202919 with the change (+4): the change adds
#: metta_reference_enroll/1 and metta_reference_source_bound/5 to the
#: metta_engine module (engine/metta/reference_refresh.pl and
#: reference_sources.pl), and on a tree that defines them and never calls them
#: this twin reads 202919 (+4), which only a walk over SWI's predicate or atom
#: tables can move, by visiting more entries or visiting them in another order;
#: it read 202915 against its pin 202911 at the base, so +4 of the distance is
#: the trunk's own and is not attributed here [measured
#: 2026-09-26T11:17:50+10:00: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-26, 202919 to 202930 (+11), Registering a source's names
#: answers each name's Prolog arities in standard order, one msort/2 per
#: registration that adds names, where they came in the procedure table's order
#: and set the order of the arity/2 facts [measured 2026-09-26T12:30:09+10:00:
#: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-26, 202930 to 202991 (+61), A Prolog function registered
#: without its arity is claimed from its lowest arity's file through
#: aggregate_all(min(Arity, File), ...), where the scan took the first arity
#: the procedure table answered [measured 2026-09-26T13:03:18+10:00: min-of-3
#: serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-26, 202991 to 202997 (+6), The engine module defines three
#: predicates more, builtin_seat_prefixes/1, builtin_implementation_gap/2,
#: validate_builtin_implementation_gaps/2 and builtin_surface_predicate/3 in
#: and builtin_surface_predicate_name/1 out, and a program pays for each
#: predicate visible from the engine wherever it walks them:
#: existing_predicate_arities/2 two inferences a predicate for each load that
#: registers more than twelve names, and a restricted space twenty-seven a
#: predicate when it publishes the engine's core; three facts appended to
#: engine/metta/registration.pl on 07b75d16e move 14-lib_roman_pair_helpers,
#: 02-restricted_spaces and 37-statistics_lib by the same +6, +87 and +30
#: [measured 2026-09-26T14:29:24+10:00: min-of-3 serial fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-27, 202997 to 203276 (+279), the host switch to swipl-
#: patched.7 and the seat changes it needs: +17 the host switch to swipl-
#: patched.7, which delivers the heartbeat inside loops, so a held engine ticks
#: and the held goals read its ticks from the raw counter, 9 inferences a tick,
#: and whose three new system predicates ('$heartbeat'/0, '$file_hash'/2,
#: '$qlf_source_changed'/2) filereader's walk of every visible predicate
#: (existing_predicate_arities/2) meets, 2 inferences each; +9 the seat's
#: interrupt poll crossing only on its arming thread, whose hook costs 3
#: inferences a tick more and whose start goal runs on every new thread and
#: engine; +3 the poll's tick record updated in place, 3 inferences a tick more
#: than replacing it; +250 the held goals reading Used through metta_py_work/2,
#: which leaves a held engine's own ticks out and reads the tick term inside
#: its opening edge, 5 inferences a held reading [measured
#: 2026-09-27T03:41:21+10:00: one full twins lane of the trunk and one with
#: this landing, wt-merge battery 1, the trunk on swipl-patched.6 and every
#: part on .7, each through a same-shape host shim; command=python
#: extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-27, 203276 to 203281 (+5), a force of a waiting function
#: takes the typing policy and the specializer's lock before translation:
#: spaces:metta_ensure_compiled/2 stabilises the policy and takes the
#: specializer's mutex around the translation once per force, and the
#: translation's own per-pair stabilisation re-enters through
#: with_typing_policy_stable/1's first clause [measured
#: 2026-09-27T09:56:55+10:00: one full twins lane before this commit and one
#: with it, each read in one battery of the landing's HEAD after a QLF purge
#: and one warm-up; command=python extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-27, 203281 to 203341 (+60), the constructive negation's
#: engine additions, each counted in this twin's own run: 1 registration walk
#: over more than twelve names (filereader:existing_predicate_arities/2), each
#: now reading 31 more predicates at 2 inferences (+62); -2 of clause-indexing
#: layout [measured 2026-09-27T18:31:56+10:00: one full twins lane with this
#: landing, in a battery of its tree at 775d3cf35, beside one of the base in a
#: battery of 775d3cf35 from 2026-09-27T18:40:06+10:00, which reads the old
#: pin; command=python extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-28, 203341 to 203339 (-2), -2 at tsm-licence's notices
#: reader as its block lookahead amended it: engine/host_notices.pl, which
#: every boot loads, opens a component block only where its Component field
#: directly follows the line of 78 '=', the calls not traced; read on swipl-
#: patched.8, the count above on .7, which no longer runs [measured
#: 2026-09-28T12:31:49+10:00: full twins lanes in wt-merge's battery 1 on
#: swipl-patched.8 at this boundary, engine/host_notices.pl as amended against
#: the day before's as first written; command=sh tools/check.sh twins].
#: RE-PINNED 2026-09-27, 203339 to 203170 (-169), +2 at the host switch to
#: swipl-patched.8, whose swi-heartbeat-inferences-charged-to-the-program
#: leaves the interrupt poll's own inferences out of every count, so a window
#: the seat's calibrated poll correction read 1 to 3 low on .7 reads exactly;
#: -171 at interrupts B's seat change, which drops the poll's boot calibration,
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
#: RE-PINNED 2026-09-27, 203170 to 203172 (+2), +2 at janus-contract A, whose
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
#: RE-PINNED 2026-09-27, 203172 to 191231 (-11941), -11,941 at walk-tax B,
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
#: RE-PINNED 2026-09-29, 191231 to 191603 (+372), this twin reads 191235 before
#: the change and 191603 with the change (+368): each definition marks its name
#: as changed and a sweep repairs only the receipts naming a marked name, where
#: it re-checked every receipt the process held: with that use this twin reads
#: 191603 where the definitions alone read 191235 (+368); it read 191235
#: against its pin 191231 before this step, a distance of +4 that is not this
#: step's (+4 the earlier steps' moves inside its tolerance) and is not
#: attributed here [measured 2026-09-29T06:43:22+10:00: min-of-3 serial fresh
#: processes; command=python extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-29, 191603 to 191677 (+74), this twin reads 191603 before
#: the change and 191677 with the change (+74): a definition that cannot move
#: its space's source map leaves the space's source reader published, so a load
#: beside a from row publishes the face once per runnable instead of once per
#: definition: with that use this twin reads 191677 where the definitions alone
#: read 191603 (+74) [measured 2026-09-29T06:51:16+10:00: min-of-3 serial fresh
#: processes; command=python extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-29, 191677 to 191872 (+195), this twin reads 191677 before
#: the change and 191872 with the change (+195): a mark names the module its
#: definition changed in, and a sweep repairs only the receipts held by that
#: module and its declared descendants: with that use this twin reads 191872
#: where the definitions alone read 191677 (+195) [measured
#: 2026-09-29T06:56:26+10:00: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-29, 191872 to 192470 (+598), this twin reads 191872 before
#: the change and 192470 with the change (+598): every operation that registers
#: a name outside a load opens a registration unit, files there the repairs its
#: registrations owe, and drains them once when it finishes, so a caller
#: compiled before the name became a function is repaired: with that use this
#: twin reads 192470 where the definitions alone read 191872 (+598) [measured
#: 2026-09-29T20:23:08+10:00: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-29, 192470 to 192355 (-115), this twin reads 192470 before
#: the change and 192355 with the change (-115): a call site forces the
#: function it names before deciding the call's shape, so a call of a waiting
#: function builds the application protocol an eager load builds, and the
#: protocol's marker test around a value the translation already holds is
#: decided at compile time: with that use this twin reads 192355 where the
#: definitions alone read 192470 (-115) [measured 2026-09-29T20:34:58+10:00:
#: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-30, 192355 to 191892 (-463), this twin reads 192355 before
#: the change and 191892 with the change (-463): a named space's prelude-tier
#: type readers look the prelude's row up before asking whether it governs
#: there, and builtin_result_type/3 asks whether a program took a builtin over
#: only for a builtin whose result is evaluated (engine/metta/types.pl,
#: engine/translator/lowering.pl), so a lookup of a name the prelude does not
#: declare costs one indexed miss and no ownership probe [measured
#: 2026-09-30T04:17:07+10:00: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-30, 191892 to 192226 (+334), the twins lane reads this
#: twin at 191896 before this change and at 192226 with it (+330): every import
#: request that succeeds, a load or a receipt still current, now records who
#: asked for the source (engine/metta/interop.pl, record_import_request/2
#: writing import_request/3), so unimport! of a package can leave a file
#: another live requester still asks for; it read 191896 against its pin 191892
#: before this change, +4 from an earlier commit of this landing, the takeover
#: read through a module's compiled predicate, inside the allowance [measured
#: 2026-09-30T04:34:13+10:00: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
BUDGET = 192226
