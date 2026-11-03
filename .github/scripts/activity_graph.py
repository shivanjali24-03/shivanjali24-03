"""Generate a themed activity graph SVG from the GitHub contribution calendar.

Usage:
  GITHUB_TOKEN=... python activity_graph.py <username> <output.svg>
  python activity_graph.py --demo <output.svg>     # render with sample data
"""
import json
import os
import sys
import urllib.request
from collections import OrderedDict
from datetime import date, timedelta

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}
"""


def fetch_days(login, token):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json",
                 "User-Agent": "profile-activity-graph"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        payload = json.load(r)
    if "errors" in payload:
        raise SystemExit(f"GraphQL error: {payload['errors']}")
    cal = payload["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    return [(date.fromisoformat(d["date"]), d["contributionCount"])
            for w in cal["weeks"] for d in w["contributionDays"]]


def demo_days():
    import random
    random.seed(7)
    start = date.today() - timedelta(days=364)
    return [(start + timedelta(i), random.choice([0, 0, 1, 2, 3, 5, 8]) if i % 3 else 0)
            for i in range(365)]


def stats(days):
    days = sorted(days)
    total = sum(c for _, c in days)
    active = sum(1 for _, c in days if c)
    best = cur = 0
    for _, c in days:
        cur = cur + 1 if c else 0
        best = max(best, cur)
    # current streak: allow today to be empty
    streak = 0
    for i, (_, c) in enumerate(reversed(days)):
        if c:
            streak += 1
        elif i > 0:
            break
    busiest = max(days, key=lambda d: d[1]) if days else (date.today(), 0)
    return total, active, best, streak, busiest


def monthly(days):
    months = OrderedDict()
    end = max(d for d, _ in days)
    y, m = end.year, end.month
    keys = []
    for _ in range(12):
        keys.append((y, m))
        m -= 1
        if m == 0:
            y, m = y - 1, 12
    for k in reversed(keys):
        months[k] = 0
    for d, c in days:
        if (d.year, d.month) in months:
            months[(d.year, d.month)] += c
    return months


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render(days):
    months = monthly(days)
    # keep the cards and the bars on exactly the same 12-month window
    first_y, first_m = next(iter(months))
    days = [(d, c) for d, c in days if (d.year, d.month) >= (first_y, first_m)]
    total, active, best, streak, busiest = stats(days)
    W, H = 1200, 420
    cx0, cy0, cw, ch = 70, 150, 1080, 200  # chart box
    vals = list(months.values())
    vmax = max(vals + [1])
    n = len(vals)
    slot = cw / n
    bw = slot * 0.56
    names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    bars, labels, tops = [], [], []
    for i, ((yy, mm), v) in enumerate(months.items()):
        h = 0 if v == 0 else max(6, v / vmax * (ch - 24))
        x = cx0 + i * slot + (slot - bw) / 2
        y = cy0 + ch - h
        delay = 0.08 * i
        if h:
            bars.append(
                f'<rect class="bar" style="animation-delay:{delay:.2f}s" x="{x:.1f}" y="{y:.1f}" '
                f'width="{bw:.1f}" height="{h:.1f}" rx="7" fill="url(#barg)"/>')
            bars.append(
                f'<text class="val" style="animation-delay:{delay + .4:.2f}s" x="{x + bw / 2:.1f}" '
                f'y="{y - 9:.1f}" text-anchor="middle">{v}</text>')
        else:
            bars.append(f'<rect x="{x:.1f}" y="{cy0 + ch - 3:.1f}" width="{bw:.1f}" height="3" rx="1.5" fill="#2e1065"/>')
        lab = names[mm - 1] + (f" '{str(yy)[2:]}" if mm == 1 or i == 0 else "")
        labels.append(f'<text x="{x + bw / 2:.1f}" y="{cy0 + ch + 26}" text-anchor="middle" class="lab">{lab}</text>')
        tops.append((x + bw / 2, y if h else cy0 + ch - 2))

    line = " ".join(f"{px:.1f},{py:.1f}" for px, py in tops)
    grid = "".join(
        f'<line x1="{cx0}" x2="{cx0 + cw}" y1="{cy0 + ch * f:.1f}" y2="{cy0 + ch * f:.1f}" stroke="#7c3aed" stroke-opacity=".15" stroke-dasharray="4 6"/>'
        for f in (0, .25, .5, .75, 1))

    cards = [
        ("CONTRIBUTIONS", total, "last 12 months"),
        ("ACTIVE DAYS", active, "days with commits"),
        ("LONGEST STREAK", f"{best}d", "in a row"),
        ("BUSIEST DAY", busiest[1], busiest[0].strftime("%b %d, %Y")),
    ]
    card_svg = []
    cwid = 250
    for i, (k, v, sub) in enumerate(cards):
        x = 70 + i * (cwid + 26.7)
        card_svg.append(
            f'<g class="card" style="animation-delay:{.1 * i:.1f}s">'
            f'<rect x="{x:.1f}" y="30" width="{cwid}" height="84" rx="14" fill="#a855f7" fill-opacity=".08" stroke="#a855f7" stroke-opacity=".35"/>'
            f'<text x="{x + 18:.1f}" y="56" class="k">{k}</text>'
            f'<text x="{x + 18:.1f}" y="92" class="v">{esc(v)}</text>'
            f'<text x="{x + cwid - 16:.1f}" y="92" text-anchor="end" class="sub">{esc(sub)}</text></g>')

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#05010f"/><stop offset="1" stop-color="#0b0726"/></linearGradient>
    <linearGradient id="barg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#00e5ff"/><stop offset=".55" stop-color="#a855f7"/><stop offset="1" stop-color="#7c3aed" stop-opacity=".6"/></linearGradient>
    <linearGradient id="edge" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#00f0ff"/><stop offset=".5" stop-color="#a855f7"/><stop offset="1" stop-color="#ff2bd6"/></linearGradient>
    <filter id="glow"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
    <style>
      .k{{font-size:12px;fill:#00e5ff;letter-spacing:2px;font-weight:700}}
      .v{{font-size:30px;fill:#f5f3ff;font-weight:800}}
      .sub{{font-size:12px;fill:#a78bfa}}
      .lab{{font-size:13px;fill:#c4b5fd}}
      .val{{font-size:13px;fill:#f5f3ff;font-weight:700;animation:fade .6s ease-out both}}
      .title{{font-size:14px;fill:#e9d5ff;letter-spacing:3px;font-weight:700}}
      .bar{{transform-box:fill-box;transform-origin:bottom;animation:grow .9s cubic-bezier(.2,.8,.2,1) both}}
      .card{{animation:fade .8s ease-out both}}
      .trend{{stroke-dasharray:2400;stroke-dashoffset:0;animation:draw 2.2s ease-out both}}
      @keyframes grow{{from{{transform:scaleY(.15)}}to{{transform:scaleY(1)}}}}
      @keyframes fade{{from{{opacity:.3}}to{{opacity:1}}}}
      @keyframes draw{{from{{stroke-dashoffset:2400}}to{{stroke-dashoffset:0}}}}
    </style>
  </defs>
  <rect width="{W}" height="{H}" rx="22" fill="url(#bg)"/>
  {''.join(card_svg)}
  <text x="{cx0}" y="{cy0 - 14}" class="title">MONTHLY CONTRIBUTIONS</text>
  {grid}
  {''.join(bars)}
  <polyline class="trend" points="{line}" fill="none" stroke="#ff2bd6" stroke-width="2" stroke-opacity=".7" filter="url(#glow)"/>
  {''.join(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="3.5" fill="#ff2bd6"/>' for px, py in tops)}
  {''.join(labels)}
  <rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="21" fill="none" stroke="url(#edge)" stroke-opacity=".55" stroke-width="2"/>
</svg>
'''


def main():
    if len(sys.argv) == 3 and sys.argv[1] == "--demo":
        days, out = demo_days(), sys.argv[2]
    elif len(sys.argv) == 3:
        token = os.environ.get("GITHUB_TOKEN")
        if not token:
            raise SystemExit("GITHUB_TOKEN is required")
        days, out = fetch_days(sys.argv[1], token), sys.argv[2]
    else:
        raise SystemExit(__doc__)
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    with open(out, "w") as f:
        f.write(render(days))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
