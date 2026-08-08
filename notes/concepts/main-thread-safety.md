---
id: main-thread-safety
title: Main Thread Safety
type: concept
tags: [medieval-factions, architecture, concurrency]
summary: Bukkit state may only be read on the server's main thread, so anything doing I/O snapshots first and sends afterwards.
created: 2026-08-07
updated: 2026-08-07
sources:
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/kotlin/com/dansplugins/factionsystem/dpc/MfDpcApiService.kt
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    lines: 13-21
    claim: The DPC API service documents that Bukkit plugin data structures are not thread-safe, that collectSnapshot must be called from the main server thread, and that the returned snapshot is an immutable view safe to serialize off it.
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/kotlin/com/dansplugins/factionsystem/MedievalFactions.kt
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    lines: 498-509
    claim: The faction sync task is scheduled with runTaskTimer on the main thread so snapshot collection can touch Bukkit state, while the HTTP send is dispatched asynchronously.
---

A Bukkit server runs game logic on one thread. Plugin data structures reachable
from that logic are not thread-safe, and reading them from a background thread
produces corruption that surfaces far from its cause.

## Snapshot on, send off

[[dpc-api-faction-sync]] is the clearest worked example in the codebase, and its
class comment states the rule outright. The work is split in two:

1. **`collectSnapshot()`** — runs on the main thread. It walks the faction
   service and the members lists, and returns an immutable `SyncSnapshot`.
2. **`dispatchAsync()`** — safe from any thread. It serializes the snapshot and
   hands it to the JDK `HttpClient`, which does the I/O on its own pool.

The scheduled task is therefore registered with `runTaskTimer` — the *main
thread* variant — even though its purpose is a network call. This looks backwards
until you see the split: the expensive part is already asynchronous inside
`HttpClient`, and scheduling the task asynchronously would only move the *unsafe*
part off the main thread.

## The general rule

The pattern generalises to anything the plugin does off-thread: **collect an
immutable snapshot on the main thread, then act on the snapshot elsewhere.**
Never hold a reference to live Bukkit or service state across a thread boundary.

## Where it also shows up

- [[faction-events]] pass `!server.isPrimaryThread` to the Bukkit `Event`
  constructor, so listeners are told truthfully which thread they are on.
- [[gate]] checks `isChunkLoaded` before reading a block, avoiding a synchronous
  chunk load on the main thread.
- The [[service-layer]] caches use `ConcurrentHashMap` and
  `CopyOnWriteArrayList`, because reads can legitimately arrive from async
  listeners even when writes do not.

## Related

Getting this wrong is not usually a crash — it is a rare, unreproducible
inconsistency. That is why the constraint is written into a class comment rather
than left implicit.
