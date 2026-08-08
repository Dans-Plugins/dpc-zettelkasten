---
id: dpc-conventions
title: DPC Conventions
type: concept
moc: moc-conventions-and-process
tags: [dpc, conventions, process]
summary: The repository that writes the organization's standards down, using Medieval Factions as the worked example throughout.
created: 2026-08-07
updated: 2026-08-07
sources:
  - repo: Dans-Plugins/dpc-conventions
    path: README.md
    ref: 9dc9aa37e9ed58722d86a914c563b5ceeaa07bec
    claim: dpc-conventions documents standards across DPC projects with the stated goal of bringing every plugin to the same level of completeness and quality as Medieval Factions.
  - repo: Dans-Plugins/dpc-conventions
    path: docs/GITHUB_COPILOT_INSTRUCTIONS.md
    ref: 9dc9aa37e9ed58722d86a914c563b5ceeaa07bec
    claim: Every DPC plugin repository must have a .github/copilot-instructions.md that links back to the conventions repository and describes the plugin's architecture, stack and community norms.
---

dpc-conventions holds the standards every repository in the organization is
measured against. It contains no code — six documents and a ready-to-use prompt.

## The documents

| Document | Covers |
|---|---|
| `README_STRUCTURE.md` | The sections every plugin README must have, in order |
| `DOCUMENTATION_PRACTICES.md` | [[two-tier-documentation]] — repo files versus wiki pages |
| `CONTRIBUTING_STANDARDS.md` | What a complete `CONTRIBUTING.md` contains |
| `TESTING_AND_CI.md` | [[testing-and-ci]] |
| `RELEASE_AUTOMATION.md` | [[release-automation]] |
| `GITHUB_COPILOT_INSTRUCTIONS.md` | The required `.github/copilot-instructions.md` |

Five of the six point at [[medieval-factions]] as the reference implementation.
The standard is not an abstract ideal; it is "look at what the flagship does".

`GITHUB_COPILOT_INSTRUCTIONS.md` is the exception, and so is the
`CLAUDE_PROMPT.md` at the repository root — neither mentions the flagship at
all, because both describe a file each repository must write about *itself*
rather than a shape to copy from elsewhere.

## Conventions for coding agents

`GITHUB_COPILOT_INSTRUCTIONS.md` is the one with no equivalent in most
organizations' standards. It requires every repository to carry a
`.github/copilot-instructions.md` describing the plugin's architecture, stack,
and community norms, and linking back to dpc-conventions.

The reasoning is stated plainly: without it, an AI contributor has no awareness
of the conventions, the architecture, or the branch and issue workflow, and its
first suggestion will be inconsistent with the rest of the project. Machine
readers are treated as a first-class audience for documentation.

## One notable exception

`LICENSE` is explicitly excluded from the standardisation effort — the
documentation practices note says not to add, change, or remove it, because
licensing is left to the repository owner. Everything else in a repository root
is fair game for alignment; that one file is not.

## Related

This zettelkasten applies the same instinct one level up: standards and
architecture written down, each claim traceable to a source.
