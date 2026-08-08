---
id: moc-web-and-infrastructure
title: Web and Infrastructure
type: moc
tags: [moc, dpc, web, infrastructure]
summary: The community website, the containerised Minecraft server, and the data path that connects a live game server to the public site.
created: 2026-08-07
updated: 2026-08-07
---

Not everything in the organization runs inside Minecraft.

## The website

[[dansplugins-dot-com]] is the community's public face: a Next.js application
listing the plugins, hosting guides, and — since the addition of accounts —
letting players claim a profile.

## The server

[[dpc-mc-server]] is an infrastructure-as-code Spigot server. It pins specific
plugin JARs into a Docker image, which makes it the closest thing the
organization has to an integration environment: if a change breaks the
interaction between two plugins, this is where it shows up.

## The connection between them

[[dpc-api-faction-sync]] is the bridge. A running [[medieval-factions]] server
can be configured to POST its faction roster to the website's API on an
interval, which is how live in-game data reaches a public web page.

That path is the most operationally dangerous code in the organization, because
a bad request does not corrupt one server's data — it corrupts the shared
registry. The note explains the guards that exist because of it.

## Distribution

[[dans-plugin-manager]] closes the loop for server operators, pulling published
plugin releases onto a running server without a manual download.
