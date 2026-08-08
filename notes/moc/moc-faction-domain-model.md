---
id: moc-faction-domain-model
title: Faction Domain Model
type: moc
tags: [moc, medieval-factions, domain-model]
summary: Guided path through the nouns of the simulation — factions, power, land, and the relationships between them.
created: 2026-08-07
updated: 2026-08-07
---

The domain model is small enough to hold in your head, and almost all of it
hangs off one number. This map walks it in dependency order rather than
alphabetically.

## Start with power

Every player carries [[player-power]], a scalar that rises with time online and
falls on death. A [[faction]]'s [[faction-power]] is the sum of its members'
power, plus a conditional contribution from its vassals. That single number is
the currency of the whole simulation: it decides how much land a faction may
hold, via the [[demesne-limit]].

This is the design's central lever. Territory is not bought, it is *staffed* —
land follows people, and a faction that empties out loses its grip on the map.

## Then land

Land is claimed one Minecraft chunk at a time; see [[claimed-chunk]]. Whether a
non-member may build inside a claim depends on [[faction-flag]] settings and, for
members, on the [[faction-permission]] granted by their [[faction-role]].

## Then politics

Factions relate to each other through [[faction-relationship]] — allied, at war,
or bound in the liege/vassal hierarchy described in [[vassalage]]. Relationship
changes are two-sided, which is what [[approval-request]] exists to mediate.

## Then the trimmings

Several features are self-contained and can be read in any order once the above
is clear: [[law]] (a faction's written rules), [[gate]] (redstone-triggered
walls), and [[locked-block]] (per-player container locks that operate
independently of faction land).

## What ties it together

Nothing in this map is stored as an object graph — every one of these concepts
is persisted through its own repository, and read back through the
[[service-layer]]. If you are tracing a value from a command to the database,
[[moc-plugin-architecture]] is the map you want next.
