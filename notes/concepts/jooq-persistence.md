---
id: jooq-persistence
title: jOOQ Persistence
type: concept
tags: [medieval-factions, architecture, persistence]
summary: Storage is jOOQ over a Hikari pool, with Flyway migrations and a configurable SQL dialect — H2 by default, MySQL or PostgreSQL optionally.
created: 2026-08-07
updated: 2026-08-07
sources:
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/kotlin/com/dansplugins/factionsystem/MedievalFactions.kt
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    lines: 150-184
    claim: The plugin builds a HikariDataSource from config, runs Flyway migrations from a classpath location into an mf_schema_history table with baselineOnMigrate enabled, then creates a jOOQ DSL context using a dialect read from config.
  - repo: Dans-Plugins/Medieval-Factions
    path: DATABASE_QUERYING.md
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    claim: The default database is embedded H2 with AUTO_SERVER=true, MODE=MYSQL and DATABASE_TO_UPPER=false, which allows a second process to query the file while the server runs.
---

[[medieval-factions]] persists through jOOQ against a HikariCP connection pool,
with the schema managed by Flyway. All three are configured once in `onEnable`
and never referenced again outside the `Jooq*Repository` classes.

## The default is a file

Out of the box the database is embedded H2 at `./medieval_factions_db`, with
three settings that matter:

- `AUTO_SERVER=true` — H2 starts a TCP server beside the embedded database, so
  an operator can query the live data with a SQL client while the Minecraft
  server is running. This is what makes `DATABASE_QUERYING.md` possible.
- `MODE=MYSQL` — H2 emulates MySQL, so SQL written for one mostly works on both.
- `DATABASE_TO_UPPER=false` — identifiers stay lowercase and case-sensitive.

A server that outgrows the file changes `database.url` and `database.dialect`
and nothing else; the `SQLDialect` is read straight from config and handed to
jOOQ, which is what makes MySQL and PostgreSQL viable without touching code.

## Flyway owns the schema

Migrations live on the classpath under
`com/dansplugins/factionsystem/db/migration`, with history in a dedicated
`mf_schema_history` table. Two configuration choices are worth noting:
`baselineOnMigrate(true)` with `baselineVersion("0")` lets Flyway adopt a
database it did not create, and `validateOnMigrate(false)` tolerates checksum
drift rather than refusing to start.

The migration runs with the plugin's own classloader temporarily installed as
the thread context classloader, and the original restored afterwards. That dance
is required because Flyway scans the classpath by reflection, and inside a
Bukkit server the thread context classloader is not the one holding the
plugin's resources.

## Related

The repositories built on this DSL are described in [[repository-pattern]], and
the version-column protocol they implement is [[optimistic-locking]].
