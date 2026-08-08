---
id: optimistic-locking
title: Optimistic Locking
type: concept
moc: moc-plugin-architecture
tags: [medieval-factions, architecture, persistence, concurrency]
summary: Every mutable record carries a version column; a write that does not match the version it read is rejected rather than silently overwriting.
created: 2026-08-07
updated: 2026-08-07
sources:
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/kotlin/com/dansplugins/factionsystem/faction/JooqMfFactionRepository.kt
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    lines: 170-174
    claim: The update sets version to version plus one, constrains the WHERE clause on both the id and the previously read version, and throws OptimisticLockingFailureException when no rows were affected.
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/kotlin/com/dansplugins/factionsystem/faction/MfFactionService.kt
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    lines: 198-202
    claim: The service maps an OptimisticLockingFailureException to the CONFLICT service failure type.
---

Nearly every persisted record in [[medieval-factions]] — [[faction]],
[[player-power|player]], [[law]], [[gate]], [[locked-block]] — carries an
integer `version`. It is not domain data; it is a concurrency protocol.

## The protocol

```sql
UPDATE mf_faction
   SET ..., version = :version + 1
 WHERE id = :id
   AND version = :version
```

If the row's version has moved since it was read, the `WHERE` matches nothing,
the affected-row count is zero, and the repository throws
`OptimisticLockingFailureException`. The [[service-layer]] maps that to a
`CONFLICT` failure, which a command turns into "someone else changed this, try
again".

## Why optimistic rather than locked

Two properties of the plugin make this the right trade:

- **Conflicts are rare.** Two players editing the same [[faction]] in the same
  instant is unusual. Taking a row lock on every write would pay a cost on every
  operation to protect against something that almost never happens.
- **Records are immutable.** Domain objects are Kotlin `data class` values with
  `copy()`. A caller always holds a complete snapshot including the version it
  read, so the version travels with the object for free — there is nothing extra
  to thread through.

Pessimistic locking would also mean holding a database transaction open across
game logic, and game logic on a Bukkit server runs on the main thread. A held
lock there is a stalled server.

## Failing loudly beats a lost update

The alternative to rejecting the write is accepting it, which silently discards
whatever the other writer did. For a [[faction]] record — carrying the roster,
the roles, and the flags — a lost update means a player's changes vanish with no
error anywhere. A `CONFLICT` a player can retry is a much better failure.

## Related

Because roles and flags live inline on the faction record, editing either bumps
the same version as renaming the faction. Fine-grained concurrent edits within
one faction are therefore not possible by design.
