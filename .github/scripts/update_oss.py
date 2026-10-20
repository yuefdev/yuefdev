"""Refresh the profile's accepted OSS contributions using public GitHub PRs."""

from datetime import datetime, timezone
from hashlib import sha256
from html import escape
import json
import os
from textwrap import shorten
from urllib.request import Request, urlopen

from update_profile import API, PALETTES, ROOT, USER, txt

QUERY = """
query($login: String!, $cursor: String) {
  user(login: $login) {
    pullRequests(first: 100, after: $cursor, states: MERGED,
                 orderBy: {field: CREATED_AT, direction: DESC}) {
      totalCount
      pageInfo { endCursor hasNextPage }
      nodes {
        number title url mergedAt
        repository {
          nameWithOwner url isPrivate stargazerCount
          owner { login }
          primaryLanguage { name }
        }
      }
    }
  }
}
"""


def fetch_page(cursor):
    request = Request(
        API + "/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": USER, "cursor": cursor}}).encode(),
        headers={"Authorization": "Bearer " + os.environ["GH_TOKEN"],
                 "User-Agent": "yuefdev-profile", "Content-Type": "application/json"},
    )
    with urlopen(request, timeout=35) as response:
        result = json.load(response)
    if result.get("errors"):
        raise ValueError("GitHub could not return complete PR data: " + str(result["errors"]))
    return result["data"]["user"]["pullRequests"]


def collect():
    nodes, cursor, expected = [], None, None
    while True:
        page = fetch_page(cursor)
        if expected is None:
            expected = page["totalCount"]
        if page["totalCount"] != expected:
            raise ValueError("GitHub PR list changed during pagination; keeping the previous snapshot")
        nodes.extend(page["nodes"])
        if not page["pageInfo"]["hasNextPage"]:
            break
        next_cursor = page["pageInfo"]["endCursor"]
        if not next_cursor or next_cursor == cursor:
            raise ValueError("GitHub returned an incomplete pagination cursor")
        cursor = next_cursor
    if len(nodes) != expected or len({node["url"] for node in nodes}) != expected:
        raise ValueError("GitHub returned incomplete PR data; keeping the previous snapshot")
    return summarise(nodes, datetime.now(timezone.utc).date().isoformat())


def summarise(nodes, updated):
    prs, repositories = [], {}
    for node in sorted(nodes, key=lambda n: n["mergedAt"], reverse=True):
        repo = node["repository"]
        if repo["isPrivate"]:
            continue
        pr = {"repository": repo["nameWithOwner"], "number": node["number"],
              "title": node["title"], "url": node["url"], "merged_at": node["mergedAt"]}
        prs.append(pr)
        if repo["owner"]["login"].casefold() == USER.casefold():
            continue
        name = repo["nameWithOwner"]
        if name not in repositories:
            repositories[name] = {
                "name": name, "url": repo["url"], "stars": repo["stargazerCount"],
                "language": (repo["primaryLanguage"] or {}).get("name", ""),
                "merged": 0, "latest": pr,
            }
        repositories[name]["merged"] += 1
    repos = sorted(repositories.values(), key=lambda r: (-r["stars"], r["name"].casefold()))
    return {"username": USER, "updated": updated,
            "scope": "All-time public merged PRs authored by yuefdev. Upstream excludes repositories owned by yuefdev. Featured projects are ordered by GitHub stars, not a measure of contribution size.",
            "total_merged": len(prs), "upstream_merged": sum(r["merged"] for r in repos),
            "upstream_repositories": len(repos), "repositories": repos, "pull_requests": prs}


def chart(data, theme, mobile=False):
    p = PALETTES[theme]
    w, h = (640, 1284) if mobile else (1200, 640)
    featured = data["repositories"][:6]
    names = ", ".join(r["name"] for r in featured)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="oss-title oss-desc">',
        '<title id="oss-title">Contributing upstream.</title>',
        f'<desc id="oss-desc">{data["upstream_merged"]} accepted upstream PRs across {data["upstream_repositories"]} external projects; {data["total_merged"]} total public merged PRs including own repositories. Featured: {escape(names)}. Updated {data["updated"]}.</desc>',
        f'<rect width="{w}" height="{h}" rx="24" fill="{p["bg"]}"/>',
        '<g font-family="Segoe UI, Arial, sans-serif">',
        txt(36, 49, "ENGINEERING IN THE OPEN", 14, p["accent"], 700, letter_spacing="1.6"),
        txt(36, 96, "Contributing upstream.", 38, p["text"], 700),
        txt(36, 128, "Accepted changes. Established projects.", 18, p["muted"]),
        txt(36 if mobile else 1164, 157 if mobile else 48, "UPDATED " + data["updated"], 13,
            p["muted"], text_anchor="start" if mobile else "end"),
    ]
    metrics = [(data["upstream_merged"], "Upstream merges"),
               (data["upstream_repositories"], "External projects"),
               (data["total_merged"], "Total merged PRs")]
    gap, width, top = (16, 178.67, 184) if mobile else (16, 365.33, 156)
    for i, (value, label) in enumerate(metrics):
        x = round(36 + i * (width + gap), 2)
        parts += [f'<rect x="{x}" y="{top}" width="{width}" height="106" rx="14" fill="{p["panel"]}" stroke="{p["line"]}"/>',
                  txt(x + 18, top + 49, f"{value:,}", 42, p["accent"] if i == 0 else p["text"], 700),
                  txt(x + 18, top + 80, label, 14, p["muted"])]
    parts.append(txt(36, 341 if mobile else 293, "FEATURED PROJECTS / BY GITHUB STARS", 13,
                     p["muted"], 600, letter_spacing="1"))
    for i, repo in enumerate(featured):
        x = 36 if mobile else round(36 + (i % 3) * 381.33, 2)
        y = 366 + i * 144 if mobile else 313 + (i // 3) * 138
        width = 568 if mobile else 365.33
        star_count = f'{repo["stars"] / 1000:.1f}k' if repo["stars"] >= 1000 else str(repo["stars"])
        language = " · " + repo["language"] if repo["language"] else ""
        accepted = f'{repo["merged"]} merged PR' + ("s" if repo["merged"] != 1 else "") + language
        parts += [f'<rect x="{x}" y="{y}" width="{width}" height="128" rx="14" fill="{p["panel"]}" stroke="{p["line"]}"/>',
                  f'<path d="M{x + 18} {y + 24}V{y + 43}M{x + 18} {y + 33}Q{x + 31} {y + 33} {x + 31} {y + 21}" fill="none" stroke="{p["accent"]}" stroke-width="2"/>']
        for cx, cy in [(x + 18, y + 21), (x + 31, y + 18), (x + 18, y + 46)]:
            parts.append(f'<circle cx="{cx}" cy="{cy}" r="3" fill="{p["panel"]}" stroke="{p["accent"]}" stroke-width="2"/>')
        parts += [txt(x + 47, y + 36, repo["name"], 22 if mobile else 18, p["text"], 600),
                  txt(x + 18, y + 72, shorten(repo["latest"]["title"], width=67 if mobile else 43, placeholder="…"),
                      16 if mobile else 14, p["muted"]),
                  txt(x + 18, y + 105, accepted, 13, p["accent"]),
                  txt(x + width - 18, y + 105, "★ " + star_count, 13, p["muted"], text_anchor="end")]
    if not featured:
        parts.append(txt(36, 390, "No accepted upstream PRs yet.", 18, p["muted"]))
    parts += [txt(36, h - 30, "PUBLIC PRs · ALL TIME · OWN REPOS EXCLUDED FROM UPSTREAM", 11 if mobile else 12, p["muted"]),
              "</g></svg>"]
    return "\n".join(parts) + "\n"


def markdown(value):
    return escape(value, quote=False).replace("\\", "\\\\").replace("|", "\\|").replace("[", "\\[").replace("]", "\\]").replace("\n", " ").replace("\r", " ")


def readme_block(data, revision, language):
    base = f"https://raw.githubusercontent.com/{USER}/{USER}/main/assets/generated/oss"
    alt = f'{data["upstream_merged"]} merged upstream PRs across {data["upstream_repositories"]} external projects; {data["total_merged"]} total public merged PRs.'
    picture = f'''<picture>
  <source media="(max-width: 600px) and (prefers-color-scheme: dark)" srcset="{base}-dark-mobile.svg?v={revision}">
  <source media="(max-width: 600px)" srcset="{base}-light-mobile.svg?v={revision}">
  <source media="(prefers-color-scheme: dark)" srcset="{base}-dark.svg?v={revision}">
  <img src="{base}-light.svg?v={revision}" alt="{alt}" width="1200">
</picture>'''
    links = " · ".join(f'[{r["name"]}]({r["latest"]["url"]})' for r in data["repositories"][:6])
    if language == "tr":
        note = "GitHub Actions ile saatte bir yenilenir. Upstream sayıları bana ait depoları içermez; tüm zamanların herkese açık, birleştirilmiş PR'ları sayılır."
        details = "Katkılar, son birleştirmeler ve veri kaynağı"
    else:
        note = "Refreshed hourly by GitHub Actions. Upstream excludes my own repositories; counts cover all-time public merged PRs."
        details = "Accepted changes, latest merges and verification"
    return f'{picture}\n\n{links}\n\n<sub>{note}</sub>\n\n[{details}](./OPEN_SOURCE.md)'


def details_block(data):
    parts = [f'## Accepted upstream · {data["updated"]}', "",
             f'**{data["upstream_merged"]} merged PRs across {data["upstream_repositories"]} external projects**, out of **{data["total_merged"]} total public merged PRs** including my own repositories.', "",
             "## Featured accepted contributions", "",
             "Projects are ordered by GitHub stars. Each link below is an actual merged PR; stars describe the project, not the size of my contribution.", "",
             "| Project | Stars | Merged PRs | Latest accepted change |", "| --- | ---: | ---: | --- |"]
    for repo in data["repositories"][:6]:
        pr = repo["latest"]
        parts.append(f'| [{repo["name"]}]({repo["url"]}) | {repo["stars"]:,} | {repo["merged"]} | [{markdown(pr["title"])} (#{pr["number"]})]({pr["url"]}) |')
    external = {r["name"] for r in data["repositories"]}
    parts += ["", "## Latest upstream merges", ""]
    for pr in [pr for pr in data["pull_requests"] if pr["repository"] in external][:5]:
        parts.append(f'- **{pr["merged_at"][:10]}** · [{pr["repository"]} #{pr["number"]}]({pr["url"]}) — {markdown(pr["title"])}')
    return "\n".join(parts)


def replace_block(text, content):
    start, end = "<!-- OSS:START -->", "<!-- OSS:END -->"
    if text.count(start) != 1 or text.count(end) != 1 or text.index(start) > text.index(end):
        raise ValueError("Expected exactly one OSS marker pair; keeping the existing document")
    before, _, rest = text.partition(start)
    _, _, after = rest.partition(end)
    return before + start + "\n" + content + "\n" + end + after


def main():
    data = collect()
    payload = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    revision = sha256(payload.encode()).hexdigest()[:12]
    folder = ROOT / "assets" / "generated"
    outputs = {folder / "oss-data.json": payload}
    for theme in PALETTES:
        for mobile in (False, True):
            outputs[folder / f'oss-{theme}{"-mobile" if mobile else ""}.svg'] = chart(data, theme, mobile)
    for name, language in [("README.md", "en"), ("README.tr.md", "tr")]:
        path = ROOT / name
        outputs[path] = replace_block(path.read_text(encoding="utf-8"), readme_block(data, revision, language))
    path = ROOT / "OPEN_SOURCE.md"
    outputs[path] = replace_block(path.read_text(encoding="utf-8"), details_block(data))
    # Prepare every output before replacing the last successful snapshot.
    for path, content in outputs.items():
        temporary = path.with_name(path.name + ".tmp")
        temporary.write_text(content, encoding="utf-8")
        temporary.replace(path)
    print(json.dumps({key: data[key] for key in ("updated", "total_merged", "upstream_merged", "upstream_repositories")}))


if __name__ == "__main__":
    main()
