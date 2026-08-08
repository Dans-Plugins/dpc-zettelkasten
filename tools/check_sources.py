#!/usr/bin/env python3
"""Check every citation against GitHub.

For each `sources:` entry this answers two separate questions:

  1. Is the citation *valid*? — does the file still exist at the pinned commit,
     and does the cited line range fall inside it? A pinned SHA should never
     rot, so a failure here means the citation was wrong when it was written.
  2. Has the cited code *drifted*? — is the file at the repository's current
     default-branch HEAD identical to the pinned blob? Drift is not an error;
     it is the signal that a human or the zettelkasten-verify skill should
     re-read the note and decide whether its claim still holds.

Requires the GitHub CLI (`gh`) to be installed and authenticated.

Usage:
    python3 tools/check_sources.py                 # everything
    python3 tools/check_sources.py --note faction  # one note
    python3 tools/check_sources.py --drift-only    # only report drift
    python3 tools/check_sources.py --json          # machine-readable
"""

import argparse
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import zklib  # noqa: E402

_head_cache = {}
_blob_cache = {}


def gh_api(path):
    try:
        out = subprocess.run(
            ["gh", "api", path],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
        )
    except FileNotFoundError:
        zklib.fail("the GitHub CLI (`gh`) is required; see https://cli.github.com/")
    if out.returncode != 0:
        return None, out.stderr.decode("utf-8", "replace").strip()
    return json.loads(out.stdout.decode("utf-8")), None


def head_sha(repo):
    if repo not in _head_cache:
        data, err = gh_api("repos/%s" % repo)
        if data is None:
            _head_cache[repo] = (None, err)
        else:
            branch = data.get("default_branch", "main")
            commit, err2 = gh_api("repos/%s/commits/%s" % (repo, branch))
            _head_cache[repo] = ((commit or {}).get("sha"), err2) if commit else (None, err2)
    return _head_cache[repo]


def blob_sha(repo, ref, path):
    """Git blob id for a file at a ref — cheap identity check without content."""
    key = (repo, ref, path)
    if key not in _blob_cache:
        parent = os.path.dirname(path)
        data, err = gh_api("repos/%s/contents/%s?ref=%s" % (repo, parent, ref) if parent
                           else "repos/%s/contents?ref=%s" % (repo, ref))
        if data is None:
            _blob_cache[key] = (None, None, err)
        else:
            entry = next((e for e in data if e.get("path") == path), None)
            _blob_cache[key] = (
                (entry.get("sha"), entry.get("size"), None) if entry
                else (None, None, "not found at %s" % ref[:7])
            )
    return _blob_cache[key]


def line_count(repo, ref, path):
    data, err = gh_api("repos/%s/contents/%s?ref=%s" % (repo, path, ref))
    if data is None or "content" not in data:
        return None
    import base64
    raw = base64.b64decode(data["content"]).decode("utf-8", "replace")
    return len(raw.split("\n"))


def check(note, source, want_lines):
    repo, ref, path = source["repo"], source["ref"], source["path"]
    record = {
        "note": note.id,
        "repo": repo,
        "path": path,
        "ref": ref,
        "lines": source.get("lines", ""),
        "claim": source.get("claim", ""),
        "url": zklib.source_url(source),
        "status": "ok",
        "detail": "",
    }

    pinned_sha, size, err = blob_sha(repo, ref, path)
    if pinned_sha is None:
        record["status"] = "invalid"
        record["detail"] = "file not found at pinned commit (%s)" % (err or "unknown error")
        return record

    if want_lines and source.get("lines"):
        total = line_count(repo, ref, path)
        if total is not None:
            end = int(source["lines"].split("-")[-1])
            if end > total:
                record["status"] = "invalid"
                record["detail"] = "cited line %d is past end of file (%d lines)" % (end, total)
                return record

    current_ref, err = head_sha(repo)
    if current_ref is None:
        record["status"] = "unknown"
        record["detail"] = "could not resolve default branch HEAD (%s)" % (err or "unknown error")
        return record

    record["headRef"] = current_ref
    if current_ref == ref:
        record["detail"] = "pinned at current HEAD"
        return record

    current_sha, _, err = blob_sha(repo, current_ref, path)
    if current_sha is None:
        record["status"] = "drifted"
        record["detail"] = "file has been deleted or moved since the pinned commit"
    elif current_sha != pinned_sha:
        record["status"] = "drifted"
        record["detail"] = "file has changed since the pinned commit"
        record["compareUrl"] = "https://github.com/%s/compare/%s...%s" % (repo, ref, current_ref)
    else:
        record["detail"] = "unchanged since the pinned commit"
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--note", help="only check this note id")
    parser.add_argument("--repo", help="only check citations to this repo")
    parser.add_argument("--drift-only", action="store_true", help="suppress ok results")
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("--skip-line-check", action="store_true",
                        help="skip line-range bounds checks (one extra API call each)")
    args = parser.parse_args()

    try:
        notes = zklib.load_notes()
    except zklib.NoteError as exc:
        zklib.fail(str(exc))

    if args.note:
        notes = [n for n in notes if n.id == args.note]
        if not notes:
            zklib.fail("no note with id %r" % args.note)

    results = []
    for note in notes:
        for source in note.sources:
            if args.repo and source["repo"] != args.repo:
                continue
            results.append(check(note, source, not args.skip_line_check))

    if args.as_json:
        print(json.dumps(results, indent=2, sort_keys=True))
    else:
        symbols = {"ok": "ok      ", "drifted": "DRIFTED ", "invalid": "INVALID ", "unknown": "unknown "}
        shown = [r for r in results if not (args.drift_only and r["status"] == "ok")]
        for r in shown:
            print("%s%s -> %s/%s%s" % (
                symbols[r["status"]], r["note"], r["repo"], r["path"],
                (":" + r["lines"]) if r["lines"] else "",
            ))
            print("          %s" % r["detail"])
            if r["status"] != "ok":
                print("          %s" % r["url"])
        if shown:
            print("")
        counts = {}
        for r in results:
            counts[r["status"]] = counts.get(r["status"], 0) + 1
        print("%d citations checked: %s" % (
            len(results),
            ", ".join("%d %s" % (v, k) for k, v in sorted(counts.items())) or "none",
        ))

    return 1 if any(r["status"] == "invalid" for r in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
