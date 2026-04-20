#!/usr/bin/env python3
"""List open PRs across repos, filter by authors / drafts / labels, flag stale PRs, notify Slack.

GitHub logins to match on PR authors come from expanding Kubernetes-style **OWNERS** (approvers +
reviewers) using **OWNERS_ALIASES** in the same repository checkout (defaults: repo root adjacent to
``gh-notifier/``). Override paths with OWNERS_FILE and OWNERS_ALIASES_FILE.

Designed to be initiated from openshift/release on a schedule with env vars driving repos, labels,
and notification.
"""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable

# -----------------------------------------------------------------------------
# Environment (defaults are conservative)
# -----------------------------------------------------------------------------


def _env(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def _int_env(name: str, default: int) -> int:
    raw = _env(name, str(default))
    try:
        return int(raw)
    except ValueError:
        return default


STALE_DAYS = _int_env("STALE_DAYS", 7)
GITHUB_TOKEN = _env("GITHUB_TOKEN")
SLACK_WEBHOOK_URL = _env("SLACK_WEBHOOK_URL", "")

# Comma-separated org/repo pairs
_REPOS_RAW = _env("GITHUB_REPOS", "openshift-eng/edge-tooling")

# Semicolon or comma separated label tokens (GitHub compares labels names case-sensitively but we normalize)
_EXCLUDE_DEFAULT = "do-not-merge/hold,do-not-merge/work-in-progress,wip,work in progress"


def _label_set(raw: str) -> set[str]:
    if not raw:
        return set()
    toks = re.split(r"[;,]", raw)
    return {t.strip().lower() for t in toks if t.strip()}


EXCLUDE_LABELS = _label_set(_env("EXCLUDE_LABELS", _EXCLUDE_DEFAULT))
REQUIRED_LABELS = {x.lower() for x in re.split(r"[;,]", _env("REQUIRED_LABELS", "")) if x.strip()}
FORBIDDEN_LABELS = _label_set(_env("FORBIDDEN_LABELS", ""))

MAX_PRS_IN_MESSAGE = 20
CHUNK_MAX_LEN = 2800


def _parse_repos(raw: str) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for chunk in re.split(r"[,\s]+", raw):
        chunk = chunk.strip()
        if not chunk or "/" not in chunk:
            continue
        org, repo = chunk.split("/", 1)
        org, repo = org.strip(), repo.strip()
        if org and repo:
            out.append((org, repo))
    return out or [("openshift-eng", "edge-tooling")]


REPOS = _parse_repos(_REPOS_RAW)

_OWNERS_SECTIONS = frozenset({"approvers", "reviewers"})


def parse_owners_aliases(text: str) -> dict[str, list[str]]:
    """Parse OWNERS_ALIASES ``aliases:`` block into alias name -> GitHub logins."""
    aliases: dict[str, list[str]] = {}
    in_aliases = False
    current_key: str | None = None
    for raw_line in text.splitlines():
        line = raw_line.split("#", 1)[0].rstrip()
        stripped = line.strip()
        if not stripped:
            continue
        if stripped == "aliases:":
            in_aliases = True
            current_key = None
            continue
        if not in_aliases:
            continue
        # Another top-level YAML key ends the aliases document section we care about.
        if not line.startswith(" ") and stripped.endswith(":"):
            break
        m = re.match(r"^  ([A-Za-z0-9_.-]+):\s*$", line)
        if m:
            current_key = m.group(1)
            aliases.setdefault(current_key, [])
            continue
        m = re.match(r"^ +-\s+(\S+)", line)
        if m and current_key is not None:
            aliases[current_key].append(m.group(1).strip())
    return aliases


def parse_owners_raw_entries(text: str) -> list[str]:
    """Collect raw ``- name`` entries from approvers and reviewers sections only."""
    entries: list[str] = []
    current: str | None = None
    for raw_line in text.splitlines():
        line = raw_line.split("#", 1)[0].rstrip()
        stripped = line.strip()
        if not stripped:
            continue
        if re.match(r"^[a-zA-Z0-9_.-]+:\s*$", stripped) and not stripped.startswith("-"):
            key = stripped[:-1].strip()
            current = key if key in _OWNERS_SECTIONS else None
            continue
        if current and stripped.startswith("- "):
            val = stripped[2:].strip()
            if val:
                entries.append(val)
    return entries


def github_logins_from_owners(owners_text: str, aliases_text: str) -> set[str]:
    """Expand OWNERS approvers/reviewers using OWNERS_ALIASES; unknown names are treated as logins."""
    alias_map = parse_owners_aliases(aliases_text)
    logins: set[str] = set()
    for raw in parse_owners_raw_entries(owners_text):
        key = raw.strip()
        if not key:
            continue
        if key in alias_map:
            for u in alias_map[key]:
                u = u.strip()
                if u:
                    logins.add(u.lower())
        else:
            logins.add(key.lower())
    return logins


def load_github_logins_from_owners_files(owners_path: Path, aliases_path: Path) -> set[str]:
    if not owners_path.is_file():
        raise OSError(f"OWNERS file not found: {owners_path}")
    if not aliases_path.is_file():
        raise OSError(f"OWNERS_ALIASES file not found: {aliases_path}")
    return github_logins_from_owners(
        owners_path.read_text(encoding="utf-8"),
        aliases_path.read_text(encoding="utf-8"),
    )


# -----------------------------------------------------------------------------
# GitHub API (urllib, no extra deps)
# -----------------------------------------------------------------------------


def gh_request(path: str, query: dict[str, str] | None = None) -> object:
    if not GITHUB_TOKEN:
        sys.stderr.write("GITHUB_TOKEN is not set\n")
        sys.exit(1)
    url = "https://api.github.com" + path
    if query:
        url += "?" + urllib.parse.urlencode(query)
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "User-Agent": "edge-tooling-pr-notifier",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        sys.stderr.write(f"GitHub API error {e.code} {path}: {body}\n")
        raise


def iter_pulls(org: str, repo: str) -> Iterable[dict]:
    page = 1
    while True:
        data = gh_request(
            f"/repos/{urllib.parse.quote(org)}/{urllib.parse.quote(repo)}/pulls",
            {"state": "open", "per_page": "100", "page": str(page), "sort": "updated", "direction": "desc"},
        )
        if not isinstance(data, list) or not data:
            return
        yield from data
        if len(data) < 100:
            return
        page += 1


def parse_github_ts(ts: str) -> datetime:
    if ts.endswith("Z"):
        ts = ts[:-1] + "+00:00"
    return datetime.fromisoformat(ts).astimezone(timezone.utc)


def pr_label_names_lower(pr: dict) -> set[str]:
    labels = pr.get("labels") or []
    return {(x.get("name") or "").lower() for x in labels if isinstance(x, dict)}


def forbidden_label_display_names(pr: dict, forbidden_lower: set[str]) -> list[str]:
    out: list[str] = []
    for lb in pr.get("labels") or []:
        if not isinstance(lb, dict):
            continue
        name = lb.get("name") or ""
        if name.lower() in forbidden_lower:
            out.append(name)
    return sorted(out, key=str.lower)


def days_since(older: datetime, newer: datetime) -> int:
    return int((newer - older).total_seconds() // 86400)


@dataclass
class AttentionPR:
    org: str
    repo: str
    number: int
    title: str
    html_url: str
    author: str
    base_branch: str
    age_days: int
    inactive_days: int
    missing_labels: list[str] = field(default_factory=list)
    forbidden_labels: list[str] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)

    @property
    def repo_full(self) -> str:
        return f"{self.org}/{self.repo}"


def pr_matches_filters(pr: dict, author_allowlist: set[str]) -> bool:
    if pr.get("draft"):
        return False
    login = (pr.get("user") or {}).get("login") or ""
    if not author_allowlist or login.lower() not in author_allowlist:
        return False
    labels = pr_label_names_lower(pr)
    if labels & EXCLUDE_LABELS:
        return False
    return True


def pr_attention_row(pr: dict, org: str, repo: str) -> AttentionPR | None:
    """Return a row only when this PR needs attention (same rules as before)."""
    reasons: list[str] = []
    labels = pr_label_names_lower(pr)
    missing: list[str] = []
    if REQUIRED_LABELS and not REQUIRED_LABELS.issubset(labels):
        missing = sorted(REQUIRED_LABELS - labels)
        reasons.append(f"missing required label(s): {', '.join(missing)}")
    forbidden = forbidden_label_display_names(pr, FORBIDDEN_LABELS)
    if forbidden:
        reasons.append(f"has forbidden label(s): {', '.join(forbidden)}")
    updated = parse_github_ts(pr["updated_at"])
    created = parse_github_ts(pr["created_at"])
    now = datetime.now(timezone.utc)
    stale_cut = now - timedelta(days=STALE_DAYS)
    if updated <= stale_cut:
        reasons.append(f"no activity for >= {STALE_DAYS} days (updated_at)")
    if created <= stale_cut:
        reasons.append(f"open for >= {STALE_DAYS} days (created_at)")
    if not reasons:
        return None
    base_branch = str((pr.get("base") or {}).get("ref") or "")
    return AttentionPR(
        org=org,
        repo=repo,
        number=int(pr["number"]),
        title=str(pr.get("title") or ""),
        html_url=str(pr.get("html_url") or ""),
        author=str((pr.get("user") or {}).get("login") or ""),
        base_branch=base_branch,
        age_days=days_since(created, now),
        inactive_days=days_since(updated, now),
        missing_labels=missing,
        forbidden_labels=forbidden,
        reasons=reasons,
    )


# -----------------------------------------------------------------------------
# Slack Block Kit (aligned with internal/slack/slack.go)
# -----------------------------------------------------------------------------


def slack_escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def format_label_list(labels: list[str]) -> str:
    parts = ["`" + lb.replace("`", "'") + "`" for lb in labels]
    return ", ".join(parts)


def _label_mode_line() -> str:
    if REQUIRED_LABELS:
        joined = ", ".join(sorted(REQUIRED_LABELS))
        return f"Label rules: *fixed list* · {joined}"
    if FORBIDDEN_LABELS:
        joined = ", ".join(sorted(FORBIDDEN_LABELS))
        return f"Label rules: *forbidden set* · {joined}"
    return "Label rules: *none* (no REQUIRED_LABELS / FORBIDDEN_LABELS)"


def _fallback_summary(open_count: int, attention: int, fetched_iso: str) -> str:
    return (
        f"PR dashboard · {open_count} open · {attention} need attention · updated {fetched_iso}"
    )


def _plain_header(text: str) -> dict[str, Any]:
    return {"type": "header", "text": {"type": "plain_text", "text": text, "emoji": True}}


def _context_line(mrkdwn: str) -> dict[str, Any]:
    return {"type": "context", "elements": [{"type": "mrkdwn", "text": mrkdwn}]}


def _section_mrkdwn(text: str) -> dict[str, Any]:
    return {"type": "section", "text": {"type": "mrkdwn", "text": text}}


def _section_fields(left: str, right: str) -> dict[str, Any]:
    return {
        "type": "section",
        "fields": [
            {"type": "mrkdwn", "text": left},
            {"type": "mrkdwn", "text": right},
        ],
    }


def _divider() -> dict[str, Any]:
    return {"type": "divider"}


def _chunk_section_blocks(blocks: list[dict[str, Any]], text: str) -> None:
    text = text.strip()
    if not text:
        return
    while text:
        chunk = text
        if len(chunk) > CHUNK_MAX_LEN:
            chunk = text[:CHUNK_MAX_LEN]
            cut = chunk.rfind("\n")
            if cut > CHUNK_MAX_LEN // 2:
                chunk = text[:cut]
        if not chunk:
            chunk = text[: min(len(text), CHUNK_MAX_LEN)]
        blocks.append(_section_mrkdwn(chunk))
        text = text[len(chunk) :].lstrip("\n")


def build_slack_payload(
    *,
    fetched_at: datetime,
    open_pr_count: int,
    attention: list[AttentionPR],
    fetch_errors: list[str],
) -> dict[str, Any]:
    """Build the same JSON shape as hubhelper's slack.webhookPayload."""
    att_n = len(attention)
    blocks: list[dict[str, Any]] = [
        _plain_header("Pull request dashboard"),
        _context_line(
            f":clock3: Data from *{fetched_at.strftime('%Y-%m-%d %H:%M')} UTC* · {_label_mode_line()}"
        ),
        _section_fields(
            f"*Open PRs*\n_{open_pr_count}_ after filters",
            f"*Need attention*\n_{att_n}_",
        ),
    ]
    if fetch_errors:
        blocks.append(_divider())
        err_lines = ["*:warning: Errors*"]
        for e in fetch_errors:
            safe = e.replace("`", "'")
            err_lines.append(f"• `{safe}`")
        blocks.append(_section_mrkdwn("\n".join(err_lines)))
    blocks.append(_divider())
    if not attention:
        blocks.append(_section_mrkdwn("✅ *All clear* — no PRs need attention right now."))
    else:
        shown_n = min(len(attention), MAX_PRS_IN_MESSAGE)
        blocks.append(
            _section_mrkdwn(
                f"*PRs needing attention* — showing _{shown_n}_ of _{len(attention)}_"
            )
        )
        pr_lines: list[str] = []
        shown = 0
        for p in attention:
            if shown >= MAX_PRS_IN_MESSAGE:
                rest = len(attention) - shown
                pr_lines.append(f"\n_…and {rest} more not listed._\n")
                break
            shown += 1
            title = slack_escape(p.title)
            if len(title) > 120:
                title = title[:117] + "…"
            link_text = f"{p.repo_full}#{p.number} — {title.replace('|', '·')}"
            pr_lines.append(f"*{shown}.* <{p.html_url}|{slack_escape(link_text)}>")
            base = p.base_branch or "—"
            line2 = (
                f"   `{slack_escape(p.author)}` · base `{slack_escape(base)}` · "
                f"open *{p.age_days}d* · idle *{p.inactive_days}d*"
            )
            if p.missing_labels:
                line2 += f" · *Missing:* {format_label_list(p.missing_labels)}"
            if p.forbidden_labels:
                line2 += f"  · *Should not have:* {format_label_list(p.forbidden_labels)}"
            pr_lines.append(line2)
            pr_lines.append("")
        body = "\n".join(pr_lines).rstrip()
        _chunk_section_blocks(blocks, body)
    return {
        "text": _fallback_summary(open_pr_count, att_n, fetched_at.astimezone(timezone.utc).isoformat()),
        "blocks": blocks,
    }


def slack_post_payload(payload: dict[str, Any]) -> None:
    webhook = SLACK_WEBHOOK_URL
    if not webhook:
        sys.stderr.write("SLACK_WEBHOOK_URL is not set\n")
        sys.exit(1)
    body = json.dumps(payload).encode()
    req = urllib.request.Request(
        webhook,
        data=body,
        headers={"Content-Type": "application/json", "User-Agent": "edge-tooling-pr-notifier"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            _ = resp.read()
    except urllib.error.HTTPError as e:
        sys.stderr.write(f"Slack HTTP error {e.code}: {e.read().decode(errors='replace')}\n")
        raise


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    owners_path = Path(_env("OWNERS_FILE", str(repo_root / "OWNERS")))
    aliases_path = Path(_env("OWNERS_ALIASES_FILE", str(repo_root / "OWNERS_ALIASES")))
    try:
        author_allowlist = load_github_logins_from_owners_files(owners_path, aliases_path)
    except OSError as e:
        sys.stderr.write(f"{e}\n")
        return 1
    if not author_allowlist:
        sys.stderr.write(
            "No GitHub logins after expanding OWNERS with OWNERS_ALIASES "
            f"(owners={owners_path}, aliases={aliases_path})\n"
        )
        return 1
    fetched_at = datetime.now(timezone.utc)
    open_count = 0
    items: list[AttentionPR] = []
    for org, repo in REPOS:
        for pr in iter_pulls(org, repo):
            if not isinstance(pr, dict):
                continue
            if not pr_matches_filters(pr, author_allowlist):
                continue
            open_count += 1
            row = pr_attention_row(pr, org, repo)
            if row:
                items.append(row)

    fetch_errors: list[str] = []

    if not items:
        print(f"No PRs need attention across {len(REPOS)} repo(s) ({open_count} open after filters).")
    else:
        print(f"{len(items)} open PR(s) need attention (of {open_count} after filters).")

    if SLACK_WEBHOOK_URL:
        payload = build_slack_payload(
            fetched_at=fetched_at,
            open_pr_count=open_count,
            attention=items,
            fetch_errors=fetch_errors,
        )
        slack_post_payload(payload)
        print("Slack notification sent.")
    elif items:
        lines = [
            f"{len(items)} open PR(s) need attention (stale activity, age, or label rules).",
            f"Lookback: {STALE_DAYS} day(s); repos: {', '.join(f'{o}/{r}' for o, r in REPOS)}",
            "",
        ]
        for it in items:
            lines.append(f"- {it.repo_full}#{it.number} by {it.author}")
            lines.append(f"  {it.html_url}")
            for r in it.reasons:
                lines.append(f"  - {r}")
            lines.append(f"  title: {it.title}")
            lines.append("")
        print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
