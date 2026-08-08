---
id: notification
title: Notification
type: concept
moc: moc-plugin-architecture
tags: [medieval-factions, architecture, integration]
summary: A one-method interface for reaching an offline player, with implementations chosen at startup based on which plugins are installed.
created: 2026-08-07
updated: 2026-08-07
sources:
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/kotlin/com/dansplugins/factionsystem/notification/MfNotificationService.kt
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    lines: 5-7
    claim: The notification service interface declares a single method taking a player id and a notification.
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/kotlin/com/dansplugins/factionsystem/notification/mailboxes/MailboxesNotificationService.kt
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    lines: 10-16
    claim: The Mailboxes-backed implementation looks the plugin up by name, returns silently if it is absent, and forwards the notification through the Mailboxes API's sendPluginMessageToPlayer.
  - repo: Dans-Plugins/Medieval-Factions
    path: src/main/kotlin/com/dansplugins/factionsystem/MedievalFactions.kt
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    lines: 559-563
    claim: The implementation is chosen at startup by a when expression that prefers Mailboxes, falls back to RpkNotificationService when rpk-notification-lib-bukkit is present, and otherwise uses the no-op service.
---

When [[medieval-factions]] needs to tell a player something and that player is
offline, it hands the message to an `MfNotificationService`. The interface has
one method and no return value.

## Three implementations, chosen once

`setupNotificationService()` is a single `when` expression evaluated during
`onEnable`:

1. **Mailboxes** — if the [[mailboxes]] plugin is installed, the message waits
   in the player's in-game mail.
2. **RPKit** — otherwise, if `rpk-notification-lib-bukkit` is installed.
3. **No-op** — otherwise, the message is discarded.

The order is a preference, not a negotiation: with both installed, Mailboxes
wins and RPKit is never consulted. The rest of the codebase never learns which
was chosen. `MfFaction.sendMessage` illustrates the intended
use: message online members directly, and route the offline ones through the
notification service.

## Degrading quietly

The Mailboxes implementation begins by fetching the plugin from Bukkit's plugin
manager and casting it, returning immediately on a null or failed cast. A
notification to an unreachable backend is dropped, not raised.

That is the right call for this particular payload — a faction announcement is
not worth a stack trace in the console on every send, and the alternative
(throwing from a notification path) would let a missing optional dependency
break faction operations. It does mean a misconfigured server loses messages
silently.

## Why an interface at all

The no-op implementation is the tell. Rather than scatter
`if (mailboxesInstalled)` checks through the codebase, the plugin resolves the
question once at startup and lets the type system carry the answer. This is the
same shape as [[map-integration]], and it is the pattern to copy when integrating
any optional plugin.

## Related

The `MfNotification` record itself is just a title and a body — no severity, no
routing hints. Anything richer would have to be encoded in the text.
