---
id: value-class-identifier
title: Value Class Identifier
type: concept
tags: [medieval-factions, architecture, kotlin]
summary: Every record's id is a Kotlin inline value class wrapping a UUID string, making identifiers type-safe at compile time and free at runtime.
created: 2026-08-07
updated: 2026-08-07
sources:
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/kotlin/com/dansplugins/factionsystem/faction/MfFactionId.kt
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    lines: 5-10
    claim: A faction id is a JvmInline value class wrapping a String, with a generate function producing a random UUID string.
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/kotlin/com/dansplugins/factionsystem/player/MfPlayerId.kt
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    lines: 7-14
    claim: A player id is a value class over a String that converts to and from a Bukkit OfflinePlayer, using the player's unique id as its value.
---

`MfFactionId`, `MfPlayerId`, `MfLawId`, `MfGateId`, `MfLockedBlockId`,
`MfDuelId`, `MfFactionRoleId` — every identifier in the plugin is a
`@JvmInline value class` wrapping a `String`.

## What it buys

At compile time these are distinct types: a function taking an `MfFactionId`
cannot be handed an `MfPlayerId`, even though both are strings underneath. In a
codebase where nearly every method signature takes at least one identifier, that
is the difference between a compiler error and a bug that only appears when two
UUIDs get swapped.

At runtime, Kotlin erases the wrapper. An `MfFactionId` in a local variable *is*
a `String` — no allocation, no indirection. The safety is free.

## Where the boundary lives

Each id class owns its own conversions, which keeps the awkward casts in one
place:

- `MfFactionId.generate()` produces a fresh random UUID string.
- `MfPlayerId.fromBukkitPlayer()` and `.toBukkitPlayer()` bridge to Bukkit's
  `OfflinePlayer`, so the rest of the plugin can pass a player identity around
  without depending on the Bukkit API.

That second pair is the more interesting one: it means the domain model refers
to players by a value it owns, not by a Bukkit object whose lifecycle the server
controls.

## The catch

Value classes and Java interoperation do not always agree, which is why domain
classes are peppered with `@get:JvmName("getId")`. Without it, Kotlin mangles
the getter name for a value-class-typed property, and Java callers — including
[[expansion-plugin|expansions]] written in Java such as [[fiefs]] — cannot see
it. The annotation is the tax for keeping the public API usable from Java.

## Related

The unwrapping to a plain column value happens in the [[repository-pattern]]
implementations, so the database sees only strings.
