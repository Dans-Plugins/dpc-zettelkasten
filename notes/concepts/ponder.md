---
id: ponder
title: Ponder
type: concept
tags: [ponder, library, ecosystem]
summary: The community's shared Java/Kotlin library — a multi-module Gradle build providing command abstraction, caching, and Bukkit helpers.
created: 2026-08-07
updated: 2026-08-07
sources:
  - repo: Dans-Plugins/Ponder
    path: settings.gradle
    ref: ff5276ae2fe0e2f5ac5de9c7ba45dd6d0a04d61f
    claim: Ponder is a multi-project Gradle build with three modules, ponder-bukkit, ponder-cache and ponder-commands.
  - repo: Dans-Plugins/Ponder
    path: ponder-cache/src/main/java/preponderous/ponder/cache/Cache.java
    ref: ff5276ae2fe0e2f5ac5de9c7ba45dd6d0a04d61f
    claim: The cache module exposes a generic Cache interface with get, set, containsKey, remove, removeMatching, keys and clear.
  - repo: Dans-Plugins/Ponder
    path: README.md
    ref: ff5276ae2fe0e2f5ac5de9c7ba45dd6d0a04d61f
    claim: Ponder modules are published to repo.dansplugins.com under the com.dansplugins group and are also available via GitHub Packages.
---

Ponder is the shared library DPC plugins build on. It is small — three modules,
each a handful of files — and published as Maven artifacts rather than shaded
into each plugin.

## The three modules

| Module | Contents |
|---|---|
| `ponder-bukkit` | Bukkit/Spigot helpers — distance calculations, plugin lookups |
| `ponder-cache` | A generic `Cache<K, V>` interface with a default implementation and a `CacheManager` |
| `ponder-commands` | A `Command` abstraction, a `CommandService` registry, and typed `CommandResult` values |

`ponder-commands` is the interesting one architecturally. `CommandService` is a
two-method interface — `addCommand(name, command)` and `getCommand(name)` — and
results are typed values such as `IncorrectUsageFailure` rather than booleans.
That is the same "failures are values" instinct visible in the flagship's
[[service-layer]].

## Published, not vendored

Modules are consumed from `repo.dansplugins.com` (the community's Nexus) and
from GitHub Packages, under the `com.dansplugins` group. Publishing rather than
copying means a fix reaches every consumer on the next dependency bump.

The caveat is version skew across the fleet. [[fiefs]] still builds against a
vendored `Ponder-v0.15-alpha-2.jar` predating the current module layout, so
"which Ponder?" is a real question when reading an older plugin.

## Related

Ponder lives in the Dans-Plugins organization but is named for
[Preponderous](https://github.com/Preponderous-Software), and its package root
is still `preponderous.ponder` while its Maven group is `com.dansplugins`. No
source in the repository explains the mismatch, so treat it as a naming artefact
rather than a boundary that means something.
