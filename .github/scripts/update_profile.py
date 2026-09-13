"""Generate first-party profile charts from public GitHub data (stdlib only)."""

from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta, timezone
from html import escape
from html.parser import HTMLParser
import json
import math
import os
from pathlib import Path
import re
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[2]
USER = "yuefdev"
API = "https://api.github.com"
PALETTES = {
    "dark": dict(bg="#10151c", panel="#151c25", line="#2a3542", text="#f2f5f0", muted="#a2adba", accent="#c5f277"),
    "light": dict(bg="#f6f8f3", panel="#ffffff", line="#d9e0d2", text="#17211c", muted="#59685c", accent="#427519"),
}
COLORS = ["#a5d95f", "#73b9ef", "#bd9ae8", "#e6ad6b", "#e77f90", "#8d9daf"]


def fetch(url):
    headers = {"User-Agent": "yuefdev-profile", "Accept": "application/vnd.github+json" if url.startswith(API) else "text/html"}
    # The calendar is always fetched anonymously, even when a token is available.
    if url.startswith(API) and os.environ.get("GH_TOKEN"):
        headers["Authorization"] = "Bearer " + os.environ["GH_TOKEN"]
    with urlopen(Request(url, headers=headers), timeout=35) as response:
        return response.read().decode("utf-8")


class Calendar(HTMLParser):
    def __init__(self):
        super().__init__()
        self.cells, self.counts = {}, {}
        self.tip, self.parts = None, []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("data-date") and attrs.get("id"):
            self.cells[attrs["id"]] = attrs["data-date"]
            if "data-count" in attrs:
                self.counts[attrs["id"]] = int(attrs["data-count"])
        if tag == "tool-tip" and attrs.get("for"):
            self.tip, self.parts = attrs["for"], []

    def handle_data(self, data):
        if self.tip:
            self.parts.append(data)

    def handle_endtag(self, tag):
        if tag == "tool-tip" and self.tip:
            match = re.search(r"\b(No|[\d,]+) contributions?\b", " ".join(self.parts), re.I)
            if match:
                value = match.group(1)
                self.counts[self.tip] = 0 if value.lower() == "no" else int(value.replace(",", ""))
            self.tip, self.parts = None, []

    def days(self):
        missing = set(self.cells) - set(self.counts)
        if missing:
            raise ValueError(f"GitHub calendar format changed: {len(missing)} counts missing")
        return {day: self.counts[key] for key, day in self.cells.items()}


def collect():
    today = datetime.now(timezone.utc).date()
    # Six named calendar months, including the current partial month.
    month_index = today.year * 12 + today.month - 1 - 5
    start = date(month_index // 12, month_index % 12 + 1, 1)
    public_days = {}
    for year in range(start.year, today.year + 1):
        parser = Calendar()
        parser.feed(fetch(f"https://github.com/users/{USER}/contributions?from={year}-01-01&to={year}-12-31"))
        public_days.update(parser.days())
    days = []
    cursor = start
    while cursor <= today:
        key = cursor.isoformat()
        if key not in public_days:
            raise ValueError(f"GitHub calendar did not return {key}")
        days.append({"date": key, "count": public_days[key]})
        cursor += timedelta(days=1)

    repos, page = [], 1
    while True:
        batch = json.loads(fetch(f"{API}/users/{USER}/repos?type=owner&per_page=100&page={page}"))
        repos.extend(r for r in batch if not r["fork"] and not r["private"])
        if len(batch) < 100:
            break
        page += 1
    language_repos = sorted((r for r in repos if r.get("language")), key=lambda r: r["name"].lower())
    with ThreadPoolExecutor(max_workers=4) as pool:
        language_results = list(pool.map(lambda r: json.loads(fetch(r["languages_url"])), language_repos))
    languages = Counter()
    for result in language_results:
        languages.update(result)
    if not languages:
        raise ValueError("No language data returned; keeping the previous charts")
    months = Counter()
    for day in days:
        months[day["date"][:7]] += day["count"]
    return {
        "username": USER,
        "updated": today.isoformat(),
        "period_start": start.isoformat(),
        "contribution_source": f"https://github.com/{USER}?tab=overview",
        "contribution_scope": "Counts visible on the public GitHub calendar; current month is partial. These can include anonymized private counts if enabled by the profile owner.",
        "contributions": dict(sorted(months.items())),
        "total_contributions": sum(d["count"] for d in days),
        "active_days": sum(d["count"] > 0 for d in days),
        "language_scope": "GitHub language bytes across owned public, non-fork repositories with detected languages. Includes vendored or generated code counted by GitHub. Not a proficiency score.",
        "language_repositories": [r["full_name"] for r in language_repos],
        "language_bytes": dict(languages.most_common()),
    }


def txt(x, y, value, size=18, color=None, weight=400, **attrs):
    extra = " ".join(f'{k.replace("_", "-")}="{escape(str(v), quote=True)}"' for k, v in attrs.items())
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{weight}" {extra}>{escape(str(value))}</text>'


def chart(data, theme, mobile=False):
    p = PALETTES[theme]
    w, h = (640, 990) if mobile else (1200, 460)
    title = "GitHub, in context."
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc">',
             f'<title id="title">{title}</title>',
             f'<desc id="desc">Public calendar contributions from {data["period_start"]} to {data["updated"]}: {data["total_contributions"]}. Code composition by GitHub language bytes: {escape(json.dumps(data["language_bytes"]))}. Current month is partial. Language bytes are not proficiency.</desc>',
             f'<rect width="{w}" height="{h}" rx="24" fill="{p["bg"]}"/>',
             '<g font-family="Segoe UI, Arial, sans-serif">',
             txt(36, 49, "ACTIVITY / CODE COMPOSITION", 14, p["accent"], 700, letter_spacing="1.6"),
             txt(36, 96, title, 34, p["text"], 700)]
    if not mobile:
        parts.append(txt(1164, 48, "UPDATED " + data["updated"], 13, p["muted"], 400, text_anchor="end"))
    else:
        parts.append(txt(36, 124, "UPDATED " + data["updated"], 14, p["muted"]))

    x, y = 36, 170 if mobile else 145
    plot_w = 568 if mobile else 542
    parts += [txt(x, y, "Visible contributions", 21, p["text"], 600),
              txt(x, y + 31, f'{data["total_contributions"]:,} contributions  /  {data["active_days"]} active days', 16, p["muted"])]
    max_count = max(data["contributions"].values(), default=0)
    scale = max(10, math.ceil(max_count / 10) * 10)
    baseline = y + 202
    for i in range(3):
        yy = baseline - i * 61
        parts.append(f'<path d="M{x + 33} {yy}H{x + plot_w}" stroke="{p["line"]}"/>')
        parts.append(txt(x + 23, yy + 5, round(scale * i / 2), 12, p["muted"], text_anchor="end"))
    step = (plot_w - 50) / 6
    for i, (month, count) in enumerate(data["contributions"].items()):
        bx = x + 46 + i * step
        bh = count / scale * 122
        parts.append(f'<rect x="{bx:.2f}" y="{baseline - max(2, bh):.2f}" width="{step - 22:.2f}" height="{max(2, bh):.2f}" rx="5" fill="{p["accent"]}" opacity="{0.5 if i == 5 else 1}"><title>{month}: {count} contributions</title></rect>')
        parts.append(txt(round(bx + (step - 22) / 2, 2), round(baseline - max(2, bh) - 10, 2), count, 14, p["text"], 600, text_anchor="middle"))
        label = date.fromisoformat(month + "-01").strftime("%b") + ("*" if i == 5 else "")
        parts.append(txt(round(bx + (step - 22) / 2, 2), baseline + 26, label, 14, p["muted"], text_anchor="middle"))
    parts.append(txt(x, baseline + 57, "Public calendar  ·  *Current month so far", 14, p["muted"]))

    if mobile:
        x, y, cw = 36, 543, 568
        parts.append(f'<path d="M36 500H604" stroke="{p["line"]}"/>')
    else:
        x, y, cw = 640, 145, 524
        parts.append(f'<path d="M607 131V412" stroke="{p["line"]}"/>')
    parts += [txt(x, y, "Languages in my public repositories", 21, p["text"], 600),
              txt(x, y + 31, f'{len(data["language_repositories"])} repositories  /  forks excluded', 16, p["muted"])]
    items = list(data["language_bytes"].items())
    shown = items[:5]
    if len(items) > 5:
        shown.append(("Other", sum(value for _, value in items[5:])))
    total = sum(data["language_bytes"].values())
    bx = x
    for i, (name, value) in enumerate(shown):
        bw = cw * value / total
        parts.append(f'<rect x="{bx:.3f}" y="{y + 53}" width="{bw:.3f}" height="17" fill="{COLORS[i]}"><title>{escape(name)}: {value:,} bytes</title></rect>')
        bx += bw
    for i, (name, value) in enumerate(shown):
        yy = y + 107 + i * (41 if mobile else 24)
        parts.append(f'<circle cx="{x + 5}" cy="{yy - 5}" r="5" fill="{COLORS[i]}"/>')
        parts += [txt(x + 22, yy, name, 17 if mobile else 15, p["text"]),
                  txt(x + cw, yy, f"{value / total:.1%}", 17 if mobile else 15, p["muted"], text_anchor="end")]
    note_y = y + (382 if mobile else 259)
    parts.append(txt(x, note_y, "Share of code bytes · not a proficiency score", 14, p["muted"]))
    parts.append("</g></svg>")
    return "\n".join(parts) + "\n"


def main():
    data = collect()
    # Fetch and validate everything before replacing any previously valid file.
    outputs = {"github-data.json": json.dumps(data, indent=2, ensure_ascii=False) + "\n"}
    for theme in PALETTES:
        for mobile in [False, True]:
            outputs[f'github-{theme}{"-mobile" if mobile else ""}.svg'] = chart(data, theme, mobile)
    folder = ROOT / "assets" / "generated"
    folder.mkdir(parents=True, exist_ok=True)
    for name, content in outputs.items():
        temporary = folder / (name + ".tmp")
        temporary.write_text(content, encoding="utf-8")
        temporary.replace(folder / name)
    print(json.dumps({"updated": data["updated"], "contributions": data["total_contributions"], "active_days": data["active_days"], "language_repositories": len(data["language_repositories"])}))


if __name__ == "__main__":
    main()
