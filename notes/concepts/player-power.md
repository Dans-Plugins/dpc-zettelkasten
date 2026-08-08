---
id: player-power
title: Player Power
type: concept
moc: moc-faction-domain-model
tags: [medieval-factions, domain-model, power]
summary: The per-player scalar that accrues with time online and is lost on death, and which sums into a faction's strength.
created: 2026-08-07
updated: 2026-08-07
sources:
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/kotlin/com/dansplugins/factionsystem/player/MfPlayer.kt
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    lines: 7-16
    claim: A player record stores power and powerAtLogout alongside the player id, name, bypass flag, and chat channel.
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/resources/config.yml
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    lines: 8-15
    claim: Player power is configured by initialPower 5, maxPower 20, minPower -5, hoursToReachMaxPower 12, hoursToReachMinPower 72, powerLostOnDeath 1, and powerGainedOnKill 1.
---

Every player has a power score. It is the atom that [[faction-power]] is built
from, and the mechanism by which player activity turns into territorial control.

## The dials

The defaults in `config.yml` describe the intended rhythm:

| Setting | Default | Meaning |
|---|---|---|
| `initialPower` | 5 | Where a new player starts |
| `maxPower` | 20 | Individual ceiling |
| `minPower` | -5 | Individual floor — power can go negative |
| `hoursToReachMaxPower` | 12 | Time from zero to ceiling |
| `hoursToReachMinPower` | 72 | Time from zero to floor |
| `powerLostOnDeath` | 1 | Deducted when you die |
| `powerGainedOnKill` | 1 | Awarded to the killer |

The asymmetry between the two "hours to reach" values is the design statement:
climbing takes 12 hours, falling takes 72. Power is easier to build than to
lose, which keeps a faction from evaporating over a quiet week.

## Negative power

The floor is below zero. A player who has died repeatedly does not merely stop
contributing to their faction — they subtract from it, dragging the faction
below its [[demesne-limit]] and exposing its claims. This is what makes sustained
warfare bite: killing the same defender repeatedly is territorially meaningful,
not just cosmetic.

## Power at logout

The record stores `powerAtLogout` separately from `power`. The two fields let
the plugin reconstruct what a player's power should be when they return, rather
than requiring a background task that ticks every offline player. It is the same
trick as computing [[faction-power]] on read: store the inputs, derive the value.

## Related

The player record also carries `isBypassEnabled` (an operator override for land
protection) and the player's [[faction]] chat channel — both incidental to power,
but stored on the same row.
