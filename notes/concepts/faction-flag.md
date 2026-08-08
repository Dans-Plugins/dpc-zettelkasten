---
id: faction-flag
title: Faction Flag
type: concept
moc: moc-faction-domain-model
tags: [medieval-factions, domain-model, governance]
summary: Per-faction toggles that change how the simulation treats a faction — land access for allies, friendly fire, mob protection, and map colour.
created: 2026-08-07
updated: 2026-08-07
sources:
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/kotlin/com/dansplugins/factionsystem/faction/flag/MfFlags.kt
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    lines: 7-70
    claim: The built-in flags are alliesCanInteractWithLand, vassalageTreeCanInteractWithLand, neutral, color, allowFriendlyFire, acceptBonusPower, enableMobProtection, liegeChainCanInteractWithLand, and protectVillagerTrade.
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/kotlin/com/dansplugins/factionsystem/faction/flag/MfFlag.kt
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    claim: A flag is typed, with boolean and string constructors, and carries a default supplier plus an optional validator.
---

A flag is a typed, per-[[faction]] setting whose default comes from the server
configuration and whose value the faction can then change. Where
[[faction-permission]] governs what *members* may do, flags govern how the world
treats the faction as a whole.

## The built-in set

| Flag | What it changes |
|---|---|
| `alliesCanInteractWithLand` | Allies may build in the faction's [[claimed-chunk|claims]] |
| `vassalageTreeCanInteractWithLand` | The whole [[vassalage]] tree may build |
| `liegeChainCanInteractWithLand` | The chain of lieges may build |
| `neutral` | The faction opts out of war |
| `color` | Hex colour used by [[map-integration]] |
| `allowFriendlyFire` | Members may damage each other |
| `acceptBonusPower` | Operator-granted power counts toward [[faction-power]] |
| `enableMobProtection` | Hostile mob behaviour inside claims |
| `protectVillagerTrade` | Villager trading protection inside claims |

Three of the nine are about land access, and each names a different slice of the
[[faction-relationship]] graph. That is the recurring theme: a flag is usually
the switch that turns a diplomatic fact into a physical permission.

## Typed with validation

`MfFlag` is generic over its value type. Boolean flags read their default
straight from config; the `color` flag is a string with a supplier that can
generate a random pleasant colour when the config says `random`, and a validator
that rejects anything not matching `#RRGGBB`. Validation returns a localised
failure message rather than throwing, so a bad `/f flag set` is a player-facing
error rather than a stack trace.

## Server override

A server can force a policy regardless of what factions want. The clearest
example: when `factions.allowNeutrality` is false, `MfFactionService` clears the
`neutral` flag on every existing faction at startup rather than merely refusing
future changes. Configuration wins over stored state.

## Related

Flags live inline on the [[faction]] record as `MfFlagValues`, so changing one is
a faction write subject to [[optimistic-locking]].
