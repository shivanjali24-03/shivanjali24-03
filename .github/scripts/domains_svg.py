"""Render the animated 'Industries I build for' card grid (assets/domains.svg)."""
import sys

CARDS = [
    ("Healthcare", "#22c55e", "HIPAA", "Patient portals, clinic &amp;", "scheduling apps, secure PHI", "M-14 -4h8v-8h12v8h8v12h-8v8h-12v-8h-8z"),
    ("CRM", "#00e5ff", None, "Leads, contacts, sales", "pipelines &amp; dashboards", "M-14 10a14 9 0 0 1 28 0M0 -14a7 7 0 1 1 0 .1"),
    ("ERP", "#a855f7", None, "Inventory, orders, HR,", "finance &amp; multi-module apps", "M-14 14v-14l9 -6v6l9 -6v6l10 -6v20z"),
    ("Billing &amp; Invoicing", "#ff2bd6", None, "Invoices, subscriptions,", "payments, tax &amp; receipts", "M-11 -15h22v30l-5.5 -4l-5.5 4l-5.5 -4l-5.5 4zM-6 -7h12M-6 -1h12M-6 5h8"),
    ("Custom Development", "#facc15", None, "Tailor-made software,", "built from scratch to spec", "M-6 -10l-9 10l9 10M6 -10l9 10l-9 10M3 -14l-6 28"),
    ("Admin Portals", "#38bdf8", None, "Role-based portals,", "reports &amp; analytics", "M-15 -13h30v26h-30zM-15 -5h30M-7 -5v18"),
]

W, H = 1200, 400
COLS, CW, CH, GX, GY, X0, Y0 = 3, 340, 130, 30, 26, 70, 92


def render():
    parts = []
    for i, (name, col, tag, l1, l2, icon) in enumerate(CARDS):
        r, c = divmod(i, COLS)
        x, y = X0 + c * (CW + GX), Y0 + r * (CH + GY)
        d = 0.12 * i
        tag_svg = ""
        if tag:
            tag_svg = (f'<rect x="{x + CW - 92}" y="{y + 18}" width="74" height="24" rx="12" fill="{col}" fill-opacity=".18" stroke="{col}" class="pulse"/>'
                       f'<text x="{x + CW - 55}" y="{y + 35}" text-anchor="middle" font-size="12" font-weight="800" fill="{col}" letter-spacing="1">{tag}</text>')
        parts.append(f'''
    <g class="card" style="animation-delay:{d:.2f}s">
      <rect x="{x}" y="{y}" width="{CW}" height="{CH}" rx="18" fill="{col}" fill-opacity=".06" stroke="{col}" stroke-opacity=".45"/>
      <rect x="{x}" y="{y}" width="5" height="{CH}" rx="2.5" fill="{col}"/>
      <circle cx="{x + 52}" cy="{y + 50}" r="27" fill="{col}" fill-opacity=".12" stroke="{col}" stroke-opacity=".5"/>
      <path transform="translate({x + 52} {y + 50})" d="{icon}" fill="none" stroke="{col}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>
      <text x="{x + 94}" y="{y + 57}" font-size="21" font-weight="800" fill="#f5f3ff">{name}</text>
      {tag_svg}
      <text x="{x + 28}" y="{y + 100}" font-size="14" fill="#c4b5fd">{l1}</text>
      <text x="{x + 28}" y="{y + 119}" font-size="14" fill="#c4b5fd">{l2}</text>
    </g>''')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="ui-sans-serif, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#05010f"/><stop offset="1" stop-color="#0b0726"/></linearGradient>
    <linearGradient id="edge" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#00f0ff"/><stop offset=".5" stop-color="#a855f7"/><stop offset="1" stop-color="#ff2bd6"/></linearGradient>
    <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" fill="none" stroke="#7c3aed" stroke-opacity=".12"/></pattern>
    <style>
      .card{{animation:rise .8s cubic-bezier(.2,.8,.2,1) both}}
      @keyframes rise{{from{{opacity:.3;transform:translateY(10px)}}to{{opacity:1;transform:translateY(0)}}}}
      .pulse{{animation:pulse 2.2s ease-in-out infinite}}
      @keyframes pulse{{0%,100%{{stroke-opacity:.35}}50%{{stroke-opacity:1}}}}
      .scan{{animation:scan 6s linear infinite}}
      @keyframes scan{{from{{transform:translateX(-200px)}}to{{transform:translateX({W + 200}px)}}}}
    </style>
  </defs>
  <rect width="{W}" height="{H}" rx="22" fill="url(#bg)"/>
  <rect width="{W}" height="{H}" rx="22" fill="url(#grid)"/>
  <rect class="scan" x="0" y="0" width="140" height="{H}" fill="url(#edge)" opacity=".05"/>
  <text x="{X0}" y="58" font-family="ui-monospace, Menlo, Consolas, monospace" font-size="15" font-weight="700" fill="#00e5ff" letter-spacing="3">&lt;/&gt; INDUSTRIES I BUILD FOR</text>
  {''.join(parts)}
  <rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="21" fill="none" stroke="url(#edge)" stroke-opacity=".55" stroke-width="2"/>
</svg>
'''


if __name__ == "__main__":
    open(sys.argv[1], "w").write(render())
    print("wrote", sys.argv[1])
