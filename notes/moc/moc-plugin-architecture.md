---
id: moc-plugin-architecture
title: Plugin Architecture
type: moc
tags: [moc, medieval-factions, architecture]
summary: How the flagship is layered — services over repositories over jOOQ — and the cross-cutting concerns that shape every feature.
created: 2026-08-07
updated: 2026-08-07
---

[[medieval-factions]] has a consistent internal shape, and once you have seen
one feature you have seen them all. This map describes that shape.

## The three layers

1. **Commands** parse player input and delegate immediately.
2. **Services** own the in-memory state and the business rules —
   [[service-layer]].
3. **Repositories** are interfaces that hide storage — [[repository-pattern]] —
   implemented against [[jooq-persistence]].

A new feature is almost always: a data class, an ID value class
([[value-class-identifier]]), a repository interface, a jOOQ implementation, a
service, and a command.

## Cross-cutting concerns

- **[[optimistic-locking]]** — every mutable record carries a version; a stale
  write is rejected rather than silently overwriting.
- **[[main-thread-safety]]** — Bukkit state is not thread-safe, so anything
  doing I/O must snapshot on the main thread and act off it.
- **[[faction-events]]** — the plugin fires cancellable Bukkit events, which is
  the supported extension point for other plugins.
- **[[legacy-data-migration]]** — flat files from version 4 are read once and
  written into the database.

## Where to attach

If you are writing an [[expansion-plugin]], the seams that matter are
[[faction-events]] (react to things) and the [[service-layer]] (read and change
things). If you are integrating an external system, look at how [[notification]]
and [[map-integration]] define an interface and swap in an implementation at
startup — that is the pattern to copy.
