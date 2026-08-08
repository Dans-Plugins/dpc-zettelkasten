---
id: repository-pattern
title: Repository Pattern
type: concept
tags: [medieval-factions, architecture, persistence]
summary: Each domain record gets a storage-agnostic interface plus a jOOQ implementation, so services never name a database.
created: 2026-08-07
updated: 2026-08-07
sources:
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/kotlin/com/dansplugins/factionsystem/faction/MfFactionRepository.kt
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    lines: 5-13
    claim: The faction repository interface declares only getFaction by id, name and player id, getFactions, upsert and delete, with no SQL or storage concepts.
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/kotlin/com/dansplugins/factionsystem/faction/JooqMfFactionRepository.kt
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    lines: 27
    claim: The jOOQ implementation of the faction repository is a separate class named after its technology.
---

Every persisted record type in [[medieval-factions]] has two files: an interface
named `Mf<Thing>Repository` and an implementation named `JooqMf<Thing>Repository`.
The naming convention is the whole convention — the technology appears in the
implementation's name and nowhere else.

## What the interface says

`MfFactionRepository` declares six methods: three overloads of `getFaction`, a
`getFactions`, an `upsert`, and a `delete`. There is no `save`/`update` split,
no query language, no transaction handle, and no `Connection`. A caller cannot
tell from the interface whether the data lives in a database, a flat file, or
memory.

Note `upsert` rather than separate insert and update. Because domain records are
immutable data classes carrying their own [[value-class-identifier]], the caller
always has a complete record in hand and never needs to express "change these
three columns".

## Why bother

Three payoffs, in descending order of how much they actually matter here:

1. **Testability.** A fake repository is a `MutableMap` and twenty lines.
2. **Dialect independence.** The interface is what lets H2, MySQL, and
   PostgreSQL all work — see [[jooq-persistence]].
3. **Replaceability.** In principle the storage could be swapped. In practice
   nobody has, and this is the weakest of the three arguments.

## The mapping happens in the implementation

The jOOQ classes are where domain records meet columns, including the awkward
parts: [[faction-role]] lists are serialized to a JSON column with Gson, and
[[value-class-identifier]] values are unwrapped to strings. Keeping that in the
implementation is what allows the domain model to be shaped for the simulation
rather than for the schema.

## Related

The repository is also where [[optimistic-locking]] lives, because the version
check has to be part of the same statement as the write.
