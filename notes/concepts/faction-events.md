---
id: faction-events
title: Faction Events
type: concept
tags: [medieval-factions, architecture, extensibility]
summary: The plugin fires cancellable Bukkit events for every meaningful faction change, and derives which to fire by diffing the record it is about to save.
created: 2026-08-07
updated: 2026-08-07
sources:
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/kotlin/com/dansplugins/factionsystem/event/faction/FactionCreateEvent.kt
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    lines: 9-14
    claim: FactionCreateEvent extends Bukkit's Event and implements both FactionEvent and Cancellable, and exposes the faction as a mutable var so a listener can substitute it.
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/kotlin/com/dansplugins/factionsystem/faction/MfFactionService.kt
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    lines: 70-92
    claim: The save method compares the incoming faction against the previously stored one and fires a create, rename or description-change event accordingly, throwing EventCancelledException if a listener cancels.
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/kotlin/com/dansplugins/factionsystem/command/faction/kick/MfFactionKickCommand.kt
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    lines: 98
    claim: FactionKickEvent is constructed in the kick command with its isAsync argument hardcoded to true, unlike the other eleven event constructions which pass !server.isPrimaryThread.
---

[[medieval-factions]] fires Bukkit events for faction lifecycle changes:
`FactionCreateEvent`, `FactionRenameEvent`, `FactionDescriptionChangeEvent`,
`FactionPrefixChangeEvent`, `FactionJoinEvent`, `FactionLeaveEvent`,
`FactionKickEvent`, `FactionDisbandEvent`, `FactionClaimEvent`, and
`FactionUnclaimEvent`.

All implement the marker interface `FactionEvent`, which guarantees a
`factionId` — so a listener can handle the whole family generically.

## Mostly derived by diffing, not by call site

The notable design choice is where events come from. `MfFactionService.save()`
takes a complete [[faction]] record, loads the previously stored one, and
compares them field by field: a null previous state means create; a changed name
means rename; a changed description means a description change.

Callers therefore mostly do not choose which event to fire — they just save a
modified copy. Because the domain records are immutable data classes edited with
`copy()`, "what changed" is a comparison the service can make reliably, and no
call site can forget to announce its change.

The cost is that a single save can fire several events, and their ordering is
whatever order the diff checks run in.

The exceptions are worth knowing: claim and unclaim are fired by
`MfClaimService`, and `FactionKickEvent` is fired directly by the kick
*command* — the only event in the plugin raised outside a service.

## Cancellable, and mutable

Events are `Cancellable`. A cancelling listener causes the service to throw
`EventCancelledException`, which the `Result4k` wrapper converts into a
`ServiceFailure` — the caller sees a failed result, not an exception. See
[[service-layer]].

`FactionCreateEvent` goes further: `faction` is a `var`, and the service saves
`event.faction` rather than the original. A listener can therefore *rewrite* the
faction on its way to storage — enforcing a naming policy, say — not merely veto
it.

## Async correctness, with one gap

Eleven of the twelve event constructions in the plugin pass
`!plugin.server.isPrimaryThread`, so Bukkit is told truthfully whether the event
is being fired asynchronously. Getting this wrong is a common source of
hard-to-trace plugin bugs; see [[main-thread-safety]].

`FactionKickEvent` is the twelfth. It passes a hardcoded `true`, asserting the
event is always async — and it is constructed inside a command, which normally
runs on the main thread. Nothing in the repository explains the choice; treat it
as a discrepancy to check rather than a pattern to copy.

Note also that relationship changes have their own events —
`RelationshipCreateEvent` and `RelationshipDeleteEvent` in
`event/relationship/` — outside the faction family described here.

## Related

For an [[expansion-plugin]] these events are the supported extension point.
Reading state is done through the [[service-layer]]; reacting to change is done
here.
