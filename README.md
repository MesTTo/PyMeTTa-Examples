# PyMeTTa by example

Every file here is a **twin**: one MeTTa example from
[the MeTTa corpus](https://github.com/MesTTo/MeTTa-Examples), written again in
Python against PyMeTTa's surface. A twin proves every claim its original
makes, and it does so with **no MeTTa source text**: no strings to parse and no
s-expressions. So the pair answers a question prose cannot: given a thing
MeTTa says one way, what does Python say?

Each section below is a real pair, MeTTa on the left of the page and its twin
underneath, shortest first. The Python is the twin's body verbatim; its
docstring and obligation header are the only things cut.

## An equation is a function

```metta
(= (f $x) (* $x $x))

!(test (f 1) 1)
```

```python
def f(x: int) -> int:
    return x * x

assert f(1) == [1]
```

A MeTTa equation is a Python function, defined with `def` and nothing else.
The annotations are the signature MeTTa would have written as `(: f (-> Number
Number))`. The answer comes back as a **list**, because a MeTTa call can answer any
number of answers and one is not a special case, so `[1]` rather than `1`.

## A pattern selects on shape, not on names

```metta
(= (h (justdata haha $B) $C)
   (+ $B $C))

!(test (h (justdata haha 30) 40) 70)
```

```python
def h(data, c: int) -> int:           # (= (h (justdata haha $B) $C)
    match data:                       #    (+ $B $C))
        case (S.justdata, S.haha, b):
            return fn.add(b, c)

assert h(S.justdata(S.haha, 30), 40) == [70]
```

MeTTa's head pattern becomes Python's `match`. `S.justdata` is the symbol
factory: a symbol comes from `S`, never from a string, so the type checker and
your editor can both see it. `fn.add` is the engine's `+` reached by its
Python name. `b` is match-bound, so its type is not known statically and the
engine does the addition.

## Many answers are ordinary iteration

```metta
!(test (collapse (1 2 3))
       ((1 2 3)))
```

```python
assert m.eval(Expression((1, 2, 3))) == [Expression((1, 2, 3))]
```

Nondeterminism is not a special mode. A form with several answers hands them
back as a list, and `collapse` gathers a superposition into one expression.
`Expression` builds an ordered atom from any iterable, so `(1 2 3)` is
`Expression((1, 2, 3))` and no string is parsed on the way.

## Python is a notation, not a foreign country

```metta
!(import! &self "_fixtures/python_import_file.py")

!(test (repr (py-call (python_import_file.greet "MeTTa User")))
       "Hello, MeTTa User from Python!")
```

```python
m += lib(FIXTURE)

py = m.fn.py_call
greeting = py(S["python_import_file.greet"](ground("MeTTa User")))
assert greeting == [S["Hello, MeTTa User from Python!"]]
```

`m += lib(...)` loads a module into the space. `S["..."]` is the bracket door,
for a head whose name is not a Python identifier. `ground(...)` marks a Python
value as a grounded atom, the thing MeTTa treats as opaque, which is how a
Python string crosses without becoming structure.

## A recursive definition with a budget

```metta
!(add-atom &self (= (fib $N)
                    (if (< $N 2)
                        $N
                        (+ (fib (- $N 1))
                           (fib (- $N 2))))))

!(test (with-pragma! ((max-stack-depth 100000000)) (fib 30)) 832040)
```

```python
def fib(n: int) -> int:
    return n if n < 2 else fib(n - 1) + fib(n - 2)

raised = (S.max_stack_depth(100_000_000),)
assert m.fn.with_pragma(raised, S.fib(30)) == [832040]
```

The recursion is Python's own, and it runs in the engine. A pragma is a tuple
of settings passed to `with_pragma`, so `max-stack-depth` is
`S.max_stack_depth`, through the underscore-to-hyphen map, which is the one
respelling this surface does.

## Types, and reading a type back

```metta
(: apply (-> (-> $tx $ty) $tx $ty))
(= (apply $f $x) ($f $x))

!(test (let (get-type apply) (-> (-> Bool Bool) Bool $result) $result)
       Bool)
```

```python
def apply[X, Y](f: Callable[[X], Y], x: X) -> Y:
    return f(x)

assert apply(S["not"], FALSE) == [True]

assert m.solve(arrow(arrow(bool, bool), bool, V.result),
               fn.get_type(S.apply)).result == S.Bool
```

A MeTTa arrow type is a Python generic signature: `(-> (-> $tx $ty) $tx $ty)`
is `[X, Y](f: Callable[[X], Y], x: X) -> Y`. The last claim goes the other
way, asking the engine for a type and binding the answer: `V.result` is a
variable, `m.solve` unifies, and `.result` reads that binding off by name.

## Depth is operational, answers are not

A twin states the same answer claim as its MeTTa original, but the two routes
need not spend the same execution resource. `fib.py(n)` recurses on Python's
stack and is bounded by `sys.getrecursionlimit()`, while the compiled equation
runs under the engine's last-call optimization (LCO) and spends reduction fuel
rather than Python frames.

The two therefore part company on DEPTH and never on the answer. Under a
recursion limit of 80 both routes agree for every `n` up to 20; at `n=100`,
`fib.py` raises `RecursionError` while the engine answers
354224848179261915075. Whenever both routes finish, they must answer the same
value, so a depth divergence is an operational fact about the route and never
a disagreement about what the program means.

That is executed rather than asserted here: `test_docs_law.py`'s
`test_twin_depth_divergence_is_operational_not_an_answer_difference` builds
the probe, drops the limit and requires both halves.

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
| `ch04-spaces-and-matching` | 19 | A space as the thing a program lives in, across two sections: what a write makes visible to a later match, and how a pattern's shape, not its names, selects. |
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
| `ch18-performance` | 20 | Two sections: larger workloads (a million atoms, million-step kernels) and memoisation and tabling. |
| `ch19-spaces-backed-by-anything` | 10 | Four sections: spaces of your own (inherited, restricted, parametric), a space in C, a builtin in C, and a space on MORK. |
| `ch20-extending-the-engine` | 38 | Six sections: translator rules, MeTTa written in MeTTa, the Prolog underneath, modules and the catalog, files and processes, and tokens and the reader. |
| `ch22-a-reasoner-you-can-serve` | 27 | Three sections: logic programs, weighted answers, and search, up to a dependently-typed backward chainer. |

## Where a twin cannot follow

Some things MeTTa says have no Python spelling yet. A twin never fakes one:
what it cannot say becomes an entry in [`residue.json`](residue.json), naming
the missing spelling and the work it waits on. The backlog derives itself from
the corpus rather than being maintained by hand, so this directory is also the
honest measure of how much of MeTTa Python can currently express.
