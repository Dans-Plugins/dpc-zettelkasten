---
id: release-automation
title: Release Automation
type: concept
moc: moc-conventions-and-process
tags: [dpc, conventions, ci]
summary: Creating a GitHub Release triggers a workflow that builds the plugin and attaches the jar, so every release has a reproducible artifact.
created: 2026-08-07
updated: 2026-08-07
sources:
  - repo: Dans-Plugins/dpc-conventions
    path: docs/RELEASE_AUTOMATION.md
    ref: 9dc9aa37e9ed58722d86a914c563b5ceeaa07bec
    claim: The convention is a .github/workflows/release.yml triggered on release creation that checks out, sets up JDK 17, builds with Gradle and uploads the built jar to the release.
  - repo: Dans-Plugins/Medieval-Factions
    path: .github/workflows/release.yml
    ref: 3a51c55366b544d31429fae8bcb64efaf1878e15
    claim: The flagship's release workflow follows the convention but adds a step that clones Ponder at tag 2.0.0 and publishes it to the local Maven repository before building.
---

Every DPC plugin should build and attach its own jar when a release is created.
The convention specifies the workflow file down to the steps.

## The workflow

`.github/workflows/release.yml`, triggered `on: release: types: [created]`, with
`permissions: contents: write`. It checks out, sets up JDK 17 (Temurin), makes
`gradlew` executable, runs `./gradlew clean build`, and uploads `build/libs/*.jar`
to the release.

## Why drafts matter

The trigger fires on release *creation*, including drafts. That is deliberate: a
maintainer can create a draft release, let CI build and attach the jar, and hand
that artifact to users as an experimental build before deciding to publish.
Testing a release candidate needs no separate pipeline.

## Why it is a convention and not a nicety

Manual jar uploads fail in two ways that automation removes. They can be
forgotten — leaving a release with notes and no download. And they can be built
from a dirty working tree, so the published jar does not correspond to the tag.
Building in CI from a clean checkout makes the artifact a function of the commit.

There is also a consumer that depends on it: [[dans-plugin-manager]] installs
plugins by reading GitHub releases. A release without an attached jar is a
release DPM cannot install.

## The flagship deviates, for a reason

[[medieval-factions]] follows the template but inserts a step before the build:
it clones [[ponder]] at tag `2.0.0` and runs `publishToMavenLocal`. The library
version it needs is not resolvable from a public repository at build time, so CI
builds it from source first.

That is worth knowing before copying the convention's workflow verbatim into a
plugin that depends on Ponder — the template alone will not resolve the
dependency.

## Related

[[testing-and-ci]] covers the build and test side. Both live in
[[dpc-conventions]].
