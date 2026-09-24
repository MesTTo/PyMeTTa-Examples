"""Purpose: reach every File head from Python.

Bytes, publication, renames, trees, traversal, globbing, paths, kinds, links,
scopes and handles, in the order the MeTTa original walks them.

A path is text, so paths are `G(...)` strings joined by the library's own
`path-join`. Bytes are tuples of integers, traversal and globbing are answer
streams a list comprehension drains, and a scope takes a FUNCTION: `@m.define`
gives the engine one it applies to the handle or directory it acquired, and a
generator there is the nondeterministic body the MeTTa original writes with
`superpose`.

Guarantees: the same claims as 19-file_lib.metta
[tested: python extensions/python/tools/twin_coverage.py examples/ch08-data/08-03-the-shipped-libraries/19-file_lib.metta; commit=e40ef941310bddd1f57074eb559e78aac8a263b0].
Owns resources: one temporary directory holds everything and `delete-tree!`
removes it at the end; every handle this file opens is closed.
Open Obligations:
  To Do: None
  Hacks: None
  Future Enhancements: None.
"""

import metta
from metta import G, S, V, lib
from metta._errors.errors import MettaError


def twin(m):
    """Every File operation, through the functions the library publishes."""
    m += lib.file

    join = m.fn.path_join
    read, write, append = m.fn["read-file!"], m.fn["write-file!"], m.fn["append-file!"]
    read_bytes, write_bytes = m.fn["read-bytes!"], m.fn["write-bytes!"]
    kind, exists, dir_exists = m.fn.file_kind, m.fn["file-exists"], m.fn["dir-exists"]
    open_, close = m.fn["file-open!"], m.fn["file-close!"]
    size, seek, exact = m.fn["file-get-size!"], m.fn["file-seek!"], m.fn["file-read-exact!"]
    read_all, read_some = m.fn["file-read-to-string!"], m.fn["file-read-bytes!"]
    walk, glob, listing = m.fn.dir_walk, m.fn.dir_glob, m.fn["list-dir!"]
    remove_tree, link_at, link_of = m.fn["delete-tree!"], m.fn["make-link!"], m.fn["read-link"]

    def refused(call):
        """Whether evaluating a call raises, which is what if-error reads."""
        try:
            list(m.eval(call))
        except MettaError:
            return True
        return False

    # A fresh directory, minted exclusively, is where the whole twin works.
    directory = m.fn["temp-dir!"](G("file-lib")).one()

    def under(relative):
        """A path inside that directory, built the way the original builds it."""
        return join(directory, relative).one()

    assert dir_exists(directory) == [True]
    assert kind(directory) == [S.directory]

    # Text files: the whole-file trio and the lines as data.
    notes = under(G("notes.txt"))
    assert write(notes, G("alpha\nbeta\n")) == [True]
    assert append(notes, G("gamma\n")) == [True]
    assert read(notes) == [G("alpha\nbeta\ngamma\n")]
    assert list(m.fn["file-lines!"](notes).one()) == [G("alpha"), G("beta"), G("gamma")]
    lines = metta.space(m.fn["file-space!"](notes).one())
    assert [row.text for row in lines[S.line(2, V.text)]] == [G("beta")]
    assert exists(notes) == [True]
    assert kind(notes) == [S.file]

    # Bytes are integers 0 to 255, whole-file and by handle.
    blob = under(G("blob.bin"))
    assert write_bytes(blob, (0, 1, 255, 10)) == [True]
    assert m.fn["append-bytes!"](blob, (7,)) == [True]
    assert list(read_bytes(blob).one()) == [0, 1, 255, 10, 7]
    handle = open_(blob, G("rb")).one()
    assert list(read_some(handle, 2).one()) == [0, 1]
    assert list(read_some(handle).one()) == [255, 10, 7]
    close(handle).one()
    handle = open_(blob, G("wb")).one()
    assert m.fn["file-write-bytes!"](handle, (65, 66)) == [True]
    close(handle).one()
    assert read(blob) == [G("AB")]

    # A byte operation on a text handle, and an invalid byte, refuse by name.
    handle = open_(blob, G("r")).one()
    assert refused(S["file-read-bytes!"](handle))
    close(handle).one()
    assert refused(S["write-bytes!"](blob, (1, 300)))

    # The handle surface: size, seek, exact reads, and the three streams.
    handle = open_(notes, G("r")).one()
    assert size(handle) == [17]
    assert exact(handle, 5) == [G("alpha")]
    assert seek(handle, 6) == [True]
    assert exact(handle, 4) == [G("beta")]
    assert read_all(handle) == [G("\ngamma\n")]
    close(handle).one()
    handle = open_(notes, G("a")).one()
    assert m.fn["file-write!"](handle, G("delta\n")) == [True]
    close(handle).one()
    assert list(m.fn["file-lines!"](notes).one()) == [
        G("alpha"), G("beta"), G("gamma"), G("delta"),
    ]
    assert m.fn.stdin() == [0]
    assert m.fn.stdout() == [1]
    assert m.fn.stderr() == [2]
    assert m.fn["stderr!"](G("")) == [True]

    # replace-file! publishes by rename, so a reader holding the old file keeps
    # reading it while the path already names the new one.
    handle = open_(notes, G("r")).one()
    assert m.fn["replace-file!"](notes, G("fresh")) == [True]
    assert exact(handle, 5) == [G("alpha")]
    close(handle).one()
    assert read(notes) == [G("fresh")]
    assert m.fn["replace-file!"](blob, (104, 105)) == [True]
    assert read(blob) == [G("hi")]

    # copy-file! publishes the same way, byte for byte, replacing on success only.
    copied = under(G("blob-copy.bin"))
    assert m.fn["copy-file!"](blob, copied) == [True]
    assert list(read_bytes(copied).one()) == [104, 105]
    assert refused(S["copy-file!"](under(G("absent.bin")), copied))
    assert list(read_bytes(copied).one()) == [104, 105]

    # Directories, trees and links.
    tree = under(G("tree"))
    assert m.fn["make-dir!"](under(G("tree/deep/deeper"))) == [True]
    assert write(under(G("tree/deep/deeper/leaf.txt")), G("leaf")) == [True]
    assert write(under(G("tree/deep/note.md")), G("note")) == [True]
    assert write(under(G("tree/.hidden")), G("h")) == [True]
    assert link_at(G("deep"), under(G("tree/shortcut"))) == [True]
    assert link_at(G(".."), under(G("tree/deep/up"))) == [True]
    assert kind(under(G("tree/shortcut"))) == [S.link]
    assert link_of(under(G("tree/shortcut"))) == [G("deep")]
    assert m.fn["same-file"](under(G("tree/shortcut")), under(G("tree/deep"))) == [True]
    assert m.fn["same-file"](under(G("tree/deep")), under(G("tree/deep/note.md"))) == [False]
    assert list(listing(tree).one()) == [G(".hidden"), G("deep"), G("shortcut")]

    # A walk answers every descendant, depth first, names in codepoint order;
    # links are reported and not entered unless asked.
    assert list(walk(tree)) == [
        under(G("tree/.hidden")), under(G("tree/deep")), under(G("tree/deep/deeper")),
        under(G("tree/deep/deeper/leaf.txt")), under(G("tree/deep/note.md")),
        under(G("tree/deep/up")), under(G("tree/shortcut")),
    ]
    assert len(list(walk(tree, ((S.follow_links, True),)))) == 11

    # A glob selects by pattern: a literal component joins without listing,
    # * ? [] {} filter one directory, and ** matches zero or more levels.
    assert list(glob(tree, G("deep/*.md"))) == [under(G("tree/deep/note.md"))]
    assert list(glob(tree, G("**/*.txt"))) == [under(G("tree/deep/deeper/leaf.txt"))]
    assert list(glob(tree, G("*"))) == [under(G("tree/deep")), under(G("tree/shortcut"))]
    assert list(glob(tree, G("*"), ((S.hidden, True),))) == [
        under(G("tree/.hidden")), under(G("tree/deep")), under(G("tree/shortcut")),
    ]
    assert list(glob(tree, G("{deep,other}/note.m?"))) == [under(G("tree/deep/note.md"))]
    assert list(glob(tree, G("**/*.md"), ((S.follow_links, True),))) == [
        under(G("tree/deep/note.md")), under(G("tree/shortcut/note.md")),
    ]
    assert list(glob(tree, G("nowhere/*"))) == []
    assert refused(S.dir_glob(tree, G("[unclosed")))

    # copy-dir! builds the copy beside its destination and publishes it with one
    # rename; links are recreated with the text they hold.
    copy = under(G("copies/tree"))
    assert m.fn["copy-dir!"](tree, copy) == [True]
    assert read(join(copy, G("deep/deeper/leaf.txt")).one()) == [G("leaf")]
    assert link_of(join(copy, G("shortcut")).one()) == [G("deep")]
    assert refused(S["copy-dir!"](tree, copy))
    assert refused(S["copy-dir!"](tree, join(tree, G("inside")).one()))

    # rename-file! is the host's rename, and nothing is ever copied.
    note, renamed = join(copy, G("deep/note.md")).one(), join(copy, G("deep/renamed.md")).one()
    assert m.fn["rename-file!"](note, renamed) == [True]
    assert kind(note) == [S.missing]
    assert read(renamed) == [G("note")]
    assert refused(S["rename-file!"](join(copy, G("deep")).one(),
                                     join(copy, G("deep/deeper")).one()))

    # delete-tree! unlinks a link root and leaves its target alone, then
    # removes a whole tree.
    assert remove_tree(join(copy, G("shortcut")).one()) == [True]
    assert dir_exists(join(copy, G("deep")).one()) == [True]
    assert remove_tree(copy) == [True]
    assert dir_exists(copy) == [False]
    assert m.fn["delete-dir!"](under(G("copies"))) == [True]

    # Lexical paths never touch the filesystem; path-resolve does.
    assert join(G("reports"), G("sales.csv")) == [G("reports/sales.csv")]
    assert m.fn.path_parent(G("reports/sales.csv")) == [G("reports")]
    assert m.fn.path_name(G("reports/sales.csv")) == [G("sales.csv")]
    assert m.fn.path_extension(G("reports/sales.tar.gz")) == [G("gz")]
    assert m.fn.path_stem(G("reports/sales.tar.gz")) == [G("sales.tar")]
    assert list(m.fn.path_parts(G("/reports/2026/sales.csv")).one()) == [
        G("/"), G("reports"), G("2026"), G("sales.csv"),
    ]
    assert m.fn.path_normalize(G("reports/./2026/../sales.csv")) == [G("reports/sales.csv")]
    assert m.fn.path_normalize(G("/x/../../y")) == [G("/y")]
    assert m.fn.path_relative(G("/a/b/c"), G("/a/d")) == [G("../b/c")]
    assert m.fn.path_absolute(G("/x/./y")) == [G("/x/y")]
    assert m.fn.path_parent(m.fn.path_absolute(G("rel")).one()) == m.fn.path_absolute(G("."))
    assert m.fn.path_resolve(under(G("tree/shortcut/deeper/leaf.txt"))) == [
        under(G("tree/deep/deeper/leaf.txt")),
    ]
    assert m.fn.path_resolve(under(G("tree/deep/up/.hidden"))) == [under(G("tree/.hidden"))]

    # Metadata is a queryable snapshot; file-kind names what is missing.
    metadata = metta.space(m.fn["file-metadata!"](notes).one())
    assert [row.bytes for row in metadata[S.size(V.bytes)]] == [5]
    assert kind(under(G("nothing"))) == [S.missing]
    assert refused(S.read_link(notes))

    # A scope applies a function to the resource it acquired and releases it on
    # every exit, so every answer of a nondeterministic body streams while the
    # handle is still open. These three are the example's three lambdas, and a
    # compiled body reads a library head as the MeTTa call it is.
    @m.define
    def size_then_two(handle):
        # (|-> ($h) (superpose ((file-get-size! $h) (file-read-exact! $h 2))))
        yield S["file-get-size!"](handle)
        yield S["file-read-exact!"](handle, 2)

    # The name to write is a PARAMETER, so the compiled body carries no text of
    # its own and the scope receives the partial application.
    @m.define
    def fill_and_list(name, work):
        # (|-> ($work) (let $written (write-file! (path-join $work "scratch") "x")
        #                (list-dir! $work)))
        _written = S["write-file!"](S.path_join(work, name), name)
        return S["list-dir!"](work)

    @m.define
    def close_then_read(handle):
        # (|-> ($h) (let $closed (file-close! $h) (file-read-to-string! $h)))
        _closed = S["file-close!"](handle)
        return S["file-read-to-string!"](handle)

    assert m.fn["with-file"](notes, G("r"), S["file-read-to-string!"]) == [G("fresh")]
    assert m.fn["with-file"](notes, G("r"), S["|->"]((V.h,), S["file-get-size!"](V.h))) == [5]
    assert list(m.fn["with-file"](notes, G("r"), S.size_then_two)) == [5, G("fr")]
    assert list(m.fn["with-temp-dir"](G("file-lib-scope"),
                                      S.fill_and_list(G("scratch"))).one()) == [G("scratch")]
    assert refused(S.with_file(notes, G("r"), S.close_then_read))

    # temp-path! mints a fresh file the caller owns; a prefix names, never places.
    scratch = m.fn["temp-path!"](G("file-lib")).one()
    assert exists(scratch) == [True]
    assert m.fn["delete-file!"](scratch) == [True]
    assert refused(S["temp-path!"](G("logs/run")))

    # Everything the twin made goes with the one directory.
    assert remove_tree(directory) == [True]
    assert dir_exists(directory) == [False]


#: MEASURED on this branch rather than inherited: this twin is new, so there is
#: no earlier pin to move. The 90 claims cover 56 heads at 60 arities; the
#: example pays 245,536 inferences for the same work
#: [measured 2026-09-12: 209508 inferences, minimum of three serial fresh
#: processes and five single runs with zero spread (ai-tmp/ai-lib3-file-spread.log);
#: command=python extensions/python/tools/twin_coverage.py --measure --rounds 3
#: examples/ch08-data/08-03-the-shipped-libraries/19-file_lib.metta;
#: fixture=the File library at its functional commit, artifacts purged before
#: the run; commit=e40ef941310bddd1f57074eb559e78aac8a263b0].
#: RE-PINNED 2026-09-12, 209508 to 209603 (+95), File transfers newly owned
#: streams through adopt_file_stream/2 and claims a close atomically; HTTP also
#: verifies transaction refusal before server lifecycle effects [measured
#: 2026-09-12: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=0f22b69cfca5c108e4126bdd56ab9bb2e493744d].
#: RE-PINNED 2026-09-13, 209603 to 209621 (+18), File exports its shared stream
#: borrowing and rollback operations; failed Socket and HTTP publication now
#: withdraws the registered stream before closing it [measured 2026-09-13: min-
#: of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=781ee98e188c23ea7ef9298636d6e5e6c7fdc727].
#: RE-PINNED 2026-09-13, 209621 to 209635 (+14), File privately exports its
#: existing staged publisher with callback qualification; Compression shares
#: that ownership and publication protocol [measured 2026-09-13: min-of-3
#: serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=7b42d5ee5cecb82709617b7ed08dfa2c1441f268].
#: RE-PINNED 2026-09-13, 209635 to 210166 (+531), File exports its staged
#: publisher to Compression; the shared native builder accepts the private
#: archive provider recipe. All consumers are remeasured after those dependency
#: changes [measured 2026-09-13: min-of-3 serial fresh processes;
#: command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=7b42d5ee5cecb82709617b7ed08dfa2c1441f268].
#: RE-PINNED 2026-09-13, 210166 to 210172 (+6), Exporting and protecting the
#: shared segment body continuation changes the measured module setup cost.
#: Both consumers retain their claims and stored contents; their fresh counts
#: move by 6 and 19 inferences [measured 2026-09-13: min-of-3 serial fresh
#: processes; command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=6471fbad35eced5ed6440ebf2c25a053b20221f3].
#: RE-PINNED 2026-09-14, 210172 to 232066 (+21894), String now derives nine
#: text recipes through MeTTa equations, with one function parameter for
#: padding and complete validation before empty construction; all import
#: consumers are measured after the provider change [measured 2026-09-14: min-
#: of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=118b805aedbee6de22be4f6131d97c3d6b9156de].
#: RE-PINNED 2026-09-21, 232066 to 469787 (+237721), the sixty libraries
#: derived in MeTTa landed with merge 97763e7fa eight hours after the previous
#: pin 55d451b67, so every example importing one now pays a MeTTa derivation
#: where it paid a Prolog body instead, which the 2026-09-14 ruling accepts
#: explicitly as the price of a library that survives the engine swap [measured
#: 2026-09-21: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=6e09cb25d5495c2db3283166e6ce4e07eefecfb2].
#: RE-PINNED 2026-09-24, 469787 to 491294 (+21507), placed on the full-
#: configuration first-parent ladder from the pin commit 6e09cb25d: at
#: 43e964002, where the lane was last recorded green, the twin already read
#: past its pin in the configuration this ladder measures, a fresh clone in a
#: battery; it reads the filesystem or git, whose state is not part of the
#: tree, so that part of its move follows where it runs rather than what it
#: runs; the 120 commits 43e964002..c09dc4868, where the per-commit probe sweep
#: puts each step at one commit: 5b4e7e53d reads a translator rule's declared
#: type where the rule lives; aea2e5e03 and 6922f54c9 carry the csv and
#: lib_file refusal vocabulary; d27805154 carries lib 19a231b, whose
#: regenerated faces declare six libraries' inputs %Undefined%, so their calls
#: stop paying a declared-type check (vector_lib -7278, statistics_lib -6453);
#: 33219ffa0 resolves a bare library name to its pkg.metta; 0cd329450 adds the
#: platform refusal kind, one metta_refusal_declaration/4 row that
#: metta_catalog_preset/1 turns into one more (refusal ...) catalog row and one
#: more refusal-kind vocabulary member, measured at +10 to +15 on most twins;
#: and d8231f103 refuses a library spec that walks out of the library root;
#: a7955cd07 carried lib 629c86c, the library split, which moved every
#: library's surface out of its pkg.metta manifest into lib.metta beside it, so
#: an import reads the manifest and then imports the library's own source as a
#: second file; 54784fded reads the builtin type surface from every .metta in
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
#: current only when every nested receipt does; f2822e2ae: the boot host check
#: (metta_require_patched_host, called once in qlf_load_engine) adds about
#: 10.3k inferences to every later load of a library's Prolog half; measured
#: 507,704 to 518,008 on text_lib's twin, mechanism below the predicate not
#: isolated; the commits 63fc952ac..8d45268e3, which the ladder did not split;
#: their runtime changes are 31c0afd8a (the host refusal's message), 7472c4907,
#: which marks a module's reference face dirty instead of walking its forward
#: closure, so support_stabilize/3 walks the face's dependents only when the
#: recomputed value moved and an event that changes nothing recompiles no
#: caller, 7054c11f7, which carries lib 62ca61c's bisecting bit length in
#: _support/statistics.metta, and the Python-seat pointers; da91bc244 confines
#: an exact removal's selection to its own atom: native_retract_one/2 now
#: records the selected clause's head, a clause/3 lookup per exact removal, and
#: checks each removal made while the selector is live against it, a few
#: inferences per removal (+8 on most twins, +24 to +192 on the library twins
#: that withdraw package rows) [measured 2026-09-24: min-of-3 serial fresh
#: processes; command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=WORKTREE].
#: RE-PINNED 2026-09-24, 491294 to 326542 (-164752), 0a81c782f loads a
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
#: RE-PINNED 2026-09-24, 326542 to 327171 (+629), 2126ab6 installs every
#: library's native half through lib/_support/native_install.pl, which tests
#: for a statically linked host and loads library(shlib) only where there is
#: none, where each half used to load shlib itself, so a process importing a
#: library with a native half now loads that module once [measured 2026-09-24:
#: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=d832d20e8edfdad28ad52815757ba9e685ad2de3].
#: RE-PINNED 2026-09-24, 327171 to 338696 (+11525), +11,519 at ae1cc8936, where
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
#: RE-PINNED 2026-09-24, 338696 to 338487 (-209), d4a365c16 holds the support
#: graph's visited set and the reference refresh's space sets in SWI tries
#: instead of library(nb_set): a membership check is one foreign call where
#: nb_set probed in Prolog, four inferences a step past a taken slot, from a
#: slot a library space's path-bearing name decided, and a walk over a node or
#: two pays a few inferences more for the trie's setup (-24); gate-perf's
#: d781eab8f carries an exact removal's selected head from the code that
#: selected it, so a withdrawal copies its equation once: 23 inferences fewer
#: for each equation removal the twin adopts and 4 for each it selects (-207);
#: the packages job's 90be572a9 and 4003462fe register Prolog through one
#: engine service: +22 for each library the twin imports (ten new engine
#: predicates and two user imports in the registration walk at two inferences
#: each, less the retired loaded_extension_file/2), and 146 inferences for a
#: Prolog file's origin or 220 for a text's SHA-256 on a twin that registers
#: Prolog (+22); each step read serially on its own committed tree, from gate-
#: perf's pin at c7d7244fb, and the fixed tree 4ff69551e reads what 4003462fe
#: does [measured 2026-09-24: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=4ff69551e0e226442cf7257b96af858adda957a4].
#: RE-PINNED 2026-09-24, 338487 to 338824 (+337), +335 at the change this re-
#: pin lands with, which publishes a from row by itself when rows are all a
#: space owes: its 36 predicates visible to filereader's registration walk cost
#: a batch above twelve names 72 inferences, each restricted space's core about
#: 28 a predicate, and every whole publication and face event its ledger's
#: bookkeeping [measured 2026-09-24: the twins lane alone on 8d651070d with the
#: change before this one and with this change too, one after the other in
#: battery 117's one path, every component at its pin; command=sh
#: tools/check.sh twins (twin_coverage.py inside tools/bounded.sh);
#: commit=e4b7448d1f1bd98733f1b04c3906aaa42f35ef1a].
#: RE-PINNED 2026-09-25, 338824 to 338846 (+22), the py-* doors change makes
#: more predicates visible from filereader, and
#: filereader:existing_predicate_arities/2 walks every predicate visible there
#: at two inferences each whenever a source registering more than twelve names
#: loads: on one tree the change's new engine predicates alone, defined with
#: their two boot uses taken out, make eight more visible and move this twin by
#: 16 for each such load, and the whole change by 20, ten more at its loads
#: (i-arity-walk-all-predicates) [measured 2026-09-25T02:51:24+10:00: min-of-3
#: serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-25, 338846 to 338833 (-13), the registration refusal kind
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
#: the base [measured 2026-09-25T06:28:52+10:00: min-of-3 serial fresh
#: processes; command=python extensions/python/tools/twin_coverage.py --repin].
BUDGET = 338833
