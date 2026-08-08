---
id: legacy-data-migration
title: Legacy Data Migration
type: concept
tags: [medieval-factions, architecture, persistence]
summary: Version 4's flat JSON files are backed up and read once into the database, behind a deliberate server shutdown that forces the operator to configure storage first.
created: 2026-08-07
updated: 2026-08-07
sources:
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/kotlin/com/dansplugins/factionsystem/MedievalFactions.kt
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    lines: 126-141
    claim: When the stored config version starts with v4, the plugin takes a backup, writes migrateMf4 into the config, logs instructions, and shuts the server down instead of migrating immediately.
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/kotlin/com/dansplugins/factionsystem/legacy/MfLegacyDataMigrator.kt
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    lines: 37-47
    claim: A dedicated migrator class exposes backup and migrate entry points and has private per-record methods for config, players, factions, claimed chunks and locked blocks.
---

Medieval Factions 4 stored its data in flat JSON files. Version 5 stores it in a
database (see [[jooq-persistence]]). The `legacy` package exists to carry a
version 4 server across that gap exactly once.

## The deliberate shutdown

The interesting decision is what happens on first boot after the upgrade. On
detecting a `v4.` version string in the config, the plugin does *not* migrate.
It:

1. Backs up the old data files.
2. Writes fresh defaults and sets `migrateMf4: true`.
3. Logs that the server is shutting down for migration, and that a database
   should be configured now if one is wanted.
4. Calls `server.shutdown()`.

Migration then runs on the *next* start. This costs the operator a restart and
buys something worth more: a chance to point `database.url` at MySQL before any
data is written. Migrating first and asking later would strand every server on
the default embedded H2 file, and there is no second migration to move them.

The forced stop is also honest about risk. Migration is irreversible; a server
that hits it unaware would otherwise discover the change mid-session with
players connected.

## Legacy records are separate types

`MfLegacyFaction`, `MfLegacyClaimedChunk`, `MfLegacyGate`,
`MfLegacyLockedBlock`, `MfLegacyPowerRecord`, `MfLegacyActivityRecord`,
`MfLegacyLocation` mirror the version 4 JSON shapes rather than reusing the
current domain classes.

Keeping them separate is what lets the current model evolve freely — [[faction]]
can gain and lose fields without anyone having to reason about whether a change
breaks the reading of a five-year-old JSON file. The legacy classes are frozen by
definition, because the format they describe will never change again.

## Related

The migrator writes through the same repositories as everything else, so
migrated data goes through the same validation and gets the same
[[optimistic-locking]] version columns as data created today.
