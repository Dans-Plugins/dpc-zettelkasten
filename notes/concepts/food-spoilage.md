---
id: food-spoilage
title: Food Spoilage
type: concept
moc: moc-plugin-ecosystem
tags: [food-spoilage, ecosystem, persistence]
summary: A standalone plugin that gives food an expiry date carried on the item stack itself, with no database and no repeating task — spoilage is evaluated the moment a player touches the item.
created: 2026-08-24
updated: 2026-08-24
sources:
  - repo: Dans-Plugins/FoodSpoilage
    path: src/main/java/spoilagesystem/timestamp/LocalTimeStampService.java
    ref: f5fbff6bea0703194652af264a6fe94326e7b7f7
    lines: 39-60
    claim: Stamping an item writes the expiry moment both into the item's PersistentDataContainer under the namespaced key "expiry" and into the item's lore, and writes nothing anywhere else.
  - repo: Dans-Plugins/FoodSpoilage
    path: src/main/java/spoilagesystem/FoodSpoilage.java
    ref: f5fbff6bea0703194652af264a6fe94326e7b7f7
    lines: 36-81
    claim: onEnable registers eleven Bukkit listeners through Ponder's EventHandlerRegistry and starts no repeating or scheduled task.
  - repo: Dans-Plugins/FoodSpoilage
    path: src/main/java/spoilagesystem/listeners/PlayerInteractListener.java
    ref: f5fbff6bea0703194652af264a6fe94326e7b7f7
    lines: 28-62
    claim: A stamped item is only turned into rotten flesh when a player interacts with it and its stored expiry has already passed, at which point the held stack is swapped and the interaction cancelled.
  - repo: Dans-Plugins/FoodSpoilage
    path: src/main/java/spoilagesystem/listeners/BlockCookListener.java
    ref: f5fbff6bea0703194652af264a6fe94326e7b7f7
    lines: 12-34
    claim: The BlockCookEvent handler is deliberately a no-op because stamping the furnace output with custom data makes Minecraft 1.20.5+'s canBurn() similarity check fail and stalls the furnace after one item.
  - repo: Dans-Plugins/FoodSpoilage
    path: src/main/java/spoilagesystem/timestamp/LocalTimeStampService.java
    ref: f5fbff6bea0703194652af264a6fe94326e7b7f7
    lines: 121-166
    claim: Reading an expiry tries the persistent data container first and falls back to parsing the date back out of the item's lore, with the persistent-data parse failure swallowed under a comment saying logging it would spam the console on servers upgraded from pre-3.0.0.
---

Food Spoilage gives every edible item an expiry date, and keeps that date on the
item. There is no table, no cache file and no repeating task: the expiry is a
string in the stack's persistent data container, mirrored into its lore, and it
travels with the stack through hoppers, chests, drops and restarts because
Minecraft already persists item metadata.

## Stamp on arrival, judge on use

Eleven listeners cover the ways food enters play — crafting, fishing, mob drops,
item spawns, pickups, joining, and opening or closing a container — and each one
stamps anything edible that is not already stamped. Nothing sweeps inventories
looking for expired food. The check happens at the point of contact: interact
with a stack whose date has passed and it is replaced in your hand with rotten
flesh and the interaction cancelled.

Because state lives on the item rather than in storage, the plugin needs nothing
like the [[repository-pattern]] the flagship uses. It does still read the older
lore-only representation, the same "keep reading the previous format" instinct as
[[legacy-data-migration]] at a much smaller scale — and that fallback is load
bearing: the expiry is written with `ISO_OFFSET_DATE`, which carries no
time-of-day, so the same formatter cannot parse it back into an `OffsetDateTime`
and the persistent-data read fails silently every time. I verified that round
trip against the JDK rather than finding it stated anywhere; no comment, commit
or issue in the repository records whether it is intended.

## The furnace is left alone

The one deliberate hole is cooking. `BlockCookListener` handles the event and
does nothing, and its Javadoc records why: since Minecraft 1.20.5 the furnace
re-runs `canBurn()` every tick, comparing the vanilla recipe result against the
output slot by strict data-component equality. A stamped output no longer
matches, so the furnace stops after one item. Leaving furnace output vanilla and
stamping it later, when it reaches a player, is the workaround — and it is why
`InventoryCloseListener` exists at all.

## Related

The plugin extends `PonderBukkitPlugin` and registers its listeners through
[[ponder]]'s `EventHandlerRegistry`. It ships in the curated jar set on
[[dpc-mc-server]], and unlike an [[expansion-plugin]] it has no dependency on
[[medieval-factions]] — its only optional integration is with RPKit's food
library, which it serves by registering itself as that library's expiry service.
