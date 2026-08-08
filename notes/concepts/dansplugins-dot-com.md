---
id: dansplugins-dot-com
title: dansplugins.com
type: concept
tags: [dpc, web]
summary: The community's Next.js website — plugin directory, guides, and player accounts — backed by a separate dpc-api service.
created: 2026-08-07
updated: 2026-08-07
sources:
  - repo: Dans-Plugins/dansplugins-dot-com
    path: README.md
    ref: 21faae72f893a5267d4d754a0fd97d1c183f3aba
    claim: The site is a Next.js application serving as the central hub for the community at dansplugins.com, showcasing plugins and linking to documentation and support.
  - repo: Dans-Plugins/dansplugins-dot-com
    path: utils/apiBase.ts
    ref: 21faae72f893a5267d4d754a0fd97d1c183f3aba
    claim: The site resolves a separate dpc-api backend from the NEXT_PUBLIC_API_URL environment variable, defaulting to a local dev-portal origin.
---

dansplugins.com is the community's public face: a Next.js and MUI application
listing the plugins, hosting guides, and — since accounts were added — letting
players claim a profile and like things.

## A front end, not a backend

The site holds almost no data of its own. `utils/apiBase.ts` resolves a separate
**dpc-api** service from `NEXT_PUBLIC_API_URL`, and the `services/` directory is
a set of thin clients against it: `claimService`, `likeService`,
`profileService`, `backlogService`, `featureRequestService`, `visitService`.

That separation is why this repository is TypeScript with no database. It also
means the site is not the receiving end of [[dpc-api-faction-sync]] — dpc-api
is, and the site reads what dpc-api stores.

## Failing soft

The service clients wrap their fetches in `try`/`catch` and return an empty
array on any error. A page whose data call fails renders empty rather than
erroring.

For a public site whose backend is a separately deployed service, that is the
right default: a visitor browsing the plugin list should not see a 500 because
the likes endpoint is down. The trade-off is that a genuine outage looks
identical to "there is nothing here".

## More than a brochure

The `pages/` directory shows the scope: a plugin index, guides, news, a roadmap,
a leaderboard, commissions, a developer portal, per-user profile pages at
`/u/[username]`, plus `sitemap.xml` and `robots.txt` generated server-side. The
`__tests__/` directory holds a test file for most modules in `services/` and
`utils/`, run with Vitest.

## Related

Static plugin metadata lives in `pages/data/plugins.json`, checked into the
repository — the directory of plugins is versioned, while the live data behind
it is not.
