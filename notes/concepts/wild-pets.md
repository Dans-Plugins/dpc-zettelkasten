---
id: wild-pets
title: Wild Pets
type: concept
moc: moc-plugin-ecosystem
tags: [wild-pets, ecosystem, configuration]
summary: A standalone plugin that turns taming into a per-entity-type recipe — a required item, a quantity, and a success chance — so that any mob can become a pet.
created: 2026-08-24
updated: 2026-08-24
sources:
  - repo: Dans-Plugins/Wild-Pets
    path: src/main/java/dansplugins/wildpets/config/EntityConfig.java
    ref: 374065a04fdb5865fc782a1424b82e3b951881b3
    lines: 8-21
    claim: An entity configuration is five immutable fields — type name, chance to succeed, required taming item, taming item amount, and an enabled flag.
  - repo: Dans-Plugins/Wild-Pets
    path: src/main/java/dansplugins/wildpets/config/EntityConfigService.java
    ref: 374065a04fdb5865fc782a1424b82e3b951881b3
    lines: 42-137
    claim: The built-in table holds 81 entity configurations across passive, neutral, hostile and boss mobs, every one enabled with a chance to succeed of 0.5, with Endermite listed twice.
  - repo: Dans-Plugins/Wild-Pets
    path: src/main/java/dansplugins/wildpets/config/EntityConfigService.java
    ref: 374065a04fdb5865fc782a1424b82e3b951881b3
    lines: 23-32
    claim: A configuration is selected by comparing the entity's type name case-insensitively against each row's type, and the default configuration is returned when no row matches.
  - repo: Dans-Plugins/Wild-Pets
    path: src/main/java/dansplugins/wildpets/config/EntityConfigService.java
    ref: 374065a04fdb5865fc782a1424b82e3b951881b3
    lines: 164-166
    claim: The default configuration is constructed inline as type "default" with a 0.25 chance to succeed, 10 wheat, and enabled true.
  - repo: Dans-Plugins/Wild-Pets
    path: src/main/java/dansplugins/wildpets/listeners/InteractionHandler.java
    ref: 374065a04fdb5865fc782a1424b82e3b951881b3
    lines: 83-136
    claim: A taming attempt is refused when the entity's configuration is disabled or the player is at the pet limit, requires the configured material and amount in the main hand, and removes that amount from the held stack whether the roll succeeds or fails.
---

Vanilla Minecraft tames a handful of species. Wild Pets replaces that with a
lookup table: each entity type gets a row saying what taming it costs and how
likely an attempt is to work — and a type with no row still gets one.

## A row per entity type

An entity configuration is five fields: type name, success chance, required
item, item amount, and an enabled flag. The plugin ships 81 of them, from
passive animals through hostile mobs to the Ender Dragon and the Wither. Every
shipped row is enabled at a 0.5 chance, so the difference between mobs is
entirely the item and the quantity — 8 sweet berries for a fox, 64 ender eyes
for the Ender Dragon. The `enabled` flag is the per-type off switch.

## A fallback that is never a wall

Lookup compares the entity's type name against each row, case-insensitively.
On no match it returns a default configuration built inline: 0.25 chance, 10
wheat. An unlisted entity type is therefore *harder* to tame than anything in
the table, but never refused. Nothing in the repository explains the choice of
0.25 or of wheat, so treat those numbers as unexplained.

The consequence is that a key which cannot match degrades silently rather than
erroring. The shipped table contains `Wandering Trader` — with a space, which
an enum constant name cannot contain — and rows like `Piglin_Baby` and
`Chicken_Jockey` that name variants rather than types. My reading is that these
rows are unreachable and those mobs fall through to the default; I have not run
a server to confirm it.

## The attempt is a transaction

Right-clicking in taming mode checks the enabled flag, the owner's pet limit,
and the held stack against the row's material and amount, then rolls. The stack
is decremented by the required amount on failure as well as on success, so a
failed attempt has a price.

## Related

Taming is entered as a mode — `/wp tame` flags the player and the next
right-click supplies the target — which is the same shape as the flagship's
[[player-interaction-status]]. A tamed pet carries an owner plus an access list
and can be locked against everyone else, which is [[locked-block]]'s design
applied to a mob rather than a chest.
