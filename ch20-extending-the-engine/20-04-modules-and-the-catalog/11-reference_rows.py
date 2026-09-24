"""Purpose: reference_rows.metta in Python through stored rows and shared claims.

from_ is sugar over adding a from row. get_property reads the same engine
claims as the MeTTa head and the library card.
Guarantees: the twin checks homes, metadata, occurrence bags and withdrawal
[tested: examples/ch20-extending-the-engine/20-04-modules-and-the-catalog/11-reference_rows.metta; commit=90ba93eb8f6e98ebfefc55416859bf13de6a8427].
"""

from metta import S, V, ground


def twin(m):
    """Reference a changing home and withdraw exactly that reference."""
    home = m.metta.space(S.reference_home)
    home += S.internal(S.module_helper)

    @home.define
    def module_helper(x: int) -> int:
        return x + 1

    @home.define
    def module_answer(x: int) -> int:
        return module_helper(x)

    home += S["@doc"](S.module_answer, S["@desc"](ground("Add one at home")))
    home += S.home_data(S.kept)
    m += S.internal(S.module_helper)

    # The same head defined here as at home, so the Python name says which:
    # `name=` opts this definition in to the head the home already carries.
    @m.define(name="module-helper")
    def module_helper_here(x: int) -> int:
        return x + 100

    m.from_(home)
    assert m.fn.module_answer(2) == [3]
    assert m.fn.module_helper(2) == [102]
    assert m[S.home_data(V.x)] == []
    assert m[S["="](S.module_answer(V.x), V.body)] == []
    assert m[S[":"](S.module_answer, V.type)].type == [S["->"](S.Number, S.Number)]
    assert S.visibility(S.public) in m.get_property(S.module_answer)
    assert S.visibility(S.internal) in m.get_property(S.module_helper)
    origins = [p for p in m.get_property(S.module_answer) if p.head == S.origin]
    assert len(origins) == 1
    assert origins[0].args[0] == home and origins[0].args[2] == -1
    assert home.fn.module_helper(2) == [3]

    later = S["="](S.module_later(), 9)
    home += later
    home += later
    assert m.fn.module_later() == [9, 9]
    home -= later
    assert m.fn.module_later() == [9]
    m.remove(S["from"](home))
    assert m.eval(S.module_answer(2)) == [S.module_answer(2)]
    assert m[S[":"](S.module_answer, V.type)] == []


#: Initial reference-row price includes defining both homes, checking claims,
#: observing new duplicate occurrences, and withdrawing their reference.
#: [measured: 67053 inferences, min-of-3 fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --measure --rounds 3 examples/ch20-extending-the-engine/20-04-modules-and-the-catalog/11-reference_rows.metta;
#: fixture=built native engine; commit=90ba93eb8f6e98ebfefc55416859bf13de6a8427]
#: RE-PINNED 2026-09-10, 67053 to 66933 (-120), The reference, visibility and
#: property declarations add six heads to the cold-import census. Partial
#: catalog reads now sort occurrence tokens; source-scoped claims and cache
#: reservations change first translation work. The explicitly revised lib_he
#: examples load upstream equations. Warm imports save nine inferences through
#: one rollback collection; ordinary call and row slopes stay unchanged
#: [measured 2026-09-10: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=90ba93eb8f6e98ebfefc55416859bf13de6a8427].
#: RE-PINNED 2026-09-11, 66933 to 65601 (-1332), end-of-wave re-pin on the
#: merged tree after FROM's reference rows and four engine units, the closed-
#: set derivations and two host services, BINDING's one native evaluation entry
#: and boot import, W-OBSERVE's observer guard, PERF's receipts batching and
#: cursor retirement, and the three REDS repairs (derived runtime resources and
#: the shared loader, the tool-lane repairs, the corpus example); serial
#: minimum of three fresh processes through the lane's run_twin with
#: file_search_cache_time=9223372036854775807 set before child boot [measured
#: 2026-09-11: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=57f84148ba2684015f052d533f3197eca07b1f7b].
#: RE-PINNED 2026-09-11, 65601 to 65786 (+185), engine/metta/limits.pl
#: (docs/host-workarounds.md: swi-autoload-cut-installs-the-undefined-
#: supervisor, swi-findall-bag-push-window): every first-use resolution of an
#: undefined predicate pays one inference for the catch around the trap query,
#: and a twin that bounds pays one inference per findall under the bound plus
#: the first bound of its process installing the findall scope [measured
#: 2026-09-11: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=23ed2559a7c9b5712e1f6f4710ed02f8d5c6a23d].
#: RE-PINNED 2026-09-13, 66933 to 95712 (+28779). Reference publication
#: retains its imported definitions and now canonicalizes argument patterns.
#: The prior pin also fails at c75181adc, which measures 65601. Current source
#: and twin still prove 13 claims and store the same atoms.
#: [measured: 95712 inferences, min-of-3 fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --measure --rounds 3 examples/ch20-extending-the-engine/20-04-modules-and-the-catalog/11-reference_rows.metta;
#: fixture=built native engine; commit=a95e6c90c910db30c72311abadd58dee5349978c]
#: RE-PINNED 2026-09-18, 95712 to 110662 (+14950), the branch's landings since
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
#: RE-PINNED 2026-09-18, 110662 to 110870 (+208), 49478d67a landed the
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
#: RE-PINNED 2026-09-18, 110870 to 109771 (-1099), the trunk merged (f97c4b0a3,
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
#: RE-PINNED 2026-09-19, 109771 to 109956 (+185), cost follows the answer: a
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
#: RE-PINNED 2026-09-21, 109956 to 110639 (+683), the sixty libraries derived
#: in MeTTa landed with merge 97763e7fa eight hours after the previous pin
#: 55d451b67, so every example importing one now pays a MeTTa derivation where
#: it paid a Prolog body instead, which the 2026-09-14 ruling accepts
#: explicitly as the price of a library that survives the engine swap [measured
#: 2026-09-21: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=6e09cb25d5495c2db3283166e6ce4e07eefecfb2].
#: RE-PINNED 2026-09-24, 110639 to 91302 (-19337), placed on the full-
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
#: undocumented stopped reporting specializer residues; the 16 commits
#: 63b910f4f..7af4035f0, among them 4bcb4182d moving the package laws into
#: engine/packages.pl and 754d6c010 reading a ./ or ../ source as a path, which
#: moved none of the twelve sweep probes; 814b99468 retains a self-call's
#: function_view dependency, so a recursive body is rebuilt as a caller of its
#: own function whenever an arriving equation changes that view (fib's rebuilds
#: 1 to 2 and newtons_method's energy 2 to 4, each reached from
#: spaces:add_function_atom/7 through lib_memo's automatic reconcile), the fix
#: that took lib_statistics and lib_random to green; the 22 commits
#: d6e09995c..232f4b1ae, which moved none of the twelve sweep probes; 6167a0fb2
#: makes import currency transitive: each nested load records an
#: import_nested_source/3 edge to every import still in flight above it, and a
#: cached import answers current only when every nested receipt does;
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
#: that withdraw package rows) [measured 2026-09-24: min-of-3 serial fresh
#: processes; command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=WORKTREE].
#: CORRECTED 2026-09-24: the RE-PINNED 2026-09-24 paragraph above charges about
#: 10.3k inferences per load of a library's Prolog half to f2822e2ae's boot
#: host check (metta_require_patched_host); the check was never that cost: from
#: f2822e2ae on it refused every compile child the stock swipl ran, the swipl
#: the lane's PATH finds, so no child wrote an artifact and every governed half
#: a half loads, lib/_support/native_build.pl among them, compiled from source
#: in every process; 0a81c782f starts the child from the running home's own
#: swipl, and this twin reads its budget, 91302, in the lanes at that commit
#: and at its parent [measured 2026-09-24: 47 of the 47 compile children the
#: lane's warm-up started ran the stock swipl and were refused by the host
#: check, writing no artifact, and one full lane per side; command=python
#: extensions/python/tools/twin_coverage.py; commit=0a81c782fd6ba00984c36e58e228f73bca810dee].
#: RE-PINNED 2026-09-24, 91302 to 91232 (-70), 0847c3d4c decides a platform
#: capability the first time anything reads it, by whether every library its
#: census row names resolves, where only a failed load used to record anything,
#: and 984eabe23 keeps each verdict in a flag decided under a mutex so two
#: threads' first reads agree; the count moves by what the twin's reads now
#: decide, about 660 inferences for a one-library capability and 1,964 for
#: markup's three, and by a few where it reads the census without deciding
#: [measured 2026-09-24: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=d832d20e8edfdad28ad52815757ba9e685ad2de3].
#: RE-PINNED 2026-09-24, 91232 to 85484 (-5748), -5,888 at b7e3d3bcb, which
#: rebinds a reference head only when its roots, their settledness or a root
#: home's definitions changed; +240 at no commit, the same code read in battery
#: 117's path against battery 115's: before 850d2a660 this count followed the
#: functor-hash order of its open reads, which follows what a process allocated
#: first; +55 at 850d2a660, which reads a native space's lengths in ascending
#: arity rather than functor-hash order; -155 at b5eb39acd, which names get-
#: property's and setup!'s subject by the rule a from source follows [measured
#: 2026-09-24: min-of-3 serial fresh processes at HEAD in battery 118 holding
#: the committed tree alone (BATTERY_KEEP='', 11:56); each step read with its
#: parent and child in turn in battery 115 (10:42 to 11:18), 117 (11:01 to
#: 12:10) or 120 (12:04 to 12:13) from committed trees or this job's patched
#: copies of them, none from a working tree; 850d2a660's and 0f6d29ba6's split
#: from provider-carry's own pairs, aaeea643a's on the ladder before 10:05;
#: command=python extensions/python/tools/twin_coverage.py --measure --rounds
#: 3; commit=c7d7244fbe6d32d024ca8c61b336008e98b156ef].
#: RE-PINNED 2026-09-24, 85484 to 80544 (-4940), d4a365c16 holds the support
#: graph's visited set and the reference refresh's space sets in SWI tries
#: instead of library(nb_set): a membership check is one foreign call where
#: nb_set probed in Prolog, four inferences a step past a taken slot, from a
#: slot a library space's path-bearing name decided, and a walk over a node or
#: two pays a few inferences more for the trie's setup (-5091); gate-perf's
#: d781eab8f carries an exact removal's selected head from the code that
#: selected it, so a withdrawal copies its equation once: 23 inferences fewer
#: for each equation removal the twin adopts and 4 for each it selects (-4);
#: the packages job's 90be572a9 and 4003462fe register Prolog through one
#: engine service: +22 for each library the twin imports (ten new engine
#: predicates and two user imports in the registration walk at two inferences
#: each, less the retired loaded_extension_file/2), and 146 inferences for a
#: Prolog file's origin or 220 for a text's SHA-256 on a twin that registers
#: Prolog (+155); each step read serially on its own committed tree, from gate-
#: perf's pin at c7d7244fb, and the fixed tree 4ff69551e reads what 4003462fe
#: does [measured 2026-09-24: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=4ff69551e0e226442cf7257b96af858adda957a4].
#: RE-PINNED 2026-09-24, 80544 to 80799 (+255), +255 at the change this re-pin
#: lands with, which groups a whole reference face's heads in one pass over its
#: sorted entries where each head searched the whole face, and whose three
#: imports into the engine module are one more predicate filereader's
#: registration walk reads above twelve names, pairs_keys/2, and three a
#: restricted space's core steps over as it enumerates that module's predicates
#: [measured 2026-09-24: the twins lane alone on the base 8d651070d and on the
#: base with this change, one after the other in battery 117's one path, every
#: component at its pin; command=sh tools/check.sh twins (twin_coverage.py
#: inside tools/bounded.sh); commit=8bda9d5525a8174a8304376e111df8da258076a9].
#: RE-PINNED 2026-09-24, 80799 to 83072 (+2273), +2,273 at the change this re-
#: pin lands with, which publishes a from row by itself when rows are all a
#: space owes: its 36 predicates visible to filereader's registration walk cost
#: a batch above twelve names 72 inferences, each restricted space's core about
#: 28 a predicate, and every whole publication and face event its ledger's
#: bookkeeping [measured 2026-09-24: the twins lane alone on 8d651070d with the
#: change before this one and with this change too, one after the other in
#: battery 117's one path, every component at its pin; command=sh
#: tools/check.sh twins (twin_coverage.py inside tools/bounded.sh);
#: commit=e4b7448d1f1bd98733f1b04c3906aaa42f35ef1a].
#: RE-PINNED 2026-09-24, 83072 to 82987 (-85), the host switch of
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
#: extensions/python/tools/twin_coverage.py --repin; commit=622e425d40c126681c04c7f7f81d92618ab83d0d].
#: RE-PINNED 2026-09-25, 82987 to 82832 (-155), the py-* doors change adds
#: engine predicates, and on one tree those alone move this twin by the whole
#: -155: a scan over the space's storage clauses stops sooner where the new
#: predicates change the order of the tables it reads (under SWI's profiler, 79
#: calls fewer each of spaces:metta_storage_term/4, clause/3, functor/3 and
#: >=/2), the order dependence a-atom-order-canonical names [measured
#: 2026-09-25T02:57:39+10:00: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
BUDGET = 82832
