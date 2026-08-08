---
id: faction-relationship
title: Faction Relationship
type: concept
moc: moc-faction-domain-model
tags: [medieval-factions, domain-model, diplomacy]
summary: Diplomacy is stored as directed edges between factions, typed as ally, at war, vassal, or liege.
created: 2026-08-07
updated: 2026-08-07
sources:
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/kotlin/com/dansplugins/factionsystem/relationship/MfFactionRelationshipType.kt
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    lines: 3-8
    claim: The relationship type enum has exactly four values, ALLY, AT_WAR, VASSAL, and LIEGE.
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/kotlin/com/dansplugins/factionsystem/relationship/MfFactionRelationship.kt
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    claim: A relationship is a record of an id, a factionId, a targetId and a type — a directed edge from one faction to another.
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/kotlin/com/dansplugins/factionsystem/relationship/MfFactionRelationshipService.kt
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    lines: 101-121
    claim: Both getLiege and getVassals confirm the reverse edge before accepting a result — getLiege requires a matching VASSAL edge back, and getVassals filters to targets that carry a matching LIEGE edge back.
---

Diplomacy is not a field on the [[faction]] record. It is a separate table of
directed edges, each carrying one of four types: `ALLY`, `AT_WAR`, `VASSAL`, or
`LIEGE`.

## Directed, not symmetric

Each row records a relationship *from* one faction *to* another. Two of the four
types are inverses — A's `VASSAL` edge to B pairs with B's `LIEGE` edge to A —
so a hierarchy is represented by two rows, not one.

The service enforces that pairing rather than assuming it. `getLiege` reads the
faction's own `LIEGE` edge, then checks the reverse direction for a matching
`VASSAL` edge before accepting the answer; `getVassals` filters symmetrically. A
half-written hierarchy — one row present, its counterpart missing — resolves to
no relationship at all rather than to a lopsided one.

Storing both directions also means "who are my allies?" and "who considers me an
ally?" are the same cheap query.

## Why relationships get an approval step

Because a relationship change binds two independent groups of players, it cannot
be a unilateral command. [[approval-request]] exists for exactly the three
relationship transitions that need consent — war, alliance, and vassalisation.

## Effect on the rest of the model

Relationships are read by more of the codebase than any other domain concept:

- [[faction-power]] walks a faction's vassals to compute their contribution.
- [[faction-flag]] settings such as `alliesCanInteractWithLand` and
  `vassalageTreeCanInteractWithLand` turn relationship type into land access.
- Combat rules consult war status before allowing PvP between factions.

## Related

[[vassalage]] covers the liege/vassal pair specifically, since it carries
mechanical weight that alliance does not.
