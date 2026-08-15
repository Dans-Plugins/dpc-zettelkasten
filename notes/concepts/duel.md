---
id: duel
title: Duel
type: concept
moc: moc-faction-domain-model
tags: [medieval-factions, domain-model, combat]
summary: A consented fight between two players in which the losing blow is cancelled and both duellists are restored to the health and position they started from.
created: 2026-08-14
updated: 2026-08-14
sources:
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/kotlin/com/dansplugins/factionsystem/duel/MfDuel.kt
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    lines: 7-20
    claim: A duel records both player ids, both starting health values, both starting positions and an end time.
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/kotlin/com/dansplugins/factionsystem/command/duel/accept/MfDuelAcceptCommand.kt
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    lines: 81-95
    claim: Accepting an invite deletes the invite and creates the duel, snapshotting each player's current health and location and setting the end time to now plus the configured duels.duration.
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/kotlin/com/dansplugins/factionsystem/listener/EntityDamageListener.kt
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    lines: 31-55
    claim: When damage during a duel would take a participant to zero health or below the damage event is cancelled, and both duellists have their potion effects cleared, fire ticks zeroed, health set back to the recorded starting value and are teleported to their recorded starting position.
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/kotlin/com/dansplugins/factionsystem/listener/EntityDamageListener.kt
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    lines: 56-101
    claim: The winner is given a head belonging to the loser, dropped on the ground if their inventory is full, nearby players are told who won, and the duel row is then deleted asynchronously.
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/kotlin/com/dansplugins/factionsystem/listener/EntityDamageListener.kt
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    lines: 106-118
    claim: The trophy is a PLAYER_HEAD whose owning player is the loser, named after them and given the lore "Lost in a duel against" the winner.
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/kotlin/com/dansplugins/factionsystem/duel/MfDuelService.kt
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    lines: 25-35
    claim: The duel service loads every stored duel and duel invite into memory in its constructor.
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/kotlin/com/dansplugins/factionsystem/MedievalFactions.kt
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    lines: 406-421
    claim: At startup the plugin removes any boss bar keyed duel_ whose duel no longer exists.
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/kotlin/com/dansplugins/factionsystem/MedievalFactions.kt
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    lines: 423-461
    claim: A repeating task drives each duel's boss bar from the time remaining and, once the end time passes, performs the same restoration and announces a tie.
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/resources/config.yml
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    lines: 111-113
    claim: Duels default to a duration of PT2M and a notification distance of 64.
---

A duel is a fight two players agree to, which nobody dies in. It sits inside
[[medieval-factions]] without touching the faction model at all: no
[[faction]] id appears anywhere on the record, and challenger and challenged are
plain player ids.

## The record is a snapshot

`MfDuel` stores both participants' **health and position as they were when the
duel began**, taken at the moment the invite is accepted, along with an end
time. Positions use [[spatial-value-types|MfPosition]], so yaw and pitch are
captured too; the duellists are put back facing the way they were.

## Death is replaced, not survived

The interesting mechanic is in `EntityDamageListener`. When a participant would
drop to zero health or below, the damage event is **cancelled** — the losing
blow never lands. Both players are then cleaned up and reset: potion effects
cleared, fire extinguished, health restored, teleported back. The winner is
restored too, so a duel costs neither side anything material.

What changes hands is a trophy: the winner is given the loser's head — a
`PLAYER_HEAD` carrying the loser as its owning player, named after them, with
the lore *"Lost in a duel against"* the winner — dropped at their feet if their
inventory is full. The duel row is then deleted.

## Ending on time

A duel also ends when its clock runs out. A repeating task drives a boss bar per
duel from the remaining time against the configured `duels.duration` (default
`PT2M`, parsed as an ISO-8601 duration), and on expiry runs the identical
restoration and announces a **tie** to players within `duels.notificationDistance`
blocks. Both outcomes share the same ending; only the message and the head
differ.

## Why it is persisted

Duels go through the [[service-layer]] to a repository and carry a `version` for
[[optimistic-locking]], and the service loads them all at startup. A duel
therefore outlives a restart mid-fight — and because the boss bar does not, the
plugin sweeps boss bars named `duel_*` whose duel no longer exists during
startup.

## Related

Like [[locked-block]], a duel is player-owned state living inside a
faction-shaped plugin. Its restoration path is also why an in-flight teleport is
cancelled on damage, handled in the same listener.
