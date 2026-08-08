---
id: faction-role
title: Faction Role
type: concept
moc: moc-faction-domain-model
tags: [medieval-factions, domain-model, governance]
summary: A named bundle of permission overrides that a faction assigns to its members.
created: 2026-08-07
updated: 2026-08-07
sources:
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/kotlin/com/dansplugins/factionsystem/faction/role/MfFactionRole.kt
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    lines: 9-30
    claim: A role holds an id, a name, and a map of permission names to nullable booleans, and resolves a permission by falling back from the role to the faction default to the permission's own default.
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/kotlin/com/dansplugins/factionsystem/faction/role/MfFactionRoles.kt
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    claim: A new faction is created with three roles, Owner, Officer and Member, with Member set as the default role.
---

A role is a named set of [[faction-permission]] overrides. Each member of a
[[faction]] holds exactly one, and a faction defines its own roles rather than
picking from a fixed list.

## Three-level resolution

The permission map is `Map<String, Boolean?>`, and the nullability carries
meaning. Looking up whether a role grants a permission walks three levels:

1. **The role's own value**, if it is not null.
2. **The faction's default** for that permission.
3. **The permission's built-in default.**

Null therefore means *inherit*, distinct from an explicit `false` meaning *deny*.
That distinction is what lets a faction change a default and have every role
that has not opted out follow along — a role with all-null values tracks the
faction's policy automatically.

## Serialized by name

Roles store `permissionsByName: Map<String, Boolean?>` and resolve those strings
to permission objects on read, discarding any that no longer parse. Storing
names rather than object references means a permission that is removed from the
plugin does not break deserialization of existing factions — the stale entry is
simply dropped. It also means a typo silently becomes a no-op, which is the cost
of that robustness.

Roles implement Bukkit's `ConfigurationSerializable`, so they round-trip through
the same serialization the rest of the plugin's configuration uses.

## Defaults

A new faction is not created with an empty role set. `MfFactionRoles.defaults()`
builds three: **Owner**, **Officer**, and **Member** — with Member as the
`defaultRoleId` that new joiners receive. Owner is granted everything, Officer a
curated middle tier (diplomacy, kicking, setting home, and managing the Member
role), and Member nothing but the permissions whose own default is `true`.

A freshly founded faction is therefore immediately governable, and the three-tier
shape is a suggestion rather than a constraint — a faction can create, delete,
and rename roles from there.

## Related

[[faction-permission]] describes what can be granted. Roles are stored inline on
the [[faction]] record rather than in their own table, which is why changing a
role bumps the faction's [[optimistic-locking]] version.
