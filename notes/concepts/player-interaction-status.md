---
id: player-interaction-status
title: Player Interaction Status
type: concept
moc: moc-plugin-architecture
tags: [medieval-factions, architecture, interaction]
summary: A per-player mode that makes the next block a player clicks mean something other than "use this block".
created: 2026-08-14
updated: 2026-08-14
sources:
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/kotlin/com/dansplugins/factionsystem/interaction/MfInteractionStatus.kt
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    lines: 3-12
    claim: Interaction status is an enum of eight values, five belonging to block locking and three to gate creation.
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/kotlin/com/dansplugins/factionsystem/listener/PlayerInteractListener.kt
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    lines: 67-102
    claim: The interact listener branches on the player's interaction status, cancels the event for every non-null status, and falls through to the normal protection checks only when the status is null.
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/kotlin/com/dansplugins/factionsystem/interaction/MfInteractionService.kt
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    lines: 15-35
    claim: The service writes the status through its repository first and updates the in-memory ConcurrentHashMap only when that write succeeds.
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/kotlin/com/dansplugins/factionsystem/listener/PlayerQuitListener.kt
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    lines: 25-26
    claim: Quitting unloads the player's interaction status from the cache rather than clearing it.
---

Some commands need a *block* as an argument, and a block cannot be typed. The
plugin solves this by putting the player into a mode: the command announces what
the next click will mean, and the click supplies the argument.

## Eight modes, two features

`MfInteractionStatus` has eight values, and every one of them belongs to a
feature already described elsewhere in this collection. `LOCKING`, `UNLOCKING`,
`CHECKING_ACCESS`, `ADDING_ACCESSOR` and `REMOVING_ACCESSOR` serve
[[locked-block]]; `SELECTING_GATE_POSITION_1`, `SELECTING_GATE_POSITION_2` and
`SELECTING_GATE_TRIGGER` serve [[gate]]. Neither of those notes names the
mechanism, because the mechanism lives in neither package — it is the seam
between a command and the click that completes it.

## The click is consumed, not shared

`PlayerInteractListener` opens by branching on the status. Each non-null branch
runs its handler and sets `event.isCancelled = true`, so a player in a mode does
not also open the chest they clicked. Only the `null` branch falls through to
`applyProtections`, the ordinary claim and lock enforcement.

Gate selection is a small state machine within this: selecting position 1
advances the player to `SELECTING_GATE_POSITION_2`, and the trigger click clears
the status back to `null`.

## Persisted, not just cached

`MfInteractionService` keeps statuses in a `ConcurrentHashMap`, but every change
goes through a repository first and reaches the cache only if that write
succeeded — the same write-through discipline as the rest of the
[[service-layer]], including mapping an [[optimistic-locking]] failure to
`CONFLICT`.

The consequence, which follows from the code rather than from anything stated in
it: quitting calls `unloadInteractionStatus`, which drops the cache entry
without deleting the row, and logging in reloads it. A player who types `/lock`
and disconnects is therefore still in `LOCKING` mode when they return. **No
comment, commit message or document in the repository explains why the status is
durable rather than session-scoped.**

## Related

The modes are cancellable from the command side too — `/lock cancel` refuses
unless the player is actually in `LOCKING`, then sets the status to `null`.
Compare [[main-thread-safety]] for why the listener reads a cached value instead
of querying storage on every click.
