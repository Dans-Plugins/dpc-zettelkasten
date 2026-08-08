---
id: faction-permission
title: Faction Permission
type: concept
moc: moc-faction-domain-model
tags: [medieval-factions, domain-model, governance]
summary: The individually grantable capabilities inside a faction, each with a default and a type.
created: 2026-08-07
updated: 2026-08-07
sources:
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/kotlin/com/dansplugins/factionsystem/faction/permission/MfFactionPermission.kt
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    claim: A faction permission is a data class of a name, a translate function taking the faction, and a default boolean, with equality and hashCode defined on the name alone.
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/kotlin/com/dansplugins/factionsystem/faction/permission/MfFactionPermissions.kt
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    claim: A registry holds the permission types, builds the permission set for a faction from its roles, and parses permission names back into permission objects.
---

A permission is one capability a faction can grant or withhold — claiming land,
inviting members, editing [[law]], and so on. Permissions are the leaves of the
governance model; [[faction-role]] bundles them.

## Parameterised by role

Some permissions are not a single capability but a family: the ability to modify
*a particular* role. `MfFactionPermissions.permissionsFor(factionId, roles)`
builds the permission set for a specific faction from its specific roles, which
means the available permissions differ between factions.

This is why permissions are stored and resolved **by name** rather than by
reference — the object graph is per-faction and rebuilt at load, so only the
string is stable enough to persist.

## Defaults are per-permission

Each permission declares its own default, consulted last in the three-level
resolution described in [[faction-role]]. A faction can shift the middle level
by setting `defaultPermissionsByName` on the [[faction]] record, and a role can
shift the top level. The permission's own default is the backstop that
guarantees every lookup terminates in a boolean.

## Serialization

Dedicated serializers exist for a permission and for a map of permissions,
keeping the encoding of permission state in one place rather than scattered
through the repositories that persist roles.

## Related

Permissions govern members. Non-members are governed by [[faction-flag]] settings
and by their [[faction-relationship]] to the landowner — two separate systems
that meet at the block-interaction check on a [[claimed-chunk]].
