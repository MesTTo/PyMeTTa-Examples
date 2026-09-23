"""Purpose: a collection of (Key Value) pairs read as a relation, from Python.

A pair is a two-element tuple and a relation is a tuple of them, so the example's
`bind!` is an ordinary Python name. The lookup answers once per value, which is
what `list()` collects, and no answer at all is the empty list the example's
`collapse` compares against `()`.

Guarantees: the same claims as 24-pairs_lib.metta
[tested: python extensions/python/tools/twin_coverage.py examples/ch08-data/08-03-the-shipped-libraries/24-pairs_lib.metta; commit=6471fbad35eced5ed6440ebf2c25a053b20221f3].
Open Obligations:
  To Do: None
  Hacks: None
  Future Enhancements: None.
"""

from metta import Expression, S, V, lib
from metta._errors.errors import MettaError


def twin(m):
    """Project, swap, sort, group, ungroup, look up and refuse."""
    m += lib.pairs

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

    is_pairs, keys, values = m.fn.pairs_is, m.fn.pairs_keys, m.fn.pairs_values
    swap, lookup = m.fn.pairs_swap, m.fn.pairs_lookup
    by_key, by_value = m.fn.pairs_sort_by_key, m.fn.pairs_sort_by_value
    group, ungroup = m.fn.pairs_group, m.fn.pairs_ungroup

    # A relation is a collection of two-element expressions, so nothing has to be
    # built: this one holds three sales, one city twice.
    sales = ((S.sydney, 120), (S.perth, 90), (S.sydney, 30))

    # pairs-is asks whether a collection is a relation; every other head asks the
    # same question and names the element that is not a pair.
    assert is_pairs(sales) == [True]
    assert is_pairs(((S.a, 1), (S.b,))) == [False]
    assert is_pairs(()) == [True]
    assert is_pairs(7) == [False]

    # The two projections keep order and keep duplicates, so their length is the
    # relation's own. lib_functional's unzip answers both sides at once.
    assert elements(keys(sales)) == [S.sydney, S.perth, S.sydney]
    assert elements(values(sales)) == [120, 90, 30]
    assert elements(keys(())) == []

    # pairs-swap is the converse relation with the order kept, which is how a
    # lookup by value is written: swap, then look up.
    assert rows(swap(sales)) == [(120, S.sydney), (90, S.perth), (30, S.sydney)]
    assert rows(swap(swap(sales).one())) == [
        (S.sydney, 120), (S.perth, 90), (S.sydney, 30),
    ]

    # Both orderings are STABLE, so the two sydney rows keep their relative order
    # under a sort by key, and nothing is dropped.
    assert rows(by_key(sales)) == [(S.perth, 90), (S.sydney, 120), (S.sydney, 30)]
    assert rows(by_value(sales)) == [(S.sydney, 30), (S.perth, 90), (S.sydney, 120)]
    assert rows(by_key(((S.b, 1), (S.a, 2), (S.b, 0), (S.a, 1)))) == [
        (S.a, 2), (S.a, 1), (S.b, 1), (S.b, 0),
    ]

    # pairs-group reads the relation as a multimap: every key once, in the
    # standard order of terms, with every value it has. It sorts by key ITSELF,
    # because the host's grouping gathers only adjacent pairs and would answer
    # sydney twice here.
    assert rows(group(sales)) == [(S.perth, Expression((90,))), (S.sydney, Expression((120, 30)))]
    assert elements(group(())) == []
    assert rows(group(((S.a, 1),))) == [(S.a, Expression((1,)))]

    # pairs-ungroup inverts it, so a round trip is the relation sorted by key.
    assert rows(ungroup(group(sales).one())) == [
        (S.perth, 90), (S.sydney, 120), (S.sydney, 30),
    ]
    assert rows(ungroup(((S.a, (1, 2)), (S.b, ())))) == [(S.a, 1), (S.a, 2)]
    assert elements(ungroup(())) == []

    # pairs-lookup answers once per value the key has, in the relation's order,
    # so a key with two values is two answers and an absent key is none at all.
    assert list(lookup(sales, S.sydney)) == [120, 30]
    assert list(lookup(sales, S.perth)) == [90]
    assert list(lookup(sales, S.darwin)) == []
    # An absent key really is NO answer rather than an empty one.
    assert (S.none if list(lookup(sales, S.darwin)) == [] else S.found) == S.none
    assert (S.none if list(lookup(sales, S.perth)) == [] else S.found) == S.found
    # A key is compared as a term. A fresh variable does not match a city symbol.
    assert list(lookup(sales, V.city)) == []

    # The refusals name the element that is not a pair, which is the whole of the
    # repair when a relation is built by hand.
    assert refused(S.pairs_keys(((S.a, 1), S.b)))
    assert refused(S.pairs_group(((S.a, 1), (S.b, 2, 3))))
    # A collection that is not even a collection is refused by the DECLARATION
    # rather than by the head, so it answers the engine's own BadArgType where
    # the others raise. if-error reads both the same way.
    assert list(m.eval(S.pairs_lookup(7, S.a))) == [
        S.Error(S.pairs_lookup(7, S.a), S.BadArgType(1, S.Expression, S.Number)),
    ]
    assert refused(S.pairs_ungroup(((S.a, 1),)))

    arithmetic, error_data = S["+"](1, 2), S.Error(S.a, S.b)
    literal_rows = ((S.a, arithmetic), (S.b, error_data))
    assert is_pairs(V.x) == [False]
    assert is_pairs(S.quote(((S["+"], S.a), (S.Error, S.b)))) == [True]
    assert keys(S.quote(((S["+"], S.a), (S.Error, S.b)))) == [(S["+"], S.Error)]
    assert values(S.quote(literal_rows)) == [(arithmetic, error_data)]
    assert rows(swap(S.quote(literal_rows))) == [(arithmetic, S.a), (error_data, S.b)]
    assert group(S.quote(((S.b, arithmetic), (S.a, 2), (S.b, error_data)))) == [
        ((S.a, (2,)), (S.b, (arithmetic, error_data))),
    ]
    assert rows(ungroup(S.quote(((S.a, ()), (S.b, (arithmetic, error_data)))))) == [
        (S.b, arithmetic), (S.b, error_data),
    ]
    assert list(lookup(S.quote(((S.a, arithmetic), (S.a, error_data))), S.a)) == [
        arithmetic, error_data,
    ]
    assert list(lookup(S.quote(((V.key, 7), (S.a, 8))), V.key)) == [7]


#: MEASURED on this branch rather than inherited: this twin is new, so there is
#: no earlier pin to move. The 28 claims cover the nine heads, the stability and
#: the refusals, and the twin costs LESS than the example: a `collapse` the
#: example writes is `list()` here, which the lookup's answers stream into
#: directly [measured 2026-09-12: 47584 inferences against the example's 47975,
#: minimum of three serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --measure --rounds 3
#: examples/ch08-data/08-03-the-shipped-libraries/24-pairs_lib.metta;
#: fixture=lib_pairs at its functional commit, artifacts purged before the run;
#: commit=40b3353b9ae721bf42b832fb953e93a5dc230e6c].
#: RE-PINNED 2026-09-13, 47584 to 813769: collection operations now compose
#: MeTTa matching, folds and application; segment continuations are protected
#: compiler helpers. The example measures 837557 for the same claims
#: [measured: 813769 inferences; command=python extensions/python/tools/twin_coverage.py --measure --rounds 3 examples/ch08-data/08-03-the-shipped-libraries/24-pairs_lib.metta;
#: fixture=minimum of three serial fresh processes after purging engine/lib QLF;
#: commit=6471fbad35eced5ed6440ebf2c25a053b20221f3].
#: RE-PINNED 2026-09-13, 813769 to 815106 (+1337), The validated range
#: continuation now lives in the private support file rather than appearing as
#: a public library head. The import adds its measured loading cost without
#: changing the continuation body [measured 2026-09-13: min-of-3 serial fresh
#: processes; command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=6471fbad35eced5ed6440ebf2c25a053b20221f3].
#: RE-PINNED 2026-09-13, 815106 to 807134 (-7972), Math and Statistics derive
#: their recipes from MeTTa equations; Statistics consolidates finite laws and
#: adds reflective claims. Their collection dependencies share the proper
#: finite expression boundary in lib/_support/collections_data.pl [measured
#: 2026-09-13: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=6fa571d1b7059b610f73e9feed657711414251e5].
#: RE-PINNED 2026-09-13, 807134 to 807156 (+22), Vector, Math and the shared
#: collection boundary declare their native effects. The engine reads late
#: provider declarations and retains definition analysis for computed function
#: heads [measured 2026-09-13: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=1d0b78a359f58de49f2f98bed50a6480d56cd5f6].
#: RE-PINNED 2026-09-14, 807156 to 858307 (+51151), Functional applies finished
#: callback arguments through reduce; Statistics derives exact coefficient rows
#: and Combinatorics retires its native probability provider [measured
#: 2026-09-14: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=e1be99ea1c08f70444c1c35cada441e089777906].
#: RE-PINNED 2026-09-21, 858307 to 866089 (+7782), the sixty libraries derived
#: in MeTTa landed with merge 97763e7fa eight hours after the previous pin
#: 55d451b67, so every example importing one now pays a MeTTa derivation where
#: it paid a Prolog body instead, which the 2026-09-14 ruling accepts
#: explicitly as the price of a library that survives the engine swap [measured
#: 2026-09-21: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=6e09cb25d5495c2db3283166e6ce4e07eefecfb2].
#: RE-PINNED 2026-09-24, 866089 to 877006 (+10917), placed on the full-
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
#: RE-PINNED 2026-09-24, 877006 to 875207 (-1799), 0a81c782f loads a library's
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
#: extensions/python/tools/twin_coverage.py --repin; commit=WORKTREE].
BUDGET = 875207
