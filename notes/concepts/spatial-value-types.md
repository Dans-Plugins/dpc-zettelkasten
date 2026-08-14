---
id: spatial-value-types
title: Spatial Value Types
type: concept
moc: moc-plugin-architecture
tags: [medieval-factions, architecture, domain-model]
summary: Positions are stored as plain records holding a world UUID and numbers, never as live Bukkit objects, and are converted at the boundary.
created: 2026-08-14
updated: 2026-08-14
sources:
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/kotlin/com/dansplugins/factionsystem/area/MfPosition.kt
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    lines: 7-27
    claim: MfPosition holds a world UUID with double x, y and z plus yaw and pitch, and converts to a Bukkit Location only through toBukkitLocation, which returns null when the world is not loaded.
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/kotlin/com/dansplugins/factionsystem/area/MfBlockPosition.kt
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    lines: 8-26
    claim: MfBlockPosition holds a world UUID and integer coordinates, with named conversions to and from a Bukkit Block.
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/kotlin/com/dansplugins/factionsystem/area/MfChunkPosition.kt
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    lines: 7-21
    claim: MfChunkPosition holds a world UUID and an x and z chunk coordinate, converting to and from a Bukkit Chunk.
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/kotlin/com/dansplugins/factionsystem/area/MfCuboidArea.kt
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    lines: 10-14
    claim: MfCuboidArea is two corner block positions and throws IllegalStateException on construction if the two corners are in different worlds.
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/kotlin/com/dansplugins/factionsystem/area/MfCuboidArea.kt
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    lines: 16-87
    claim: Min and max corners, height, width, depth, centre, the block list, contains and distanceSquared are all computed from the two stored corners rather than stored.
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/kotlin/com/dansplugins/factionsystem/gate/MfGate.kt
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    lines: 13-24
    claim: A gate stores its area as an MfCuboidArea and its trigger as an MfBlockPosition.
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/kotlin/com/dansplugins/factionsystem/claim/MfClaimedChunk.kt
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    lines: 8-17
    claim: MfClaimedChunk stores worldId, x and z as its own fields rather than an MfChunkPosition, offering constructors that accept a Bukkit Chunk or an MfChunkPosition.
---

The records that get persisted do not hold Bukkit objects. The `area` package
supplies four plain types — a precise position, a block, a chunk, and a cuboid —
each carrying a world **UUID** and numbers, and each crossing into Bukkit only
through an explicit named conversion.

## Why a UUID and not a world

A `World` is a live server object; a `UUID` is a value. Storing the identifier
rather than the reference is what lets these records be written to columns by
[[jooq-persistence]], survive a restart, and be held across a thread boundary
without violating [[main-thread-safety]].

The conversions back are correspondingly *nullable*: `toBukkitLocation()` and
`toBukkitBlock()` resolve the world by UUID and yield null if the server has no
such world loaded. Every caller has to decide what an unresolvable position
means, rather than receiving a stale object.

## The cuboid is derived, not stored

`MfCuboidArea` keeps only two corners and computes everything else — `minPosition`
and `maxPosition` per axis, height, width, depth, centre, the full block list,
and a `contains` test. Its `init` block rejects a pair of corners in different
worlds outright, so a mixed-world area cannot exist even briefly.

It also carries `distanceSquared`, which clamps the query point onto the box per
axis before measuring — the distance to the *nearest face*, not to the centre,
and squared to avoid a square root.

## Who uses them

These are the vocabulary the rest of the model is written in. A [[gate]] stores
an `MfCuboidArea` plus a trigger `MfBlockPosition`; a [[locked-block]] is a
block position with an owner; a [[duel]] snapshots both participants as
`MfPosition`, yaw and pitch included, so it can put them back exactly as they
stood.

Adoption is not uniform. [[claimed-chunk]] predates or sidesteps the pattern —
`MfClaimedChunk` stores `worldId`, `x` and `z` as loose fields and merely offers
a convenience constructor taking an `MfChunkPosition`. Whether that is history
or intent is not recorded anywhere in the repository.

## Related

The same instinct — replace a primitive or a framework object with a small
purpose-built type — appears at the identity layer as
[[value-class-identifier]]. Here it buys persistence and thread safety; there it
buys type safety between otherwise identical strings.
