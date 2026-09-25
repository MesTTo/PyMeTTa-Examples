"""Purpose: compose grammar values and inspect their ordinary parser functions.

A grammar is a built term, so every form is `S.<name>(...)` and the whole grammar
is an ordinary Python value that can be named and reused. The grammar parameter
is held, which is what lets the term through unevaluated; text is `G("...")`
because these operations are about TEXT. A parse that matches many ways is many
answers, so `list()` is the example's `collapse` and `.one()` the single answer.

`letter?`, `double`, `sum`, `field` and `row` are `@m.define` functions, and the
two that answer a GRAMMAR return the built term, which is what `ref` evaluates
when the parse reaches it.

Guarantees: the same claims as 27-parsing_lib.metta
[tested: python extensions/python/tools/twin_coverage.py examples/ch08-data/08-03-the-shipped-libraries/27-parsing_lib.metta; commit=3c1d074a2069bc150a95cedc1946e0627a17a132].
Open Obligations:
  To Do: None
  Hacks: None
  Future Enhancements: None.
"""

from metta import G, S, V, fn, lib
from metta._errors.errors import MettaError


def twin(m):
    """Build grammars, run them whole and by prefix, and refuse a bad one."""
    m += lib.parsing
    # lib_unicode is beside it for the one primitive that takes a FUNCTION: the
    # classes here are ASCII, and a Unicode class is (char-if f) over unicode-is.
    m += lib.unicode

    def refused(call):
        """Whether evaluating a call raises, which is what if-error reads."""
        try:
            list(m.eval(call))
        except MettaError:
            return True
        return False

    def values(answers):
        """Every answer of a parse, as a list."""
        return list(answers)

    def elements(answers):
        """One answer's expression, as a list."""
        return list(answers.one())

    def rows(answers):
        """One answer's expression of expressions, as a list of tuples."""
        return [tuple(row) for row in answers.one()]

    parse, prefix = m.fn.grammar_parse, m.fn.grammar_parse_prefix
    forms, is_grammar = m.fn.grammar_forms, m.fn.grammar_is

    # A grammar is an expression, and grammar-parse runs it over the whole text.
    # Every way it matches is an answer, so a grammar that does not match answers
    # NOTHING rather than raising, which is what makes the combinators compose.
    assert parse(S.lit(G("ab")), G("ab")) == [G("ab")]
    assert values(parse(S.lit(G("ab")), G("ax"))) == []
    assert values(parse(S.lit(G("ab")), G("abc"))) == []

    # The primitives. A leaf answers the text it matched, except the two numbers,
    # which answer the number, and eos, which answers ().
    assert parse(S.any(), G("x")) == [G("x")]
    assert parse(S.char_in(G("aeiou")), G("e")) == [G("e")]
    assert values(parse(S.char_in(G("aeiou")), G("z"))) == []
    assert parse(S.char_not_in(G("aeiou")), G("z")) == [G("z")]
    assert parse(S.digits(), G("1024")) == [G("1024")]
    assert parse(S.integer(), G("-42")) == [-42]
    assert parse(S.number(), G("3.5")) == [3.5]
    assert parse(S.nonblanks(), G("word")) == [G("word")]
    assert parse(S.blanks(), G("  ")) == [G("  ")]
    assert parse(S.blanks(), G("")) == [G("")]
    assert parse(S.until(G(",")), G("ab")) == [G("ab")]
    assert parse(S.quoted(), G('"a\\nb"')) == [G("a\nb")]
    assert parse(S.rest(), G("whatever")) == [G("whatever")]
    assert elements(parse(S.eos(), G(""))) == []

    # char-if takes a FUNCTION, applied where the grammar was written, so a class
    # the primitives do not have is one line: this is Unicode's own letter class,
    # which holds for a letter no ASCII test would accept.
    @m.define(name="letter?")
    def letter(c):
        return fn.unicode_is(c, S.letter)

    assert elements(parse(S.many1(S.char_if(S["letter?"])), G("héllo"))) == [
        G("h"), G("é"), G("l"), G("l"), G("o"),
    ]
    assert values(parse(S.char_if(S["letter?"]), G("1"))) == []

    # cat runs its parts in turn and answers their values; skip drops one, so a
    # separator contributes nothing to the answer.
    assert elements(parse(S.cat(S.digits(), S.lit(G("-")), S.digits()), G("12-34"))) == [
        G("12"), G("-"), G("34"),
    ]
    assert elements(parse(S.cat(S.digits(), S.skip(S.lit(G("-"))), S.digits()), G("12-34"))) == [
        G("12"), G("34"),
    ]
    assert elements(parse(S.cat(S.skip(S.lit(G("#"))), S.rest()), G("#tag"))) == [G("tag")]

    # alt answers once per branch that matches, which is a superposition and not a
    # first-match choice: a grammar that is ambiguous says so. Both branches match
    # "12" here.
    assert values(parse(S.alt(S.digits(), S.nonblanks()), G("12"))) == [G("12"), G("12")]
    assert values(parse(S.alt(S.lit(G("a")), S.lit(G("b"))), G("a"))) == [G("a")]
    assert values(parse(S.alt(S.any(), S.rest()), G("x"))) == [G("x"), G("x")]
    assert values(parse(S.alt(S.lit(G("a")), S.lit(G("b"))), G("c"))) == []

    # many and many1 repeat, longest match first; optional answers (V) or ().
    assert elements(parse(S.many(S.char_in(G("ab"))), G("aab"))) == [G("a"), G("a"), G("b")]
    assert elements(parse(S.many(S.char_in(G("ab"))), G(""))) == []
    assert values(parse(S.many1(S.char_in(G("ab"))), G(""))) == []
    # The optional's own value is a collection, so a cat over it answers a
    # collection and a string side by side: (("-") "7") signed, (() "7") not.
    signed = list(parse(S.cat(S.optional(S.lit(G("-"))), S.digits()), G("-7")).one())
    assert [list(signed[0]), signed[1]] == [[G("-")], G("7")]
    unsigned = list(parse(S.cat(S.optional(S.lit(G("-"))), S.digits()), G("7")).one())
    assert [list(unsigned[0]), unsigned[1]] == [[], G("7")]

    # sep-by is the list a separator holds, and its values are the parts only.
    assert elements(parse(S.sep_by(S.digits(), S.lit(G(","))), G("1,2,3"))) == [
        G("1"), G("2"), G("3"),
    ]
    assert elements(parse(S.sep_by(S.digits(), S.lit(G(","))), G("1"))) == [G("1")]
    assert elements(parse(S.sep_by(S.digits(), S.lit(G(","))), G(""))) == []

    # between drops both ends and token eats the blanks around a part, which is
    # what a language with free whitespace needs.
    assert parse(S.between(S.lit(G("(")), S.digits(), S.lit(G(")"))), G("(5)")) == [G("5")]
    assert parse(S.token(S.digits()), G("  5 ")) == [G("5")]
    assert elements(parse(S.sep_by(S.token(S.digits()), S.lit(G(","))), G(" 1 , 2 "))) == [
        G("1"), G("2"),
    ]

    # map applies a function to a value and as tags one, so a grammar builds the
    # parse TREE rather than a list of strings to read again.
    @m.define
    def double(n):
        return fn.mul(2, n)

    assert parse(S.map(S.double, S.integer()), G("21")) == [42]
    assert elements(parse(S["as"](S.amount, S.integer()), G("7"))) == [S.amount, 7]
    assert rows(parse(S.many(S["as"](S.digit, S.char_in(G("12")))), G("12"))) == [
        (S.digit, G("1")), (S.digit, G("2")),
    ]

    # A grammar refers to itself through ref, which evaluates a function of no
    # arguments when the parse reaches it, so a nested language is expressible.
    # This one is a parenthesised sum of numbers.
    # The text inside a COMPILED body is a plain Python string literal, not
    # G("("): a G(...) there is a host object the grammar check refuses, where a
    # literal lowers to the String the form wants.
    @m.define
    def sum_():
        return S.alt(
            S.integer(),
            S.between(S.lit("("), S.sep_by(S.ref(S.sum_), S.lit("+")), S.lit(")")),
        )

    assert parse(S.ref(S.sum_), G("7")) == [7]
    assert elements(parse(S.ref(S.sum_), G("(1+2)"))) == [1, 2]
    # A number is a leaf and a nested sum is a collection, so the nesting is read
    # by asking each part whether it holds anything.
    nested = list(parse(S.ref(S.sum_), G("(1+(2+3))")).one())
    assert nested[0] == 1
    assert list(nested[1]) == [2, 3]
    assert values(parse(S.ref(S.sum_), G("(1+)"))) == []

    # A prefix parse answers the value with the unread rest, which is how a reader
    # takes one construct at a time. The longest match comes first.
    assert elements(prefix(S.digits(), G("12ab"))) == [G("12"), G("ab")]
    # The first answer is the greedy one, taken without draining the rest.
    longest = next(iter(prefix(S.many(S.char_in(G("ab"))), G("aab!"))))
    assert [list(longest[0]), longest[1]] == [[G("a"), G("a"), G("b")], G("!")]
    assert elements(prefix(S.rest(), G("all"))) == [G("all"), G("")]
    assert values(prefix(S.lit(G("z")), G("ab"))) == []

    # A real format, in seven forms: a CSV row of quoted or bare fields. The bare
    # field stops at a QUOTE as well as at a comma, which is what makes the
    # grammar unambiguous.
    @m.define
    def field():
        return S.alt(S.quoted(), S.until(',"'))

    @m.define
    def row():
        return S.cat(S.sep_by(S.ref(S.field), S.lit(",")), S.skip(S.eos()))

    assert [list(part) for part in parse(S.ref(S.row), G("a,b,c")).one()] == [
        [G("a"), G("b"), G("c")],
    ]
    assert [list(part) for part in parse(S.ref(S.row), G('"x,y",z')).one()] == [
        [G("x,y"), G("z")],
    ]

    # The vocabulary is data, and a value that is not a grammar is refused BEFORE
    # any text is read, naming the form that is wrong rather than answering
    # nothing.
    assert len(forms().one()) == 26
    assert is_grammar(S.cat(S.digits(), S.eos())) == [True]
    assert is_grammar(S.lit(7)) == [False]
    assert is_grammar(S.many()) == [False]
    assert is_grammar(7) == [False]
    assert refused(S.grammar_parse(S.nosuch(), G("a")))
    assert refused(S.grammar_parse(S.cat(S.digits(), S.nosuch()), G("1")))
    # A number where the text belongs is refused by the DECLARATION rather than by
    # the head, so it answers the engine's own BadArgType; if-error reads both the
    # same way.
    assert list(m.eval(S.grammar_parse(S.digits(), 7))) == [
        S.Error(S.grammar_parse(S.digits(), 7), S.BadArgType(2, S.String, S.Number)),
    ]

    assert is_grammar(S.alt()) == [True]
    assert values(parse(S.alt(), G(""))) == []
    assert parse(S.cat(), G("")) == [()]
    assert prefix(S.many(S.any()), G("ab")) == [
        ((G("a"), G("b")), G("")), ((G("a"),), G("b")), ((), G("ab")),
    ]
    assert parse(S.many(S.skip(S.lit(G("x")))), G("xx")) == [((), ())]
    literal = S["+"](1, 2)
    callback = S["|->"]((V.text,), S.quote(literal))
    assert parse(S.map(callback, S.any()), G("x")) == [literal]
    error = S.Error(S.data, S.code)
    callback = S["|->"]((V.text,), S.quote(error))
    assert parse(S.map(callback, S.any()), G("x")) == [error]
    callback = S["|->"]((V.text,), S.quote(S.Empty))
    assert parse(S.map(callback, S.any()), G("x")) == [S.Empty]
    callback = S["|->"]((V.text,), S.quote((V.x, V.y, V.x)))
    assert m.eval(S["=="](S.grammar_parse(S.map(callback, S.any()), G("x")),
                          S.quote((V.x, V.y, V.x)))) == [True]

    parser = m.fn.grammar_parser(S.any()).one()
    assert m.fn.apply_to(parser, S.quote(((literal, S.Empty),))) == [((literal,), (S.Empty,))]
    parser = m.fn.grammar_parser(S.lit(G("x"))).one()
    assert m.fn.get_metatype(parser) == [S.Expression]
    recipe = m.match(S["="](S.grammar_parser(V.grammar), V.body)).one()
    compile_grammar = m.eval(S["|->"]((recipe.grammar,), recipe.body))[0]
    parser = m.fn.apply_to(compile_grammar, (S.digits(),)).one()
    assert m.fn.apply_to(parser, ((G("1"), G("2"), G("!")),)) == [((G("12"),), (G("!"),))]

    m.add(S.parsing_form(S.pure_value, (S.Atom,), S.parsing_example_value))
    m.add(S[":"](S.parsing_example_value, S["->"](S.Atom, S.Atom, S.Expression)))
    m.add(S["="](S.parsing_example_value(V.value, V.input), S.quote(((V.value,), V.input))))
    assert parse(S.pure_value(literal), G("")) == [literal]
    assert len(forms().one()) == 27
    # This assertion is literal code: grammar-is must not execute the ref target.
    never = (S["|->"], (), (S.assertEqual, False, True))
    assert is_grammar(S.ref(never)) == [True]
    assert refused(S.grammar_parse(S.many(S.cat()), G("")))


#: MEASURED on this branch rather than inherited: this twin is new, so there is
#: no earlier pin to move. The 58 claims cover the fourteen primitives, the
#: eleven combinators, the recursion through ref, the prefix parse and the
#: refusals, and the two sides cost almost exactly the same: a grammar is a TERM,
#: so building one in Python and writing one in MeTTa are the same work, and the
#: five compiled definitions are what the twin pays extra for
#: [measured 2026-09-12: 90024 inferences against the example's 89803, minimum of
#: three serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --measure --rounds 3
#: examples/ch08-data/08-03-the-shipped-libraries/27-parsing_lib.metta;
#: fixture=lib_parsing at its functional commit, artifacts purged before the run;
#: commit=7bdd5ace3f8272c2806ac0b925e56a78dc0894a8].
#: RE-PINNED 2026-09-12, 90024 to 89855 (-169), the greedy prefix answer taken
#: through next(iter(...)) rather than a list slice, which stops draining the
#: rest [measured 2026-09-12: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=7bdd5ace3f8272c2806ac0b925e56a78dc0894a8].
#: RE-PINNED 2026-09-14, 89855 to 4666804 (+4576949), Parsing derives written
#: callable grammars and literal contributions in MeTTa, adding sixteen
#: executable claims [measured 2026-09-14: min-of-3 serial fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=3c1d074a2069bc150a95cedc1946e0627a17a132].
#: RE-PINNED 2026-09-14, 4666804 to 4666705 (-99), The parsing twin uses
#: shared-context identity comparison and holds the ref assertion as literal
#: code [measured 2026-09-14: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=3c1d074a2069bc150a95cedc1946e0627a17a132].
#: RE-PINNED 2026-09-14, 4666705 to 4701005 (+34300), String now derives nine
#: text recipes through MeTTa equations, with one function parameter for
#: padding and complete validation before empty construction; all import
#: consumers are measured after the provider change [measured 2026-09-14: min-
#: of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=118b805aedbee6de22be4f6131d97c3d6b9156de].
#: RE-PINNED 2026-09-14, 4701005 to 4701011 (+6), Closure publishes the shared
#: rendering and IEEE services, refreshes the callable projection and annotates
#: native protocol domains; every direct and transitive library consumer is
#: measured again [measured 2026-09-14: min-of-3 serial fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=b7866b4d874879ff0cb212eb1c6af60dddaa39c6].
#: RE-PINNED 2026-09-21, 4701011 to 4701104 (+93), the sixty libraries derived
#: in MeTTa landed with merge 97763e7fa eight hours after the previous pin
#: 55d451b67, so every example importing one now pays a MeTTa derivation where
#: it paid a Prolog body instead, which the 2026-09-14 ruling accepts
#: explicitly as the price of a library that survives the engine swap [measured
#: 2026-09-21: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=6e09cb25d5495c2db3283166e6ce4e07eefecfb2].
#: RE-PINNED 2026-09-24, 4701104 to 4735279 (+34175), placed on the full-
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
#: the 20 commits 6167a0fb2..864c4bac0, where the sweep puts the probes' only
#: step at e1acacad2, which clears a space's import bookkeeping from the module
#: that owns it; f2822e2ae: the boot host check (metta_require_patched_host,
#: called once in qlf_load_engine) adds about 10.3k inferences to every later
#: load of a library's Prolog half; measured 507,704 to 518,008 on text_lib's
#: twin, mechanism below the predicate not isolated; the commits
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
#: RE-PINNED 2026-09-24, 4735279 to 4672532 (-62747), 0a81c782f loads a
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
#: RE-PINNED 2026-09-24, 4672532 to 4673869 (+1337), both: 2126ab6 installs the
#: library's native half through lib/_support/native_install.pl, loaded once
#: per process, and 0847c3d4c with 984eabe23 decides on its first read each
#: platform capability the twin reads, in a flag under a mutex; a792976 loads
#: process, socket and HTTP's libraries through the census and refuses per
#: call, which moves process_lib by 44 and socket_lib by -603 [measured
#: 2026-09-24: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=d832d20e8edfdad28ad52815757ba9e685ad2de3].
#: RE-PINNED 2026-09-24, 4673869 to 4691106 (+17237), +36 at aaeea643a, whose
#: seat 5b0b92274 adds twelve predicates to module user that filereader's
#: registration walk above forty names reads at three inferences each; +9 at
#: b7e3d3bcb, whose three new metta_engine predicates that walk reads at three
#: inferences each; +17,174 at ae1cc8936, where a registration batch of
#: thirteen names or more walks the visible predicate table at two inferences a
#: predicate that asking per name spent inside one C call, and a batch above
#: forty tests each predicate with a dict at one inference fewer than the AVL;
#: +18 at b5eb39acd, whose three new engine exports the registration walk above
#: twelve names reads at two inferences each [measured 2026-09-24: min-of-3
#: serial fresh processes at HEAD in battery 118 holding the committed tree
#: alone (BATTERY_KEEP='', 11:56); each step read with its parent and child in
#: turn in battery 115 (10:42 to 11:18), 117 (11:01 to 12:10) or 120 (12:04 to
#: 12:13) from committed trees or this job's patched copies of them, none from
#: a working tree; 850d2a660's and 0f6d29ba6's split from provider-carry's own
#: pairs, aaeea643a's on the ladder before 10:05; command=python
#: extensions/python/tools/twin_coverage.py --measure --rounds 3;
#: commit=c7d7244fbe6d32d024ca8c61b336008e98b156ef].
#: RE-PINNED 2026-09-24, 4691106 to 4689561 (-1545), d4a365c16 holds the
#: support graph's visited set and the reference refresh's space sets in SWI
#: tries instead of library(nb_set): a membership check is one foreign call
#: where nb_set probed in Prolog, four inferences a step past a taken slot,
#: from a slot a library space's path-bearing name decided, and a walk over a
#: node or two pays a few inferences more for the trie's setup (-1266); gate-
#: perf's d781eab8f carries an exact removal's selected head from the code that
#: selected it, so a withdrawal copies its equation once: 23 inferences fewer
#: for each equation removal the twin adopts and 4 for each it selects (-345);
#: the packages job's 90be572a9 and 4003462fe register Prolog through one
#: engine service: +22 for each library the twin imports (ten new engine
#: predicates and two user imports in the registration walk at two inferences
#: each, less the retired loaded_extension_file/2), and 146 inferences for a
#: Prolog file's origin or 220 for a text's SHA-256 on a twin that registers
#: Prolog (+66); each step read serially on its own committed tree, from gate-
#: perf's pin at c7d7244fb, and the fixed tree 4ff69551e reads what 4003462fe
#: does [measured 2026-09-24: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=4ff69551e0e226442cf7257b96af858adda957a4].
#: RE-PINNED 2026-09-24, 4689561 to 4689567 (+6), +6 at the change this re-pin
#: lands with, which groups a whole reference face's heads in one pass over its
#: sorted entries where each head searched the whole face, and whose three
#: imports into the engine module are one more predicate filereader's
#: registration walk reads above twelve names, pairs_keys/2, and three a
#: restricted space's core steps over as it enumerates that module's predicates
#: [measured 2026-09-24: the twins lane alone on the base 8d651070d and on the
#: base with this change, one after the other in battery 117's one path, every
#: component at its pin; command=sh tools/check.sh twins (twin_coverage.py
#: inside tools/bounded.sh); commit=8bda9d5525a8174a8304376e111df8da258076a9].
#: RE-PINNED 2026-09-24, 4689567 to 4689896 (+329), +329 at the change this re-
#: pin lands with, which publishes a from row by itself when rows are all a
#: space owes: its 36 predicates visible to filereader's registration walk cost
#: a batch above twelve names 72 inferences, each restricted space's core about
#: 28 a predicate, and every whole publication and face event its ledger's
#: bookkeeping [measured 2026-09-24: the twins lane alone on 8d651070d with the
#: change before this one and with this change too, one after the other in
#: battery 117's one path, every component at its pin; command=sh
#: tools/check.sh twins (twin_coverage.py inside tools/bounded.sh);
#: commit=e4b7448d1f1bd98733f1b04c3906aaa42f35ef1a].
#: RE-PINNED 2026-09-24, 4689896 to 4689816 (-80), the host switch of
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
#: RE-PINNED 2026-09-25, 4689816 to 4689822 (+6), the pragma refusal defines
#: require_metta_pragma_capability/2 in the engine module, and on the same tree
#: defining it without calling it moves this twin by the whole of the change's
#: move, so the cost is one more engine predicate and functor met through the
#: engine's walks over its predicate and functor tables, among them
#: filereader:existing_predicate_arities/2, which charges two inferences for
#: each predicate visible from the loading module at every load of a source
#: registering more than twelve names (i-arity-walk-all-predicates); the
#: change's work at a pragma write does not reach this twin [measured
#: 2026-09-25T00:48:26+10:00: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-25, 4689822 to 4689883 (+61), the py-* doors change makes
#: more predicates visible from filereader, and
#: filereader:existing_predicate_arities/2 walks every predicate visible there
#: at two inferences each whenever a source registering more than twelve names
#: loads: on one tree the change's new engine predicates alone, defined with
#: their two boot uses taken out, move this twin by 16 for each such load and
#: the whole change by 20, each give or take one or two inferences that move
#: with where the new names land in SWI's tables and that SWI's profiler, which
#: lists no system predicate, does not place (i-arity-walk-all-predicates)
#: [measured 2026-09-25T02:56:35+10:00: min-of-3 serial fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-25, 4689883 to 4689874 (-9), the registration refusal kind
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
#: the base [measured 2026-09-25T06:29:01+10:00: min-of-3 serial fresh
#: processes; command=python extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-25, 4689874 to 4685155 (-4719), the host evaluation door
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
#: more than twelve names [measured 2026-09-25T06:47:28+10:00: min-of-3 serial
#: fresh processes; command=python extensions/python/tools/twin_coverage.py
#: --repin].
#: RE-PINNED 2026-09-25, 4685155 to 4685185 (+30), Runtime.reclaim(), the
#: reclamation barrier metta_py_reclaim/1, adds five predicates to user, and
#: existing_predicate_arities/2 walks every user predicate about twice per
#: large load (i-arity-walk-all-predicates) [measured
#: 2026-09-25T11:25:25+10:00: one full twins lane before this commit and one
#: with it, the two read on one battery path at the landing's HEAD;
#: command=python extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-25, 4685185 to 4685251 (+66), both specializer doors
#: prepare a specialization's predicate with
#: spaces:metta_prepare_function_predicate/3 before asserting its clauses
#: [measured 2026-09-25T11:29:10+10:00: one full twins lane before this commit
#: and one with it, the two read on one battery path at the landing's HEAD;
#: command=python extensions/python/tools/twin_coverage.py].
BUDGET = 4685251
