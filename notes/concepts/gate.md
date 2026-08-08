---
id: gate
title: Gate
type: concept
moc: moc-faction-domain-model
tags: [medieval-factions, domain-model, territory]
summary: A faction-owned wall of blocks that opens and closes when a redstone trigger block is powered.
created: 2026-08-07
updated: 2026-08-07
sources:
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/kotlin/com/dansplugins/factionsystem/gate/MfGate.kt
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    lines: 13-39
    claim: A gate holds a faction id, a cuboid area, a trigger block position, a material and a status, and decides whether to open or close by testing whether the trigger block is directly or indirectly powered.
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/kotlin/com/dansplugins/factionsystem/gate/MfGateStatus.kt
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    claim: Gate status is an enum with four values, OPEN, OPENING, CLOSED and CLOSING.
---

A gate is a rectangular region of blocks owned by a [[faction]] that fills and
empties itself in response to redstone. It is the castle-drawbridge affordance:
a wall you can open without breaking it.

## The record

`MfGate` stores a cuboid `area`, a single `trigger` block position, the
`material` to fill the area with, and a `status`. It does *not* store the blocks
themselves — the material plus the area is enough to reconstruct the wall.

## Guarded against unloaded chunks

Both `shouldOpen()` and `shouldClose()` begin by resolving the trigger's world
and checking `isChunkLoaded` before touching the block, returning `false` if
either fails. This is the load-bearing detail: a gate whose trigger sits in an
unloaded chunk must be treated as *unchanged*, not as unpowered. Reading a block
in an unloaded chunk would force a synchronous chunk load on the server thread —
a stall on the main thread every tick, for every gate on the server.

The consequence players see is that a gate only responds while someone is nearby
enough to keep its trigger loaded.

## Four states, not two

`MfGateStatus` is `OPEN`, `OPENING`, `CLOSED`, `CLOSING`. The transitional
states exist because a gate does not change in one tick — it is animated block
by block, and a gate caught mid-open must not be told to open again.

Because the status is persisted rather than inferred from the blocks, the plugin
knows what a gate believes it is after a restart, and after the area's blocks
have been altered by other means.

## Related

Gates are one of the record types carried across by [[legacy-data-migration]],
so the format predates the current database schema.
