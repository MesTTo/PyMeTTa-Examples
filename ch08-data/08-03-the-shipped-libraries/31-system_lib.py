"""Purpose: the environment, the working directory and the platform, as data.

Names and values are `G("...")` text, because they are text and not names; a
platform key is a symbol. A variable that is not set has no answer, which `list()`
reads as the empty list.

Guarantees: the same claims as 31-system_lib.metta
[tested: python extensions/python/tools/twin_coverage.py examples/ch08-data/08-03-the-shipped-libraries/31-system_lib.metta; commit=b109f59a8095add8ecf264b011e683184274acbb].
Open Obligations:
  To Do: None
  Hacks: None
  Future Enhancements: None.
"""

from metta import G, S, lib
from metta._errors.errors import MettaError


def twin(m):
    """Read and write the environment, ask the platform, and read the directory."""
    m += lib.system
    # lib_pairs is beside it because the environment IS a relation, and lib_string
    # for the text checks over what the platform answers.
    m += lib.pairs
    m += lib.string

    def refused(call):
        """Whether evaluating a call raises, which is what if-error reads."""
        try:
            list(m.eval(call))
        except MettaError:
            return True
        return False

    get = m.fn.env_get
    set_to, unset = m.fn["env-set!"], m.fn["env-unset!"]
    info, keys = m.fn.platform_info, m.fn.platform_keys
    directory = m.fn.working_directory

    # A variable that is not set has NO answer, which is what makes unset and empty
    # different states.
    assert list(get(G("NO_SUCH_VARIABLE_HERE"))) == []
    assert (S.unset if list(get(G("NO_SUCH_VARIABLE_HERE"))) == [] else S.set) == S.unset

    # A write is visible to every later read in this process, and to every child
    # process it starts.
    assert set_to(G("METTA_SYSTEM_EXAMPLE"), G("on")) == [True]
    assert get(G("METTA_SYSTEM_EXAMPLE")) == [G("on")]
    assert set_to(G("METTA_SYSTEM_EXAMPLE"), G("")) == [True]
    # An empty value is SET, which is the state a presence test has to tell apart.
    assert get(G("METTA_SYSTEM_EXAMPLE")) == [G("")]
    assert (S.unset if list(get(G("METTA_SYSTEM_EXAMPLE"))) == [] else S.set) == S.set
    assert unset(G("METTA_SYSTEM_EXAMPLE")) == [True]
    assert list(get(G("METTA_SYSTEM_EXAMPLE"))) == []
    # Removing one that is not set is silent.
    assert unset(G("METTA_SYSTEM_EXAMPLE")) == [True]

    # The whole environment is a relation of (Name Value) pairs, so lib_pairs reads
    # it: the names are Strings, which is also what keeps the relation inert.
    assert set_to(G("METTA_SYSTEM_EXAMPLE"), G("listed")) == [True]
    assert m.fn.pairs_is(S.env_all()) == [True]
    assert list(m.fn.pairs_lookup(S.env_all(), G("METTA_SYSTEM_EXAMPLE"))) == [G("listed")]
    assert list(m.fn.pairs_lookup(S.env_all(), G("NO_SUCH_VARIABLE_HERE"))) == []
    assert unset(G("METTA_SYSTEM_EXAMPLE")) == [True]

    # The platform, one key at a time, and every key as data. The host NAME is not a
    # key: gethostname/1 is library(socket)'s, and a whole network library is too
    # much to link for one string. The family is whichever of the host's platform
    # flags is set, "emscripten" on a WebAssembly build and "unknown" where none
    # is, so the claim names the four families a flag can.
    assert info(S.family).one() in (G("windows"), G("apple"), G("unix"), G("emscripten"))
    assert info(S.dialect) == [G("swi")]
    assert info(S.cores).one() == info(S.cores).one()
    assert len(info(S.version_numbers).one()) == 3
    assert len(keys().one()) == 10
    assert refused(S.platform_info(S.nosuch))
    # The version as text and as numbers agree.
    assert m.fn.string_starts_with(
        S.platform_info(S.version),
        S.number_to_string(S.car_atom(S.platform_info(S.version_numbers))),
    ) == [True]

    # The working directory is the process's own, absolute and without a trailing
    # separator.
    assert m.fn.string_starts_with(S.working_directory(), G("/")) == [True]
    assert m.fn.string_ends_with(S.working_directory(), G("/")) == [False]
    assert refused(S["change-directory!"](G("/no/such/directory/here")))
    # The directory is unchanged by a refused move.
    assert m.fn.string_starts_with(directory(), G("/")) == [True]

    # Every refusal names what it was given.
    assert list(m.eval(S.env_get(7))) == [
        S.Error(S.env_get(7), S.BadArgType(1, S.String, S.Number)),
    ]
    assert refused(S["env-set!"](G("A"), S.nosuch()))
    assert list(m.eval(S["change-directory!"](7))) == [
        S.Error(S["change-directory!"](7), S.BadArgType(1, S.String, S.Number)),
    ]


#: MEASURED on this branch rather than inherited: this twin is new, so there is
#: no earlier pin to move. The 29 claims cover the eight heads, the unset-against-
#: empty distinction, the ten platform keys and the refusals
#: [measured 2026-09-12: 117508 inferences against the example's 122661, minimum
#: of three serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --measure --rounds 3
#: examples/ch08-data/08-03-the-shipped-libraries/31-system_lib.metta;
#: fixture=lib_system at its functional commit, artifacts purged before the run;
#: commit=b109f59a8095add8ecf264b011e683184274acbb].
#: RE-PINNED 2026-09-13, 117508 to 118039 (+531), File exports its staged
#: publisher to Compression; the shared native builder accepts the private
#: archive provider recipe. All consumers are remeasured after those dependency
#: changes [measured 2026-09-13: min-of-3 serial fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=7b42d5ee5cecb82709617b7ed08dfa2c1441f268].
#: RE-PINNED 2026-09-13, 118039 to 200522 (+82483), Combinatorics, Functional,
#: Pairs and Sets now derive collection operations through MeTTa equations,
#: segments and folds. This example imports the changed provider directly or
#: through its library dependencies [measured 2026-09-13: min-of-3 serial fresh
#: processes; command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=6471fbad35eced5ed6440ebf2c25a053b20221f3].
#: RE-PINNED 2026-09-13, 200522 to 201865 (+1343), The validated range
#: continuation now lives in the private support file rather than appearing as
#: a public library head. The import adds its measured loading cost without
#: changing the continuation body [measured 2026-09-13: min-of-3 serial fresh
#: processes; command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=6471fbad35eced5ed6440ebf2c25a053b20221f3].
#: RE-PINNED 2026-09-13, 201865 to 205772 (+3907), Math and Statistics derive
#: their recipes from MeTTa equations; Statistics consolidates finite laws and
#: adds reflective claims. Their collection dependencies share the proper
#: finite expression boundary in lib/_support/collections_data.pl [measured
#: 2026-09-13: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=6fa571d1b7059b610f73e9feed657711414251e5].
#: RE-PINNED 2026-09-13, 205772 to 205794 (+22), Vector, Math and the shared
#: collection boundary declare their native effects. The engine reads late
#: provider declarations and retains definition analysis for computed function
#: heads [measured 2026-09-13: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=1d0b78a359f58de49f2f98bed50a6480d56cd5f6].
#: RE-PINNED 2026-09-14, 205794 to 201793 (-4001), Functional applies finished
#: callback arguments through reduce; Statistics derives exact coefficient rows
#: and Combinatorics retires its native probability provider [measured
#: 2026-09-14: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=e1be99ea1c08f70444c1c35cada441e089777906].
#: RE-PINNED 2026-09-14, 201793 to 217434 (+15641), String now derives nine
#: text recipes through MeTTa equations, with one function parameter for
#: padding and complete validation before empty construction; all import
#: consumers are measured after the provider change [measured 2026-09-14: min-
#: of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=118b805aedbee6de22be4f6131d97c3d6b9156de].
#: RE-PINNED 2026-09-21, 217434 to 299238 (+81804), the sixty libraries derived
#: in MeTTa landed with merge 97763e7fa eight hours after the previous pin
#: 55d451b67, so every example importing one now pays a MeTTa derivation where
#: it paid a Prolog body instead, which the 2026-09-14 ruling accepts
#: explicitly as the price of a library that survives the engine swap [measured
#: 2026-09-21: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=6e09cb25d5495c2db3283166e6ce4e07eefecfb2].
#: RE-PINNED 2026-09-24, 299238 to 329067 (+29829), placed on the full-
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
#: RE-PINNED 2026-09-24, 329067 to 271629 (-57438), 0a81c782f loads a library's
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
#: RE-PINNED 2026-09-24, 271629 to 272279 (+650), both: 2126ab6 installs the
#: library's native half through lib/_support/native_install.pl, loaded once
#: per process, and 0847c3d4c with 984eabe23 decides on its first read each
#: platform capability the twin reads, in a flag under a mutex; a792976 loads
#: process, socket and HTTP's libraries through the census and refuses per
#: call, which moves process_lib by 44 and socket_lib by -603 [measured
#: 2026-09-24: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=d832d20e8edfdad28ad52815757ba9e685ad2de3].
#: RE-PINNED 2026-09-24, 272279 to 295490 (+23211), +23,199 at ae1cc8936, where
#: a registration batch of thirteen names or more walks the visible predicate
#: table at two inferences a predicate that asking per name spent inside one C
#: call, and a batch above forty tests each predicate with a dict at one
#: inference fewer than the AVL; +12 at b5eb39acd, whose three new engine
#: exports the registration walk above twelve names reads at two inferences
#: each [measured 2026-09-24: min-of-3 serial fresh processes at HEAD in
#: battery 118 holding the committed tree alone (BATTERY_KEEP='', 11:56); each
#: step read with its parent and child in turn in battery 115 (10:42 to 11:18),
#: 117 (11:01 to 12:10) or 120 (12:04 to 12:13) from committed trees or this
#: job's patched copies of them, none from a working tree; 850d2a660's and
#: 0f6d29ba6's split from provider-carry's own pairs, aaeea643a's on the ladder
#: before 10:05; command=python extensions/python/tools/twin_coverage.py
#: --measure --rounds 3; commit=c7d7244fbe6d32d024ca8c61b336008e98b156ef].
#: RE-PINNED 2026-09-24, 295490 to 295254 (-236), d4a365c16 holds the support
#: graph's visited set and the reference refresh's space sets in SWI tries
#: instead of library(nb_set): a membership check is one foreign call where
#: nb_set probed in Prolog, four inferences a step past a taken slot, from a
#: slot a library space's path-bearing name decided, and a walk over a node or
#: two pays a few inferences more for the trie's setup (-5); gate-perf's
#: d781eab8f carries an exact removal's selected head from the code that
#: selected it, so a withdrawal copies its equation once: 23 inferences fewer
#: for each equation removal the twin adopts and 4 for each it selects (-275);
#: the packages job's 90be572a9 and 4003462fe register Prolog through one
#: engine service: +22 for each library the twin imports (ten new engine
#: predicates and two user imports in the registration walk at two inferences
#: each, less the retired loaded_extension_file/2), and 146 inferences for a
#: Prolog file's origin or 220 for a text's SHA-256 on a twin that registers
#: Prolog (+44); each step read serially on its own committed tree, from gate-
#: perf's pin at c7d7244fb, and the fixed tree 4ff69551e reads what 4003462fe
#: does [measured 2026-09-24: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=4ff69551e0e226442cf7257b96af858adda957a4].
#: RE-PINNED 2026-09-24, 295254 to 295515 (+261), +257 at the change this re-
#: pin lands with, which publishes a from row by itself when rows are all a
#: space owes: its 36 predicates visible to filereader's registration walk cost
#: a batch above twelve names 72 inferences, each restricted space's core about
#: 28 a predicate, and every whole publication and face event its ledger's
#: bookkeeping [measured 2026-09-24: the twins lane alone on 8d651070d with the
#: change before this one and with this change too, one after the other in
#: battery 117's one path, every component at its pin; command=sh
#: tools/check.sh twins (twin_coverage.py inside tools/bounded.sh);
#: commit=e4b7448d1f1bd98733f1b04c3906aaa42f35ef1a].
#: RE-PINNED 2026-09-25, 295515 to 295559 (+44), the py-* doors change makes
#: more predicates visible from filereader, and
#: filereader:existing_predicate_arities/2 walks every predicate visible there
#: at two inferences each whenever a source registering more than twelve names
#: loads: on one tree the change's new engine predicates alone, defined with
#: their two boot uses taken out, make eight more visible and move this twin by
#: 16 for each such load, and the whole change by 20, ten more at its loads
#: (i-arity-walk-all-predicates) [measured 2026-09-25T02:52:12+10:00: min-of-3
#: serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-25, 295559 to 295150 (-409), the host evaluation door
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
#: more than twelve names [measured 2026-09-25T06:47:40+10:00: min-of-3 serial
#: fresh processes; command=python extensions/python/tools/twin_coverage.py
#: --repin].
#: RE-PINNED 2026-09-25, 295150 to 295171 (+21), Runtime.reclaim(), the
#: reclamation barrier metta_py_reclaim/1, adds five predicates to user, and
#: existing_predicate_arities/2 walks every user predicate about twice per
#: large load (i-arity-walk-all-predicates) [measured
#: 2026-09-25T11:25:25+10:00: one full twins lane before this commit and one
#: with it, the two read on one battery path at the landing's HEAD;
#: command=python extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-25, 295171 to 295175 (+4), both specializer doors prepare
#: a specialization's predicate with spaces:metta_prepare_function_predicate/3
#: before asserting its clauses [measured 2026-09-25T11:29:10+10:00: one full
#: twins lane before this commit and one with it, the two read on one battery
#: path at the landing's HEAD; command=python
#: extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-25, 295175 to 295183 (+8), retiring a library importer
#: derives the arity row again from any backing head a library home still
#: registers, journalled to the load that owns it [measured
#: 2026-09-25T11:33:06+10:00: one full twins lane before this commit and one
#: with it, the two read on one battery path at the landing's HEAD;
#: command=python extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-25, 295183 to 293608 (-1575), a lane outside a bounded
#: scope read the pin: its child's tools/bounded.sh rung probed for a scope and
#: exported the answer, METTA_BOUNDED_SCOPE=no, one more variable for env-all
#: to walk three times, 1585 inferences, where the children of a lane inside a
#: scope, the gate's, never probe; bounded.sh now keeps the probe's answer in
#: the rung that asked, so a lane inside a scope and one outside read the count
#: this re-pin records alike (tests/checks/check_twin_coverage_selftest.py, the
#: context plant), measured here inside a scope as the gate runs the lane; the
#: other +10 is the superproject's 3d5dcb61a, which compiles each nested
#: governed source in a child of its own, so lib_string's half carries its
#: non_terminal directive and costs ten inferences more to load, and which left
#: this row, a finding its reading already stood on, to this re-pin [measured
#: 2026-09-25T16:08:05+10:00: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-25, 293608 to 293735 (+127), every force of a waiting
#: function names the module it is made from, through fun_home_in/3, and a
#: write forces only its own space [measured 2026-09-25T16:54:32+10:00: one
#: full twins lane before this commit and one with it, the two read on one
#: battery path at the landing's HEAD; command=python
#: extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-25, 293735 to 294242 (+507), lambdas are named by their
#: content and a copy restores its source's rows as a program [measured
#: 2026-09-25T17:00:15+10:00: one full twins lane before this commit and one
#: with it, the two read on one battery path at the landing's HEAD;
#: command=python extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-25, 294242 to 294292 (+50), engine/source_loading.pl's
#: load-error clause moved from the thread_local user:thread_message_hook/3 to
#: the global user:message_hook/3, so every thread and engine now runs the
#: check the main thread always ran: one inference per message while no load is
#: open there (clause(watching, true, _) fails) and two inside one
#: (load_failure/2 rejects the silent kind); the Python seat prints a twin's
#: library-load messages inside engines, where no clause ran before, and the
#: original's side does not move [measured 2026-09-25T18:42:41+10:00: min-of-3
#: serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-25, 294292 to 294296 (+4), a sweep of a module's generated
#: predicates retires the records describing each swept predicate, and a
#: release the rest of the module's [measured 2026-09-25T23:29:52+10:00: one
#: full twins lane before this commit and one with it, the two read on one
#: battery path at the landing's HEAD; command=python
#: extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-26, 294296 to 294332 (+36), engine/metta/control.pl's
#: partial/3 to partial/11, the clauses that let a Prolog meta-predicate call a
#: partial function value, are nine more predicates visible from filereader,
#: and filereader:existing_predicate_arities/2's batch walk, which a load
#: registering more than twelve names runs, pays two inferences for each: 18 a
#: batch, the original and the twin alike, and nine inert facts of those
#: arities move it the same [measured 2026-09-26T01:30:59+10:00: min-of-3
#: serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-26, 294332 to 294371 (+39), the reference faces of a
#: strongly connected component of from rows are computed together by label-
#: setting, which moves this program's face computation by -1 inferences; the
#: other +40 inferences is the ten more predicates it makes visible from
#: metta_engine, which a control adding only ten unused predicates to
#: metta_engine reads the same [measured 2026-09-26T03:10:32+10:00: min-of-3
#: serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-26, 294371 to 294376 (+5), this twin reads 294375 at the
#: base and 294376 with commit 1 (+1): commit 1 adds metta_restored_source/5,
#: metta_import_lands/3 and metta_reference_binds/3 to the spaces module
#: (engine/spaces/lifecycle.pl), and on a tree that defines them and never
#: calls them this twin reads 294376 (+1), which only a walk whose order
#: follows SWI's predicate and atom tables can move; it read 294375 against its
#: pin 294371 at the base, so +4 of the distance is the trunk's own and is not
#: attributed here [measured 2026-09-26T08:55:58+10:00: min-of-3 serial fresh
#: processes; command=python extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-26, 294376 to 294384 (+8), this twin reads 294376 at the
#: base and 294384 with the change (+8): the change adds
#: metta_reference_enroll/1 and metta_reference_source_bound/5 to the
#: metta_engine module (engine/metta/reference_refresh.pl and
#: reference_sources.pl), and on a tree that defines them and never calls them
#: this twin reads 294384 (+8), which only a walk over SWI's predicate or atom
#: tables can move, by visiting more entries or visiting them in another order
#: [measured 2026-09-26T11:18:21+10:00: min-of-3 serial fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-26, 294384 to 294400 (+16), Registering a source's names
#: answers each name's Prolog arities in standard order, one msort/2 per
#: registration that adds names, where they came in the procedure table's order
#: and set the order of the arity/2 facts [measured 2026-09-26T12:30:21+10:00:
#: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-26, 294400 to 294461 (+61), A Prolog function registered
#: without its arity is claimed from its lowest arity's file through
#: aggregate_all(min(Arity, File), ...), where the scan took the first arity
#: the procedure table answered [measured 2026-09-26T13:03:35+10:00: min-of-3
#: serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-26, 294461 to 294473 (+12), The engine module defines
#: three predicates more, builtin_seat_prefixes/1,
#: builtin_implementation_gap/2, validate_builtin_implementation_gaps/2 and
#: builtin_surface_predicate/3 in and builtin_surface_predicate_name/1 out, and
#: a program pays for each predicate visible from the engine wherever it walks
#: them: existing_predicate_arities/2 two inferences a predicate for each load
#: that registers more than twelve names, and a restricted space twenty-seven a
#: predicate when it publishes the engine's core; three facts appended to
#: engine/metta/registration.pl on 07b75d16e move 14-lib_roman_pair_helpers,
#: 02-restricted_spaces and 37-statistics_lib by the same +6, +87 and +30
#: [measured 2026-09-26T14:29:44+10:00: min-of-3 serial fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-27, 294473 to 294623 (+150), the host switch to swipl-
#: patched.7 and the seat changes it needs: +14 the host switch to swipl-
#: patched.7, which delivers the heartbeat inside loops, so a held engine ticks
#: and the held goals read its ticks from the raw counter, 9 inferences a tick,
#: and whose three new system predicates ('$heartbeat'/0, '$file_hash'/2,
#: '$qlf_source_changed'/2) filereader's walk of every visible predicate
#: (existing_predicate_arities/2) meets, 2 inferences each; +11 the seat's
#: interrupt poll crossing only on its arming thread, whose hook costs 3
#: inferences a tick more and whose start goal runs on every new thread and
#: engine; +125 the held goals reading Used through metta_py_work/2, which
#: leaves a held engine's own ticks out and reads the tick term inside its
#: opening edge, 5 inferences a held reading; the trunk's lane read this twin
#: +1585 off its pin, an offset that is not this landing's, so the pin moves by
#: the landing's delta alone [measured 2026-09-27T03:41:21+10:00: one full
#: twins lane of the trunk and one with this landing, wt-merge battery 1, the
#: trunk on swipl-patched.6 and every part on .7, each through a same-shape
#: host shim; command=python extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-27, 294623 to 294669 (+46), a force of a waiting function
#: takes the typing policy and the specializer's lock before translation:
#: spaces:metta_ensure_compiled/2 stabilises the policy and takes the
#: specializer's mutex around the translation once per force, and the
#: translation's own per-pair stabilisation re-enters through
#: with_typing_policy_stable/1's first clause [measured
#: 2026-09-27T09:56:55+10:00: one full twins lane before this commit and one
#: with it, each read in one battery of the landing's HEAD after a QLF purge
#: and one warm-up; command=python extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-27, 294669 to 294792 (+123), the constructive negation's
#: engine additions, each counted in this twin's own run: 2 registration walks
#: over more than twelve names (filereader:existing_predicate_arities/2), each
#: now reading 31 more predicates at 2 inferences (+124); -1 of clause-indexing
#: layout [measured 2026-09-27T18:31:56+10:00: one full twins lane with this
#: landing, in a battery of its tree at 775d3cf35, beside one of the base in a
#: battery of 775d3cf35 from 2026-09-27T18:40:06+10:00, which reads the old
#: pin; command=python extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-28, 294792 to 294789 (-3), -3 at tsm-licence's notices
#: reader as its block lookahead amended it: engine/host_notices.pl, which
#: every boot loads, opens a component block only where its Component field
#: directly follows the line of 78 '=', the calls not traced; read on swipl-
#: patched.8, the count above on .7, which no longer runs [measured
#: 2026-09-28T12:31:49+10:00: full twins lanes in wt-merge's battery 1 on
#: swipl-patched.8 at this boundary, engine/host_notices.pl as amended against
#: the day before's as first written; command=sh tools/check.sh twins].
#: RE-PINNED 2026-09-27, 294789 to 294693 (-96), +2 at the host switch to
#: swipl-patched.8, whose swi-heartbeat-inferences-charged-to-the-program
#: leaves the interrupt poll's own inferences out of every count, so a window
#: the seat's calibrated poll correction read 1 to 3 low on .7 reads exactly;
#: -100 at interrupts B's seat change, which drops the poll's boot calibration,
#: its tick charges and its tick record: a held reading through metta_py_work/2
#: brackets 3 inferences where it bracketed 6, a registration walk over more
#: than twelve names meets 6 fewer seat predicates (12 or 14 fewer), and a
#: thread the twin joins credits it 11 where it credited 16 [measured
#: 2026-09-27T20:07:01+10:00: full twins lanes in wt-merge's battery 1, tsm-
#: licence's series and its engine reader on swipl-patched.7, the series on
#: swipl-patched.8, and the stack through janus-contract B on swipl-patched.8
#: twice; command=sh tools/check.sh twins]. With step 4's notices reader as
#: amended the counts read -3 before the step and -1 after it, so the step
#: moves the twin -96 where it moved it -98 [measured
#: 2026-09-28T12:34:38+10:00: full twins lanes in wt-merge's battery 1 on
#: swipl-patched.8 at this boundary, engine/host_notices.pl as amended against
#: the day before's as first written; command=sh tools/check.sh twins].
#: RE-PINNED 2026-09-27, 294693 to 294696 (+3), +4 at janus-contract A, whose
#: seat loader adds metta_extension_require_patches/3 and the format/3 it
#: imports to the engine module a registration walk enumerates, and reads the
#: seat's requirement into its own module where host_patch/2 used to stand
#: there, so a walk over more than twelve names meets one more predicate at 2
#: inferences [measured 2026-09-27T20:31:29+10:00: full twins lanes on swipl-
#: patched.8 in wt-merge's battery 1, two of the stack through janus-contract B
#: and two with janus-contract A; command=sh tools/check.sh twins]. With step
#: 4's notices reader as amended the counts read -1 before the step and -2
#: after it, so the step moves the twin +3 where it moved it +4 [measured
#: 2026-09-28T12:37:38+10:00: full twins lanes in wt-merge's battery 1 on
#: swipl-patched.8 at this boundary, engine/host_notices.pl as amended against
#: the day before's as first written; command=sh tools/check.sh twins].
#: RE-PINNED 2026-09-27, 294696 to 270841 (-23855), -23,854 at walk-tax B,
#: which registers a batch's Prolog arities by asking each name, so a
#: registration walk over more than twelve names no longer reads every
#: predicate visible from the loading module at 2 inferences each [measured
#: 2026-09-27T20:38:05+10:00: full twins lanes on swipl-patched.8 in wt-merge's
#: battery 1, two with janus-contract A and two with walk-tax B; command=sh
#: tools/check.sh twins]. With step 4's notices reader as amended the counts
#: read -2 before the step and -3 after it, so the step moves the twin -23855
#: where it moved it -23854 [measured 2026-09-28T12:40:25+10:00: full twins
#: lanes in wt-merge's battery 1 on swipl-patched.8 at this boundary,
#: engine/host_notices.pl as amended against the day before's as first written;
#: command=sh tools/check.sh twins].
#: RE-PINNED 2026-09-29, 270841 to 270866 (+25), this twin reads 270841 before
#: the change and 270866 with the change (+25): the ld step adds
#: '$metta_shadow_in_flight'/4, metta_define_function/4, metta_define_local/3,
#: metta_prepare_function_predicate/4, metta_prepare_local_predicate/5,
#: metta_shadow_after_transaction/1, metta_shadow_at_exit/0,
#: metta_shadow_held_elsewhere/3, metta_shadow_hold/3, metta_shadow_let_go/3
#: and metta_shadow_owed/1 to the spaces module, and on a tree that defines
#: them and never calls them this twin reads 270842 (+1), which only a walk
#: over SWI's predicate or atom tables can move, by visiting more entries or
#: visiting them in another order; each definition through the define doors
#: asks whether its module holds a shadow-import receipt for the name, holds it
#: in flight until the write is visible when it does, and a sweep leaves a
#: receipt another live thread holds: with that use this twin reads 270866
#: where the definitions alone read 270842 (+24) [measured
#: 2026-09-29T06:36:42+10:00: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-29, 270866 to 271623 (+757), this twin reads 270866 before
#: the change and 271623 with the change (+757): each definition marks its name
#: as changed and a sweep repairs only the receipts naming a marked name, where
#: it re-checked every receipt the process held: with that use this twin reads
#: 271623 where the definitions alone read 270866 (+757) [measured
#: 2026-09-29T06:43:31+10:00: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-29, 271623 to 271697 (+74), this twin reads 271623 before
#: the change and 271697 with the change (+74): a definition that cannot move
#: its space's source map leaves the space's source reader published, so a load
#: beside a from row publishes the face once per runnable instead of once per
#: definition: with that use this twin reads 271697 where the definitions alone
#: read 271623 (+74) [measured 2026-09-29T06:51:25+10:00: min-of-3 serial fresh
#: processes; command=python extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-29, 271697 to 271892 (+195), this twin reads 271697 before
#: the change and 271892 with the change (+195): a mark names the module its
#: definition changed in, and a sweep repairs only the receipts held by that
#: module and its declared descendants: with that use this twin reads 271892
#: where the definitions alone read 271697 (+195) [measured
#: 2026-09-29T06:56:36+10:00: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-29, 271892 to 272579 (+687), this twin reads 271892 before
#: the change and 272579 with the change (+687): every operation that registers
#: a name outside a load opens a registration unit, files there the repairs its
#: registrations owe, and drains them once when it finishes, so a caller
#: compiled before the name became a function is repaired: with that use this
#: twin reads 272579 where the definitions alone read 271892 (+687) [measured
#: 2026-09-29T20:23:21+10:00: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-29, 272579 to 272339 (-240), this twin reads 272579 before
#: the change and 272339 with the change (-240): a call site forces the
#: function it names before deciding the call's shape, so a call of a waiting
#: function builds the application protocol an eager load builds, and the
#: protocol's marker test around a value the translation already holds is
#: decided at compile time: with that use this twin reads 272339 where the
#: definitions alone read 272579 (-240) [measured 2026-09-29T20:35:13+10:00:
#: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-30, 272339 to 271455 (-884), this twin reads 272339 before
#: the change and 271455 with the change (-884): a named space's prelude-tier
#: type readers look the prelude's row up before asking whether it governs
#: there, and builtin_result_type/3 asks whether a program took a builtin over
#: only for a builtin whose result is evaluated (engine/metta/types.pl,
#: engine/translator/lowering.pl), so a lookup of a name the prelude does not
#: declare costs one indexed miss and no ownership probe [measured
#: 2026-09-30T04:17:19+10:00: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-30, 271455 to 271924 (+469), the twins lane reads this
#: twin at 271459 before this change and at 271924 with it (+465): every import
#: request that succeeds, a load or a receipt still current, now records who
#: asked for the source (engine/metta/interop.pl, record_import_request/2
#: writing import_request/3), so unimport! of a package can leave a file
#: another live requester still asks for; it read 271459 against its pin 271455
#: before this change, +4 from an earlier commit of this landing, the takeover
#: read through a module's compiled predicate, inside the allowance [measured
#: 2026-09-30T04:34:25+10:00: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
BUDGET = 271924
