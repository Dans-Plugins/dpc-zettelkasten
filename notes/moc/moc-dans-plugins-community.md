---
id: moc-dans-plugins-community
title: Dan's Plugins Community
type: moc
tags: [moc, dpc, index]
summary: The root map — an index of the six Maps of Content, and through them every concept note in the collection.
created: 2026-08-07
updated: 2026-08-08
sources:
  - repo: Dans-Plugins/dpc-conventions
    path: README.md
    ref: 9dc9aa37e9ed58722d86a914c563b5ceeaa07bec
    claim: DPC stands for Dans Plugins Community and treats Medieval Factions as its flagship reference implementation.
---

Dan's Plugins Community (DPC) is a collection of open-source Minecraft plugins
built around a single ambition: let players simulate societies.
[[medieval-factions]] is the flagship — sovereign nations, claimed land,
diplomacy, war — and most other repositories in the organization either extend
it, support it, or share its conventions.

**This is a map of maps.** It holds no claims of its own. Every concept note in
the collection lives under exactly one of the maps below, and each map is a
curated route through its cluster rather than an alphabetical dump.

---

## [[moc-medieval-factions|The flagship]]

The largest repository in the organization, and the reference implementation
every convention points back at. It is big enough to need two maps of its own:

### → [[moc-faction-domain-model]] — the nouns of the simulation

What the game is *about*. Almost all of it hangs off one number.

- **The currency of the whole game** — [[player-power]] · [[faction-power]] ·
  [[demesne-limit]]
- **The state** — [[faction]] · [[claimed-chunk]]
- **Politics** — [[faction-relationship]] · [[vassalage]] ·
  [[approval-request]]
- **Internal governance** — [[faction-role]] · [[faction-permission]] ·
  [[faction-flag]]
- **Props for roleplay** — [[law]] · [[gate]] · [[locked-block]]

*Start with [[demesne-limit]]. It is one inequality, and the rest of the
simulation is arranged around it.*

### → [[moc-plugin-architecture]] — how it is built

The shape every feature in the codebase takes.

- **The three layers** — [[service-layer]] · [[repository-pattern]] ·
  [[jooq-persistence]]
- **Cross-cutting concerns** — [[optimistic-locking]] ·
  [[value-class-identifier]] · [[main-thread-safety]]
- **Seams other software attaches to** — [[faction-events]] ·
  [[notification]] · [[map-integration]]
- **History still in the tree** — [[legacy-data-migration]]

*Start with [[service-layer]]. Once you have seen one feature you have seen
them all.*

---

## → [[moc-plugin-ecosystem]] — the other plugins

What surrounds the flagship: the shared library, the official expansions, and
the plugins it talks to at runtime.

- **The library** — [[ponder]]
- **Expansions** — [[expansion-plugin]] · [[fiefs]] · [[currencies]]
- **Runtime neighbours** — [[mailboxes]]
- **Distribution** — [[dans-plugin-manager]]

---

## → [[moc-conventions-and-process]] — the standards

What every repository in the organization is held to.

- [[dpc-conventions]] · [[two-tier-documentation]] · [[release-automation]] ·
  [[testing-and-ci]]

---

## → [[moc-web-and-infrastructure]] — outside Minecraft

The public site, the containerised server, and the pipe between them.

- [[dansplugins-dot-com]] · [[dpc-mc-server]] · [[dpc-api-faction-sync]]

---

## How to read this collection

**If you have never touched the codebase**, read [[medieval-factions]], then
[[faction]], then [[faction-power]]. Those three carry most of the vocabulary
everything else assumes.

**If you are here to change code**, go straight to [[moc-plugin-architecture]].

**If you are here to check something**, every concept note carries citations to
a Dans-Plugins repository pinned at a commit SHA. Open the source panel and
follow the link — the claim is meant to be falsifiable by reading the code it
points at. See [the note format](../../docs/NOTE_FORMAT.md) for the rules.
