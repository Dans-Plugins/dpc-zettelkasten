#!/usr/bin/env python3
"""Build the offline zettelkasten explorer.

Renders every note to HTML and embeds the whole graph in a single
self-contained `site/index.html` that works from the filesystem with no server,
no network, and no build dependencies.

Usage:
    python3 tools/build.py [--out site/index.html]
"""

import argparse
import datetime
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import md  # noqa: E402
import zklib  # noqa: E402

TEMPLATE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "template.html")
GITHUB_BASE = "https://github.com/Dans-Plugins/dpc-zettelkasten/blob/main/"


def make_wikilink_renderer(by_id, note_id, unresolved):
    def wikilink(target, anchor, label):
        text = label or (by_id[target].title if target in by_id else target)
        if target not in by_id:
            unresolved.append((note_id, target))
            return '<span class="wl broken" title="no note with id \'%s\'">%s</span>' % (
                md.escape(target), md.escape(text)
            )
        href = "#/" + target + (("#" + md.slugify(anchor)) if anchor else "")
        return '<a class="wl" href="%s" data-id="%s">%s</a>' % (
            md.escape(href), md.escape(target), md.escape(text)
        )
    return wikilink


def build_payload(notes):
    by_id = zklib.index_by_id(notes)
    backlinks = zklib.backlink_map(notes)
    unresolved = []
    payload = {}

    for note in notes:
        headings = []
        html = md.render(
            note.body,
            wikilink=make_wikilink_renderer(by_id, note.id, unresolved),
            headings=headings,
        )
        sources = []
        for source in note.sources:
            sources.append({
                "repo": source["repo"],
                "path": source["path"],
                "ref": source["ref"],
                "shortRef": source["ref"][:7],
                "lines": source.get("lines", ""),
                "claim": source.get("claim", ""),
                "url": zklib.source_url(source),
                "label": zklib.source_label(source),
            })
        payload[note.id] = {
            "id": note.id,
            "title": note.title,
            "type": note.type,
            "tags": note.tags,
            "summary": note.summary,
            "updated": note.meta.get("updated", ""),
            "html": html,
            "toc": [{"level": lvl, "text": txt, "slug": slug} for lvl, txt, slug in headings],
            "links": [t for t in note.links if t in by_id],
            "backlinks": backlinks.get(note.id, []),
            "sources": sources,
            "sourcePath": note.rel_path,
            "sourceUrl": GITHUB_BASE + note.rel_path,
            "text": (note.title + " " + note.summary + " " + note.body).lower(),
        }

    return payload, unresolved


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default=os.path.join("site", "index.html"))
    args = parser.parse_args()

    try:
        notes = zklib.load_notes()
        payload, unresolved = build_payload(notes)
    except zklib.NoteError as exc:
        zklib.fail(str(exc))

    for note_id, target in unresolved:
        sys.stderr.write("warning: %s links to unknown note [[%s]]\n" % (note_id, target))

    repos = {}
    for note in notes:
        for source in note.sources:
            repos.setdefault(source["repo"], set()).add(source["ref"])

    meta = {
        "generated": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        "noteCount": len(notes),
        "mocCount": sum(1 for n in notes if n.type == "moc"),
        "conceptCount": sum(1 for n in notes if n.type == "concept"),
        "citationCount": sum(len(n.sources) for n in notes),
        "linkCount": sum(len(payload[n.id]["links"]) for n in notes),
        "repos": sorted(repos),
        "home": "moc-dans-plugins-community" if "moc-dans-plugins-community" in payload else sorted(payload)[0],
    }

    with open(TEMPLATE_PATH, "r", encoding="utf-8") as handle:
        template = handle.read()

    html = template.replace(
        "/*__NOTES__*/null", json.dumps(payload, ensure_ascii=False, sort_keys=True)
    ).replace(
        "/*__META__*/null", json.dumps(meta, ensure_ascii=False, sort_keys=True)
    )

    out_path = os.path.join(zklib.REPO_ROOT, args.out) if not os.path.isabs(args.out) else args.out
    out_dir = os.path.dirname(out_path)
    if out_dir and not os.path.isdir(out_dir):
        os.makedirs(out_dir)
    with open(out_path, "w", encoding="utf-8") as handle:
        handle.write(html)

    print(
        "built %s — %d notes (%d MOCs, %d concepts), %d links, %d citations across %d repos"
        % (
            os.path.relpath(out_path, zklib.REPO_ROOT),
            meta["noteCount"], meta["mocCount"], meta["conceptCount"],
            meta["linkCount"], meta["citationCount"], len(meta["repos"]),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
