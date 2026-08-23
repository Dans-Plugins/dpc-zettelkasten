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

A citation for which neither question could be answered — GitHub timed out or
rate-limited, `gh` is not authenticated, the network is down — is reported
`unknown`, which is deliberately not the same as `invalid`. A pinned commit
cannot rot, so an invalid citation means the note was wrong when it was
written; an unanswered call establishes nothing either way and must never be
recorded as a broken citation, nor counted as a passing one.

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
import re
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import zklib  # noqa: E402

_head_cache = {}
_blob_cache = {}

# Statuses worth asking again about. A 504 in particular is routine against the
# contents API and usually succeeds on the next attempt. 403 is left out: bad
# credentials will never come good, and a secondary rate limit outlasts any
# backoff short enough to sit inside a CI job.
_RETRY_STATUS = (429, 500, 502, 503, 504)
_ATTEMPTS = 3
_BACKOFF_SECONDS = 1.0


def http_status(stderr):
    """The HTTP status `gh` reported, or None if it never reached an endpoint.

    `gh` writes failures as `gh: Not Found (HTTP 404)`. Output without that
    suffix — no credentials, DNS failure, connection reset — means the request
    was never answered, which is not the same as being answered "no".
    """
    match = re.search(r"\(HTTP (\d{3})\)", stderr)
    return int(match.group(1)) if match else None


def gh_api(path):
    """Call the API, retrying while the failure looks transient.

    Returns `(data, err, missing)`. `missing` is True only for a 404 — the one
    reply that proves the thing asked about is genuinely not there. Every other
    failure leaves the question unanswered, and callers must report that
    difference rather than collapsing it into an absence.
    """
    for attempt in range(_ATTEMPTS):
        try:
            out = subprocess.run(
                ["gh", "api", path],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
            )
        except FileNotFoundError:
            zklib.fail("the GitHub CLI (`gh`) is required; see https://cli.github.com/")
        if out.returncode == 0:
            return json.loads(out.stdout.decode("utf-8")), None, False
        err = out.stderr.decode("utf-8", "replace").strip()
        status = http_status(err)
        if status == 404:
            return None, err, True
        if status not in _RETRY_STATUS or attempt == _ATTEMPTS - 1:
            return None, err, False
        time.sleep(_BACKOFF_SECONDS * (2 ** attempt))
    # Unreachable while _ATTEMPTS is at least 1. Kept explicit so that a
    # misconfigured attempt count degrades to "unanswered" rather than to a
    # tuple-unpacking error three frames away from the cause.
    return None, "no attempt was made", False


def head_sha(repo):
    if repo not in _head_cache:
        data, err, _ = gh_api("repos/%s" % repo)
        if data is None:
            _head_cache[repo] = (None, err)
        else:
            branch = data.get("default_branch", "main")
            commit, err2, _ = gh_api("repos/%s/commits/%s" % (repo, branch))
            _head_cache[repo] = ((commit or {}).get("sha"), err2) if commit else (None, err2)
    return _head_cache[repo]


def blob_sha(repo, ref, path):
    """Git blob id for a file at a ref — cheap identity check without content.

    Returns `(sha, size, err, missing)`. `missing` separates "the API says this
    file is not there" from "the API did not say", which the caller reports as
    two different statuses.
    """
    key = (repo, ref, path)
    if key not in _blob_cache:
        parent = os.path.dirname(path)
        data, err, absent = gh_api("repos/%s/contents/%s?ref=%s" % (repo, parent, ref) if parent
                                   else "repos/%s/contents?ref=%s" % (repo, ref))
        if data is None:
            _blob_cache[key] = (None, None, err, absent)
        else:
            entry = next((e for e in data if e.get("path") == path), None)
            _blob_cache[key] = (
                (entry.get("sha"), entry.get("size"), None, False) if entry
                else (None, None, "not found at %s" % ref[:7], True)
            )
    return _blob_cache[key]


def line_count(repo, ref, path):
    """Line count of a file at a ref.

    Returns `(count, unanswered, err)`. A None count with `unanswered` False is
    not a failure: GitHub omits inline content for a blob too large to return
    that way, which simply leaves the bounds check unperformed.
    """
    data, err, absent = gh_api("repos/%s/contents/%s?ref=%s" % (repo, path, ref))
    if data is None:
        return None, not absent, err
    if "content" not in data:
        return None, False, None
    import base64
    raw = base64.b64decode(data["content"]).decode("utf-8", "replace")
    return len(raw.split("\n")), False, None


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

    pinned_sha, size, err, missing = blob_sha(repo, ref, path)
    if pinned_sha is None:
        # Only a definitive absence is a broken citation. A pinned commit does
        # not rot, so "not found" means the note was wrong when written —
        # whereas an unanswered call means nothing has been established.
        record["status"] = "invalid" if missing else "unknown"
        record["detail"] = "%s (%s)" % (
            "file not found at pinned commit" if missing
            else "could not check the pinned commit",
            err or "unknown error",
        )
        return record

    if want_lines and source.get("lines"):
        total, unanswered, err = line_count(repo, ref, path)
        if unanswered:
            record["status"] = "unknown"
            record["detail"] = "could not check the cited line range (%s)" % (err or "unknown error")
            return record
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

    current_sha, _, err, missing = blob_sha(repo, current_ref, path)
    if current_sha is None and not missing:
        record["status"] = "unknown"
        record["detail"] = "could not check the current HEAD (%s)" % (err or "unknown error")
    elif current_sha is None:
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

    # An unanswered call does not fail the build — a GitHub outage is not a
    # defect in the collection — but it must not pass quietly either, or a green
    # run reads as a verification that never happened. Written to stderr so it
    # survives `--json` without corrupting the document on stdout.
    unchecked = sum(1 for r in results if r["status"] == "unknown")
    if unchecked:
        sys.stderr.write(
            "warning: %d of %d citations could not be checked and are NOT verified; "
            "re-run when GitHub is reachable\n" % (unchecked, len(results))
        )

    return 1 if any(r["status"] == "invalid" for r in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
