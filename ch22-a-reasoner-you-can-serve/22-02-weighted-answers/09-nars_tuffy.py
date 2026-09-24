"""Purpose: examples/ch22-a-reasoner-you-can-serve/22-02-weighted-answers/09-nars_tuffy.metta in Python: the Tuffy smokers knowledge base.

Ten NARS sentences say who smokes, who is friends with whom, that friends of
smokers smoke, and that smokers get cancer. The claim asks NARS what it makes
of Edward being cancerous, and gets back a truth value and the five premises it
came from.

The knowledge base is ONE equation whose body is a ten-element expression, so
it is written as data: a Python tuple of ten `sentence(...)` calls. NARS spells
four things with punctuation, so each gets a named Python function and the ten
rows then read as the logic they are: `-->` is inheritance, `==>` implication,
`[] p` the property `p`, and U+00D7 the product of two terms. That last head is
written as the escape `\N{MULTIPLICATION SIGN}` and called `multiplication-sign`
in prose, because a bare one is a confusable ruff refuses.

`kb` is ONE equation whose body is DATA, so it goes through the write door as
the atom it is. The punctuation heads are not what keeps it there: measured
2026-08-24, `S["-->"](a, S["[]"](b))` inside a compiled body stores
`(--> $a ([] $b))`. What a compiled body cannot do is CALL the seven host
helpers that make the ten rows readable, because a body is pure atoms, so
compiling `kb` would mean inlining every bracket again. The import takes the
space HANDLE, because a space crosses a term position as itself.
Guarantees:
  - every ordered atom assembled in this file passes one iterable to
    Expression [tested: test_expression_assembles_one_ordered_atom_from_an_iterable; commit=b1599bdc8201a04a3689c1a88707b6f4b53b4d22]
"""

from metta import Expression, S, V, equation, lib


def inheritance(subject, predicate):
    """`(--> subject predicate)`, NARS inheritance."""
    return S["-->"](subject, predicate)


def implication(premise, conclusion):
    """`(==> premise conclusion)`, NARS implication."""
    return S["==>"](premise, conclusion)


def product(left, right):
    """`(multiplication-sign left right)`, the NARS product of two terms.

    The head is the REAL U+00D7, and it matches the rules in
    `lib/lib_nars/pkg.metta` because the engine reads its sources as UTF-8
    whatever the locale, which `twin_coverage.py`'s `_environment` pins to
    `LC_ALL=C` [measured 2026-08-23 under `LC_ALL=C`: 0 U+FFFD replacement
    characters and 12 real U+00D7 heads in the imported library, where the
    locale-dependent reader gave 123 replacements over the 51 `|-` clauses;
    commit=3459d4f6fce103269ff5cdd575edec4bb9e4be95].
    """
    return S["\N{MULTIPLICATION SIGN}"](left, right)


def prop(name):
    """`([] name)`, the NARS property `name`."""
    return S["[]"](name)


def sentence(statement, strength, ident):
    """`(Sentence (statement (stv strength 0.9)) (ident))`, one row of the KB.

    Every row of this example carries the same 0.9 confidence, so only the
    strength varies.
    """
    return S.Sentence((statement, S.stv(strength, 0.9)), (ident,))


def friends(left, right):
    """`(--> (multiplication-sign left right) friend)`, the friendship relation."""
    return inheritance(product(left, right), S.friend)


def smokes(who):
    """`(--> who ([] smokes))`."""
    return inheritance(who, prop(S.smokes))


def twin(m):
    """State ten sentences, then ask NARS about one of their consequences."""
    # The library's file name is `lib_nars.metta`, and the factory attribute
    # door maps every underscore to a hyphen, so the name takes the bracket.
    # !(import! &self (library lib_nars))
    m += lib.nars

    # The knowledge base, as the ten rows it is. `$1` and `$2` in the first two
    # rows are the rules' variables; everything below them is ground.
    # (= (kb)
    #    ((Sentence ((==> (--> (multiplication-sign $1 $2) friend)
    #                     (==> (--> $1 ([] smokes))
    #                          (--> $2 ([] smokes))))
    #                (stv 0.4 0.9)) (1))
    #     (Sentence ((==> (--> $1 ([] smokes))
    #                     (--> $1 ([] cancerous)))
    #                (stv 0.6 0.9)) (2))
    #     (Sentence ((--> (multiplication-sign Anna Bob) friend) (stv 1.0 0.9)) (3))
    #     (Sentence ((--> (multiplication-sign Anna Edward) friend) (stv 1.0 0.9)) (4))
    #     (Sentence ((--> (multiplication-sign Anna Frank) friend) (stv 1.0 0.9)) (5))
    #     (Sentence ((--> (multiplication-sign Edward Frank) friend) (stv 1.0 0.9)) (6))
    #     (Sentence ((--> (multiplication-sign Gary Helen) friend) (stv 1.0 0.9)) (7))
    #     (Sentence ((--> (multiplication-sign Gary Frank) friend) (stv 0.0 0.9)) (8))
    #     (Sentence ((--> Anna ([] smokes)) (stv 1.0 0.9)) (9))
    #     (Sentence ((--> Edward ([] smokes)) (stv 1.0 0.9)) (10))))
    m += equation(S.kb()).to(
        (
            sentence(
                implication(
                    friends(V["1"], V["2"]),
                    implication(smokes(V["1"]), smokes(V["2"])),
                ),
                0.4,
                1,
            ),
            sentence(
                implication(
                    smokes(V["1"]), inheritance(V["1"], prop(S.cancerous))
                ),
                0.6,
                2,
            ),
            sentence(friends(S.Anna, S.Bob), 1.0, 3),
            sentence(friends(S.Anna, S.Edward), 1.0, 4),
            sentence(friends(S.Anna, S.Frank), 1.0, 5),
            sentence(friends(S.Edward, S.Frank), 1.0, 6),
            sentence(friends(S.Gary, S.Helen), 1.0, 7),
            sentence(friends(S.Gary, S.Frank), 0.0, 8),
            sentence(smokes(S.Anna), 1.0, 9),
            sentence(smokes(S.Edward), 1.0, 10),
        )
    )

    # Edward smokes, so Edward is cancerous, and the answer names the five
    # sentences the derivation used.
    # !(test (NARS.Query (kb) (--> Edward ([] cancerous)))
    #        ((stv 0.6 0.48941156079382964) (2 5 6 9 10)))
    assert m.fn["NARS.Query"](
        S.kb(), inheritance(S.Edward, prop(S.cancerous))
    ) == [Expression((S.stv(0.6, 0.48941156079382964), Expression((2, 5, 6, 9, 10))))]


#: Inferences this twin spends, its own tripwire. A PLACEHOLDER: the wave's
#: integrator prices all 218 budgets in one pass on the merged tree, so no
#: figure measured in a single agent's worktree is pinned here
#: [assumed: 1 is a placeholder rather than a measurement; commit=6a3e8b959229afa7adce172704045d1456a40df6].
#: PRICED 2026-08-25 by the corpus pricing pass: tools/twin_coverage.py --measure min-of-3 on p14-integration at the store-wave merge, pinned exactly under the suite's two-sided +-4 deterministic allowance.
#: RE-PINNED 2026-08-25, 586166175 to 586166213, at the flat-door
#: typed-dispatch gate and the library import door landing
#: together: every flat call prices one declaration read through
#: type_declaration_in/3, a declared head's flat call routes
#: through the same call-site typed dispatch the engine's own
#: form runs (metta_py_typed_dispatch_applies/2, the P14.9
#: residue retirement), and an import-bearing twin now spells
#: its import as `m += lib.x` on the write door [measured
#: 2026-08-25 through tools/twin_coverage.py --measure min-of-3
#: on the tree carrying both].
#: RE-PINNED 2026-08-25, 586166213 to 586165716, on the QLF-boot final
#: tree: the engine now boots through engine/qlf_boot.pl, and any
#: boot-content change moves twin counts a few tens through SWI's
#: clause-indexing shape (qlf_boot.pl's header carries the A/B),
#: so the corpus re-pins once on the exact shipping tree
#: [measured 2026-08-25 through tools/twin_coverage.py --measure
#: min-of-3 on the final tree].
#: RE-PINNED 2026-08-25, 586165716 to 586165692, on the release tree:
#: the typed-dispatch question moved engine-side
#: (metta_typed_dispatch_applies/2, one extra frame per direct
#: call), the conformance kit gained the family, source and
#: round-trip laws, extensions gained the spaces([...]) readying
#: moment, and any boot-content change also moves counts a few
#: tens through SWI's clause-indexing shape (qlf_boot.pl's header
#: carries the A/B), so the corpus re-pins once on the exact
#: shipping tree [measured 2026-08-25 through
#: tools/twin_coverage.py --measure min-of-3 after a canonical
#: single-boot QLF regeneration].
#: RE-PINNED 2026-08-25, 586165692 to 586165578, at the release cut: the
#: identity-wire merge (numeric ownership seams, exact-primitive
#: wire, Python operator dispatch), the rules-body staging split
#: (ground folds, op-call staging), and the door-combinations
#: example growing the corpus each move counts through SWI's
#: clause-indexing shape (qlf_boot.pl's header carries the A/B),
#: so the whole corpus re-pins once on the exact release tree
#: [measured 2026-08-25 through tools/twin_coverage.py --measure
#: min-of-3 after a canonical single-boot QLF regeneration].
#: RE-PINNED 2026-08-26, 586165578 to 586175343 (+9765), by the open-tail-index
#: pricing pass, one sweep over the whole corpus after four attributed
#: engine movements: the writable-specialization merge 5c731b03 prices
#: each lazily translated match-bearing equation (~+1,500, first-call
#: probe 2,208 to 3,724 across that merge alone;
#: ai-brief-p14-specializer-translation-tax names the follow-up), the
#: relational-candidate rows of 6917bef7, and the open-tail head-index
#: and deprecation apply-seam fixes recovering their shares; the
#: remainder is compiled-image layout, the class this file's own chain
#: documents [measured: min-of-3 serial fresh processes; command=python extensions/python/tools/twin_coverage.py --measure --rounds 3; fixture=p14-integration open-tail-index pricing tree with engine/reader.so; commit=5ca9ef775933e349f8dc3ec64ec3cb85273a5a00].
#: RE-PINNED 2026-08-26, 586175343 to 586174992 (-351), on the composed
#: async-scheduler tree: a live operation call pays the six-inference
#: admission probe the baseline's p14_async_scheduler_comment prices,
#: and the scheduler, context-callback and exact-memo lifecycle clauses
#: move compiled-image layout by tens, the class this file's chain
#: documents [measured: min-of-3 serial fresh processes; command=python extensions/python/tools/twin_coverage.py --measure --rounds 3; fixture=merged p14-audit-async composed tree with engine/reader.so; commit=5059173b1767600ce4df0f6b7841d88116ee62d3].
#: RE-PINNED 2026-08-26, 586174992 to 586174869 (-123), at the tabling-seam
#: merge: compiled-image layout from the library's dispatch and
#: reflection clauses, the tens-scale class this file's chain documents
#: [measured: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --measure --rounds 3;
#: fixture=tabling-seam merged tree with engine/reader.so;
#: commit=694c12f70da25a28ffe22f9209f1d75d56921f93].
#: RE-PINNED 2026-08-26, 586174869 to 586173138 (-1731), by the
#: specializer argument-walk fix this file's own chain named as the
#: follow-up. Planning a specialization grafts a call argument onto the
#: equation's head pattern one position at a time, and that walk
#: metacalled a yall lambda per position, so each fresh process paid
#: '>>'/4's one-time resolution wherever its first binding plan landed
#: and 13 further inferences at every later position. The walk is
#: first-order now, at 4.0 inferences per position against 17.0.
#: [measured: two independent full-lane rounds on this tree agreeing exactly, against one on the unchanged tree and one on the same tree plus an inert never-called clause; command=python extensions/python/tools/twin_coverage.py; fixture=p14-specializer-tax off 694c12f7 with engine/reader.so and the MORK backend; commit=7e7cac85fee08c117032b2efa5a58a40f3b21365].
#: RE-PINNED 2026-09-01, 586173138 to 4735420 (-581437718), one corpus pricing
#: pass on the merged tree for the 2026-08-27..09-01 engine span
#: (8e75816d..f0744f86), whose four mechanisms are decomposed per lane in
#: benchmarks/baseline.json and ai-parametricity-audit.md passes 10-16: the
#: seam-offer routing and its one-wrap fold (net +8 inferences per evaluation),
#: the strict-scope removal leaving the eval path, the doubling cursor chunk
#: (~3 engine-side inferences per answer replacing per-answer crossings; drains
#: halve on CPU), and the aligned-path work; thirteen twins additionally carry
#: the idiom sweep's local deltas tabulated in the twin-idioms notes, none
#: above 347 [measured 2026-09-01: min-of-3 serial fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=51b792423cec5787614d1488c0793b8a50eaa6fc].
#: RE-PINNED 2026-09-01, 4735420 to 4735304 (-116), the subtract-atom primitive
#: and Counter's grain for -=: a new engine head shifts every twin's load
#: structure, the removal doors changed meaning where a twin spells one, and
#: the quad twin stopped being a different program [measured 2026-09-01: min-
#: of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=c6a40460b1db341198a6150e3600f502831a6e83].
#: RE-PINNED 2026-09-01, 4735304 to 4735313 (+9), generic Python operators now
#: dispatch through live protocols while source twins explicitly name
#: relational engine heads [measured 2026-09-01: min-of-3 serial fresh
#: processes; command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=e3787593132a7ece2d300397045f7415709847c9].
#: RE-PINNED 2026-09-02, 4735313 to 4737638 (+2325), static contract discharge
#: and policy-stable recompilation [measured 2026-09-02: min-of-3 serial fresh
#: processes; command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=c00341f0ff9d83d1b9338ca86ad51708eaf07ebd].
#: RE-PINNED 2026-09-02, 4737638 to 4737853 (+215), static contract discharge
#: with policy checks confined to invalidated contracts [measured 2026-09-02:
#: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=c00341f0ff9d83d1b9338ca86ad51708eaf07ebd].
#: RE-PINNED 2026-09-02, 4737853 to 4737934 (+81), P43 protects both generated
#: policy-check fallbacks from space-local capture [measured 2026-09-02: min-
#: of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=c00341f0ff9d83d1b9338ca86ad51708eaf07ebd].
#: RE-PINNED 2026-09-06, 4737934 to 4695293 (-42641), the one pricing pass at
#: the 0.8.0 release cut, and trunk's own movement rather than any mechanism in
#: this twin: each pin was taken on the base its own branch had, and the
#: September merge wave has moved the engine's clause layout, the evaluation
#: path and the library's write doors since [measured 2026-09-06: min-of-3
#: serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=b96e1a15260b7538a8e42be613bcc5dd0dddd136].
#: RE-PINNED 2026-09-07, 4695293 to 4696274 (+981), trunk's own movement since
#: each twin's pin was taken on the base its own branch had: twenty-two first-
#: parent steps between the 0.8.0 release re-pin and this tree, the prelude's
#: move into Prolog the largest of them at +39 to +115 a twin and -65,806 on
#: the error algebra, the live-views merge -45 on every twin that writes, the
#: catalog and get-type repairs +169 on the types chapter, and the rest SWI
#: clause-indexing layout as the boot image grew; this tree also stores the
#: compiled default space operand as &self rather than a (context-space) call
#: [measured 2026-09-07: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=9010a79b01c9b2a66b96a3952fa378fb3e939dc3].
#: RE-PINNED 2026-09-08, 4696274 to 4695327 (-947), metta_substitute_self/3
#: probes the term for the text &self before walking it, one C write and one C
#: substring probe, where the twins-lane merge's one-equation door (08f6f4df)
#: walked every natively added equation in a named space unconditionally, so
#: every twin that adds or defines an equation in a named space drops by about
#: that equation's size in inferences; the same probe now guards the reader's
#: per-form door (record_translated_from/4), the deferred door's fallback
#: (stored_equation_source/4), a batch's arriving equations
#: (mark_or_translate_equation/5) and the removal probe (remove_equation/6),
#: where the walk is new and skipped for a term that never says &self, and a
#: twin that only removes or re-adds such equations pays the two-inference
#: probe per door crossing instead. Every twin here re-reads its budget on this
#: tree, minimum of three fresh processes [measured 2026-09-08: min-of-3 serial
#: fresh processes; command=python extensions/python/tools/twin_coverage.py
#: --repin; commit=856434d7c1d381b3f3d7cbbd008f46c0d41b61aa].
#: RE-PINNED 2026-09-08, 4695327 to 4693628 (-1699), the evaluation-fuel scope
#: marker is a trailed write (fix/every-intermittent-root-caused, f6e05ca9):
#: `$metta_fuel_scope` is written open with b_setval/2 at scope open and read
#: with b_getval/2 where nb_current/2 used to answer, so an abandoned scope
#: closes itself when an exception unwinds the trail and the cleanup is the
#: fast ordinary exit, and every runnable form pays fewer inferences per scope;
#: a twin drops by about the count of its runnables, and the engine bench reads
#: evaluate and translate 1642 lower each on the same tree. Every twin here re-
#: reads its budget on the merged tree, minimum of three fresh processes
#: [measured 2026-09-08: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=3fc65f02ce807c359f1a52026f950f345da2a9af].
#: RE-PINNED 2026-09-08, 4693628 to 4694831 (+1203), The engine and library
#: predicates now resolve through their owning modules and the explicit engine
#: facade; compiled program lookup crosses the added metta_engine tier
#: [measured 2026-09-08: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=ede2ac57e213a0d4502c6bbbca6227f97015b720].
#: RE-PINNED 2026-09-08, 4694831 to 4694860 (+29), the module boundary merged
#: with trunk's later packages (refactor/engine-and-libraries-as-modules at
#: b64291369): every space now resolves through one more chain link, prelude ->
#: metta_engine -> user, the engine's measured export list is imported into the
#: host tier at boot, the closed-sets watch point costs one inference per
#: &metta write, and a cursor opened by a host pays one transaction check at
#: its door; the branch pinned its budgets on its cut, trunk re-pinned the same
#: twins for the packages that landed after that cut, and only the merged tree
#: carries both, so this entry is where the two chains meet [measured
#: 2026-09-08: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=f1038acdcaf5230b6431c112f38a719d3dc9ef19].
#: RE-PINNED 2026-09-09, 4694860 to 4694895 (+35), structured concurrency
#: landed (feat/structured-concurrency merged at f80cc416d): every space mint
#: records its allocation in the library's lifetime rows, every write and run
#: pays the ownership hook and every drop asks the library whether a scope owns
#: the name, measured on a pristine control as 32 per mint, 2 per write and 44
#: per drop with none per read; measured on the merged tree [measured
#: 2026-09-09: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=0f53926c2fd9f28e188814c84253ad82e13258f7].
#: RE-PINNED 2026-09-08, 4694860 to 4699421 (+4561), Trailing occurrence
#: arguments, token allocation in native writes, exact source withdrawal and
#: transaction-safe shared-table guards change the engine work priced by this
#: twin; answer bags retain the upstream law [measured 2026-09-08: min-of-3
#: serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=7f00ac7932fefa6f380fc8d14ec583ea0c58eff4].
#: RE-PINNED 2026-09-09, 4699421 to 4699456 (+35), tokens as storage landed
#: (feat/tokens-as-storage merged): every native occurrence carries a (t actor
#: generation) token as the trailing argument of its storage clause, minted
#: through flag/3 at the write funnel, and every clause read decodes it,
#: measured on a pristine control of trunk cbf7a958d as 8 more inferences per
#: add, 31 more per remove, 4 more per atom saved and 54 more per atom loaded
#: from a fast image, none per match, plus the merged tree's own lib_thread
#: repairs; measured on the merged tree [measured 2026-09-09: min-of-3 serial
#: fresh processes; command=python extensions/python/tools/twin_coverage.py
#: --repin; commit=50e34286f66c938d89d5d367c6370ad44164c97f].
#: RE-PINNED 2026-09-08, 4694860 to 4694936 (+76), Compiled shipped typing
#: decisions and initial vocabulary facts remove repeated interpretation;
#: indexed vocabulary membership replaces member-list scans; catalog reference
#: checks now respect transaction-local erasure. Paired controls and cut counts
#: are recorded in docs/journal/2026-09-08-what-the-waivers-were-paying-for.md
#: [measured 2026-09-08: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=32650f9ff4d1c4aa0749d8eb8b153e5bb448ee5c].
#: RE-PINNED 2026-09-09, 4694936 to 4694988 (+52), Compile shipped typing
#: decisions and initial vocabulary facts, index vocabulary membership, and
#: reuse the first Python variable binding before indexing additional names;
#: retain type, transaction and variable-identity checks [measured 2026-09-09:
#: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=32650f9ff4d1c4aa0749d8eb8b153e5bb448ee5c].
#: RE-PINNED 2026-09-09, 4694988 to 4699584 (+4596), the compiled vocabulary
#: seed, the membership index, base-module type lookups and the singleton
#: decoder landed (perf/cross-engine-waivers merged): boot publishes the
#: initial vocabulary types from a compiled payload through the tokenized
#: funnel, a warm membership read touches only its own clauses, a base-module
#: type lookup skips the prelude, and a Python decode with one named variable
#: builds no index; per-operation costs of a mint, write, read, drop, run, save
#: and load are unchanged against the trunk in fresh processes; measured on the
#: merged tree, +128 against the trunk's own pin of 4699456 at da0e5755d; the
#: previous number is the branch's cut-time price, and the remaining +4468 is
#: what landed on the trunk between the cut f0d33dcad and da0e5755d, tokens as
#: storage above all [measured 2026-09-09: min-of-3 serial fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=b4341ae382c48ef225f4a52e566af6a9a71757c4].
#: RE-PINNED 2026-09-10, 4699584 to 4699576 (-8), the binding resolves Janus
#: maplist/2 at boot, removing its first-failure autoload; one compiled option
#: policy removes repeated evaluation frames, and keyed dispatch removes
#: repeated transport/context selection. Indexed source-macro hooks preserve
#: unrelated compilation costs. Same-cut controls and all before/after rows are
#: in docs/journal/2026-09-09-the-binding-collapse.md. These three fresh serial
#: processes set file_search_cache_time=9223372036854775807 before boot,
#: matching the validated full-lane/277/workers=32/file-cache-
#: time=9223372036854775807 environment. Workloads, point tolerances and
#: empirical envelopes are unchanged [measured 2026-09-10: min-of-3 serial
#: fresh processes; command=python extensions/python/tools/twin_coverage.py
#: --repin; commit=8358dfc233bf299bb23eceddd94593a62372fe4b].
#: RE-PINNED 2026-09-10, 4699576 to 4699545 (-31), automatic memo
#: reconciliation uses a trailed marker so an inference-limit signal cannot
#: leak its guard. The ordinary dirty drain saves two inferences; the first
#: unset-marker read in each engine invokes SWI's undefined-global hook.
#: Removing the old thread-local predicate also changes catalog-arity
#: enumeration order: five inferences per visited arity in
#: metta_catalog_clause/2 or the partial-list get_native_atom/3 lookup. Same-
#: worktree old/current/restore measurements, native call-site coverage and
#: actual missing-global events separate those costs. See
#: docs/journal/2026-09-09-the-binding-collapse.md. These are three fresh
#: sequential samples per row with 32 concurrent row runners, warmed library
#: artifacts, and file_search_cache_time=9223372036854775807 before boot. Every
#: workload, point allowance and empirical envelope is unchanged [measured
#: 2026-09-10: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=8358dfc233bf299bb23eceddd94593a62372fe4b].
#: RE-PINNED 2026-09-11, 4699545 to 4700793 (+1248), end-of-wave re-pin on the
#: merged tree after FROM's reference rows and four engine units, the closed-
#: set derivations and two host services, BINDING's one native evaluation entry
#: and boot import, W-OBSERVE's observer guard, PERF's receipts batching and
#: cursor retirement, and the three REDS repairs (derived runtime resources and
#: the shared loader, the tool-lane repairs, the corpus example); serial
#: minimum of three fresh processes through the lane's run_twin with
#: file_search_cache_time=9223372036854775807 set before child boot [measured
#: 2026-09-11: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=57f84148ba2684015f052d533f3197eca07b1f7b].
#: RE-PINNED 2026-09-18, 4699545 to 4707042 (+7497), the branch's landings
#: since the 09-10 pins, re-taken on the tip f06186a96: the compiled call law
#: (e59104ace: an Atom argument enters as written, a Python object crosses as a
#: value, a positional call of a bound callee is the plain application and a
#: compiled lambda is bare where it is applied), the one codec at the grounded
#: call (fd0af38f7, whose read of a call site's written keyword tail costs
#: about six inferences per translated site, read once since 7cc8fb863), the
#: runnable cache's dependency index written by the producer (a9e2c06d3, which
#: takes back the walk of the generated code 5416e741d charged at every miss),
#: the host patches of 09-17 and the class units of 09-13 to 09-16 the ladder
#: in docs/journal/2026-09-14-runnable-artifact-dependencies.md places; serial
#: minimum of three fresh processes through the lane's run_twin with
#: file_search_cache_time=9223372036854775807 set before child boot [measured
#: 2026-09-18: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=6944d06ce96fdbcd1faefb640f15dbfa0cf286dd].
#: RE-PINNED 2026-09-18, 4707042 to 4704818 (-2224), the trunk merged
#: (f97c4b0a3, petta's 61 commits since c75181adc) with the definition batch's
#: load pushed as the running load (2da1155e3): every example moved with the
#: engine, 279 of 294 cheaper (median -0.78%), through the compiled runnable
#: envelope executing each runnable form's fixed answer, name and fuel envelope
#: from compiled clauses, the trunk's trailed scopes and compiled context
#: readers (a b_getval/2 read per recorded assertion in place of the branch's
#: thread-local rows), the host listener door and the receipts loop probing the
#: owner once per set; serial minimum of three fresh processes through the
#: lane's run_twin [measured 2026-09-18: min-of-3 serial fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=55d451b670949c2dc9d2ab7bc678f33f21094bd2].
#: RE-PINNED 2026-09-21, 4704818 to 4706657 (+1839), the sixty libraries
#: derived in MeTTa landed with merge 97763e7fa eight hours after the previous
#: pin 55d451b67, so every example importing one now pays a MeTTa derivation
#: where it paid a Prolog body instead, which the 2026-09-14 ruling accepts
#: explicitly as the price of a library that survives the engine swap [measured
#: 2026-09-21: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=6e09cb25d5495c2db3283166e6ce4e07eefecfb2].
#: RE-PINNED 2026-09-24, 4706657 to 4710321 (+3664), placed on the full-
#: configuration first-parent ladder from the pin commit 6e09cb25d: a7955cd07
#: carried lib 629c86c, the library split, which moved every library's surface
#: out of its pkg.metta manifest into lib.metta beside it, so an import reads
#: the manifest and then imports the library's own source as a second file;
#: 54784fded reads the builtin type surface from every .metta in
#: lib_builtin_types' directory, which restored the 195 builtin cost rows the
#: split's manifest-only read had dropped; 63b910f4f added a clause to
#: metta_reference_internal/2 that asks the specializer's ho_specialization/3
#: registry, so every reference grade a load computes pays that lookup, which
#: is how defined-name, documented and undocumented stopped reporting
#: specializer residues; 814b99468 retains a self-call's function_view
#: dependency, so a recursive body is rebuilt as a caller of its own function
#: whenever an arriving equation changes that view (fib's rebuilds 1 to 2 and
#: newtons_method's energy 2 to 4, each reached from spaces:add_function_atom/7
#: through lib_memo's automatic reconcile), the fix that took lib_statistics
#: and lib_random to green; d6e09995c retires a load's package rows from every
#: space but its library home after package_load/3, withdrawing each through
#: metta_remove_atom_reference/1, which uncompiles the row's equation, so every
#: import into an importing space pays that withdrawal; 6167a0fb2 makes import
#: currency transitive: each nested load records an import_nested_source/3 edge
#: to every import still in flight above it, and a cached import answers
#: current only when every nested receipt does; da91bc244 confines an exact
#: removal's selection to its own atom: native_retract_one/2 now records the
#: selected clause's head, a clause/3 lookup per exact removal, and checks each
#: removal made while the selector is live against it, a few inferences per
#: removal (+8 on most twins, +24 to +192 on the library twins that withdraw
#: package rows); where a twin's move exceeds these steps, the remainder is
#: drift that stayed inside its band (four inferences, or its own declared
#: allowance) on every other interval [measured 2026-09-24: min-of-3 serial
#: fresh processes; command=python extensions/python/tools/twin_coverage.py
#: --repin; commit=WORKTREE].
#: RE-PINNED 2026-09-24, 4710321 to 4721838 (+11517), +11,511 at ae1cc8936,
#: where a registration batch of thirteen names or more walks the visible
#: predicate table at two inferences a predicate that asking per name spent
#: inside one C call, and a batch above forty tests each predicate with a dict
#: at one inference fewer than the AVL; +6 at b5eb39acd, whose three new engine
#: exports the registration walk above twelve names reads at two inferences
#: each [measured 2026-09-24: min-of-3 serial fresh processes at HEAD in
#: battery 118 holding the committed tree alone (BATTERY_KEEP='', 11:56); each
#: step read with its parent and child in turn in battery 115 (10:42 to 11:18),
#: 117 (11:01 to 12:10) or 120 (12:04 to 12:13) from committed trees or this
#: job's patched copies of them, none from a working tree; 850d2a660's and
#: 0f6d29ba6's split from provider-carry's own pairs, aaeea643a's on the ladder
#: before 10:05; command=python extensions/python/tools/twin_coverage.py
#: --measure --rounds 3; commit=c7d7244fbe6d32d024ca8c61b336008e98b156ef].
#: RE-PINNED 2026-09-24, 4721838 to 4721909 (+71), +72 at the change this re-
#: pin lands with, which publishes a from row by itself when rows are all a
#: space owes: its 36 predicates visible to filereader's registration walk cost
#: a batch above twelve names 72 inferences, each restricted space's core about
#: 28 a predicate, and every whole publication and face event its ledger's
#: bookkeeping [measured 2026-09-24: the twins lane alone on 8d651070d with the
#: change before this one and with this change too, one after the other in
#: battery 117's one path, every component at its pin; command=sh
#: tools/check.sh twins (twin_coverage.py inside tools/bounded.sh);
#: commit=e4b7448d1f1bd98733f1b04c3906aaa42f35ef1a].
#: RE-PINNED 2026-09-24, 4721909 to 4721885 (-24), the host switch of
#: /home/user/Dev/swipl-patched from .2 to .5, the native host of build 9's 36
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
#: extensions/python/tools/twin_coverage.py --repin; commit=WORKTREE].
BUDGET = 4721885
