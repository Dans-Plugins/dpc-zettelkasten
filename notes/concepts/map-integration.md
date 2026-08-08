---
id: map-integration
title: Map Integration
type: concept
tags: [medieval-factions, integration, ecosystem]
summary: Claimed territory is drawn on web maps through a one-method interface with a Dynmap implementation, wired only when the optional plugin is present.
created: 2026-08-07
updated: 2026-08-07
sources:
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/kotlin/com/dansplugins/factionsystem/map/MapService.kt
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    lines: 8-15
    claim: The map service interface declares a single method, scheduleUpdateClaims, taking a faction.
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/kotlin/com/dansplugins/factionsystem/MedievalFactions.kt
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    lines: 190
    claim: The map service is constructed only when the dynmap plugin is installed and dynmap.enableDynmapIntegration is true in the config.
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/kotlin/com/dansplugins/factionsystem/map/dynmap/DynmapService.kt
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    lines: 41-44
    claim: Scheduling an update cancels any pending tasks for that faction and schedules a fresh one 100 ticks later, so rapid successive changes collapse into a single redraw.
---

Faction territory is rendered on a live web map. The flagship's side of that is
one interface with one method: `scheduleUpdateClaims(faction)`.

## Debounced, not immediate

The method name is the design. A [[claimed-chunk]] change does not redraw the
map — it *schedules* a redraw. The Dynmap implementation is three lines:

```kotlin
taskScheduler.cancelTasks(faction.id)
taskScheduler.scheduleTask(faction.id, { updateClaims(faction) }, 100L)
```

Cancel whatever is pending for this faction, then schedule a fresh redraw 100
ticks (five seconds) out. That is a debounce: claiming land is usually a burst —
the fill and circle claim commands place dozens of chunks at once — and each
chunk would otherwise mean a full marker rebuild. Only the last change in a
burst survives to actually run.

Behind the interface, `map/builders` turns a faction's claims into polygon paths
and its details into an info popup, and `map/aliases` is three typealiases
giving that geometry names (`Point`, `Path`, `LineSegment`). `map/scheduling`
holds the `TaskScheduler` — which, incidentally, still declares the package
`com.dansplugins.factionsystem.dynmap` despite living under `map/scheduling`.

## Doubly optional

The service is created only if *both* the `dynmap` plugin is installed *and*
`dynmap.enableDynmapIntegration` is true. Both conditions are checked once at
startup, and the result is the nullable `mapService` on the [[service-layer]]
registry — so the rest of the codebase deals with a null check rather than a
runtime capability probe.

An operator can therefore run Dynmap for the base map while keeping faction
overlays off, without uninstalling anything.

## Colour comes from the faction

The colour a faction is drawn in is its `color` [[faction-flag]] — a `#RRGGBB`
string that defaults to a randomly generated pleasant colour. Map appearance is
thus player-controlled state, not a server setting.

## Related

A separate repository, `Bluemap_MedievalFactions`, provides the equivalent for
BlueMap, and [[dpc-mc-server]] ships both map plugins.
