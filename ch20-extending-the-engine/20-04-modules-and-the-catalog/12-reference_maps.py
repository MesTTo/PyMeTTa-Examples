"""Purpose: reference_maps.metta in Python using name and call-pattern maps.

from_ writes the row; the engine evaluates its map once per source head.
[tested: examples/ch20-extending-the-engine/20-04-modules-and-the-catalog/12-reference_maps.metta; commit=a95e6c90c910db30c72311abadd58dee5349978c].
"""

from metta import S, V

PAYLOAD = S["./examples/ch20-extending-the-engine/20-04-modules-and-the-catalog/_fixtures/references/maps"]


def twin(m):
    """Select and rename one canonical home's public heads."""
    m.from_(PAYLOAD, S.only((S.map_value,)))
    assert m.fn.map_value(2) == [3]
    assert m.eval(S.map_label()) == [S.map_label()]
    m.from_(PAYLOAD, S.except_((S.map_value,)))
    assert m.fn.map_label() == [S.label]
    m.from_(PAYLOAD, S.prefix(S["p."]))
    m.from_(PAYLOAD, S.rename(((S.map_value, S.renamed),)))
    m.from_(PAYLOAD, S.qualified(S.module))
    assert m.fn["p.map-value"](2) == [3]
    assert m.fn.renamed(2) == [3]
    assert m.fn["module.map-value"](2) == [3]
    assert m.fn.map_label() == [S.label]

    m.from_(PAYLOAD, S.rename(((S.map_value, S.only_two(2)),)))
    assert m.fn.only_two(2) == [3]

    m.from_(PAYLOAD, S["|->"]((V.h,), S.if_(
        S["=="](V.h, S.map_value),
        S.superpose((S.lambda_one, S.lambda_two)), S.empty(),
    )))
    assert m.fn.lambda_one(2) == [3]
    assert m.fn.lambda_two(2) == [3]
    assert m.fn.prefix(S["text."], S.word) == [S["text.word"]]
    m.fn["pragma!"](S.from_map, S.prefix(S["default."]))
    m.from_(PAYLOAD)
    assert m.fn["default.map-value"](2) == [3]
    m.fn["pragma!"](S.from_map, S.none)


#: Face publication defers dependent repairs until every linked head is ready,
#: so the shared lambda compiles once. Both spellings exercise all six maps.
#: [measured: 228075 inferences, min-of-3 fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --measure --rounds 3 examples/ch20-extending-the-engine/20-04-modules-and-the-catalog/12-reference_maps.metta;
#: fixture=built native engine; commit=90ba93eb8f6e98ebfefc55416859bf13de6a8427]
#: RE-PINNED 2026-09-10, 228075 to 227143 (-932), The reference, visibility and
#: property declarations add six heads to the cold-import census. Partial
#: catalog reads now sort occurrence tokens; source-scoped claims and cache
#: reservations change first translation work. The explicitly revised lib_he
#: examples load upstream equations. Warm imports save nine inferences through
#: one rollback collection; ordinary call and row slopes stay unchanged
#: [measured 2026-09-10: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=90ba93eb8f6e98ebfefc55416859bf13de6a8427].
#: RE-PINNED 2026-09-11, 227143 to 227465 (+322), end-of-wave re-pin on the
#: merged tree after FROM's reference rows and four engine units, the closed-
#: set derivations and two host services, BINDING's one native evaluation entry
#: and boot import, W-OBSERVE's observer guard, PERF's receipts batching and
#: cursor retirement, and the three REDS repairs (derived runtime resources and
#: the shared loader, the tool-lane repairs, the corpus example); serial
#: minimum of three fresh processes through the lane's run_twin with
#: file_search_cache_time=9223372036854775807 set before child boot [measured
#: 2026-09-11: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=57f84148ba2684015f052d533f3197eca07b1f7b].
#: RE-PINNED 2026-09-11, 227465 to 227513 (+48), engine/metta/limits.pl
#: (docs/host-workarounds.md: swi-autoload-cut-installs-the-undefined-
#: supervisor, swi-findall-bag-push-window): every first-use resolution of an
#: undefined predicate pays one inference for the catch around the trap query,
#: and a twin that bounds pays one inference per findall under the bound plus
#: the first bound of its process installing the findall scope [measured
#: 2026-09-11: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=23ed2559a7c9b5712e1f6f4710ed02f8d5c6a23d].
#: RE-PINNED 2026-09-13, 227143 to 270967 (+43824). The call-pattern row
#: installs another native alias and its declarations; later references
#: include that binding in their published faces. Mapper results now carry
#: canonical argument constraints. Native 260533; both spellings prove 12 claims.
#: [measured: 270967 inferences, min-of-3 fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --measure --rounds 3 examples/ch20-extending-the-engine/20-04-modules-and-the-catalog/12-reference_maps.metta;
#: fixture=built native engine; commit=a95e6c90c910db30c72311abadd58dee5349978c]
#: RE-PINNED 2026-09-13, 270967 to 271057 (+90). Effect planning follows
#: canonical reference bodies and keeps the defining module in its traversal.
#: [measured: 271057 twin and 260623 native inferences, min-of-3 fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --measure --rounds 3 examples/ch20-extending-the-engine/20-04-modules-and-the-catalog/12-reference_maps.metta;
#: fixture=built native engine after deleting engine/lib QLF; commit=89084b43ff1a758f703ce77cd96b026f56510116]
#: RE-PINNED 2026-09-18, 271057 to 278009 (+6952), the branch's landings since
#: the 09-10 pins, re-taken on the tip f06186a96: the compiled call law
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
#: RE-PINNED 2026-09-18, 278009 to 278326 (+317), 49478d67a landed the
#: polynomial carrier, whose preset row and variable claim every catalog scan
#: reads, the product carriers and the guard read in the fixpoint door, and the
#: binding's five-element rule read: the examples that scan the catalog moved
#: with their twins (restricted_spaces +522, the three pln twins +63 each, the
#: two tabling twins +20 and +10, reflect_lib +6) and the twins that cross the
#: seat's declaration and query paths moved with their examples unmoved (the
#: class twins between -4212 and +2841, the reference twins +208 and +317, the
#: tagged fixpoint twin +610, the documentation twins -22 and -50, types_nondet
#: +5) [measured 2026-09-18: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=bf5f100591493a91324b1d7552b5ad2731601691].
#: RE-PINNED 2026-09-18, 278326 to 276024 (-2302), the trunk merged (f97c4b0a3,
#: petta's 61 commits since c75181adc) with the definition batch's load pushed
#: as the running load (2da1155e3): every example moved with the engine, 279 of
#: 294 cheaper (median -0.78%), through the compiled runnable envelope
#: executing each runnable form's fixed answer, name and fuel envelope from
#: compiled clauses, the trunk's trailed scopes and compiled context readers (a
#: b_getval/2 read per recorded assertion in place of the branch's thread-local
#: rows), the host listener door and the receipts loop probing the owner once
#: per set; serial minimum of three fresh processes through the lane's run_twin
#: [measured 2026-09-18: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=55d451b670949c2dc9d2ab7bc678f33f21094bd2].
#: RE-PINNED 2026-09-19, 276024 to 276059 (+35), cost follows the answer: a
#: block is charged for its own thread's work and for the workers whose answers
#: it used, so a race's losers, the branches par-any and par-forall stopped,
#: and a cancelled future or timer are joined through the engine's discarding
#: door (metta_join_measured/3) and their partial spend, which only the
#: schedule sized, is taken out; lib_thread's join no longer polls on the host
#: patched for swi-thread-join-detach-window, and the seat's counter doors read
#: the discarded tally outside the window they bracket (metta_py_stats/2,
#: metta_py_work/2) [measured 2026-09-19: min-of-3 serial fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=32335687084e4d8ad43cf8800f2dedce707fa137].
#: ENVELOPED 2026-09-19: the point 276059 becomes the envelope 276059..276387
#: over 11: under the lane's own protocol (full-lane/294/workers=32, ten
#: rounds) the counter reads 276059 every time, and under the gate's concurrent
#: lanes (three runs) it reads 276387, each reading exact on its run; the extra
#: mode is the same program's work done on a different thread under load, a
#: loader flight or a settle step the foreground runs itself when the worker is
#: late, which the join accounting does not reach; an envelope states what was
#: observed and the point was a lie under the gate [measured 2026-09-19: the
#: twins lane alone on the final tree and under the gate's concurrent lanes,
#: wt-battery-2 ai-full-gate-10da82e4a.log, ai-full-gate-19fdb0b86.log, ai-
#: lanes-exports-back.log; commit=1ccbb142315d16a719807cd2c9754e4a2fcefdf1].
#: RE-OBSERVED 2026-09-21 under 'full-lane/323/workers=32/file-search-cache-
#: time=9223372036854775807/before-boot', 276059..276387 to 277614..277614 over
#: 10 observations: the corpus grew from 294 examples to 323 with the merge
#: that derived sixty libraries in MeTTa (97763e7fa), and an empirical envelope
#: is a claim about ONE scheduler's protocol, so the earlier observations could
#: not license this one; these ten are this tree's own and are not pooled with
#: that run [measured 2026-09-21: ten full-lane observations; command=python
#: extensions/python/tools/twin_coverage.py --observe --rounds 10;
#: commit=8d2e8bb94da53a1a35c79d440cc09ef56f46153e].
#: RE-OBSERVED 2026-09-21 under 'full-lane/323/workers=32/file-search-cache-
#: time=9223372036854775807/before-boot', 277614..277614 to 277614..277614 over
#: 20 observations: ten observations did not cover the tail of an example whose
#: count varies: 01-mutex_and_transaction read 23659 against the 23661..23666
#: those ten recorded, and twenty put its 23657..23669 around that reading. The
#: protocol records observed extrema exactly and refuses an invented allowance,
#: so the only lawful way to cover a tail is to observe it [measured
#: 2026-09-21: twenty full-lane observations; command=python
#: extensions/python/tools/twin_coverage.py --observe --rounds 10;
#: commit=43e964002671a680825823b7ab4c1020de20f651].
#: RE-OBSERVED 2026-09-24 under 'full-lane/323/workers=32/file-search-cache-
#: time=9223372036854775807/before-boot', 277614..277614 to 276773..276773 over
#: 20 observations: the tree under these envelopes moved after their last
#: observation at 43e964002: the package-model changes a7955cd07 (lib 629c86c's
#: library split), 54784fded, 63b910f4f, d6e09995c and 6167a0fb2, 814b99468's
#: self-call dependencies, f2822e2ae's boot host check
#: (metta_require_patched_host, called once in qlf_load_engine, which adds
#: about 10.3k inferences to every later load of a library's Prolog half,
#: mechanism below the predicate not isolated) and 7472c4907's reference faces
#: marked rather than walked, each placed on the full-configuration first-
#: parent ladder; an empirical envelope is a claim about one scheduler's
#: protocol on one tree, so these twenty observations are this tree's own and
#: are not pooled with the earlier ones [measured 2026-09-24: 20 full-lane
#: observations; command=python extensions/python/tools/twin_coverage.py
#: --observe --rounds 20; commit=WORKTREE].
#: POOLED 2026-09-24 under 'full-lane/323/workers=32/file-search-cache-
#: time=9223372036854775807/before-boot', 276773..276773 over 20 to
#: 276773..276773 over 28: the 8 whole-lane runs of this runtime the envelope
#: did not yet hold read the pin run's first lane 276773; the pin run's second
#: lane 276773; the pin run's third lane 276773; the first final lane 276773;
#: the purged lane on 49e2b250d 276773; the purged lane on 26de4ddcf 276773;
#: the purged lane after a8487162 276773; the purged lane after 878b8bd9
#: 276773. They are the pin run's own lanes on the 6a7ac233d snapshot and the
#: final lanes on 49e2b250d and 26de4ddcf, whose commits touch no path this
#: twin runs, and each reads every deterministic twin exactly as a battery
#: whose governed QLF set was compiled in place does, so none carries a moved
#: artifact's cost; the lane whose battery carried a lib_import.qlf compiled in
#: wt-merge is left out. A whole-lane run under this protocol on this runtime
#: is an observation, so the envelope is the union of the extrema and the sum
#: of the counts [measured 2026-09-24: 8 whole-lane runs, sh
#: extensions/python/check.sh twins in battery 5; command=python
#: extensions/python/tools/twin_coverage.py; commit=WORKTREE].
#: RE-OBSERVED 2026-09-24 under 'full-lane/323/workers=32/file-search-cache-
#: time=9223372036854775807/before-boot', 276773..276773 to 276893..276913 over
#: 20 observations: re-observed on the tree 0a81c782f made, which does not move
#: this twin: in one battery its twin reads 276,624 with all four of that
#: commit's engine files, with qlf_boot.pl alone at the parent, with the three
#: loaders alone at the parent and with all four at the parent, and its window
#: loads no file; its readings follow the battery's state (276,645 in the
#: parent's lane and 276,893 in the fix's, each in its own battery), which is
#: why it carries an envelope; the about 10.3k per Prolog-half load that a
#: 2026-09-24 paragraph above charges to f2822e2ae's boot host check was never
#: the check's own cost: from f2822e2ae on the check refused every compile
#: child the stock swipl ran, so no child wrote an artifact and every governed
#: half a half loads compiled from source in every process, which 0a81c782f
#: ends by starting the child from the running home's own swipl; these
#: observations are this tree's own and are not pooled with the earlier ones
#: [measured 2026-09-24: 20 full-lane observations; command=python
#: extensions/python/tools/twin_coverage.py --observe --rounds 20;
#: commit=0a81c782fd6ba00984c36e58e228f73bca810dee].
#: RE-OBSERVED 2026-09-24 under 'full-lane/323/workers=32/file-search-cache-
#: time=9223372036854775807/before-boot', 276893..276913 to 175481..175481 over
#: 21 observations: the tree moved under this envelope after its observation at
#: 0a81c782f: read serially, one fresh process a side, on each first-parent
#: rung from 0a81c782f to the fixed tree 4ff69551e in one battery, its twin
#: went from 276,893 to 175,481; the WebAssembly job's 0847c3d4c decides a
#: platform capability on its first read (-125); its 984eabe23 keeps the
#: verdict in a flag decided under a mutex (+35); provider-carry's aaeea643a
#: carries a provider's stored term back as the engine gave it (-35); gate-
#: perf's b7e3d3bcb keeps each reference head's last bind in its own row, so a
#: from row rebinds only the heads it brings (-88,808); the packages job's
#: b5eb39acd names get-property's and setup!'s subject by a from source's rule
#: (+60); d4a365c16 holds the support graph's visited set and the reference
#: refresh's space sets in tries instead of library(nb_set) (-12,539); gate-
#: perf's d781eab8f copies a withdrawn equation once (-60); the packages job's
#: registration service, 90be572a9 in the engine with 4003462fe in the seat,
#: net (+60); until d4a365c16 this count followed library(nb_set)'s probing,
#: which starts from a slot the variant hash of each space's name decides, so a
#: step before it carries a change in the names the run's spaces hold as well
#: as the work its commit adds, and d4a365c16's own step is that probing's cost
#: in this battery's path, less the few inferences a trie's setup costs a walk;
#: an empirical envelope is a claim about one scheduler's protocol on one tree,
#: so these observations are this tree's own and are not pooled with the
#: earlier ones [measured 2026-09-24: 21 full-lane observations on the fixed
#: tree, the twenty rounds of --observe and one run of the lane itself;
#: command=python extensions/python/tools/twin_coverage.py --observe --rounds
#: 20; commit=4ff69551e0e226442cf7257b96af858adda957a4].
#: RE-OBSERVED 2026-09-24 under 'full-lane/323/workers=32/file-search-cache-
#: time=9223372036854775807/before-boot', 175481..175481 to 174548..174548 over
#: 20 observations: the tree moved under this envelope by the change this
#: observation lands with, which publishes a whole reference face's heads from
#: one pass over its sorted entries where each head searched the whole face for
#: its roots, a findall over every entry per head: a whole publication over a
#: face of many heads stops paying heads times entries steps, one over a face
#: of one to three entries pays the grouping's fixed cost of about eight calls,
#: and the change's pairs_keys/2 import is one more predicate filereader's
#: registration walk reads, 2 inferences for each registration batch above
#: twelve names; these observations are the tree's own and are not pooled with
#: the earlier ones [measured 2026-09-24: 20 full-lane observations;
#: command=python extensions/python/tools/twin_coverage.py --observe --rounds
#: 20; commit=8bda9d5525a8174a8304376e111df8da258076a9].
#: RE-OBSERVED 2026-09-24 under 'full-lane/323/workers=32/file-search-cache-
#: time=9223372036854775807/before-boot', 174548..174548 to 120092..120092 over
#: 20 observations: the tree moved under this envelope by the change this
#: observation lands with, which publishes a space's from rows by themselves
#: when rows are all it owes, where each new row republished every row before
#: it: of the drain decisions while each example loads, class_decorators goes
#: by rows in 12 of 21, reference_maps in 14 of 23, class_dispatch in 5 of 38,
#: class_grains in 4 of 181, class_prototypes in 2 of 30, reference_loading in
#: 2 of 19, and class_values and class_entities in none of 3 and 14; every
#: publication now runs the ledger's decision, a stored plan and a settle,
#: about 25 to 30 inferences, every face event writes its space's ledger fact,
#: about three, and each registration batch above twelve names pays 72
#: inferences for the 36 predicates filereader's walk now sees; these
#: observations are the tree's own and are not pooled with the earlier ones
#: [measured 2026-09-24: 20 full-lane observations; command=python
#: extensions/python/tools/twin_coverage.py --observe --rounds 20;
#: commit=e4b7448d1f1bd98733f1b04c3906aaa42f35ef1a].
#: RE-OBSERVED 2026-09-24 under 'full-lane/323/workers=32/file-search-cache-
#: time=9223372036854775807/before-boot', 120092..120092 to 119969..119969 over
#: 20 observations: the host switch of /home/user/Dev/swipl-patched from .2 to
#: .5, the native host of build 9's 36 patches, moved this twin out of its
#: envelope, measured .2 against .5 through two environment shims of one shape
#: on one tree; its channel is not measured [measured 2026-09-24: 20 full-lane
#: observations; command=python extensions/python/tools/twin_coverage.py
#: --observe --rounds 20; commit=WORKTREE].
BUDGET = {
    "minimum": 119969,
    "maximum": 119969,
    "observations": 20,
    "protocol": "full-lane/323/workers=32/file-search-cache-time=9223372036854775807/before-boot"
}

#: DIVERGED 2026-09-24, the example holds 8 atoms the twin does not (8 from)
#: and the twin holds 8 atoms the example does not (8 from): the twin names its
#: fixtures by their root-relative path, ./examples/ch20-extending-the-
#: engine/20-04-modules-and-the-catalog/_fixtures/references/<name>, where the
#: example names the same files relative to itself as
#: ./_fixtures/references/<name>; a from row is stored as written, so the two
#: spaces hold the same rows under two spellings of one file (twins commit
#: aa891a0d, after d8231f103 refused the library-root walk-out and 754d6c010
#: read ./ and ../ as paths) [measured 2026-09-24: the two stored-atom
#: surpluses, one fresh process per side; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=WORKTREE].
DIVERGENCE = "ae5831c89577596fdddd123d0f9d18ce25add0be05036f5293471d2a444967a7"
