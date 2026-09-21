# PyMeTTa by example

Every file here is a **twin**: one MeTTa example from
[the MeTTa corpus](https://github.com/MesTTo/MeTTa-Examples), written again in
Python against PyMeTTa's surface. A twin proves every claim its original
makes, and it does so with **no MeTTa source text** — no strings to parse, no
s-expressions. So the pair answers a question prose cannot: given a thing
MeTTa says one way, what does Python say?

```python
"""examples/ch03-atoms-and-expressions/01-comments.metta in Python:
a definition with comments in it."""


def twin(m):
    """Define a function of no arguments, then check what it answers."""
    @m.define
    def f():
        return 42

    assert f() == [42]
```

That is the whole shape. A twin is an ordinary Python program: it takes a
space, uses the library, and asserts. There is no framework to learn.

## Running them

```sh
python extensions/python/tools/twin_coverage.py     # every twin, against every original
```

The lane runs each example and its twin and compares what they answer, so a
twin cannot drift from the program it mirrors without the lane going red.

## Reading order

Directory names are the reading order, so a listing is the index:

```text
ch07-control-flow/07-02-case/03-caseconstrain.py
^chapter          ^section   ^order within the section
```

Chapter and section numbers match the MeTTa corpus exactly, so
`ch07-control-flow/07-02-case/03-caseconstrain.py` is the twin of
`examples/ch07-control-flow/07-02-case/03-caseconstrain.metta`. Read them side
by side.

**If you are an LLM, read [llms.txt](../../../../llms.txt)** for the whole
surface with exact return shapes, rather than inferring it from here.

## What is covered

323 twins across eighteen chapters. Chapters 1, 2, 13 and 21 of the MeTTa
corpus have no twins yet: they are installation, a first program, the shell,
and the TypeScript seat, and none of those are about the Python surface.

| chapter | twins | what you learn to write in Python |
|---|---|---|
| `ch03-atoms-and-expressions` | 6 | Atoms as Python values: symbols, strings that stay values rather than structure, how an atom prints, and what reading a form gives you. |
| `ch04-spaces-and-matching` | 19 | A space as the thing a program lives in, across two sections: what a write makes visible to a later match, and how a pattern's shape — not its names — selects. |
| `ch05-equations-and-evaluation` | 26 | Equations as rewrites, in four sections: defining and redefining, source order, partial definitions, the number library, and arithmetic that runs backwards. |
| `ch06-many-answers` | 10 | Nondeterminism as ordinary Python iteration: superposition, branches that answer nothing, and collapsing many answers into one. |
| `ch07-control-flow` | 42 | Control as values, in five sections: `if` and booleans, `case`, `let` and sequencing, bounded and committed searches, and recursion. |
| `ch08-data` | 70 | The largest chapter, in three sections: atoms, lists and folds; sequence variables; and the shipped libraries exercised from Python. |
| `ch09-types` | 21 | What a type is, where it lives, what a signature does, and how the output type decides a call. |
| `ch10-errors-and-refusals` | 2 | Errors as data rather than exceptions, and raising one deliberately. |
| `ch11-python-as-a-notation` | 7 | The seam itself: the five names for it, booleans crossing, importing a `.py`, and NumPy arriving through it. |
| `ch12-testing` | 4 | The assertion family, equality against reduction, and the answer bags a failing comparison hands back. |
| `ch14-seeing-your-program` | 2 | Bounds, time and pragmas, and reading the clock and the command line. |
| `ch15-writing-transactions-and-worlds` | 6 | A counter five threads share, state cells as values, hooks at the write door, and admission pools. |
| `ch16-events-and-standing-queries` | 1 | The event layer's own declarations. |
| `ch17-concurrency-and-the-loop` | 12 | Threads through `lib_thread`, the two blocking binds, and branches running on real threads. |
| `ch18-performance` | 20 | Two sections: larger workloads — a million atoms, million-step kernels — and memoisation and tabling. |
| `ch19-spaces-backed-by-anything` | 10 | Four sections: spaces of your own (inherited, restricted, parametric), a space in C, a builtin in C, and a space on MORK. |
| `ch20-extending-the-engine` | 38 | Six sections: translator rules, MeTTa written in MeTTa, the Prolog underneath, modules and the catalog, files and processes, and tokens and the reader. |
| `ch22-a-reasoner-you-can-serve` | 27 | Three sections: logic programs, weighted answers, and search — up to a dependently-typed backward chainer. |

## Where a twin cannot follow

Some things MeTTa says have no Python spelling yet. A twin never fakes one:
what it cannot say becomes an entry in [`residue.json`](residue.json), naming
the missing spelling and the work it waits on. The backlog derives itself from
the corpus rather than being maintained by hand, so this directory is also the
honest measure of how much of MeTTa Python can currently express.
