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
---

[[medieval-factions]] fires Bukkit events for faction lifecycle changes:
`FactionCreateEvent`, `FactionRenameEvent`, `FactionDescriptionChangeEvent`,
`FactionPrefixChangeEvent`, `FactionJoinEvent`, `FactionLeaveEvent`,
`FactionKickEvent`, `FactionDisbandEvent`, `FactionClaimEvent`, and
`FactionUnclaimEvent`.

All implement the marker interface `FactionEvent`, which guarantees a
`factionId` — so a listener can handle the whole family generically.

## Derived by diffing, not by call site

The notable design choice is where events come from. `MfFactionService.save()`
takes a complete [[faction]] record, loads the previously stored one, and
compares them field by field: a null previous state means create; a changed name
means rename; a changed description means a description change.

Callers therefore do not choose which event to fire — they just save a modified
copy. Because the domain records are immutable data classes edited with
`copy()`, "what changed" is a comparison the service can make reliably, and no
call site can forget to announce its change.

The cost is that a single save can fire several events, and their ordering is
whatever order the diff checks run in.

## Cancellable, and mutable

Events are `Cancellable`. A cancelling listener causes the service to throw
`EventCancelledException`, which the `Result4k` wrapper converts into a
`ServiceFailure` — the caller sees a failed result, not an exception. See
[[service-layer]].

`FactionCreateEvent` goes further: `faction` is a `var`, and the service saves
`event.faction` rather than the original. A listener can therefore *rewrite* the
faction on its way to storage — enforcing a naming policy, say — not merely veto
it.

## Async correctness

Every event is constructed with `!plugin.server.isPrimaryThread`, so Bukkit is
told truthfully whether it is being fired asynchronously. Getting this wrong is
a common source of hard-to-trace plugin bugs; see [[main-thread-safety]].

## Related

For an [[expansion-plugin]] these events are the supported extension point.
Reading state is done through the [[service-layer]]; reacting to change is done
here.
