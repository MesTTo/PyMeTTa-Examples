"""Purpose: directed graphs as expressions, from Python.

A graph is a tuple of (Vertex Neighbours) pairs, so the example's two `bind!`
forms are ordinary Python names holding what `graph-of` answered. Where the
example NESTS one call inside another it is written here as the built call it is,
`S.graph_transpose(tasks)` rather than `transpose(tasks).one()`: draining the
inner answer would copy a whole graph into the host and pass it back, which is
the crossing the three-lane model prices per value. `rows` reads a graph or an
edge relation as a list of tuples, which is how a (Vertex Neighbours) pair and a
(From To) edge both read.

Guarantees: the same claims as 25-graph_lib.metta, including reconstructed and
specialized graph recipes and variable-sharing graphs.
[tested: python extensions/python/tools/twin_coverage.py examples/ch08-data/08-03-the-shipped-libraries/25-graph_lib.metta; commit=2951a00d660131f008c2779be828c97f53aa1555].
Open Obligations:
  To Do: None
  Hacks: None
  Future Enhancements: None.
"""

from metta import S, V, lib
from metta._errors.errors import MettaError


def twin(m):
    """Build, ask, add, remove, transpose, unite, close, reach and order."""
    m += lib.graph

    def refused(call):
        """Whether evaluating a call raises, which is what if-error reads."""
        try:
            list(m.eval(call))
        except MettaError:
            return True
        return False

    def elements(answers):
        """One answer's expression, as a list."""
        return list(answers.one())

    def rows(answers):
        """One answer's expression of pairs, as a list of tuples."""
        return [tuple(row) for row in answers.one()]

    def graph_rows(value):
        """A graph as (vertex, [neighbours]) tuples, whatever holds it."""
        return [(row[0], list(row[1])) for row in value]

    graph_of, is_graph = m.fn.graph_of, m.fn.graph_is
    vertices, edges, neighbours = m.fn.graph_vertices, m.fn.graph_edges, m.fn.graph_neighbours
    add_vertices, remove_vertices = m.fn.graph_add_vertices, m.fn.graph_remove_vertices
    add_edges, remove_edges = m.fn.graph_add_edges, m.fn.graph_remove_edges
    reachable, order, acyclic = m.fn.graph_reachable, m.fn.graph_topological_order, m.fn.graph_is_acyclic

    # A graph is built from its edges, each written (From To). Every vertex an
    # edge mentions is a vertex; the first argument adds the ISOLATED ones, and
    # the answer is a collection of (Vertex Neighbours) pairs in the standard
    # order of terms.
    tasks = graph_of((S.lunch,), ((S.wake, S.shower), (S.shower, S.dress), (S.wake, S.coffee))).one()
    assert graph_rows(tasks) == [
        (S.coffee, []),
        (S.dress, []),
        (S.lunch, []),
        (S.shower, [S.dress]),
        (S.wake, [S.coffee, S.shower]),
    ]
    assert elements(graph_of((), ())) == []
    assert graph_rows(graph_of((S.a,), ()).one()) == [(S.a, [])]

    # graph-is asks whether a value is in that shape, which includes the
    # condition a hand-written graph most often misses: every neighbour is itself
    # a vertex.
    assert is_graph(tasks) == [True]
    assert is_graph(((S.a, (S.b,)),)) == [False]
    assert is_graph(((S.b, ()), (S.a, (S.b,)))) == [False]
    assert is_graph(((S.a, ()), (S.b, ()))) == [True]
    assert is_graph(7) == [False]

    # The vertices are a SET, so lib_sets asks about them, and the edges are a
    # RELATION, so lib_pairs walks them.
    assert elements(vertices(tasks)) == [S.coffee, S.dress, S.lunch, S.shower, S.wake]
    assert rows(edges(tasks)) == [(S.shower, S.dress), (S.wake, S.coffee), (S.wake, S.shower)]
    assert elements(edges(S.graph_of((), ()))) == []

    # The neighbours of a vertex are what it points at. A vertex the graph does
    # not hold is a refusal naming it, not an empty answer that would read as a
    # sink.
    assert elements(neighbours(tasks, S.wake)) == [S.coffee, S.shower]
    assert elements(neighbours(tasks, S.lunch)) == []
    assert refused(S.graph_neighbours(tasks, S.dinner))

    # Adding and removing. A vertex arrives with no neighbours, an edge brings its
    # vertices with it, and removing a vertex removes every edge that touched it.
    assert graph_rows(add_vertices(tasks, (S.nap,)).one()) == [
        (S.coffee, []),
        (S.dress, []),
        (S.lunch, []),
        (S.nap, []),
        (S.shower, [S.dress]),
        (S.wake, [S.coffee, S.shower]),
    ]
    assert graph_rows(add_edges(S.graph_of((), ()), ((S.a, S.b),)).one()) == [
        (S.a, [S.b]), (S.b, []),
    ]
    assert graph_rows(remove_vertices(tasks, (S.shower,)).one()) == [
        (S.coffee, []), (S.dress, []), (S.lunch, []), (S.wake, [S.coffee]),
    ]
    assert graph_rows(remove_edges(tasks, ((S.wake, S.coffee),)).one()) == [
        (S.coffee, []),
        (S.dress, []),
        (S.lunch, []),
        (S.shower, [S.dress]),
        (S.wake, [S.shower]),
    ]
    # The input is left alone by all four.
    assert elements(vertices(tasks)) == [S.coffee, S.dress, S.lunch, S.shower, S.wake]

    # The transpose reverses every edge and keeps every vertex, so the union of a
    # graph and its transpose is the undirected reading of it.
    assert rows(edges(S.graph_transpose(tasks))) == [
        (S.coffee, S.wake), (S.dress, S.shower), (S.shower, S.wake),
    ]
    assert elements(vertices(S.graph_transpose(tasks))) == [
        S.coffee, S.dress, S.lunch, S.shower, S.wake,
    ]
    assert rows(edges(S.graph_union(tasks, S.graph_transpose(tasks)))) == [
        (S.coffee, S.wake), (S.dress, S.shower), (S.shower, S.dress),
        (S.shower, S.wake), (S.wake, S.coffee), (S.wake, S.shower),
    ]

    # The closure holds an edge for every path of one step or more, and
    # reachability is the same question asked from one vertex, reflexively.
    assert rows(edges(S.graph_closure(tasks))) == [
        (S.shower, S.dress), (S.wake, S.coffee), (S.wake, S.dress), (S.wake, S.shower),
    ]
    assert elements(reachable(tasks, S.wake)) == [S.coffee, S.dress, S.shower, S.wake]
    assert elements(reachable(tasks, S.lunch)) == [S.lunch]

    # A topological order puts every edge's tail before its head, and a graph with
    # a cycle has none: the refusal names a vertex that reaches itself.
    assert elements(order(tasks)) == [S.lunch, S.wake, S.coffee, S.shower, S.dress]
    assert acyclic(tasks) == [True]
    loop = graph_of((), ((S.a, S.b), (S.b, S.c), (S.c, S.a))).one()
    assert acyclic(loop) == [False]
    assert refused(S.graph_topological_order(loop))
    # A self-edge is the smallest cycle there is.
    assert acyclic(S.graph_of((), ((S.a, S.a),))) == [False]
    assert elements(reachable(loop, S.a)) == [S.a, S.b, S.c]

    # A value that is not a graph is refused by every head; core assertions
    # preserve the invalid shape in their message.
    assert refused(S.graph_vertices(((S.a, (S.b,)),)))
    # A number is refused by the DECLARATION rather than by the head, so it
    # answers the engine's own BadArgType where the others raise; if-error reads
    # both the same way.
    assert list(m.eval(S.graph_closure(7))) == [
        S.Error(S.graph_closure(7), S.BadArgType(1, S.Expression, S.Number)),
    ]
    assert refused(S.graph_add_edges(tasks, ((S.a,),)))

    assert graph_rows(m.fn.graph_union().one()) == []
    assert graph_rows(m.fn.graph_union(tasks).one()) == graph_rows(tasks)
    assert elements(vertices(S.graph_union(tasks, loop, S.graph_of((S.nap,), ())))) == [
        S.a, S.b, S.c, S.coffee, S.dress, S.lunch, S.nap, S.shower, S.wake,
    ]
    graphs = (tasks, loop)
    assert elements(vertices(S.graph_union(*graphs))) == [
        S.a, S.b, S.c, S.coffee, S.dress, S.lunch, S.shower, S.wake,
    ]
    choices = S.superpose((((S.a, S.b),), ((S.a, S.c),)))
    assert [tuple(row) for row in neighbours(S.graph_of((), choices), S.a)] == [
        (S.b,), (S.c,),
    ]

    assert is_graph(S.quote(((S.a, (V.x,)), (S.b, ())))) == [False]
    shared = ((V.x, (V.y,)), (V.y, ()))
    assert is_graph(S.quote(shared)) == [True]
    assert refused(S.graph_neighbours(tasks, V.missing))
    made = graph_of(S.quote((V.x, V.y)), S.quote(((V.x, V.y),))).one()
    assert len(made.vars) == 2 and graph_rows(made) == [
        (made[0][0], [made[1][0]]), (made[1][0], []),
    ]
    closed = m.fn.graph_closure(S.quote(shared)).one()
    assert len(closed.vars) == 2 and graph_rows(closed) == [
        (closed[0][0], [closed[1][0]]), (closed[1][0], []),
    ]
    literal = S.graph_of((), S.quote(((S["+"](1, 2), S.Error(S.data, S.code)),)))
    assert elements(neighbours(literal, S.quote(S["+"](1, 2)))) == [S.Error(S.data, S.code)]
    assert graph_rows(remove_vertices(literal, S.quote((S["+"](1, 2),))).one()) == [
        (S.Error(S.data, S.code), []),
    ]
    error_loop = S.graph_of((), S.quote(((S.Error(S.data, S.code), S.Error(S.data, S.code)),)))
    assert acyclic(error_loop) == [False]
    assert reachable(S.graph_of((), S.quote(((S.Error, S.a), (S.a, S.b)))), S.Error) == [
        (S.Error, S.a, S.b),
    ]

    row = m.match(S["="](S.graph_reachable(V.graph, V.vertex), V.body)).one()
    recipe = S["|->"]((row.graph, row.vertex), row.body)
    walk = m.eval(recipe)[0]
    assert list(m.eval((walk, tasks, S.wake))) == [(S.coffee, S.dress, S.shower, S.wake)]
    row = m.match(S["="](S.graph_reachable(tasks, V.vertex), V.body)).one()
    recipe = S["|->"]((row.vertex,), row.body)
    walk = m.eval(recipe)[0]
    assert list(m.eval((walk, S.shower))) == [(S.dress, S.shower)]

    assert elements(order(S.graph_of((S.alone,), ((S.a, S.z), (S.b, S.c))))) == [
        S.a, S.alone, S.b, S.c, S.z,
    ]
    assert acyclic(S.graph_of((), ((S.a, S.b), (S.b, S.a), (S.b, S.tail)))) == [False]


#: The preceding 34-claim native graph fixture was pinned at 92402 and needed
#: an overrun of 2649 for value crossings. The derived 52-claim fixture runs
#: inside the ordinary ten-percent band, so that overrun is retired.
#: [measured: 8975689 inferences; command=python
#: extensions/python/tools/twin_coverage.py --measure --rounds 3
#: examples/ch08-data/08-03-the-shipped-libraries/25-graph_lib.metta;
#: fixture=52 claims, fresh serial processes after engine/lib QLF purge,
#: MeTTa 8991153, equal stored contents; commit=2951a00d660131f008c2779be828c97f53aa1555].
#: RE-PINNED 2026-09-13, 8975689 to 8975711 (+22), Vector, Math and the shared
#: collection boundary declare their native effects. The engine reads late
#: provider declarations and retains definition analysis for computed function
#: heads [measured 2026-09-13: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=1d0b78a359f58de49f2f98bed50a6480d56cd5f6].
#: RE-PINNED 2026-09-14, 8975711 to 8992545 (+16834), Functional applies
#: finished callback arguments through reduce; Statistics derives exact
#: coefficient rows and Combinatorics retires its native probability provider
#: [measured 2026-09-14: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=e1be99ea1c08f70444c1c35cada441e089777906].
#: RE-PINNED 2026-09-21, 8992545 to 8921031 (-71514), the sixty libraries
#: derived in MeTTa landed with merge 97763e7fa eight hours after the previous
#: pin 55d451b67, so every example importing one now pays a MeTTa derivation
#: where it paid a Prolog body instead, which the 2026-09-14 ruling accepts
#: explicitly as the price of a library that survives the engine swap [measured
#: 2026-09-21: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=6e09cb25d5495c2db3283166e6ce4e07eefecfb2].
#: RE-PINNED 2026-09-24, 8921031 to 8937791 (+16760), placed on the full-
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
#: the commits 63fc952ac..8d45268e3, which the ladder did not split; their
#: runtime changes are 31c0afd8a (the host refusal's message), 7472c4907, which
#: marks a module's reference face dirty instead of walking its forward
#: closure, so support_stabilize/3 walks the face's dependents only when the
#: recomputed value moved and an event that changes nothing recompiles no
#: caller, 7054c11f7, which carries lib 62ca61c's bisecting bit length in
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
#: RE-PINNED 2026-09-24, 8937791 to 8935992 (-1799), 0a81c782f loads a
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
#: RE-PINNED 2026-09-24, 8935992 to 8970798 (+34806), +34,788 at ae1cc8936,
#: where a registration batch of thirteen names or more walks the visible
#: predicate table at two inferences a predicate that asking per name spent
#: inside one C call, and a batch above forty tests each predicate with a dict
#: at one inference fewer than the AVL; +18 at b5eb39acd, whose three new
#: engine exports the registration walk above twelve names reads at two
#: inferences each [measured 2026-09-24: min-of-3 serial fresh processes at
#: HEAD in battery 118 holding the committed tree alone (BATTERY_KEEP='',
#: 11:56); each step read with its parent and child in turn in battery 115
#: (10:42 to 11:18), 117 (11:01 to 12:10) or 120 (12:04 to 12:13) from
#: committed trees or this job's patched copies of them, none from a working
#: tree; 850d2a660's and 0f6d29ba6's split from provider-carry's own pairs,
#: aaeea643a's on the ladder before 10:05; command=python
#: extensions/python/tools/twin_coverage.py --measure --rounds 3;
#: commit=c7d7244fbe6d32d024ca8c61b336008e98b156ef].
#: RE-PINNED 2026-09-24, 8970798 to 8970584 (-214), d4a365c16 holds the support
#: graph's visited set and the reference refresh's space sets in SWI tries
#: instead of library(nb_set): a membership check is one foreign call where
#: nb_set probed in Prolog, four inferences a step past a taken slot, from a
#: slot a library space's path-bearing name decided, and a walk over a node or
#: two pays a few inferences more for the trie's setup (-27); gate-perf's
#: d781eab8f carries an exact removal's selected head from the code that
#: selected it, so a withdrawal copies its equation once: 23 inferences fewer
#: for each equation removal the twin adopts and 4 for each it selects (-253);
#: the packages job's 90be572a9 and 4003462fe register Prolog through one
#: engine service: +22 for each library the twin imports (ten new engine
#: predicates and two user imports in the registration walk at two inferences
#: each, less the retired loaded_extension_file/2), and 146 inferences for a
#: Prolog file's origin or 220 for a text's SHA-256 on a twin that registers
#: Prolog (+66); each step read serially on its own committed tree, from gate-
#: perf's pin at c7d7244fb, and the fixed tree 4ff69551e reads what 4003462fe
#: does [measured 2026-09-24: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=4ff69551e0e226442cf7257b96af858adda957a4].
#: RE-PINNED 2026-09-24, 8970584 to 8970590 (+6), +6 at the change this re-pin
#: lands with, which groups a whole reference face's heads in one pass over its
#: sorted entries where each head searched the whole face, and whose three
#: imports into the engine module are one more predicate filereader's
#: registration walk reads above twelve names, pairs_keys/2, and three a
#: restricted space's core steps over as it enumerates that module's predicates
#: [measured 2026-09-24: the twins lane alone on the base 8d651070d and on the
#: base with this change, one after the other in battery 117's one path, every
#: component at its pin; command=sh tools/check.sh twins (twin_coverage.py
#: inside tools/bounded.sh); commit=8bda9d5525a8174a8304376e111df8da258076a9].
#: RE-PINNED 2026-09-24, 8970590 to 8970811 (+221), +221 at the change this re-
#: pin lands with, which publishes a from row by itself when rows are all a
#: space owes: its 36 predicates visible to filereader's registration walk cost
#: a batch above twelve names 72 inferences, each restricted space's core about
#: 28 a predicate, and every whole publication and face event its ledger's
#: bookkeeping [measured 2026-09-24: the twins lane alone on 8d651070d with the
#: change before this one and with this change too, one after the other in
#: battery 117's one path, every component at its pin; command=sh
#: tools/check.sh twins (twin_coverage.py inside tools/bounded.sh);
#: commit=e4b7448d1f1bd98733f1b04c3906aaa42f35ef1a].
#: RE-PINNED 2026-09-24, 8970811 to 8970803 (-8), the host switch of
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
#: RE-PINNED 2026-09-25, 8970803 to 8970809 (+6), the pragma refusal defines
#: require_metta_pragma_capability/2 in the engine module, and on the same tree
#: defining it without calling it moves this twin by the whole of the change's
#: move, so the cost is one more engine predicate and functor met through the
#: engine's walks over its predicate and functor tables, among them
#: filereader:existing_predicate_arities/2, which charges two inferences for
#: each predicate visible from the loading module at every load of a source
#: registering more than twelve names (i-arity-walk-all-predicates); the
#: change's work at a pragma write does not reach this twin [measured
#: 2026-09-25T00:48:14+10:00: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-25, 8970809 to 8970869 (+60), the py-* doors change makes
#: more predicates visible from filereader, and
#: filereader:existing_predicate_arities/2 walks every predicate visible there
#: at two inferences each whenever a source registering more than twelve names
#: loads: on one tree the change's new engine predicates alone, defined with
#: their two boot uses taken out, make eight more visible and move this twin by
#: 16 for each such load, and the whole change by 20, ten more at its loads
#: (i-arity-walk-all-predicates) [measured 2026-09-25T02:51:55+10:00: min-of-3
#: serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-25, 8970869 to 8967581 (-3288), the host evaluation door
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
#: more than twelve names [measured 2026-09-25T06:47:20+10:00: min-of-3 serial
#: fresh processes; command=python extensions/python/tools/twin_coverage.py
#: --repin].
#: RE-PINNED 2026-09-25, 8967581 to 8967611 (+30), Runtime.reclaim(), the
#: reclamation barrier metta_py_reclaim/1, adds five predicates to user, and
#: existing_predicate_arities/2 walks every user predicate about twice per
#: large load (i-arity-walk-all-predicates) [measured
#: 2026-09-25T11:25:25+10:00: one full twins lane before this commit and one
#: with it, the two read on one battery path at the landing's HEAD;
#: command=python extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-25, 8967611 to 8967659 (+48), both specializer doors
#: prepare a specialization's predicate with
#: spaces:metta_prepare_function_predicate/3 before asserting its clauses
#: [measured 2026-09-25T11:29:10+10:00: one full twins lane before this commit
#: and one with it, the two read on one battery path at the landing's HEAD;
#: command=python extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-25, 8967659 to 8967671 (+12), retiring a library importer
#: derives the arity row again from any backing head a library home still
#: registers, journalled to the load that owns it [measured
#: 2026-09-25T11:33:06+10:00: one full twins lane before this commit and one
#: with it, the two read on one battery path at the landing's HEAD;
#: command=python extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-25, 8967671 to 8968050 (+379), every force of a waiting
#: function names the module it is made from, through fun_home_in/3, and a
#: write forces only its own space [measured 2026-09-25T16:54:32+10:00: one
#: full twins lane before this commit and one with it, the two read on one
#: battery path at the landing's HEAD; command=python
#: extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-25, 8968050 to 8619175 (-348875), lambdas are named by
#: their content and a copy restores its source's rows as a program [measured
#: 2026-09-25T17:00:15+10:00: one full twins lane before this commit and one
#: with it, the two read on one battery path at the landing's HEAD;
#: command=python extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-25, 8619175 to 8619183 (+8), engine/source_loading.pl's
#: load-error clause moved from the thread_local user:thread_message_hook/3 to
#: the global user:message_hook/3, so every thread and engine now runs the
#: check the main thread always ran: one inference per message while no load is
#: open there (clause(watching, true, _) fails) and two inside one
#: (load_failure/2 rejects the silent kind); the Python seat prints a twin's
#: library-load messages inside engines, where no clause ran before, and the
#: original's side does not move [measured 2026-09-25T18:42:16+10:00: min-of-3
#: serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-25, 8619183 to 8619189 (+6), a sweep of a module's
#: generated predicates retires the records describing each swept predicate,
#: and a release the rest of the module's [measured 2026-09-25T23:29:52+10:00:
#: one full twins lane before this commit and one with it, the two read on one
#: battery path at the landing's HEAD; command=python
#: extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-26, 8619189 to 8619243 (+54), engine/metta/control.pl's
#: partial/3 to partial/11, the clauses that let a Prolog meta-predicate call a
#: partial function value, are nine more predicates visible from filereader,
#: and filereader:existing_predicate_arities/2's batch walk, which a load
#: registering more than twelve names runs, pays two inferences for each: 18 a
#: batch, the original and the twin alike, and nine inert facts of those
#: arities move it the same [measured 2026-09-26T01:30:45+10:00: min-of-3
#: serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
#: RE-PINNED 2026-09-26, 8619243 to 8619303 (+60), the reference faces of a
#: strongly connected component of from rows are computed together by label-
#: setting, which makes ten more predicates visible from metta_engine, and a
#: control adding only ten unused predicates to metta_engine reads the same, so
#: none of the move is face work; existing_predicate_arities/2 walks every
#: visible predicate at two inferences for each batch of more than twelve names
#: a load registers (i-arity-walk-all-predicates) [measured
#: 2026-09-26T03:08:45+10:00: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin].
BUDGET = 8619303
