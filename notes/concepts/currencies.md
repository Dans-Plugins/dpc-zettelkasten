---
id: currencies
title: Currencies
type: concept
moc: moc-plugin-ecosystem
tags: [currencies, expansion, ecosystem, economy]
summary: An expansion letting factions mint physical local currencies as item stacks, and the reference example of a modern Medieval Factions expansion.
created: 2026-08-07
updated: 2026-08-07
sources:
  - repo: Dans-Plugins/Currencies
    path: src/main/kotlin/com/dansplugins/currencies/currency/Currency.kt
    ref: 41597bea085d536b59bfd564aa58f8739b4ffd92
    claim: A currency is a data class of id, version, factionId, name, description, an ItemStack, an amount, a status and a nullable legacy id.
  - repo: Dans-Plugins/Currencies
    path: src/main/kotlin/com/dansplugins/currencies/Currencies.kt
    ref: 41597bea085d536b59bfd564aa58f8739b4ffd92
    claim: Currencies builds its own Hikari data source, Flyway migrations, jOOQ DSL and Services registry, and holds a reference to the MedievalFactions plugin instance.
  - repo: Dans-Plugins/Currencies
    path: src/main/kotlin/com/dansplugins/currencies/listener/FactionDisbandListener.kt
    ref: 41597bea085d536b59bfd564aa58f8739b4ffd92
    claim: On a FactionDisbandEvent every currency belonging to that faction that is not already retired is saved with status RETIRED, rather than deleted.
---

Currencies lets the owner of a [[faction]] create and mint a local currency.
Money is physical: a currency owns an `ItemStack`, and minting produces real
items that players carry, drop, and lose.

## Physical money

That choice has consequences the plugin then has to handle. Currency items can
be renamed in an anvil, placed as blocks, and moved between inventories — hence
`PrepareAnvilListener`, `BlockPlaceListener`, `InventoryClickListener`, and
`InventoryCloseListener`. A large part of the codebase exists to stop players
from counterfeiting or destroying money through ordinary Minecraft mechanics.

Alongside the physical form there is a `Balance` record and a coinpurse UI, so
the abstract and concrete representations coexist.

## Lifecycle tied to the faction

`Currency` carries a `factionId` and a `CurrencyStatus`. When a faction
disbands, `FactionDisbandListener` — subscribed to [[faction-events]] — walks
that faction's currencies and saves each one with status `RETIRED`. Nothing is
deleted.

Coins already minted therefore survive the state that issued them. That is both
historically apt and the practical option: the money is `ItemStack`s spread
across player inventories, chests, and the ground, and nothing in the plugin
could recall them.

## A faithful copy of the flagship's architecture

Currencies repeats the flagship's shape almost line for line: `CurrencyId` as a
[[value-class-identifier]], a `version` column for [[optimistic-locking]], a
`CurrencyRepository` interface with a `JooqCurrencyRepository` implementation, a
`Services` registry, and its own Flyway migrations over its own Hikari pool.

The `legacyId` field is the tell that it, too, has been migrated from an earlier
storage format.

## Related

See [[expansion-plugin]] for the pattern in general, and [[fiefs]] for the older
style it replaced.
