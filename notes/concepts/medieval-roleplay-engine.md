---
id: medieval-roleplay-engine
title: Medieval Roleplay Engine
type: concept
moc: moc-plugin-ecosystem
tags: [medieval-roleplay-engine, ecosystem, chat]
summary: A roleplay plugin whose chat audience is computed from distance in blocks rather than from channel membership — whisper, local, emote and yell differ only by radius.
created: 2026-08-24
updated: 2026-08-24
sources:
  - repo: Dans-Plugins/Medieval-Roleplay-Engine
    path: src/main/java/dansplugins/rpsystem/utils/Messenger.java
    ref: 283dfca2c786b76bf3259a474daa6d5378b13d07
    lines: 53-81
    claim: All roleplay chat is delivered by one routine that iterates the online players and sends only to those in the same world whose distance from the speaker is strictly less than the given radius and who have not hidden that channel.
  - repo: Dans-Plugins/Medieval-Roleplay-Engine
    path: src/main/java/dansplugins/rpsystem/config/ConfigService.java
    ref: 283dfca2c786b76bf3259a474daa6d5378b13d07
    lines: 24-35
    claim: The speech ranges are four independent integer config options defaulting to 2 blocks for whisper, 25 for local chat, 25 for emotes and 50 for yelling.
  - repo: Dans-Plugins/Medieval-Roleplay-Engine
    path: src/main/java/dansplugins/rpsystem/listeners/ChatListener.java
    ref: 283dfca2c786b76bf3259a474daa6d5378b13d07
    lines: 25-59
    claim: While a player is in local chat the plugin cancels the AsyncPlayerChatEvent and re-sends the message under the character card's name, splitting any text between asterisks into a separate emote delivered at emoteRadius instead of localChatRadius.
  - repo: Dans-Plugins/Medieval-Roleplay-Engine
    path: src/main/java/dansplugins/rpsystem/commands/global/GlobalChatCommand.java
    ref: 283dfca2c786b76bf3259a474daa6d5378b13d07
    lines: 27-41
    claim: The /global command only removes the player's UUID from the local-chat set — it delivers no message of its own, so global chat is ordinary uncancelled server chat.
  - repo: Dans-Plugins/Medieval-Roleplay-Engine
    path: USER_GUIDE.md
    ref: 283dfca2c786b76bf3259a474daa6d5378b13d07
    lines: 47-49
    claim: Hiding local chat withholds the entire roleplay channel — whispers, yells, emotes, dice results and bird landing notices — and a hidden player cannot talk in local chat either.
---

Speech here has a physical range. Where [[faction-chat-channel]] resolves an
audience from the diplomacy graph, this plugin resolves one from geometry: an
utterance reaches the players standing near enough to hear it, and the speech
"modes" differ only in how far that is.

## One delivery routine, four radii

`deliverMessageToNearbyPlayers` is the whole mechanism. It walks the online
players, drops anyone in another world, drops anyone whose distance from the
speaker is not strictly less than the radius, drops anyone who has hidden that
channel, and sends. Everything above it is a caller picking a number and a
colour: whisper 2 blocks, local chat and emotes 25, yelling 50 — four separate
config integers, so an operator tunes how far a voice carries.

A character card supplies the name, so a line is attributed to the character
rather than to the Minecraft account.

## Local chat is a mode, not a command

`/local` puts a UUID into an in-memory set. While it is there the chat listener
cancels the vanilla chat event and re-broadcasts the message at
`localChatRadius`; text between asterisks is split out and sent separately at
`emoteRadius`, so `*draws his sword* Stand back!` becomes an action and a line
of dialogue with independently configurable reach.

`/global` is the mirror image, and the most revealing line in the plugin: it
takes the UUID back out of the set and does nothing else. Global chat is not a
channel this plugin delivers — it is what happens when the plugin declines to
intercept.

## One channel to mute

All roleplay output shares a single mute flag. The user guide states plainly
that hiding local chat withholds whispers, yells, emotes, dice results and bird
notices as well, and that a hidden player cannot speak in local chat. Why the
mute is that coarse is not recorded.

## Related

The plugin soft-depends on [[medieval-factions]] and [[mailboxes]], running
alongside the flagship without requiring it. One observation offered as
reasoning, not as anything the source claims: the distance walk runs inside an
`AsyncPlayerChatEvent` handler and reads live player locations there, which is
the opposite of the snapshot discipline [[main-thread-safety]] describes. No
comment or commit in the repository addresses that.
