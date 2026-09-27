"""Purpose: examples/ch19-spaces-backed-by-anything/19-01-spaces-of-your-own/06-a-shared-space-on-redis.metta in Python: a space whose atoms live in Redis.

Once attached, `&shared` is a space HANDLE like any other, so the writes are
`space += atom`, the reads are `space[pattern]` and nothing above the seam
knows there is a network under it. That is the whole point of the foreign
seam, and it is what makes this twin read like the spaces twins.

Two things can be absent and they are asked about separately, exactly as the
original asks: the provider, which a platform without library(redis) refuses
by that capability's name, and the server, which refuses a connection.
Open Obligations:
  To Do: None
  Hacks: None
  Future Enhancements: None.
"""

from metta import G, MeTTa, S, V, lib
from metta._errors.errors import MettaError

ADDRESS = G("127.0.0.1:6379")


def attached(home, space, address):
    """Whether a Redis attach succeeded, without letting the refusal escape.

    The function is looked up in the space `lib.redis` was imported into and
    APPLIED to the space being attached, exactly as the example writes
    `(import! &self ...)` and then `(redis-attach &shared ...)`. Reading it off
    `space.metta.self` asked the space being attached instead: `space.metta` is
    the engine as seen FROM that space, so its `.self` is that space and not
    the home, and the lookup raised AttributeError past the MettaError this
    catches. That failed the twin outright on a box where a missing Redis
    server should only make it answer False [measured 2026-09-21: the backing
    row registers redis-attach as lib_redis:'redis-attach'/3, and in one
    process the lookup succeeds on the home and raises on a fresh space].
    """
    try:
        list(home.fn["redis-attach"](space, address))
    except MettaError:
        return False
    return True


def available(m):
    """Whether this box has library(redis) and a server answering ADDRESS.

    The lane asks this before `twin(m)` and compares the budget below only
    where it answers True: the budget was measured against a running server,
    and without one the twin takes the same guarded path its example takes,
    whose count says nothing about it. The probe runs in an engine of its
    own, so nothing it imports or attaches moves the count `twin(m)` spends
    in the engine it is handed.
    """
    del m
    engine = MeTTa()
    try:
        home = engine.self
        try:
            home += lib.redis
        except MettaError:
            return False
        return attached(home, engine.space(S.probe), ADDRESS)
    finally:
        engine.close()


def twin(m):
    """Attach, write, join, remove, detach, and leave the store as found."""
    try:
        m += lib.redis
    except MettaError:
        return  # no provider: the platform has no library(redis)

    shared = m.metta.space(S.shared)
    if not attached(m, shared, ADDRESS):
        # The example prints its skip here. A twin has no door for prose.
        return

    detach = m.fn["redis-detach"]

    # A write goes to Redis and a read comes back from it, through the seam.
    shared += [
        S.city(S.paris, S.france),
        S.city(S.lyon, S.france),
        S.city(S.berlin, S.germany),
    ]
    assert sorted((row.c for row in shared[S.city(V.c, S.france)]), key=str) == [
        S.lyon,
        S.paris,
    ]

    # A join mixes shared facts with native ones: the engine splits the
    # conjunction per conjunct and unifies its own side.
    local = m.metta.space(S.local)
    local += S.capital(S.france, S.paris)
    assert [
        row.city
        for row in local[S.capital(V.country, V.city)]
        if shared[S.city(row.city, row.country)]
    ] == [S.paris]

    # `remove-atom` is exact and reaches the shared set, so what one process
    # takes out is gone for every other one.
    shared -= S.city(S.berlin, S.germany)
    assert shared[S.city(V.c, S.germany)] == []

    # `redis-detach` releases the binding and LEAVES the facts in Redis,
    # which is the difference from clearing a space: the next attach under
    # the same name finds them.
    detach(shared).one()
    assert attached(m, shared, ADDRESS)
    assert sorted((row.c for row in shared[S.city(V.c, S.france)]), key=str) == [
        S.lyon,
        S.paris,
    ]

    # And the name is owned while it is attached, so a second attach without
    # the detach is refused rather than raced.
    assert not attached(m, shared, ADDRESS)

    # Leaving the store as it was found, because a shared space outlives the
    # process that wrote it.
    shared -= S.city(S.paris, S.france)
    shared -= S.city(S.lyon, S.france)
    assert shared[V.any] == []
    detach(shared).one()


#: MEASURED on this branch rather than inherited: this twin is new, so there is
#: no earlier pin to move
#: [measured 2026-09-07: 113469 inferences, 0.9558x the example's 118714; command=python
#: extensions/python/tools/twin_coverage.py --measure --rounds 3;
#: fixture=docs/every-atom-has-an-example at its example commits; commit=98397cdd04679cbf40b2d515076dadc09c1b0a32].
#: RE-PINNED 2026-09-08, 113476 to 46265 (-67211), boot content moved: the
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
#: RE-PINNED 2026-09-08, 113476 to 49056 (-64420), The engine and library
#: predicates now resolve through their owning modules and the explicit engine
#: facade; compiled program lookup crosses the added metta_engine tier
#: [measured 2026-09-08: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=ede2ac57e213a0d4502c6bbbca6227f97015b720].
#: RE-PINNED 2026-09-08, 49056 to 49911 (+855), Trailing occurrence arguments,
#: token allocation in native writes, exact source withdrawal and transaction-
#: safe shared-table guards change the engine work priced by this twin; answer
#: bags retain the upstream law [measured 2026-09-08: min-of-3 serial fresh
#: processes; command=python extensions/python/tools/twin_coverage.py --repin;
#: commit=7f00ac7932fefa6f380fc8d14ec583ea0c58eff4].
#: RE-PINNED 2026-09-09, 49911 to 11910 (-38001), a library's Prolog half
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
#: RE-PINNED 2026-09-11, 11910 to 12179 (+269), end-of-wave re-pin on the
#: merged tree after FROM's reference rows and four engine units, the closed-
#: set derivations and two host services, BINDING's one native evaluation entry
#: and boot import, W-OBSERVE's observer guard, PERF's receipts batching and
#: cursor retirement, and the three REDS repairs (derived runtime resources and
#: the shared loader, the tool-lane repairs, the corpus example); serial
#: minimum of three fresh processes through the lane's run_twin with
#: file_search_cache_time=9223372036854775807 set before child boot [measured
#: 2026-09-11: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=57f84148ba2684015f052d533f3197eca07b1f7b].
#: RE-PINNED 2026-09-18, 11910 to 12763 (+853), the branch's landings since the
#: 09-10 pins, re-taken on the tip f06186a96: the compiled call law (e59104ace:
#: an Atom argument enters as written, a Python object crosses as a value, a
#: positional call of a bound callee is the plain application and a compiled
#: lambda is bare where it is applied), the one codec at the grounded call
#: (fd0af38f7, whose read of a call site's written keyword tail costs about six
#: inferences per translated site, read once since 7cc8fb863), the runnable
#: cache's dependency index written by the producer (a9e2c06d3, which takes
#: back the walk of the generated code 5416e741d charged at every miss), the
#: host patches of 09-17 and the class units of 09-13 to 09-16 the ladder in
#: docs/journal/2026-09-14-runnable-artifact-dependencies.md places; serial
#: minimum of three fresh processes through the lane's run_twin with
#: file_search_cache_time=9223372036854775807 set before child boot [measured
#: 2026-09-18: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=6944d06ce96fdbcd1faefb640f15dbfa0cf286dd].
#: RE-PINNED 2026-09-21, 12763 to 15123 (+2360), the sixty libraries derived in
#: MeTTa landed with merge 97763e7fa eight hours after the previous pin
#: 55d451b67, so every example importing one now pays a MeTTa derivation where
#: it paid a Prolog body instead, which the 2026-09-14 ruling accepts
#: explicitly as the price of a library that survives the engine swap [measured
#: 2026-09-21: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=6e09cb25d5495c2db3283166e6ce4e07eefecfb2].
#: RE-PINNED 2026-09-24, 15123 to 20937 (+5814), placed on the full-
#: configuration first-parent ladder from the pin commit 6e09cb25d: a7955cd07
#: carried lib 629c86c, the library split, which moved every library's surface
#: out of its pkg.metta manifest into lib.metta beside it, so an import reads
#: the manifest and then imports the library's own source as a second file;
#: 54784fded reads the builtin type surface from every .metta in
#: lib_builtin_types' directory, which restored the 195 builtin cost rows the
#: split's manifest-only read had dropped; 63b910f4f added a clause to
#: metta_reference_internal/2 that asks the specializer's ho_specialization/3
#: registry, so every reference grade a load computes pays that lookup, which
#: is how defined-name, documented and undocumented stopped reporting
#: specializer residues; d6e09995c retires a load's package rows from every
#: space but its library home after package_load/3, withdrawing each through
#: metta_remove_atom_reference/1, which uncompiles the row's equation, so every
#: import into an importing space pays that withdrawal; where a twin's move
#: exceeds these steps, the remainder is drift that stayed inside its band
#: (four inferences, or its own declared allowance) on every other interval
#: [measured 2026-09-24: min-of-3 serial fresh processes; command=python
#: extensions/python/tools/twin_coverage.py --repin; commit=WORKTREE].
#: RE-PINNED 2026-09-25, 20937 to 20944 (+7), every force of a waiting function
#: names the module it is made from, through fun_home_in/3, and a write forces
#: only its own space; the lanes' tree read this twin +50 off its pin before
#: the step, an offset that is not this step's, so the pin moves by the step's
#: delta alone [measured 2026-09-25T16:54:32+10:00: one full twins lane before
#: this commit and one with it, the two read on one battery path at the
#: landing's HEAD; command=python extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-27, 20944 to 20951 (+7), the host switch to swipl-
#: patched.7 and the seat changes it needs: +2 the host switch to swipl-
#: patched.7, which delivers the heartbeat inside loops, so a held engine ticks
#: and the held goals read its ticks from the raw counter, 9 inferences a tick,
#: and whose three new system predicates ('$heartbeat'/0, '$file_hash'/2,
#: '$qlf_source_changed'/2) filereader's walk of every visible predicate
#: (existing_predicate_arities/2) meets, 2 inferences each; +5 the held goals
#: reading Used through metta_py_work/2, which leaves a held engine's own ticks
#: out and reads the tick term inside its opening edge, 5 inferences a held
#: reading; the trunk's lane read this twin +118 off its pin, an offset that is
#: not this landing's, so the pin moves by the landing's delta alone [measured
#: 2026-09-27T03:41:21+10:00: one full twins lane of the trunk and one with
#: this landing, wt-merge battery 1, the trunk on swipl-patched.6 and every
#: part on .7, each through a same-shape host shim; command=python
#: extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-27, 20951 to 20954 (+3), a force of a waiting function
#: takes the typing policy and the specializer's lock before translation:
#: spaces:metta_ensure_compiled/2 stabilises the policy and takes the
#: specializer's mutex around the translation once per force, and the
#: translation's own per-pair stabilisation re-enters through
#: with_typing_policy_stable/1's first clause; the lanes' tree read this twin
#: +118 off its pin before the step, an offset that is not this step's, so the
#: pin moves by the step's delta alone [measured 2026-09-27T09:56:55+10:00: one
#: full twins lane before this commit and one with it, each read in one battery
#: of the landing's HEAD after a QLF purge and one warm-up; command=python
#: extensions/python/tools/twin_coverage.py].
#: RE-PINNED 2026-09-28, 20954 to 20952 (-2), -2 at tsm-licence's notices
#: reader as its block lookahead amended it: engine/host_notices.pl, which
#: every boot loads, opens a component block only where its Component field
#: directly follows the line of 78 '=', the calls not traced; read on swipl-
#: patched.8, the count above on .7, which no longer runs [measured
#: 2026-09-28T12:31:49+10:00: full twins lanes in wt-merge's battery 1 on
#: swipl-patched.8 at this boundary, engine/host_notices.pl as amended against
#: the day before's as first written; command=sh tools/check.sh twins].
#: RE-PINNED 2026-09-27, 20952 to 21067 (+115), +2 at the host switch to swipl-
#: patched.8, whose swi-heartbeat-inferences-charged-to-the-program leaves the
#: interrupt poll's own inferences out of every count, so a window the seat's
#: calibrated poll correction read 1 to 3 low on .7 reads exactly; -3 at
#: interrupts B's seat change, which drops the poll's boot calibration, its
#: tick charges and its tick record: a held reading through metta_py_work/2
#: brackets 3 inferences where it bracketed 6, a registration walk over more
#: than twelve names meets 6 fewer seat predicates (12 or 14 fewer), and a
#: thread the twin joins credits it 11 where it credited 16; the base read
#: 21,070 where the pin stood at 20,954, a gap of -116 this re-pin takes out
#: [measured 2026-09-27T20:07:01+10:00: full twins lanes in wt-merge's battery
#: 1, tsm-licence's series and its engine reader on swipl-patched.7, the series
#: on swipl-patched.8, and the stack through janus-contract B on swipl-
#: patched.8 twice; command=sh tools/check.sh twins]. With step 4's notices
#: reader as amended both counts read -2 [measured 2026-09-28T12:34:38+10:00:
#: full twins lanes in wt-merge's battery 1 on swipl-patched.8 at this
#: boundary, engine/host_notices.pl as amended against the day before's as
#: first written; command=sh tools/check.sh twins].
BUDGET = 21067
#: The count VARIES by a few tens, because every read and write crosses a
#: socket and the subscription thread's own work lands in the same counter.
#: Three single-round measurements on this branch gave 113484, 113469 and
#: 113484, a spread of 15, so the band is the midpoint plus a round 200
#: either side rather than the tree's deterministic 4
#: [measured 2026-09-07: python extensions/python/tools/twin_coverage.py
#: --measure --rounds 1, three times, against a redis:7.2.3-alpine container;
#: commit=98397cdd04679cbf40b2d515076dadc09c1b0a32].
ALLOWANCE = 200
