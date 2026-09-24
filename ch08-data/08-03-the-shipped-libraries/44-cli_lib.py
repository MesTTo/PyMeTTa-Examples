"""Purpose: typed options, literal tokens, custom converters and generated help.

Guarantees: the same 64 claims as 44-cli_lib.metta.
[tested: python extensions/python/tools/twin_coverage.py examples/ch08-data/08-03-the-shipped-libraries/44-cli_lib.metta; commit=83b7589a6766210414ceca14dfb9846b28c2ef78].
"""

from metta import FALSE, TRUE, G, S, V, arrow, lib, typed
from metta._errors.errors import MettaError


def twin(m):
    """Preserve argument spelling and validate options through their declarations."""
    m += lib.string
    m += lib.cli

    def option(key, *fields):
        """One native-shaped declaration with its required key."""
        return (S.opt(key), *fields)

    specification = (
        option(S.count, S.type(S.integer), S.shortflags((S.n,)),
               S.longflags((S.count, S.count2)), S.default(1),
               S.meta(G("N")), S.help(G("Item count"))),
        option(S.verbose, S.type(S.boolean), S.shortflags((S.v,)),
               S.longflags((S.verbose,)), S.default(FALSE)),
        option(S.name, S.shortflags((S.s,)), S.longflags((S.name,)), S.default(G("guest"))),
    )
    m.add(typed(S.cli_main, arrow(S.Expression, S.Symbol, S.Expression)),
          S["="](S.cli_main(V.arguments, V.duplicates),
                  S.cli_parse(specification, V.arguments, V.duplicates)),
          S["="](S.cli_plus(V.increment, V.text), S["+"](V.increment, S.parse_number(V.text))))

    def scan(arguments, policy=S.keeplast):
        """Use the same application declaration and repeat policy as the example."""
        return m.fn.cli_main(arguments, policy)

    def refused(call):
        """Keep the native failure and its context for the refusal claims."""
        try:
            list(m.eval(call))
        except MettaError as error:
            return error
        return None

    parse, help_text = m.fn.cli_parse, m.fn.cli_help
    count, verbose, name = S.count, S.verbose, S.name
    defaults = (count(1), verbose(FALSE), name(G("guest")))
    missing_count = (verbose(FALSE), name(G("guest")))

    assert m.fn.cli_types() == [(S.boolean, S.integer, S.float, S.atom, S.string, S.metta)]
    assert scan(()) == [(defaults, ())]
    assert scan((G("--count"), G("3"), G("file"))) == [((*missing_count, count(3)), (G("file"),))]
    assert scan((G("-n4"), G("--name=π🙂"), G("-v"), G("input"))) == [((count(4), name(G("π🙂")), verbose(TRUE)), (G("input"),))]
    assert scan((G("--count2=7"), G("--no-verbose")), S.keepall) == [((name(G("guest")), count(7), verbose(FALSE)), ())]
    assert scan((G("-n"), G("2"), G("--name=a"), G("--count=3")), S.keepfirst) == [((verbose(FALSE), count(2), name(G("a"))), ())]
    assert scan((G("-n"), G("2"), G("--name=a"), G("--count=3"))) == [((verbose(FALSE), name(G("a")), count(3)), ())]
    assert scan((G("-n"), G("2"), G("--name=a"), G("--count=3")), S.keepall) == [((verbose(FALSE), count(2), name(G("a")), count(3)), ())]
    assert scan((G("--verbose=false"), G("-vtrue"), G("--no-verbose")), S.keepall) == [((count(1), name(G("guest")), verbose(FALSE), verbose(TRUE), verbose(FALSE)), ())]

    assert scan((G("--name"), G(""))) == [((count(1), verbose(FALSE), name(G(""))), ())]
    assert scan((G("--name="),)) == [((count(1), verbose(FALSE), name(G(""))), ())]
    assert scan((G("--name=-v"),)) == [((count(1), verbose(FALSE), name(G("-v"))), ())]
    assert scan((G("-s--count"),)) == [((count(1), verbose(FALSE), name(G("--count"))), ())]
    assert scan((G("--count"), G("-3"))) == [((*missing_count, count(-3)), ())]
    assert scan((G("before"), G("--"), G("--count"), G("3"), G(""))) == [(defaults, (G("before"), G("--count"), G("3"), G(""),))]
    assert parse((), (G("-2"), G("-1.5"), G("-"), G(""),), S.keepall) == [((), (G("-2"), G("-1.5"), G("-"), G(""),))]
    assert parse((), (G("--"), G("--"), G(""),), S.keepall) == [((), (G("--"), G(""),))]
    text = m.fn.string_from_codes((97, 0, 98)).one()
    argument = m.fn.string_join(G(""), (G("--name="), text)).one()
    parsed = m.fn.cli_main((argument,), S.keeplast)[0]
    assert m.fn["=alpha"](parsed, ((count(1), verbose(FALSE), name(text)), ())) == [True]
    assert scan((G("--name=a=b=c"),)) == [((count(1), verbose(FALSE), name(G("a=b=c"))), ())]
    assert parse((option(S.missing, S.longflags((S.missing,))),), (), S.keepall) == [((), ())]
    assert parse((option(S.symbol, S.type(S.atom), S.default(S["_"])),
                  option(S.text, S.default(G("_")))), (), S.keepall) == [((S.symbol(S["_"]), S.text(G("_"))), ())]
    assert parse((option(S.short, S.shortflags((S.x,))), option(S.long, S.longflags((S.x,)))),
                 (G("-x"), G("left"), G("--x"), G("right"),), S.keepall) == [((S.short(G("left")), S.long(G("right"))), ())]
    assert parse((option(S.digit, S.type(S.integer), S.shortflags((G("2"),))),),
                 (G("-2"), G("7"),), S.keepall) == [((S.digit(7),), ())]
    assert parse((option(S.mark, S.longflags((S["9?"],))),), (G("--9?=yes"),), S.keepall) == [((S.mark(G("yes")),), ())]
    assert parse((option(S.verbose, S.type(S.boolean), S.longflags((S.verbose,))),
                  option(S.named, S.longflags((S.no_verbose,)))),
                 (G("--no-verbose"), G("literal"),), S.keepall) == [((S.named(G("literal")),), ())]
    assert parse((option(S.ratio, S.type(S.float), S.longflags((S.ratio,))),),
                 (G("--ratio=1.25"),), S.keepall) == [((S.ratio(1.25),), ())]
    assert parse((option(S.mode, S.type(S.atom), S.longflags((S.mode,))),),
                 (G("--mode=scan"),), S.keepall) == [((S.mode(S.scan),), ())]

    literal = (option(S.value, S.type(S.metta), S.longflags((S.value,))),)
    assert parse(literal, (G("--value=(+ 1 2)"),), S.keepall) == [((S.value(S["+"](1, 2)),), ())]
    assert parse(literal, (G("--value=()"),), S.keepall) == [((S.value(()),), ())]
    parsed = parse(literal, (G("--value=(row $x $x)"),), S.keepall)[0]
    assert m.fn["=alpha"](parsed, ((S.value(S.row(V.a, V.a)),), ())) == [True]
    positive = S.Annotated(S.Number, S.Gt(0))
    sized = (option(S.size, S.type(S.parse(positive, S.parse_number)),
                    S.longflags((S.size,)), S.default(1)),)
    assert parse(sized, (G("--size=3"),), S.keepall) == [((S.size(3),), ())]
    assert parse(sized, (), S.keepall) == [((S.size(1),), ())]
    uppercase = S["|->"]((V.x,), S.string_upper(V.x))
    assert parse((option(S.text, S.type(S.parse(S.String, uppercase)), S.longflags((S.text,))),),
                 (G("--text=hello"),), S.keepall) == [((S.text(G("HELLO")),), ())]
    assert parse((option(S.size, S.type(S.parse(S.Number, S.cli_plus(10))), S.longflags((S.size,))),),
                 (G("--size=5"),), S.keepall) == [((S.size(15),), ())]
    arguments = m.fn.quote((G("--count=9"),))[0]
    assert m.fn.cli_main(arguments, S.keeplast) == [((*missing_count, count(9)), ())]
    assert m.fn.get_metatype(m.fn["cli-arguments!"]()[0]) == [S.Expression]

    assert help_text(()) == [G("")]
    assert help_text((option(S.hidden, S.default(G("local"))),)) == [G("")]
    described = option(S.count, S.type(S.integer), S.shortflags((S.n,)),
                       S.default(1), S.meta(G("N")), S.help(G("Item count")))
    assert m.fn.string_contains(help_text(((*described, S.longflags((S.count,))),))[0], G("--count")) == [True]
    assert m.fn.string_contains(help_text((described,))[0], G("N:integer=1")) == [True]
    assert m.fn.string_contains(help_text((option(S.text, S.longflags((S.text,)), S.default(G("π")),
                                              S.help((G("First line"), G("Second line"),))),))[0], G("Second line")) == [True]
    empty_decoder = S["|->"]((V.x,), S.empty())
    assert m.fn.string_contains(help_text((option(S.text, S.type(S.parse(S.String, empty_decoder)),
                                         S.longflags((S.text,))),))[0], G("String")) == [True]

    error = refused(S.cli_main((G("--count"), G("bad")), S.keeplast))
    assert error is not None and "--count" in str(error) and "declared type" in str(error)
    assert refused(S.cli_main((G("--name"),), S.keeplast)) is not None
    assert refused(S.cli_main((G("--name"), G("--verbose"),), S.keeplast)) is not None
    assert refused(S.cli_main((G("--unknown"),), S.keeplast)) is not None
    assert refused(S.cli_main((G("--bad?"),), S.keeplast)) is not None
    assert refused(S.cli_main((G("-n=3"),), S.keeplast)) is not None
    assert refused(S.cli_main((G("-vn"),), S.keeplast)) is not None
    assert refused(S.cli_main((G("--count=bad"), G("--count=3"),), S.keeplast)) is not None
    assert refused(S.cli_parse((), (), S.unknown)) is not None
    assert refused(S.cli_parse((option(S.x), option(S.x)), (), S.keepall)) is not None
    assert refused(S.cli_parse((option(S.x, S.type(S.integer), S.type(S.integer)),), (), S.keepall)) is not None
    assert refused(S.cli_parse((option(S.x, S.longflags((S.same,))), option(S.y, S.longflags((S.same,)))), (), S.keepall)) is not None
    assert refused(S.cli_parse((option(S.x, S.longflags((G("bad name"),))),), (), S.keepall)) is not None
    assert refused(S.cli_parse((option(S.x, S.wat(1)),), (), S.keepall)) is not None
    assert refused(S.cli_parse(((S.type(S.string),),), (), S.keepall)) is not None
    assert refused(S.cli_parse((option(S.x, S.type(S.unknown)),), (), S.keepall)) is not None
    assert refused(S.cli_parse((option(S.x, S.type(S.integer), S.default(G("bad"))),), (), S.keepall)) is not None
    assert refused(S.cli_parse((option(S.x, S.type(S.metta), S.longflags((S.x,))),), (G("--x=1 2"),), S.keepall)) is not None
    assert refused(S.cli_parse((option(S.x, S.type(S.parse(positive, S.parse_number)), S.longflags((S.x,))),), (G("--x=0"),), S.keepall)) is not None
    assert refused(S.cli_parse((option(S.x, S.type(S.parse(S.String, empty_decoder)), S.longflags((S.x,))),), (G("--x=a"),), S.keepall)) is not None
    two = S["|->"]((V.x,), S.superpose((1, 2)))
    assert refused(S.cli_parse((option(S.x, S.type(S.parse(S.Number, two)), S.longflags((S.x,))),), (G("--x=a"),), S.keepall)) is not None
    wrong = S["|->"]((V.x,), G("wrong"))
    assert refused(S.cli_parse((option(S.x, S.type(S.parse(S.Number, wrong)), S.longflags((S.x,))),), (G("--x=a"),), S.keepall)) is not None


#: MEASURED: all 64 claims, including custom conversion and schema refusals.
#: The example pays 347414 inferences.
#: [measured: 367784 inferences, minimum of three fresh serial processes;
#: command=python extensions/python/tools/twin_coverage.py --measure --rounds 3
#: examples/ch08-data/08-03-the-shipped-libraries/44-cli_lib.metta;
#: fixture=lib_cli with engine/lib QLF artifacts purged; commit=83b7589a6766210414ceca14dfb9846b28c2ef78].
#: RE-PINNED 2026-09-14, 367784 to 392348 (+24564), String now derives nine
#: text recipes through MeTTa equations, with one function parameter for
#: padding and complete validation before empty construction; all import
#: consumers are measured after the provider change [measured 2026-09-14: min-
#: of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=118b805aedbee6de22be4f6131d97c3d6b9156de].
#: RE-PINNED 2026-09-21, 392348 to 477457 (+85109), the sixty libraries derived
#: in MeTTa landed with merge 97763e7fa eight hours after the previous pin
#: 55d451b67, so every example importing one now pays a MeTTa derivation where
#: it paid a Prolog body instead, which the 2026-09-14 ruling accepts
#: explicitly as the price of a library that survives the engine swap [measured
#: 2026-09-21: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=6e09cb25d5495c2db3283166e6ce4e07eefecfb2].
#: RE-PINNED 2026-09-21, 477457 to 479123 (+1666), this library gained an
#: error:has_type/2 clause for its own cli_value type and its vendored parser
#: now tests a declared default with is_of_type/2 instead of negating
#: must_be/2, which closed eight development-build failures; the extra clause
#: is consulted once per declared option, and the pin it moves past was
#: measured before that change [measured 2026-09-21: min-of-3 serial fresh
#: processes; command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=8d2e8bb94da53a1a35c79d440cc09ef56f46153e].
#: RE-PINNED 2026-09-24, 479123 to 500638 (+21515), placed on the full-
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
#: RE-PINNED 2026-09-24, 500638 to 428632 (-72006), 0a81c782f loads a library's
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
#: RE-PINNED 2026-09-24, 428632 to 429261 (+629), 2126ab6 installs every
#: library's native half through lib/_support/native_install.pl, which tests
#: for a statically linked host and loads library(shlib) only where there is
#: none, where each half used to load shlib itself, so a process importing a
#: library with a native half now loads that module once [measured 2026-09-24:
#: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=d832d20e8edfdad28ad52815757ba9e685ad2de3].
#: RE-PINNED 2026-09-24, 429261 to 440786 (+11525), +11,519 at ae1cc8936, where
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
#: RE-PINNED 2026-09-24, 440786 to 440622 (-164), d4a365c16 holds the support
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
#: RE-PINNED 2026-09-24, 440622 to 440797 (+175), +173 at the change this re-
#: pin lands with, which publishes a from row by itself when rows are all a
#: space owes: its 36 predicates visible to filereader's registration walk cost
#: a batch above twelve names 72 inferences, each restricted space's core about
#: 28 a predicate, and every whole publication and face event its ledger's
#: bookkeeping [measured 2026-09-24: the twins lane alone on 8d651070d with the
#: change before this one and with this change too, one after the other in
#: battery 117's one path, every component at its pin; command=sh
#: tools/check.sh twins (twin_coverage.py inside tools/bounded.sh);
#: commit=WORKTREE].
BUDGET = 440797
