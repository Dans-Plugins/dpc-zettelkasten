---
id: medieval-factions
title: Medieval Factions
type: concept
tags: [medieval-factions, plugin, flagship]
summary: The flagship plugin — a Kotlin Spigot plugin simulating sovereign nations, and the reference implementation every DPC convention points at.
created: 2026-08-07
updated: 2026-08-07
sources:
  - repo: Dans-Plugins/Medieval-Factions
    path: README.md
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    claim: Medieval Factions lets players create nations, claim territory, engage in warfare or politics, write laws and hold dueling tournaments, and its fifth major version was led by alyphen, the creator of RPKit.
  - repo: Dans-Plugins/dpc-conventions
    path: README.md
    ref: 9dc9aa37e9ed58722d86a914c563b5ceeaa07bec
    claim: Medieval Factions is named as the flagship plugin and the source of truth for all DPC conventions.
---

Medieval Factions is a Spigot plugin written in Kotlin that lets players
organise into feudal nations. It is the largest repository in the organization
and the most heavily documented, and [[dpc-conventions]] names it as the
reference implementation the other plugins are measured against.

## What it simulates

Players form a [[faction]], gain [[player-power]] by playing, and spend that
power's collective total on territory via the [[demesne-limit]]. Around that core
sit diplomacy ([[faction-relationship]], [[vassalage]]), internal governance
([[faction-role]], [[faction-permission]], [[faction-flag]]), and a set of
props for roleplay ([[law]], [[gate]], [[locked-block]], duels).

The design bet running through all of it: give players the mechanics of
sovereignty and let the politics be emergent. See [[law]] for the clearest
statement of that principle — the plugin stores a faction's laws and refuses to
enforce them.

## Version 5 was a rewrite

Version 4 was Java with flat-file JSON storage. Version 5 is Kotlin over a real
database, and its development was led by [alyphen](https://github.com/alyphen),
creator of RPKit. The architecture described in [[moc-plugin-architecture]] —
services over repositories over [[jooq-persistence]], immutable data classes,
[[optimistic-locking]] — arrived with that rewrite.

The seam between the two generations is still visible: [[legacy-data-migration]]
exists to carry version 4 servers across, and [[fiefs]] still builds against a
version 4 jar.

## Integration surface

Other software attaches at four points: [[faction-events]] (react),
[[service-layer]] (read and write), [[notification]] and [[map-integration]]
(supply an implementation), and [[dpc-api-faction-sync]] (push data out).

## Related

Its documentation lives beside the code per [[two-tier-documentation]]:
`USER_GUIDE.md`, `COMMANDS.md`, `CONFIG.md`, `FACTION_FLAGS.md`, and
`DATABASE_QUERYING.md`.
