"""Purpose: XML and HTML as expressions, and the selector language over them.

An element is a built term, so `S.element(name, attributes, children)` is how one
is written and `list()` reads one apart. Documents are `G("...")` text; selectors
are built terms whose parameter is held, so `S.descendant(S.item)` passes through
unevaluated. Every selector answers once per match, which `list()` collects.

Guarantees: the same claims as 29-markup_lib.metta
[tested: python extensions/python/tools/twin_coverage.py examples/ch08-data/08-03-the-shipped-libraries/29-markup_lib.metta; commit=ed976b0e70c1176a7ef9feabb0359313105c786e].
Open Obligations:
  To Do: None
  Hacks: None
  Future Enhancements: None.
"""

from metta import Expression, G, S, V, lib, solve
from metta._errors.errors import MettaError

#: The document every query below reads, as ground text rather than a name.
ORDER = G("<order id='7'><item sku='a'>apple</item><item sku='b'>pear</item><note/></order>")


def twin(m):
    """Parse, read, select, write, and refuse what the host would repair."""
    m += lib.markup

    def refused(call):
        """Whether evaluating a call raises, which is what if-error reads."""
        try:
            list(m.eval(call))
        except MettaError:
            return True
        return False

    def tree(value):
        """An element as (name, [attribute rows], [children]) tuples, all the way down.

        A text node is a leaf atom, which is not iterable, so `Expression` is the
        one shape to walk and everything else answers itself.
        """
        if not isinstance(value, Expression):
            return value
        parts = list(value)
        if len(parts) != 4 or parts[0] != S.element:
            return value
        _, name, attributes, children = parts
        return (name,
                [tuple(row) for row in attributes],
                [tree(child) for child in children])

    parse_xml, parse_html = m.fn.markup_parse_xml, m.fn.markup_parse_html
    write, select = m.fn.markup_write, m.fn.markup_select
    attribute, text = m.fn.markup_attribute, m.fn.markup_text

    # An element is (element Name Attributes Children): the name a Symbol, each
    # attribute an (attr Name Value) row and the children an expression of elements
    # and Strings. The attribute row is TAGGED because an untagged (id "7") pair is
    # an expression whose head names the engine's identity function, and it would be
    # evaluated as a call where the document is written.
    doc = parse_xml(ORDER).one()
    assert tree(doc) == (
        S.order,
        [(S.attr, S.id, G("7"))],
        [(S.item, [(S.attr, S.sku, G("a"))], [G("apple")]),
         (S.item, [(S.attr, S.sku, G("b"))], [G("pear")]),
         (S.note, [], [])],
    )
    # The shape is the interface: reading the items out of it needs no library call
    # at all, only the children and a pattern.
    children = list(doc)[3]
    pattern = S.element(S.item, (S.attr(S.sku, V.sku),), (V.text,))
    assert [(row.sku, row.text)
            for child in children
            for row in solve(pattern, child)] == [(G("a"), G("apple")), (G("b"), G("pear"))]

    # The three readers over an element. markup-text joins every text node under
    # it, markup-attribute answers one attribute's value and has NO answer for an
    # attribute the element does not carry.
    assert text(doc) == [G("applepear")]
    assert attribute(doc, S.id) == [G("7")]
    assert list(attribute(doc, S.missing)) == []
    assert text(S.element(S.p, (), ())) == [G("")]

    # The selector language. A step names elements and the three modifiers apply to
    # the step they follow, which is how XPath itself spells them.
    assert list(select(doc, (S.descendant(S.item), S.text()))) == [G("apple"), G("pear")]
    assert list(select(doc, (S.descendant(S.item), S.attribute(S.sku)))) == [G("a"), G("b")]
    assert select(doc, (S.descendant(S.item), S.index(2), S.text())) == [G("pear")]
    assert [tree(found) for found in select(doc, S.child(S.item))] == [
        (S.item, [(S.attr, S.sku, G("a"))], [G("apple")]),
        (S.item, [(S.attr, S.sku, G("b"))], [G("pear")]),
    ]
    assert [tree(found) for found in select(doc, S.self(S.order))] == [tree(doc)]
    assert list(select(doc, S.descendant(S.missing))) == []
    # A path walks down: child of a child, with the text of the last step.
    nested = parse_xml(G("<a><b><c>deep</c></b><c>shallow</c></a>")).one()
    assert list(select(nested, (S.child(S.b), S.child(S.c), S.text()))) == [G("deep")]
    assert list(select(nested, (S.descendant(S.c), S.text()))) == [G("shallow"), G("deep")]

    # Writing inverts parsing: the text is the element's own markup, with no
    # declaration and no layout, so it parses back to the same element.
    assert write(S.element(S.item, (S.attr(S.sku, G("a")),), (G("apple"),))) == [
        G('<item sku="a">apple</item>'),
    ]
    assert tree(parse_xml(S.markup_write(doc)).one()) == tree(doc)
    assert write(S.element(S.empty, (), ())) == [G("<empty/>")]
    # An attribute value written as a Number or a Symbol becomes text, because that
    # is all an XML attribute can hold.
    assert write(S.element(S.a, (S.attr(S.n, 1), S.attr(S.k, S.sym)), ())) == [
        G('<a n="1" k="sym"/>'),
    ]

    # HTML's own rules are the host's: an omitted end tag HTML allows is not an
    # error, so this parses and nests the second paragraph inside the first.
    assert tree(parse_html(G("<p>one<p>two")).one()) == (
        S.p, [], [G("one"), (S.p, [], [G("two")])],
    )
    assert text(S.markup_parse_html(G("<p>a<b>c</b></p>"))) == [G("ac")]

    # Every parse is STRICT, which is the difference between this library and the
    # host's own reader: a missing end tag, a stray close tag and text outside any
    # element are each repaired by the parser with a warning on stderr and a DOM
    # anyway, and each is a refusal here.
    assert refused(S.markup_parse_xml(G("<a><b></a>")))
    assert refused(S.markup_parse_xml(G("<a>")))
    assert refused(S.markup_parse_xml(G("not markup at all")))
    assert refused(S.markup_parse_xml(G("")))
    # An external entity is never fetched: the host refuses a SYSTEM entity and
    # this turns the warning into an error, where it would otherwise answer an
    # element with the entity's content silently missing.
    assert refused(S.markup_parse_xml(
        G("<!DOCTYPE d [<!ENTITY e SYSTEM '/etc/passwd'>]><d>&e;</d>")))

    # A selector the library does not know is refused with the five forms listed,
    # and a modifier with no step before it has nothing to modify.
    assert refused(S.markup_select(doc, S.nosuch(S.item)))
    assert refused(S.markup_select(doc, (S.text(), S.descendant(S.item))))
    assert refused(S.markup_select(doc, S.index(1)))
    # A value that is not an element is refused by every reader. The face
    # declares the element %Undefined%, so a Number reaches the Prolog body and
    # its type_error is the refusal, which the example's if-error over catch
    # reads the same way it would read a declared BadArgType.
    assert refused(S.markup_text(7))
    assert refused(S.markup_write(S.nosuch()))


#: MEASURED on this branch rather than inherited: this twin is new, so there is
#: no earlier pin to move. The 30 claims cover the six heads, the six selector
#: forms, the tagged attribute row and the nine refusals
#: [measured 2026-09-12: 110431 inferences against the example's 104638, minimum
#: of three serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --measure --rounds 3
#: examples/ch08-data/08-03-the-shipped-libraries/29-markup_lib.metta;
#: fixture=lib_markup at its functional commit, artifacts purged before the run;
#: commit=ed976b0e70c1176a7ef9feabb0359313105c786e].
#: RE-PINNED 2026-09-12, 110431 to 110488 (+57), every complaint from the host
#: parser mapped to one refusal, which added the empty-document case [measured
#: 2026-09-12: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=ed976b0e70c1176a7ef9feabb0359313105c786e].
#: RE-PINNED 2026-09-21, 110488 to 156709 (+46221), the sixty libraries derived
#: in MeTTa landed with merge 97763e7fa eight hours after the previous pin
#: 55d451b67, so every example importing one now pays a MeTTa derivation where
#: it paid a Prolog body instead, which the 2026-09-14 ruling accepts
#: explicitly as the price of a library that survives the engine swap [measured
#: 2026-09-21: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=6e09cb25d5495c2db3283166e6ce4e07eefecfb2].
#: RE-PINNED 2026-09-24, 156709 to 158681 (+1972), placed on the full-
#: configuration first-parent ladder from the pin commit 6e09cb25d: d27805154
#: carried lib 19a231b, which regenerated the six drifted Prolog faces from
#: their Prolog halves' export modes and declares this twin's refused inputs
#: %Undefined%, so each wrong value reaches the Prolog body, and the twin
#: asserts those refusals with refused(...) since twins commit aa891a0d; the
#: old assertions cannot run after d27805154 and the new ones cannot run before
#: it, so the face and the twin's own change are one step; the 77 commits
#: d27805154..c09dc4868, where the sweep puts the probes' steps at 33219ffa0 (a
#: bare library name resolves to its pkg.metta), 0cd329450 (the platform
#: refusal kind's catalog row and vocabulary member) and d8231f103 (a library
#: spec may not walk out of the library root); a7955cd07 carried lib 629c86c,
#: the library split, which moved every library's surface out of its pkg.metta
#: manifest into lib.metta beside it, so an import reads the manifest and then
#: imports the library's own source as a second file; 54784fded reads the
#: builtin type surface from every .metta in lib_builtin_types' directory,
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
#: 7472c4907 marks a module's reference face dirty instead of walking its
#: forward closure when the face's value carries the event, so
#: support_stabilize/3 walks the face's dependents only when the recomputed
#: value moved and an event that changes nothing recompiles no caller;
#: da91bc244 confines an exact removal's selection to its own atom:
#: native_retract_one/2 now records the selected clause's head, a clause/3
#: lookup per exact removal, and checks each removal made while the selector is
#: live against it, a few inferences per removal (+8 on most twins, +24 to +192
#: on the library twins that withdraw package rows) [measured 2026-09-24: min-
#: of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=WORKTREE].
#: RE-PINNED 2026-09-24, 158681 to 131865 (-26816), 0a81c782f loads a library's
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
#: RE-PINNED 2026-09-24, 131865 to 133844 (+1979), 0847c3d4c decides a platform
#: capability the first time anything reads it, by whether every library its
#: census row names resolves, where only a failed load used to record anything,
#: and 984eabe23 keeps each verdict in a flag decided under a mutex so two
#: threads' first reads agree; the count moves by what the twin's reads now
#: decide, about 660 inferences for a one-library capability and 1,964 for
#: markup's three, and by a few where it reads the census without deciding
#: [measured 2026-09-24: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=d832d20e8edfdad28ad52815757ba9e685ad2de3].
#: RE-PINNED 2026-09-24, 133844 to 133775 (-69), gate-perf's d781eab8f carries
#: an exact removal's selected head from the code that selected it, so a
#: withdrawal copies its equation once: 23 inferences fewer for each equation
#: removal the twin adopts and 4 for each it selects (-69); each step read
#: serially on its own committed tree, from gate-perf's pin at c7d7244fb, and
#: the fixed tree 4ff69551e reads what 4003462fe does [measured 2026-09-24:
#: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=4ff69551e0e226442cf7257b96af858adda957a4].
#: RE-PINNED 2026-09-24, 133775 to 133795 (+20), +20 at the change this re-pin
#: lands with, which publishes a from row by itself when rows are all a space
#: owes: its 36 predicates visible to filereader's registration walk cost a
#: batch above twelve names 72 inferences, each restricted space's core about
#: 28 a predicate, and every whole publication and face event its ledger's
#: bookkeeping [measured 2026-09-24: the twins lane alone on 8d651070d with the
#: change before this one and with this change too, one after the other in
#: battery 117's one path, every component at its pin; command=sh
#: tools/check.sh twins (twin_coverage.py inside tools/bounded.sh);
#: commit=WORKTREE].
BUDGET = 133795
