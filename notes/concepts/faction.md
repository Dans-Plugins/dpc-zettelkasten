---
id: faction
title: Faction
type: concept
tags: [medieval-factions, domain-model]
summary: The central record of the simulation — a named group of players with land, roles, diplomacy, and a power score.
created: 2026-08-07
updated: 2026-08-07
sources:
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/kotlin/com/dansplugins/factionsystem/faction/MfFaction.kt
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    lines: 14-30
    claim: A faction is a Kotlin data class holding id, version, name, description, members, invites, flags, prefix, home, bonus power, autoclaim, roles, default permissions, and applications.
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/kotlin/com/dansplugins/factionsystem/faction/MfFactionService.kt
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    lines: 30-45
    claim: The faction service keeps all factions in a ConcurrentHashMap loaded from the repository at startup.
---

A faction is the unit of political organisation: a named group of players that
can hold land, make war, and be inherited into a feudal hierarchy. Everything
else in the domain model either belongs to a faction or describes a relation
between two of them.

## What the record holds

`MfFaction` is an immutable Kotlin data class. Its fields fall into four groups:

- **Identity** — an [[value-class-identifier|id]], a `name`, an optional chat
  `prefix`, and a `description`.
- **People** — `members`, outstanding `invites`, and pending `applications`.
- **Governance** — `roles` (see [[faction-role]]), `defaultPermissionsByName`
  (see [[faction-permission]]), and `flags` (see [[faction-flag]]).
- **Territory** — a `home` position and an `autoclaim` toggle. Note that the
  claims themselves are *not* stored on the faction; see [[claimed-chunk]].

The `version` field is not domain data — it exists for [[optimistic-locking]].

## Power is computed, not stored

`power` and `maxPower` are computed properties, derived on every read from the
members' [[player-power]] and from vassals. Nothing writes a faction's power to
the database. This is what makes [[faction-power]] a live quantity that responds
to players logging in and dying, rather than a value that has to be recalculated
by a scheduled job.

The exception is `bonusPower`, an operator-granted constant that is stored — and
which the faction can decline by turning off the `acceptBonusPower` flag.

## Where it lives at runtime

`MfFactionService` loads every faction into a `ConcurrentHashMap` when the
plugin starts and serves reads from memory. Writes go through the same service
so that they can fire [[faction-events]] and be persisted through the
[[repository-pattern]]. Code should never reach past the service to the
repository — see [[service-layer]].

## Related

Membership is one half of a pair: a faction lists its members, and a
[[player-power|player]] record separately answers "which faction am I in?"
through a repository lookup. Diplomacy lives entirely outside the faction record
in [[faction-relationship]].
