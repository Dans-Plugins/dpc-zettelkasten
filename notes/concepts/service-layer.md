---
id: service-layer
title: Service Layer
type: concept
tags: [medieval-factions, architecture]
summary: Services own in-memory state, enforce the rules, fire events, and return typed failures — commands and listeners talk only to them.
created: 2026-08-07
updated: 2026-08-07
sources:
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/kotlin/com/dansplugins/factionsystem/service/Services.kt
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    lines: 19-35
    claim: A single Services class holds fifteen services, one per domain area, and the map service is nullable because it depends on an optional plugin.
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/kotlin/com/dansplugins/factionsystem/failure/ServiceFailure.kt
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    lines: 3-19
    claim: A service failure carries a type, message and cause, and the failure type enum has nine values including NOT_FOUND, CONFLICT, RULES_VIOLATION and GENERAL.
---

Every domain area in [[medieval-factions]] gets a service. The service owns the
in-memory copy of that area's data, applies the rules, fires [[faction-events]],
and delegates persistence to a repository. Nothing else in the plugin should
touch a repository directly.

## One registry

`Services` is a plain class with fifteen constructor properties — player,
faction, law, relationship, claim, lock, interaction, notification, gate, chat,
duel, potion, teleport, map, and approval request. It is constructed once during
`onEnable` and hung off the plugin instance as `plugin.services`.

There is no dependency-injection framework. Wiring is a hundred lines of
`onEnable` constructing repositories and passing them into services, which for a
plugin of this size is easier to follow than a container would be.

`mapService` is the only nullable entry: it exists only when an optional
[[map-integration]] plugin is installed. Its type carries that fact, so callers
must handle absence rather than discovering it at runtime.

## Failures are values

Mutating methods return `Result4k<T, ServiceFailure>` rather than throwing.
`ServiceFailure` carries a `type`, a `message`, and the underlying `cause`, and
`ServiceFailureType` distinguishes nine cases — `NOT_FOUND`, `BAD_REQUEST`,
`BAD_RESPONSE`, `AUTHENTICATION_REQUIRED`, `AUTHORIZATION`, `RULES_VIOLATION`,
`DUPLICATE`, `CONFLICT`, and `GENERAL`.

Each service maps exceptions to types in a small private helper — an
[[optimistic-locking]] failure becomes `CONFLICT`, everything else becomes
`GENERAL`. A command can then branch on `CONFLICT` and tell the player to try
again, which is a very different message from an internal error.

## Read from memory, write through

`MfFactionService` is the fullest example: it loads every [[faction]] into a
`ConcurrentHashMap` at startup, serves reads from that map, and on write both
persists through the [[repository-pattern]] and updates the cache. After that
one bulk load, ordinary reads never reach the database — only writes do.

## Related

The variation between services is mostly how much caching they do.
`MfLawService` caches nothing and takes only a repository — the minimum a
service can be while still owning the failure mapping.
