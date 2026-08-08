---
id: law
title: Law
type: concept
moc: moc-faction-domain-model
tags: [medieval-factions, domain-model, roleplay]
summary: Numbered lines of text a faction publishes to its members — enforced socially, not mechanically.
created: 2026-08-07
updated: 2026-08-07
sources:
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/kotlin/com/dansplugins/factionsystem/law/MfLaw.kt
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    lines: 6-22
    claim: A law is a record of id, version, factionId, text, and an optional number, and a new law is constructed from a faction and a string.
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/kotlin/com/dansplugins/factionsystem/law/MfLawService.kt
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    claim: The law service exposes only get, save, delete and move — no evaluation or enforcement of a law's text.
  - repo: Dans-Plugins/Medieval-Factions
    path: README.md
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    claim: The README describes the plugin as letting players write laws and generally attempt to recreate society, framing it as a set of mechanics rather than an enforcement system.
---

A law is a numbered line of text belonging to a [[faction]]. The plugin stores
it, orders it, and displays it — and does nothing else with it.

## Inert by construction

Nothing in the codebase reads a law's text and acts on it. `MfLawService` offers
get, save, delete, and move — there is no rule engine, no automatic punishment,
no parser. A law is a `String` with an ordinal.

Set beside [[faction-permission]], which *is* enforced, the pair marks a line:
permissions constrain what a client is *able* to do, while laws describe what
members *should* do. One is a security boundary; the other is a social one, and
only the first is the plugin's to police.

Whether that split was reasoned out or simply where the feature stopped is not
recorded anywhere. What is on the record is the README's framing of the plugin —
players "write laws" and "attempt to recreate society somewhat" — which reads as
a description of props for a society rather than of a system that runs one.

## Numbering

The `number` field is nullable, and the convenience constructor that takes a
faction and a string leaves it null — a caller adding a law does not choose where
it lands. Ordering is settled on persistence, and `MfLawService.move(law, number)`
is the only way to renumber one afterwards, delegating to the repository so the
whole faction's list is resequenced in one place rather than by each caller.

`MfLawService` is also the leanest service in the plugin: it takes a repository
and nothing else, no plugin handle. Everything it does is a repository call
wrapped in a `Result4k` — the minimal shape described in [[service-layer]].

## Related

Law shares the standard record shape — an id, a `version` for
[[optimistic-locking]], and a `factionId` foreign key — with every other
per-faction record. If you are adding a comparable feature, this is the smallest
complete example to copy.
