#!/usr/bin/env python3
"""Generate static SVG cards for the GitHub profile README."""

from __future__ import annotations

import datetime as dt
import html
import json
import os
import pathlib
import re
import urllib.error
import urllib.request


ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "assets" / "stats"
README = ROOT / "README.md"
USERNAME = os.environ.get("PROFILE_USERNAME", "stevengonsalvez")
GITHUB_TOKEN = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")


QUERY = """
query($login:String!) {
  user(login:$login) {
    followers { totalCount }
    repositories(first: 1, ownerAffiliations: OWNER) { totalCount }
    contributionsCollection {
      contributionCalendar { totalContributions }
      totalCommitContributions
      totalIssueContributions
      totalPullRequestContributions
      totalPullRequestReviewContributions
      restrictedContributionsCount
    }
  }
}
"""


def graphql(query: str, variables: dict[str, str]) -> dict:
    if not GITHUB_TOKEN:
        raise SystemExit("GH_TOKEN or GITHUB_TOKEN is required")

    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": variables}).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Content-Type": "application/json",
            "User-Agent": "stevengonsalvez-profile-stats",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"GitHub API failed: {exc.code} {body}") from exc

    if payload.get("errors"):
        raise SystemExit(json.dumps(payload["errors"], indent=2))
    return payload["data"]["user"]


def fmt(n: int) -> str:
    return f"{n:,}"


def svg_card(title: str, rows: list[tuple[str, str]], width: int = 420) -> str:
    height = 78 + len(rows) * 34
    now = dt.datetime.now(dt.UTC).strftime("%Y-%m-%d")
    row_markup = []
    y = 72
    for label, value in rows:
        row_markup.append(
            f'<text x="30" y="{y}" class="label">{html.escape(label)}</text>'
            f'<text x="{width - 30}" y="{y}" class="value" text-anchor="end">'
            f"{html.escape(value)}</text>"
        )
        y += 34

    return f"""<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="title desc">
  <title id="title">{html.escape(title)}</title>
  <desc id="desc">Generated GitHub profile statistics for {USERNAME}</desc>
  <style>
    .bg {{ fill: #0b1020; }}
    .panel {{ fill: #121a2f; stroke: #6ee7b7; stroke-width: 1.2; }}
    .title {{ fill: #f8fafc; font: 700 18px ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }}
    .label {{ fill: #a7f3d0; font: 500 14px ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }}
    .value {{ fill: #facc15; font: 700 15px ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }}
    .stamp {{ fill: #94a3b8; font: 500 11px ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }}
  </style>
  <rect class="bg" width="{width}" height="{height}" rx="8"/>
  <rect class="panel" x="10" y="10" width="{width - 20}" height="{height - 20}" rx="6"/>
  <circle cx="30" cy="31" r="5" fill="#ef4444"/>
  <circle cx="48" cy="31" r="5" fill="#f59e0b"/>
  <circle cx="66" cy="31" r="5" fill="#22c55e"/>
  <text x="30" y="55" class="title">{html.escape(title)}</text>
  {''.join(row_markup)}
  <text x="{width - 30}" y="{height - 24}" class="stamp" text-anchor="end">updated {now}</text>
</svg>
"""


def bar_card(rows: list[tuple[str, int]], width: int = 420) -> str:
    height = 90 + len(rows) * 38
    max_value = max(value for _, value in rows) or 1
    bars = []
    y = 78
    for label, value in rows:
        bar_width = max(8, int((value / max_value) * (width - 190)))
        bars.append(
            f'<text x="30" y="{y}" class="label">{html.escape(label)}</text>'
            f'<rect x="150" y="{y - 14}" width="{bar_width}" height="14" rx="3" fill="#38bdf8"/>'
            f'<text x="{width - 30}" y="{y}" class="value" text-anchor="end">{fmt(value)}</text>'
        )
        y += 38

    return f"""<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="title desc">
  <title id="title">Activity Breakdown</title>
  <desc id="desc">Contribution activity breakdown for {USERNAME}</desc>
  <style>
    .bg {{ fill: #0b1020; }}
    .panel {{ fill: #121a2f; stroke: #facc15; stroke-width: 1.2; }}
    .title {{ fill: #f8fafc; font: 700 18px ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }}
    .label {{ fill: #a7f3d0; font: 500 13px ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }}
    .value {{ fill: #facc15; font: 700 13px ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }}
  </style>
  <rect class="bg" width="{width}" height="{height}" rx="8"/>
  <rect class="panel" x="10" y="10" width="{width - 20}" height="{height - 20}" rx="6"/>
  <text x="30" y="48" class="title">activity breakdown</text>
  {''.join(bars)}
</svg>
"""


def retro_counter() -> str:
    return """<svg width="760" height="120" viewBox="0 0 760 120" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="title desc">
  <title id="title">Agentic engineering profile banner</title>
  <desc id="desc">Tasteful retro terminal banner for Steven Gonsalvez</desc>
  <style>
    .bg { fill: #09090b; }
    .scan { fill: #111827; }
    .border { stroke: #22c55e; stroke-width: 2; fill: none; }
    .title { fill: #f8fafc; font: 800 28px ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }
    .sub { fill: #a7f3d0; font: 600 15px ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }
    .amber { fill: #facc15; }
  </style>
  <rect class="bg" width="760" height="120" rx="8"/>
  <path class="scan" d="M0 18h760v3H0zM0 54h760v3H0zM0 90h760v3H0z"/>
  <rect class="border" x="8" y="8" width="744" height="104" rx="6"/>
  <text x="32" y="50" class="title">STEVEN GONSALVEZ</text>
  <text x="34" y="82" class="sub">agentic engineering / developer tools / London</text>
  <text x="610" y="48" class="sub amber">ONLINE</text>
  <text x="610" y="78" class="sub">since 2014</text>
</svg>
"""


def update_readme_stats(rows: list[tuple[str, str]]) -> None:
    if not README.exists():
        return

    stats = " / ".join(f"{value} {label}" for label, value in rows)
    replacement = f"<!-- PROFILE-STATS:START -->\n- {stats}\n<!-- PROFILE-STATS:END -->"
    text = README.read_text(encoding="utf-8")
    updated = re.sub(
        r"<!-- PROFILE-STATS:START -->.*?<!-- PROFILE-STATS:END -->",
        replacement,
        text,
        flags=re.S,
    )
    if updated == text and "<!-- PROFILE-STATS:START -->" not in text:
        updated = text.rstrip() + "\n\n" + replacement + "\n"
    README.write_text(updated, encoding="utf-8")


def main() -> None:
    user = graphql(QUERY, {"login": USERNAME})
    contributions = user["contributionsCollection"]
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    summary_rows = [
        ("year contributions", fmt(contributions["contributionCalendar"]["totalContributions"])),
        ("commits", fmt(contributions["totalCommitContributions"])),
        ("pull requests", fmt(contributions["totalPullRequestContributions"])),
        ("private aggregate", fmt(contributions["restrictedContributionsCount"])),
        ("owned repos", fmt(user["repositories"]["totalCount"])),
        ("followers", fmt(user["followers"]["totalCount"])),
    ]
    activity_rows = [
        ("commits", contributions["totalCommitContributions"]),
        ("prs", contributions["totalPullRequestContributions"]),
        ("issues", contributions["totalIssueContributions"]),
        ("reviews", contributions["totalPullRequestReviewContributions"]),
        ("private", contributions["restrictedContributionsCount"]),
    ]

    (OUT_DIR / "contribution-summary.svg").write_text(svg_card("github activity", summary_rows), encoding="utf-8")
    (OUT_DIR / "activity-breakdown.svg").write_text(bar_card(activity_rows), encoding="utf-8")
    (OUT_DIR / "retro-counter.svg").write_text(retro_counter(), encoding="utf-8")
    update_readme_stats(summary_rows)


if __name__ == "__main__":
    main()
