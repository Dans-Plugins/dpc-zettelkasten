---
id: release-channel
title: Release Channel
type: concept
moc: moc-conventions-and-process
tags: [dpm, ecosystem, ci, conventions]
summary: Each managed plugin tracks either published releases or a rolling build of its main branch, and Dan's Plugin Manager remembers the choice per plugin.
created: 2026-08-23
updated: 2026-08-23
sources:
  - repo: Dans-Plugins/Dans-Plugin-Manager
    path: USER_GUIDE.md
    ref: 3733eb51df6be11ac0239d7cffcfb2ef72e756a9
    claim: Every managed plugin tracks one of two channels — stable, the latest published GitHub release, or experimental, a build of the plugin's main branch published automatically by the repository's CI as a rolling dev prerelease.
  - repo: Dans-Plugins/Dans-Plugin-Manager
    path: COMMANDS.md
    ref: 3733eb51df6be11ac0239d7cffcfb2ef72e756a9
    claim: /dpm get takes --experimental or --stable to switch the named plugins between channels, while /dpm update takes no channel flags and follows whatever channel each plugin is already set to.
  - repo: Dans-Plugins/Dans-Plugin-Manager
    path: src/main/java/dansplugins/dpm/objects/ReleaseChannel.java
    ref: 3733eb51df6be11ac0239d7cffcfb2ef72e756a9
    claim: The channel model is an enum of exactly two values, STABLE and EXPERIMENTAL, with unrecognised stored values falling back to STABLE.
---

A channel is the answer to "which build of this plugin should the server get?"
[[dans-plugin-manager]] gives each managed plugin one of two, and there are
exactly two — the enum has no third value and unknown names fall back to stable.

| Channel | What it fetches | Who publishes it |
|---|---|---|
| `stable` (default) | The latest published GitHub release | A maintainer, when they cut one |
| `experimental` | A build of `main`, refreshed on every merge | The repository's CI, as a rolling `dev` prerelease |

## The rolling `dev` prerelease

The experimental channel is not a different way of reading the release list. It
reads *one specific release* — a prerelease tagged `dev` that each repository's
CI overwrites on every push to `main`. This is the piece that is hard to guess
from the outside: "the dev build" is a GitHub release like any other, it simply
never changes its tag.

That has a consequence DPM has to work around. Every experimental build carries
the same `dev` tag, so tag equality would report "already up to date" forever.
DPM records the version as `dev-<commit>` instead, which is what `/dpm list` and
`/dpm info` show.

It also means the stable channel cannot reach these builds even in principle:
stable resolves through GitHub's `releases/latest`, which excludes prereleases
by design.

## The choice is sticky

`/dpm get <plugin> --experimental` is not a one-off download. The channel is
remembered per plugin, so plain `/dpm get` and `/dpm update` keep that plugin on
experimental builds until `--stable` is passed. This is the behaviour of a
package manager pinning a package to a channel, which is of a piece with the
rest of DPM's [[dans-plugin-manager|apt-shaped vocabulary]].

Three edges follow from stickiness, and each guards a specific failure:

- **Dependencies keep their own channel.** A dependency pulled in automatically
  arrives from whatever channel *it* is set to, not the channel of the plugin
  that required it.
- **A plugin pinned to experimental stays pinned** even if its repository stops
  publishing a rolling build. `/dpm update` reports and skips it rather than
  silently reverting it to releases — a quiet downgrade would be worse than a
  visible stall.
- **Removing a plugin resets it to stable**, so a later reinstall does not
  silently return to unreleased code.

## Why this is the honest default for a community

[[release-automation]] describes the stable path: a maintainer creates a release,
CI builds it and attaches the jar. That path is deliberate and slow, which is
right for the servers people actually play on.

The experimental channel exists because the gap between "merged" and "released"
is where most of the useful feedback lives, and a server operator willing to run
main-branch code is the best tester the community has. The guide is blunt about
the trade — unreleased, unreviewed code that can stop a server from starting —
and DPM repeats the warning on every switch rather than burying it in docs.

Worth noting for anyone reading DPM's own version numbers: the channel feature
itself lives on `main` and is in no published DPM release, and DPM publishes no
rolling build of itself. A jar with the flags has to be built from source.
