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
BUDGET = 202911
