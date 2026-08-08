---
id: faction
title: Faction
type: concept
moc: moc-faction-domain-model
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
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/kotlin/com/dansplugins/factionsystem/faction/MfFactionService.kt
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    lines: 62-66
    claim: Finding which faction a player belongs to is a linear scan over every cached faction's member list, not an indexed lookup.
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/kotlin/com/dansplugins/factionsystem/faction/JooqMfFactionRepository.kt
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    lines: 35-42
    claim: Membership is persisted in a separate mf_faction_member table, and the repository's player lookup is a subquery against it.
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

## Membership is stored sideways

The `members` list on the record is a view, not the storage. Membership lives in
its own `mf_faction_member` table, and the repository's "which faction is this
player in?" query is a subquery against it.

In memory, though, the service answers that question by scanning every cached
faction's member list until one matches. That is fine at the scale these servers
run at, and worth knowing before calling it inside a loop over online players.

Note also that the player record itself holds no faction reference — see
[[player-power]]. The edge is stored in exactly one place, which is why a player
cannot end up in two factions through disagreeing records.

## Related

Diplomacy lives entirely outside the faction record in
[[faction-relationship]].
