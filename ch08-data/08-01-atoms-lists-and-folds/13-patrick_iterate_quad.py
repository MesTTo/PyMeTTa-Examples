"""Purpose: examples/ch08-data/08-01-atoms-lists-and-folds/13-patrick_iterate_quad.metta in Python: a triangular walk under iterate.

The step carries a triple, (t i sum), and walks the lower triangle of a
thousand-by-thousand grid: when i reaches t the row is finished, so t advances
and i restarts, and otherwise i advances. `iterate` runs it n(n+1)/2 times and
`last` takes the final state; a compiled body says both through the STATIC `fn`
namespace and passes the step by its `S` name, because the step is data there.

`quad-step` stays at the container door, and that is the residue entry this
file carries: its head destructures its second argument, where a decorated
function's parameters are always plain variables.

The division is `fn["/"]` rather than Python's `/` for the reason the body
says: a compiled `/` is Python's true division and hands `iterate` a float
bound, which is a different and enormously slower program than the example's.
Inside that built body the conditional is `if_`, the keyword builder with the
engine's own two-or-three arity, and the comparison is `S.eq`, the operator's
WORD. Both are what a STORED equation needs: Python's conditional expression
evaluates rather than building, and `V.i == V.t` is Python's own structural
equality between two variables, which is False. The arithmetic around them is
Python's own, because an operator with a VARIABLE operand builds the term.
Open Obligations:
  To Do: None
  Hacks: None
  Future Enhancements: None.
"""

from metta import Expression, S, V, equation, fn, if_, lib


def twin(m):
    """Sum t*i over the lower triangle of a thousand rows."""
    m += lib.patrick

    m += equation(S.quad_step(V.dummy, Expression((V.t, V.i, V.sum)))).to(
        if_(
            S.eq(V.i, V.t),
            Expression((V.t + 1, 1, V.sum + V.t * V.i)),
            Expression((V.t, V.i + 1, V.sum + V.t * V.i)),
        )
    )

    @m.define
    def quad_sum(n: int) -> int:
        # (= (quad-sum $n) (last (iterate 0 (/ (* $n (+ $n 1)) 2) (1 1 0) quad-step)))
        # rung: the engine's own `/` by name, because Python's `/` is TRUE
        # division and a compiled body says so faithfully, emitting the
        # float-forcing (* 1.0 ...) that hands `iterate` a float bound where
        # the example hands it an integer. That is a different program: it
        # answers the same 125417041750 and took over 280 SECONDS against the
        # example's 0.29 [measured 2026-09-01]. `//` would be exact and fast
        # but stores `floor-div` where the example stores `/`, so the twin
        # would stop mirroring it; naming the head keeps the equation
        # identical and the walk integer.
        return fn.last(fn.iterate(0, fn["/"](n * (n + 1), 2), (1, 1, 0), S.quad_step))

    assert quad_sum(1000) == [125417041750]


#: A PLACEHOLDER, not a measurement. The twins wave re-authored this file and
#: the integrator prices every budget in one pass on the merged tree, so a
#: figure measured here would pin a tree that does not ship
#: [assumed: this twin's inference cost is unmeasured on this branch;
#: commit=1e264c186c531e69acde5ad03ff6a79210626df4].
#: PRICED 2026-08-25 by the corpus pricing pass: tools/twin_coverage.py --measure min-of-3 on p14-integration at the store-wave merge, pinned exactly under the suite's two-sided +-4 deterministic allowance.
#: RE-PINNED 2026-08-25, 55099208 to 55099246, at the flat-door
#: typed-dispatch gate and the library import door landing
#: together: every flat call prices one declaration read through
#: type_declaration_in/3, a declared head's flat call routes
#: through the same call-site typed dispatch the engine's own
#: form runs (metta_py_typed_dispatch_applies/2, the P14.9
#: residue retirement), and an import-bearing twin now spells
#: its import as `m += lib.x` on the write door [measured
#: 2026-08-25 through tools/twin_coverage.py --measure min-of-3
#: on the tree carrying both].
#: RE-PINNED 2026-08-25, 55099246 to 55099188, on the QLF-boot final
#: tree: the engine now boots through engine/qlf_boot.pl, and any
#: boot-content change moves twin counts a few tens through SWI's
#: clause-indexing shape (qlf_boot.pl's header carries the A/B),
#: so the corpus re-pins once on the exact shipping tree
#: [measured 2026-08-25 through tools/twin_coverage.py --measure
#: min-of-3 on the final tree].
#: RE-PINNED 2026-08-25, 55099188 to 55099157, on the release tree:
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
#: RE-PINNED 2026-08-25, 55099157 to 55099146, at the release cut: the
#: identity-wire merge (numeric ownership seams, exact-primitive
#: wire, Python operator dispatch), the rules-body staging split
#: (ground folds, op-call staging), and the door-combinations
#: example growing the corpus each move counts through SWI's
#: clause-indexing shape (qlf_boot.pl's header carries the A/B),
#: so the whole corpus re-pins once on the exact release tree
#: [measured 2026-08-25 through tools/twin_coverage.py --measure
#: min-of-3 after a canonical single-boot QLF regeneration].
#: RE-PINNED 2026-08-26, 55099146 to 55101032 (+1886), by the open-tail-index
#: pricing pass, one sweep over the whole corpus after four attributed
#: engine movements: the writable-specialization merge 5c731b03 prices
#: each lazily translated match-bearing equation (~+1,500, first-call
#: probe 2,208 to 3,724 across that merge alone;
#: ai-brief-p14-specializer-translation-tax names the follow-up), the
#: relational-candidate rows of 6917bef7, and the open-tail head-index
#: and deprecation apply-seam fixes recovering their shares; the
#: remainder is compiled-image layout, the class this file's own chain
#: documents [measured: min-of-3 serial fresh processes; command=python extensions/python/tools/twin_coverage.py --measure --rounds 3; fixture=p14-integration open-tail-index pricing tree with engine/reader.so; commit=5ca9ef775933e349f8dc3ec64ec3cb85273a5a00].
#: RE-PINNED 2026-08-26, 55101032 to 55101004 (-28), on the composed
#: async-scheduler tree: a live operation call pays the six-inference
#: admission probe the baseline's p14_async_scheduler_comment prices,
#: and the scheduler, context-callback and exact-memo lifecycle clauses
#: move compiled-image layout by tens, the class this file's chain
#: documents [measured: min-of-3 serial fresh processes; command=python extensions/python/tools/twin_coverage.py --measure --rounds 3; fixture=merged p14-audit-async composed tree with engine/reader.so; commit=5059173b1767600ce4df0f6b7841d88116ee62d3].
#: RE-PINNED 2026-08-26, 55101004 to 55100988 (-16), at the tabling-seam
#: merge: compiled-image layout from the library's dispatch and
#: reflection clauses, the tens-scale class this file's chain documents
#: [measured: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --measure --rounds 3;
#: fixture=tabling-seam merged tree with engine/reader.so;
#: commit=694c12f70da25a28ffe22f9209f1d75d56921f93].
#: RE-PINNED 2026-08-26, 55100988 to 55099479 (-1509), by the
#: specializer argument-walk fix this file's own chain named as the
#: follow-up. Planning a specialization grafts a call argument onto the
#: equation's head pattern one position at a time, and that walk
#: metacalled a yall lambda per position, so each fresh process paid
#: '>>'/4's one-time resolution wherever its first binding plan landed
#: and 13 further inferences at every later position. The walk is
#: first-order now, at 4.0 inferences per position against 17.0.
#: [measured: two independent full-lane rounds on this tree agreeing exactly, against one on the unchanged tree and one on the same tree plus an inert never-called clause; command=python extensions/python/tools/twin_coverage.py; fixture=p14-specializer-tax off 694c12f7 with engine/reader.so and the MORK backend; commit=7e7cac85fee08c117032b2efa5a58a40f3b21365].
#: RE-PINNED 2026-09-01, 55099479 to 11528601 (-43570878), the subtract-atom
#: primitive and Counter's grain for -=: a new engine head shifts every twin's
#: load structure, the removal doors changed meaning where a twin spells one,
#: and the quad twin stopped being a different program [measured 2026-09-01:
#: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=c6a40460b1db341198a6150e3600f502831a6e83].
#: RE-PINNED 2026-09-01, 11528601 to 11528614 (+13), generic Python operators
#: now dispatch through live protocols while source twins explicitly name
#: relational engine heads [measured 2026-09-01: min-of-3 serial fresh
#: processes; command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=e3787593132a7ece2d300397045f7415709847c9].
#: RE-PINNED 2026-09-02, 11528614 to 11529543 (+929), exact numeric annotations
#: retain native operator heads, publish MeTTa type declarations, and leave
#: relational heads only where static proof is unavailable [measured
#: 2026-09-02: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=d0dfff1a3ee6c85472fd9b12d6e4aec007a9c301].
#: RE-PINNED 2026-09-02, 11529543 to 11529834 (+291), static contract discharge
#: and policy-stable recompilation [measured 2026-09-02: min-of-3 serial fresh
#: processes; command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=c00341f0ff9d83d1b9338ca86ad51708eaf07ebd].
#: RE-PINNED 2026-09-02, 11529834 to 11529854 (+20), P43 protects both
#: generated policy-check fallbacks from space-local capture [measured
#: 2026-09-02: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=c00341f0ff9d83d1b9338ca86ad51708eaf07ebd].
#: RE-PINNED 2026-09-06, 11529854 to 11529385 (-469), the one pricing pass at
#: the 0.8.0 release cut, and trunk's own movement rather than any mechanism in
#: this twin: each pin was taken on the base its own branch had, and the
#: September merge wave has moved the engine's clause layout, the evaluation
#: path and the library's write doors since [measured 2026-09-06: min-of-3
#: serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=b96e1a15260b7538a8e42be613bcc5dd0dddd136].
#: RE-PINNED 2026-09-07, 11529385 to 11529825 (+440), trunk's own movement
#: since each twin's pin was taken on the base its own branch had: twenty-two
#: first-parent steps between the 0.8.0 release re-pin and this tree, the
#: prelude's move into Prolog the largest of them at +39 to +115 a twin and
#: -65,806 on the error algebra, the live-views merge -45 on every twin that
#: writes, the catalog and get-type repairs +169 on the types chapter, and the
#: rest SWI clause-indexing layout as the boot image grew; this tree also
#: stores the compiled default space operand as &self rather than a (context-
#: space) call [measured 2026-09-07: min-of-3 serial fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=9010a79b01c9b2a66b96a3952fa378fb3e939dc3].
#: RE-PINNED 2026-09-08, 11529825 to 11529867 (+42), the merges between this
#: lane's burn-down base (dfd5003f) and the tree that merged it, placed by a
#: first-parent ladder through the lane's own driver over ten twins at
#: f8c4b672, 4af59757, 90c08119, ad762ee7, 72f9cdf2 and 249389cb (ai-
#: tmp/integrator-849a9e/mergeTW-twin-ladder.log): the catalog-types merge
#: (1a3579fa) moves every twin by a lookup-and-layout step of about +5 for a
#: twin that makes no typed call and about +35 for one that does, plus about +6
#: per compiled definition through the argument-delivery check at the write
#: (the authoring fit re-measured 1370+1307 to 1406+1309), and +1411 for the
#: catalog twin that enumerates the 280 new rows; the two-sided-fragments merge
#: (4af59757) moves the sequence-variable twins by what their fixed rows now
#: compute (+2604 for the two-sided fragments, -217 for the fence, +19 for
#: restricted spaces); the every-atom merge (90c08119) re-authored the reading-
#: forms twin into the sread half (+3017) and added forty-six twins pinned on
#: its own base 31d54e19, which the merges since moved by the same clusters;
#: the gate-hygiene merge (ad762ee7) makes the tabling twins cheaper by the wfs
#: library no longer loading eagerly. Every twin here re-reads its budget on
#: the merged tree, minimum of three fresh processes [measured 2026-09-08: min-
#: of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=08f6f4df19a283bb84ba5f679c83944b42685b2e].
#: RE-PINNED 2026-09-08, 11529867 to 11529676 (-191), metta_substitute_self/3
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
#: RE-PINNED 2026-09-08, 11529676 to 11529689 (+13), boot content moved: the
#: refusal table and the typing point are modules this package did not have,
#: three convert doors became one, per-library faces are projections, and the
#: engine gained a catalog watch point, and SWI clause-indexing shape shifts a
#: twin count by tens whenever boot content moves, the mechanism every earlier
#: entry in these chains names. The watch point itself is one inference per
#: &metta write, which a twin that defines a function pays three of (2239
#: against 2236 on ch03 01-comments with the two announcement clauses taken
#: out), and the (limit ...) rows it exists for cost nothing at all: 2239
#: either way with every row-backed bound removed, because boot seeds the
#: mirror those bounds are read from [measured 2026-09-08: min-of-3 serial
#: fresh processes; command=python extensions/python/tools/twin_coverage.py
#: --repin; commit=c26b6a4d28ef8fb50742440feed2c0578ebb0f58].
#: RE-PINNED 2026-09-08, 11529676 to 11529857 (+181), The engine and library
#: predicates now resolve through their owning modules and the explicit engine
#: facade; compiled program lookup crosses the added metta_engine tier
#: [measured 2026-09-08: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=ede2ac57e213a0d4502c6bbbca6227f97015b720].
#: RE-PINNED 2026-09-08, 11529857 to 11529867 (+10), The engine and library
#: module boundaries retain explicit lookup owners, including host registration
#: and returned callback goals [measured 2026-09-08: min-of-3 serial fresh
#: processes; command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=ede2ac57e213a0d4502c6bbbca6227f97015b720].
#: RE-PINNED 2026-09-08, 11529867 to 11529858 (-9), the module boundary merged
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
#: RE-PINNED 2026-09-08, 11529689 to 11529724 (+35), The typed host door
#: catalog is published before user code. Its declarations change catalog
#: lookup indexes; generated public names bind directly to their existing
#: bodies [measured 2026-09-08: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=b615b5a33b43252ef9826e5387da7c9bd7f6b543].
#: RE-PINNED 2026-09-09, 11529724 to 11529878 (+154), the door table landed
#: (feat/space-as-a-projection-of-door-rows merged at 6471faa37, its
#: reconciliation fixes at 58bf75947): every Space door is a generated alias
#: over its body, the catalog publishes the door contracts at boot as typed
#: atoms, and the seam's listeners publish on every registration, so boot
#: content and clause layout moved, which shifts a twin count by tens; measured
#: on the merged tree [measured 2026-09-09: min-of-3 serial fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=aeb46b14152274db84f6415c8a3dd8c98a9c9eb1].
#: RE-PINNED 2026-09-09, 11529878 to 11529923 (+45), structured concurrency
#: landed (feat/structured-concurrency merged at f80cc416d): every space mint
#: records its allocation in the library's lifetime rows, every write and run
#: pays the ownership hook and every drop asks the library whether a scope owns
#: the name, measured on a pristine control as 32 per mint, 2 per write and 44
#: per drop with none per read; measured on the merged tree [measured
#: 2026-09-09: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=0f53926c2fd9f28e188814c84253ad82e13258f7].
#: RE-PINNED 2026-09-08, 11529858 to 11530202 (+344), Trailing occurrence
#: arguments, token allocation in native writes, exact source withdrawal and
#: transaction-safe shared-table guards change the engine work priced by this
#: twin; answer bags retain the upstream law [measured 2026-09-08: min-of-3
#: serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=7f00ac7932fefa6f380fc8d14ec583ea0c58eff4].
#: RE-PINNED 2026-09-08, 11530202 to 11530142 (-60), Sharing the fast-image
#: hexadecimal validator changes the engine predicate layout. The identity twin
#: moves below its declared band while the seven engine work counters move only
#: at boot; the native add and read slopes remain unchanged. Token storage and
#: source ownership retain their earlier measured costs and answer bags
#: [measured 2026-09-08: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=7f00ac7932fefa6f380fc8d14ec583ea0c58eff4].
#: RE-PINNED 2026-09-09, 11530142 to 11530252 (+110), tokens as storage landed
#: (feat/tokens-as-storage merged): every native occurrence carries a (t actor
#: generation) token as the trailing argument of its storage clause, minted
#: through flag/3 at the write funnel, and every clause read decodes it,
#: measured on a pristine control of trunk cbf7a958d as 8 more inferences per
#: add, 31 more per remove, 4 more per atom saved and 54 more per atom loaded
#: from a fast image, none per match, plus the merged tree's own lib_thread
#: repairs; measured on the merged tree [measured 2026-09-09: min-of-3 serial
#: fresh processes; command=python extensions/python/tools/twin_coverage.py
#: --repin; commit=50e34286f66c938d89d5d367c6370ad44164c97f].
#: RE-PINNED 2026-09-08, 11529858 to 11529898 (+40), Compiled shipped typing
#: decisions and initial vocabulary facts remove repeated interpretation;
#: indexed vocabulary membership replaces member-list scans; catalog reference
#: checks now respect transaction-local erasure. Paired controls and cut counts
#: are recorded in docs/journal/2026-09-08-what-the-waivers-were-paying-for.md
#: extensions/python/tools/twin_coverage.py --repin; commit=32650f9ff4d1c4aa0749d8eb8b153e5bb448ee5c].
#: RE-PINNED 2026-09-09, 11529898 to 11530057 (+159), Compile shipped typing
#: decisions and initial vocabulary facts, index vocabulary membership, and
#: reuse the first Python variable binding before indexing additional names;
#: retain type, transaction and variable-identity checks [measured 2026-09-09:
#: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=32650f9ff4d1c4aa0749d8eb8b153e5bb448ee5c].
#: RE-PINNED 2026-09-09, 11530057 to 11530356 (+299), the compiled vocabulary
#: seed, the membership index, base-module type lookups and the singleton
#: decoder landed (perf/cross-engine-waivers merged): boot publishes the
#: initial vocabulary types from a compiled payload through the tokenized
#: funnel, a warm membership read touches only its own clauses, a base-module
#: type lookup skips the prelude, and a Python decode with one named variable
#: builds no index; per-operation costs of a mint, write, read, drop, run, save
#: and load are unchanged against the trunk in fresh processes; measured on the
#: merged tree, +104 against the trunk's own pin of 11530252 at da0e5755d; the
#: previous number is the branch's cut-time price, and the remaining +195 is
#: what landed on the trunk between the cut f0d33dcad and da0e5755d, tokens as
#: storage above all [measured 2026-09-09: min-of-3 serial fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=b4341ae382c48ef225f4a52e566af6a9a71757c4].
#: RE-PINNED 2026-09-09, 11530356 to 11530415 (+59), a library's Prolog half
#: compiles beside itself on its first import and loads from the artifact after
#: (metta_load_source/2, seam:compiled_source/1): a twin whose example imports
#: a library with a Prolog half pays the artifact load where both sides paid
#: the source consult and its compile-time expansion in every process,
#: lib_thread's import 278,309 to 5,925 inferences; every import now resolves
#: its spec and asks the boot's claim, about 180 inferences an import, and the
#: boot's content moved (the door, the seam and the three library imports the
#: tokens, receipts and seed units gained), which shifts clause layout by tens;
#: measured on this tree with the artifacts warm [measured 2026-09-09: min-of-3
#: serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=f26de01fbf3e0e3c64bb691c66a59fa959fee7f3].
#: RE-PINNED 2026-09-09, 11530415 to 11530425 (+10), engine/qlf_boot.pl gained
#: the hermetic child that writes the engine's own artifact set and every
#: library half's (qlf_child/2, qlf_regenerate_aside/1, qlf_child_boot/0,
#: qlf_shell_words/2), so no process's flags, initialisation file or packs
#: shape an artifact the tree shares; the boot file's added predicates move the
#: first definition's warm-up by ten, the load-structure movement its header
#: records for any boot-content change, and the lane's authoring constant moves
#: with it (warmup 1482); a twin importing a half pays the claim's freshness
#: check besides; measured on this tree with the artifacts warm, against the
#: pins of f26de01fb [measured 2026-09-09: min-of-3 serial fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=5f8a823d23fbed5c7395912a89ba32760e2df4b1].
#: RE-PINNED 2026-09-09, 11530425 to 11530419 (-6), Public add-atom calls
#: metta_add_atom/4 directly and the native bulk loop calls add_sexp_in/5
#: directly, removing one forwarding inference per accepted atom while keeping
#: the atomic token clock, hooks and errors. Open native enumeration uses the
#: shared native_storage_functor/2 mapping, including parametric scalar
#: storage. Receipt scopes retain the nearest unnested transaction and post no
#: cleanup when no reservation exists. Full-lane ten-round observations on the
#: repaired tree place this point below the published budget; the provisioned
#: cut is 3e5855a35d7b206c847845f12467551ea4c54a59. See the 2026-09-09 entries in
#: docs/journal/2026-09-07-every-fact-has-a-token.md. Autoload-only excursions
#: are excluded from this point selection and keep their pins [measured
#: 2026-09-09: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=8ca8a387fc61d0918484b19a1a3baf85b6523043].
#: RE-PINNED 2026-09-14, 11530419 to 11529371 (-1048), The completed standard-
#: library package derives shared collection, numeric, parsing, text and byte
#: recipes in MeTTa and loads those changed providers through every direct and
#: transitive consumer [measured 2026-09-14: min-of-3 serial fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=b7866b4d874879ff0cb212eb1c6af60dddaa39c6].
#: RE-PINNED 2026-09-11, 11530419 to 11529371 (-1048), end-of-wave re-pin on
#: the merged tree after FROM's reference rows and four engine units, the
#: closed-set derivations and two host services, BINDING's one native
#: evaluation entry and boot import, W-OBSERVE's observer guard, PERF's
#: receipts batching and cursor retirement, and the three REDS repairs (derived
#: runtime resources and the shared loader, the tool-lane repairs, the corpus
#: example); serial minimum of three fresh processes through the lane's
#: run_twin with file_search_cache_time=9223372036854775807 set before child
#: boot [measured 2026-09-11: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=57f84148ba2684015f052d533f3197eca07b1f7b].
#: RE-PINNED 2026-09-18, 11530419 to 11530155 (-264), the branch's landings
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
#: RE-PINNED 2026-09-18, 11530155 to 11529765 (-390), the trunk merged
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
#: RE-PINNED 2026-09-21, 11529765 to 11529963 (+198), the sixty libraries
#: derived in MeTTa landed with merge 97763e7fa eight hours after the previous
#: pin 55d451b67, so every example importing one now pays a MeTTa derivation
#: where it paid a Prolog body instead, which the 2026-09-14 ruling accepts
#: explicitly as the price of a library that survives the engine swap [measured
#: 2026-09-21: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=6e09cb25d5495c2db3283166e6ce4e07eefecfb2].
#: RE-PINNED 2026-09-24, 11529963 to 11533901 (+3938), placed on the full-
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
#: da91bc244 confines an exact removal's selection to its own atom:
#: native_retract_one/2 now records the selected clause's head, a clause/3
#: lookup per exact removal, and checks each removal made while the selector is
#: live against it, a few inferences per removal (+8 on most twins, +24 to +192
#: on the library twins that withdraw package rows) [measured 2026-09-24: min-
#: of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=WORKTREE].
#: RE-PINNED 2026-09-24, 11533901 to 11533878 (-23), gate-perf's d781eab8f
#: carries an exact removal's selected head from the code that selected it, so
#: a withdrawal copies its equation once: 23 inferences fewer for each equation
#: removal the twin adopts and 4 for each it selects (-23); each step read
#: serially on its own committed tree, from gate-perf's pin at c7d7244fb, and
#: the fixed tree 4ff69551e reads what 4003462fe does [measured 2026-09-24:
#: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=4ff69551e0e226442cf7257b96af858adda957a4].
#: RE-PINNED 2026-09-25, 11533878 to 11533863 (-15), the registration refusal
#: kind makes the (vocabulary refusal-kind ...) catalog row fifteen members
#: long instead of fourteen, which moves it from storage arity 17 to 18, where
#: the Python seat's (vocabulary door-answers ...) already sits, so &metta
#: keeps one storage arity fewer and each open-tail catalog lookup,
#: metta_catalog_clause/2 visiting every arity, costs five inferences less; and
#: metta_host_signal_message//2 is one more predicate the engine module
#: defines, which every walk over the engine's predicates pays: filereader's
#: existing_predicate_arities/2 two inferences a registration of more than
#: twelve names, each restricted space's core 29, and 11-reference_rows' walk
#: 240, each reproduced exactly by one inert predicate added to the engine on
#: the base [measured 2026-09-25T06:28:19+10:00: min-of-3 serial fresh
#: processes; command=python extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-25, 11533863 to 11533749 (-114), the host evaluation door
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
#: more than twelve names [measured 2026-09-25T06:45:34+10:00: min-of-3 serial
#: fresh processes; command=python extensions/python/tools/twin_coverage.py
#: --repin].
#: RE-PINNED 2026-09-25, 11533749 to 11533755 (+6), both specializer doors
#: prepare a specialization's predicate with
#: spaces:metta_prepare_function_predicate/3 before asserting its clauses
#: [measured 2026-09-25T11:29:10+10:00: one full twins lane before this commit
#: and one with it, the two read on one battery path at the landing's HEAD;
#: command=python extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-25, 11533755 to 11533776 (+21), every force of a waiting
#: function names the module it is made from, through fun_home_in/3, and a
#: write forces only its own space [measured 2026-09-25T16:54:32+10:00: one
#: full twins lane before this commit and one with it, the two read on one
#: battery path at the landing's HEAD; command=python
#: extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-25, 11533776 to 11533780 (+4), lambdas are named by their
#: content and a copy restores its source's rows as a program [measured
#: 2026-09-25T17:00:15+10:00: one full twins lane before this commit and one
#: with it, the two read on one battery path at the landing's HEAD;
#: command=python extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-26, 11533780 to 11533794 (+14), the specializer
#: substitutes only ground bindings into a specialization's stored row: it
#: tests each binding with ground/1, which SWI calls as a builtin where
#: nonvar/1 compiled inline, and leaves a binding with variables as the row's
#: own parameter instead of substituting it into the body; the lanes' tree read
#: this twin +3 off its pin before the step, an offset that is not this step's,
#: so the pin moves by the step's delta alone [measured
#: 2026-09-26T18:25:19+10:00: one full twins lane before this commit and one
#: with it, each read in one battery of the landing's HEAD after a QLF purge
#: and one warm-up; command=python extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-26, 11533794 to 11533792 (-2), the compiler's call-or-data
#: decisions ask _callable_here where they asked the process-wide is_function:
#: the catalogue first, and the defining space's own functions only when the
#: catalogue lacks the name, so a decision the catalogue answers asks a
#: different question and one it cannot answer asks two; the lanes' tree read
#: this twin +3 off its pin before the step, an offset that is not this step's,
#: so the pin moves by the step's delta alone [measured
#: 2026-09-26T18:36:57+10:00: one full twins lane before this commit and one
#: with it, each read in one battery of the landing's HEAD after a QLF purge
#: and one warm-up; command=python extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-27, 11533792 to 11533802 (+10), the host switch to swipl-
#: patched.7 and the seat changes it needs: +1035 the host switch to swipl-
#: patched.7, which delivers the heartbeat inside loops, so a held engine ticks
#: and the held goals read its ticks from the raw counter, 9 inferences a tick,
#: and whose three new system predicates ('$heartbeat'/0, '$file_hash'/2,
#: '$qlf_source_changed'/2) filereader's walk of every visible predicate
#: (existing_predicate_arities/2) meets, 2 inferences each; +345 the seat's
#: interrupt poll crossing only on its arming thread, whose hook costs 3
#: inferences a tick more and whose start goal runs on every new thread and
#: engine; +345 the poll's tick record updated in place, 3 inferences a tick
#: more than replacing it; -1715 the held goals reading Used through
#: metta_py_work/2, which leaves a held engine's own ticks out and reads the
#: tick term inside its opening edge, 5 inferences a held reading; the trunk's
#: lane read this twin +3 off its pin, an offset that is not this landing's, so
#: the pin moves by the landing's delta alone [measured
#: 2026-09-27T03:41:21+10:00: one full twins lane of the trunk and one with
#: this landing, wt-merge battery 1, the trunk on swipl-patched.6 and every
#: part on .7, each through a same-shape host shim; command=python
#: extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-27, 11533802 to 11533810 (+8), a force of a waiting
#: function takes the typing policy and the specializer's lock before
#: translation: spaces:metta_ensure_compiled/2 stabilises the policy and takes
#: the specializer's mutex around the translation once per force, and the
#: translation's own per-pair stabilisation re-enters through
#: with_typing_policy_stable/1's first clause; the lanes' tree read this twin
#: +3 off its pin before the step, an offset that is not this step's, so the
#: pin moves by the step's delta alone [measured 2026-09-27T09:56:55+10:00: one
#: full twins lane before this commit and one with it, each read in one battery
#: of the landing's HEAD after a QLF purge and one warm-up; command=python
#: extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-27, 11533810 to 11533807 (-3), -6 at interrupts B's seat
#: change, which drops the poll's boot calibration, its tick charges and its
#: tick record: a held reading through metta_py_work/2 brackets 3 inferences
#: where it bracketed 6, a registration walk over more than twelve names meets
#: 6 fewer seat predicates (12 or 14 fewer), and a thread the twin joins
#: credits it 11 where it credited 16; the base read 11,533,813 where the pin
#: stood at 11,533,810, a gap of -3 this re-pin takes out [measured
#: 2026-09-27T20:07:01+10:00: full twins lanes in wt-merge's battery 1, tsm-
#: licence's series and its engine reader on swipl-patched.7, the series on
#: swipl-patched.8, and the stack through janus-contract B on swipl-patched.8
#: twice; command=sh tools/check.sh twins].
#: RE-PINNED 2026-09-27, 11533807 to 11533795 (-12), -12 at walk-tax B, which
#: registers a batch's Prolog arities by asking each name, so a registration
#: walk over more than twelve names no longer reads every predicate visible
#: from the loading module at 2 inferences each [measured
#: 2026-09-27T20:38:05+10:00: full twins lanes on swipl-patched.8 in wt-merge's
#: battery 1, two with janus-contract A and two with walk-tax B; command=sh
#: tools/check.sh twins].
#: RE-PINNED 2026-09-29, 11533795 to 11533809 (+14), this twin reads 11533795
#: before the change and 11533809 with the change (+14): each definition
#: through the define doors asks whether its module holds a shadow-import
#: receipt for the name, holds it in flight until the write is visible when it
#: does, and a sweep leaves a receipt another live thread holds: with that use
#: this twin reads 11533809 where the definitions alone read 11533795 (+14)
#: [measured 2026-09-29T06:36:06+10:00: min-of-3 serial fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-29, 11533809 to 11533920 (+111), this twin reads 11533809
#: before the change and 11533920 with the change (+111): each definition marks
#: its name as changed and a sweep repairs only the receipts naming a marked
#: name, where it re-checked every receipt the process held: with that use this
#: twin reads 11533920 where the definitions alone read 11533809 (+111)
#: [measured 2026-09-29T06:42:45+10:00: min-of-3 serial fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-29, 11533920 to 11534033 (+113), this twin reads 11533920
#: before the change and 11534033 with the change (+113): every operation that
#: registers a name outside a load opens a registration unit, files there the
#: repairs its registrations owe, and drains them once when it finishes, so a
#: caller compiled before the name became a function is repaired: with that use
#: this twin reads 11534033 where the definitions alone read 11533920 (+113)
#: [measured 2026-09-29T20:22:12+10:00: min-of-3 serial fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-29, 11534033 to 11534039 (+6), this twin reads 11534033
#: before the change and 11534039 with the change (+6): a call site forces the
#: function it names before deciding the call's shape, so a call of a waiting
#: function builds the application protocol an eager load builds, and the
#: protocol's marker test around a value the translation already holds is
#: decided at compile time: with that use this twin reads 11534039 where the
#: definitions alone read 11534033 (+6) [measured 2026-09-29T20:34:11+10:00:
#: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-30, 11534039 to 11533888 (-151), this twin reads 11534039
#: before the change and 11533888 with the change (-151): a named space's
#: prelude-tier type readers look the prelude's row up before asking whether it
#: governs there, and builtin_result_type/3 asks whether a program took a
#: builtin over only for a builtin whose result is evaluated
#: (engine/metta/types.pl, engine/translator/lowering.pl), so a lookup of a
#: name the prelude does not declare costs one indexed miss and no ownership
#: probe [measured 2026-09-30T04:16:16+10:00: min-of-3 serial fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-30, 11533888 to 11533901 (+13), the twins lane reads this
#: twin at 11533888 before this change and at 11533901 with it (+13): a module
#: takes a name over only when the name's equations compile to a predicate of
#: that name (engine/metta/registration.pl, fun_overrides_in/2), so each reader
#: that asked fun_in/2 whether a module took a name over now also asks
#: compiled_function_name/2 when the module registers the name, one call per
#: such lookup of a module's own name [measured 2026-09-30T04:28:51+10:00: min-
#: of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-30, 11533901 to 11533939 (+38), the twins lane reads this
#: twin at 11533901 before this change and at 11533939 with it (+38): every
#: import request that succeeds, a load or a receipt still current, now records
#: who asked for the source (engine/metta/interop.pl, record_import_request/2
#: writing import_request/3), so unimport! of a package can leave a file
#: another live requester still asks for [measured 2026-09-30T04:33:46+10:00:
#: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-30, 11533939 to 11534004 (+65), the twins lane reads this
#: twin at 11533939 before this change and at 11534004 with it (+65): the
#: catalog_key_taken refusal kind adds a catalog row and a vocabulary member,
#: and a keyed catalog head's write is admitted against the rows already
#: holding its key as it lands (engine/spaces/catalog.pl,
#: metta_catalog_exclusive/3 under metta_catalog_serialised/1), so a process
#: pays for the new kind's row and member and for keyed admission of the
#: catalog rows it writes [measured 2026-09-30T04:45:58+10:00: min-of-3 serial
#: fresh processes; command=python extensions/python/tools/twin_coverage.py
#: --repin].
BUDGET = 11534004

#: DIVERGED 2026-09-07, the example holds 0 atoms the twin does not (none) and
#: the twin holds 1 atom the example does not (1 :): a Python annotation IS a (:
#: name (-> ...)) row and a docstring on a compiled function IS an (@doc name
#: ...) row, so the twin's space carries the declarations and the documentation
#: its own file states where the example leaves both unsaid [measured
#: 2026-09-07: the two stored-atom surpluses, one fresh process per side;
#: command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=9010a79b01c9b2a66b96a3952fa378fb3e939dc3].
DIVERGENCE = "db64e3801a4382dfd431ba81c46b33d24dd21eac6b8f2776059ae70bb689f5ca"
