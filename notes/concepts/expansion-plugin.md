---
id: expansion-plugin
title: Expansion Plugin
type: concept
tags: [medieval-factions, ecosystem, architecture]
summary: A plugin that hard-depends on Medieval Factions and extends the simulation — declaring the dependency in plugin.yml and reusing the flagship's identifiers, events, and permission model.
created: 2026-08-07
updated: 2026-08-07
sources:
  - repo: Dans-Plugins/Currencies
    path: src/main/resources/plugin.yml
    ref: 41597bea085d536b59bfd564aa58f8739b4ffd92
    claim: An expansion declares depend, not softdepend, on MedievalFactions so Bukkit refuses to load it without the flagship.
  - repo: Dans-Plugins/Currencies
    path: src/main/kotlin/com/dansplugins/currencies/currency/Currency.kt
    ref: 41597bea085d536b59bfd564aa58f8739b4ffd92
    claim: An expansion's own domain records reference the flagship's MfFactionId type directly and repeat its shape, with a value-class id and a version column.
  - repo: Dans-Plugins/Currencies
    path: src/main/kotlin/com/dansplugins/currencies/permission/CurrenciesFactionPermissions.kt
    ref: 41597bea085d536b59bfd564aa58f8739b4ffd92
    claim: The expansion calls addPermissionType on the flagship's own factionPermissions registry to add CREATE_CURRENCY, RETIRE_CURRENCY, CHANGE_CURRENCY_NAME, CHANGE_CURRENCY_DESCRIPTION and MINT_CURRENCY.
---

An expansion is a plugin that cannot run on its own. It declares
`depend: [MedievalFactions]` in `plugin.yml` — not `softdepend` — so Bukkit
refuses to enable it when the flagship is absent, and it reaches directly into
the flagship's types.

## What an expansion reuses

[[currencies]] is the cleanest current example, and it borrows four things:

1. **Identifiers.** `Currency` holds an `MfFactionId` — the flagship's own
   [[value-class-identifier]] — rather than a stringly-typed faction reference.
2. **Architecture.** Its own `Services` registry, `JooqCurrencyRepository`,
   Flyway migrations, and `version` column mirror
   [[moc-plugin-architecture|the flagship's shape]] exactly.
3. **Events.** `FactionCreateListener` and `FactionDisbandListener` subscribe to
   [[faction-events]], which is how a currency is retired when its issuing
   faction disbands.
4. **Permissions.** `CurrenciesFactionPermissions` calls `addPermissionType` on
   the flagship's own registry, adding `CREATE_CURRENCY`, `MINT_CURRENCY`, and
   three per-currency permissions to the flagship's [[faction-permission]]
   model — so minting rights are granted through the same `/f role` commands as
   everything else.

That fourth point is the one that makes an expansion feel native rather than
bolted on: a player never learns a separate permission system.

## Its own database

Each expansion runs its own Hikari pool, Flyway history, and jOOQ context
against its own tables. It does not read the flagship's schema. The coupling is
through the Java API and the event bus, never through shared SQL — so a schema
change in the flagship cannot break an expansion silently.

## Two generations

[[fiefs]] predates this pattern. It is Java, targets Medieval Factions 4 through
a vendored jar, and integrates through its own `MedievalFactionsIntegrator`
rather than by importing flagship types. Reading both side by side is the
fastest way to see what the version 5 rewrite changed.

## Related

Expansions are listed in the flagship's own README, which is how server owners
discover them.
