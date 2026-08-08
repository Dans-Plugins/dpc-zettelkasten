---
id: approval-request
title: Approval Request
type: concept
moc: moc-faction-domain-model
tags: [medieval-factions, domain-model, diplomacy]
summary: The consent step for the three diplomatic changes that bind two factions — war, alliance, and vassalisation.
created: 2026-08-07
updated: 2026-08-07
sources:
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/kotlin/com/dansplugins/factionsystem/approval/MfApprovalRequestType.kt
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    lines: 3-14
    claim: There are exactly three approval request types, WAR, ALLY and VASSALIZE, each mapping to a language key for localised display.
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/kotlin/com/dansplugins/factionsystem/approval/MfApprovalRequestService.kt
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    claim: Approval requests are held by a dedicated service registered alongside the plugin's other services.
---

Some actions inside a [[faction]] cannot be taken by one player alone. An
approval request is the pending state between a proposal and its acceptance.

## Exactly three types

`WAR`, `ALLY`, `VASSALIZE` — and each is a [[faction-relationship]] transition.
That the enum has no fourth member is the point: every action that binds two
independent groups of players goes through this mechanism, and everything else in
the plugin is unilateral.

## Why war needs approval

Alliance and vassalisation obviously require the other side's consent. War is
the interesting case, and the design treats it as a *mutual* state rather than
something one faction inflicts on another. A faction cannot be dragged into a war
it has not accepted — which is what makes the `neutral` [[faction-flag]] and the
`pvp.warRequiredForPlayersOfDifferentFactions` setting meaningful rather than
trivially bypassable.

## Localised by construction

Each type carries a `languageKey` rather than a display string. The pattern
appears throughout the plugin: domain enums know their language key, and the
language file supplies the words. It keeps translations out of the domain model
and means adding a locale never touches Kotlin.

## Related

The request itself is short-lived state held by `MfApprovalRequestService` and
addressed through an [[value-class-identifier]], like every other record in the
plugin.
