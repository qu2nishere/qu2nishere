"""Fetch live GitHub contribution data and render the medieval stat SVGs.

Generates:
  assets/war-chronicle.svg   - all-time deeds, current / longest streak, this year
  assets/battle-ledger.svg   - contribution grid as a wall of heraldic shields
  assets/battle-activity.svg - last 26 weeks as castle towers + marching army

Env:
  GH_TOKEN  token used for the GraphQL API (GITHUB_TOKEN is enough for public data)
  GH_USER   GitHub login (default: qu2nishere)
"""
import datetime as dt
import json
import os
import urllib.request
from collections import defaultdict

USER = os.environ.get("GH_USER", "qu2nishere")
TOKEN = os.environ.get("GH_TOKEN", "")
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
ASSETS = os.path.join(ROOT, "assets")
SERIF = "Georgia, 'Palatino Linotype', 'Book Antiqua', 'Times New Roman', serif"


# ------------------------------------------------------------------ data
def gql(query, variables):
    if os.environ.get("GH_USE_CLI"):  # local testing through the gh CLI
        import subprocess
        args = ["gh", "api", "graphql", "-f", f"query={query}"]
        for k, v in variables.items():
            args += ["-f", f"{k}={v}"]
        body = json.loads(subprocess.run(args, capture_output=True, text=True, check=True).stdout)
        return body["data"]
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={"Authorization": f"bearer {TOKEN}", "User-Agent": "medieval-chronicle"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        body = json.load(r)
    if body.get("errors"):
        raise SystemExit(f"GraphQL error: {body['errors']}")
    return body["data"]


CAL = """contributionCalendar { totalContributions
  weeks { contributionDays { date contributionCount contributionLevel } } }"""


def fetch():
    created = gql("query($u:String!){user(login:$u){createdAt}}", {"u": USER})["user"]["createdAt"]
    created = dt.datetime.fromisoformat(created.replace("Z", "+00:00"))
    now = dt.datetime.now(dt.timezone.utc)

    days = {}  # date -> count (all time)
    for year in range(created.year, now.year + 1):
        start = max(created, dt.datetime(year, 1, 1, tzinfo=dt.timezone.utc))
        end = min(now, dt.datetime(year, 12, 31, 23, 59, 59, tzinfo=dt.timezone.utc))
        data = gql(
            f"query($u:String!,$f:DateTime!,$t:DateTime!){{user(login:$u){{contributionsCollection(from:$f,to:$t){{{CAL}}}}}}}",
            {"u": USER, "f": start.isoformat(), "t": end.isoformat()},
        )
        for w in data["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]:
            for d in w["contributionDays"]:
                days[d["date"]] = d["contributionCount"]

    # last-year calendar (exactly what the GitHub profile grid shows)
    data = gql(f"query($u:String!){{user(login:$u){{contributionsCollection{{{CAL}}}}}}}", {"u": USER})
    cal = data["user"]["contributionsCollection"]["contributionCalendar"]
    return created, days, cal


def streaks(days, today):
    dates = sorted(d for d in days if d <= today.isoformat())
    longest = run = 0
    best_range = (None, None)
    run_start = None
    prev = None
    for d in dates:
        if days[d] > 0:
            dd = dt.date.fromisoformat(d)
            if prev and (dd - prev).days == 1 and run:
                run += 1
            else:
                run, run_start = 1, dd
            prev = dd
            if run > longest:
                longest, best_range = run, (run_start, dd)
        else:
            run = 0
            prev = None

    # current streak: today may still be empty without breaking it
    cur, cur_end = 0, None
    day = today
    if days.get(day.isoformat(), 0) == 0:
        day -= dt.timedelta(days=1)
    while days.get(day.isoformat(), 0) > 0:
        cur += 1
        cur_end = cur_end or day
        day -= dt.timedelta(days=1)
    cur_start = day + dt.timedelta(days=1) if cur else None
    return cur, (cur_start, cur_end), longest, best_range


def fmt_range(a, b):
    if not a:
        return ""
    f = lambda d: d.strftime("%b %d").replace(" 0", " ")
    return f(a) if a == b else f"{f(a)} – {f(b)}"


# ------------------------------------------------------------------ shared svg bits
DEFS = """
    <linearGradient id="gold" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#fff1b8"/><stop offset="45%" stop-color="#e6b84a"/><stop offset="100%" stop-color="#9c6b1c"/>
    </linearGradient>
    <linearGradient id="parch" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#f4e6c2"/><stop offset="60%" stop-color="#e6d09c"/><stop offset="100%" stop-color="#cfb47a"/>
    </linearGradient>
    <pattern id="bricks" width="24" height="12" patternUnits="userSpaceOnUse">
      <rect width="24" height="12" fill="#25242c"/>
      <path d="M0 0.5H24M0 6.5H24M0.5 0V6M12.5 6V12" stroke="#1a1a20" stroke-width="1"/>
    </pattern>
    <pattern id="bricks-lit" width="24" height="12" patternUnits="userSpaceOnUse">
      <rect width="24" height="12" fill="#3a3a46"/>
      <path d="M0 0.5H24M0 6.5H24M0.5 0V6M12.5 6V12" stroke="#262631" stroke-width="1"/>
    </pattern>
    <filter id="drop" x="-10%" y="-10%" width="120%" height="130%">
      <feDropShadow dx="0" dy="6" stdDeviation="6" flood-color="#000" flood-opacity="0.6"/>
    </filter>
    <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="2.5" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
"""

STYLE = f"""
    .serif {{ font-family: {SERIF}; }}
    .flicker {{ animation: flick 1.8s ease-in-out infinite; }}
    .flicker2 {{ animation: flick 2.3s ease-in-out infinite 0.4s; }}
    @keyframes flick {{ 0%,100% {{ opacity: 1; }} 30% {{ opacity: 0.7; }} 55% {{ opacity: 0.95; }} 75% {{ opacity: 0.8; }} }}
    .pulse {{ animation: pulse 2s ease-in-out infinite; }}
    @keyframes pulse {{ 0%,100% {{ opacity: 1; }} 50% {{ opacity: 0.3; }} }}
"""

ARMY_DEFS = """
    <g id="soldier"><g>
      <animateTransform attributeName="transform" type="translate" values="0 0;0 -1.6;0 0" dur="0.45s" repeatCount="indefinite"/>
      <rect x="-3" y="-18" width="6" height="18" rx="1.5" fill="#24242c"><animateTransform attributeName="transform" type="rotate" values="-22 0 -18;22 0 -18;-22 0 -18" dur="0.9s" repeatCount="indefinite"/></rect>
      <rect x="-3" y="-18" width="6" height="18" rx="1.5" fill="#33333d"><animateTransform attributeName="transform" type="rotate" values="22 0 -18;-22 0 -18;22 0 -18" dur="0.9s" repeatCount="indefinite"/></rect>
      <line x1="11" y1="2" x2="11" y2="-64" stroke="#8a6a3a" stroke-width="2"/>
      <path d="M11 -73L7.5 -63H14.5Z" fill="#d9dde4"/>
      <path d="M-8 -38H8L10 -16H-10Z" fill="#8b1a1a"/>
      <rect x="-1.5" y="-36" width="3" height="18" fill="#e6b84a"/><rect x="-7" y="-29" width="14" height="3" fill="#e6b84a"/>
      <rect x="-2" y="-37" width="14" height="5" rx="2.5" fill="#7d828c"/>
      <rect x="-6.5" y="-51" width="13" height="13" rx="3" fill="#aab0ba"/><rect x="0" y="-46" width="6.5" height="2" fill="#15151a"/>
      <path d="M-2 -51Q-8 -60 -14 -55Q-8 -54 -6 -50Z" fill="#c62828"/>
      <path d="M-12 -35H1V-25Q1 -17 -5.5 -13Q-12 -17 -12 -25Z" fill="#c9a227" stroke="#5a4510" stroke-width="1"/>
      <path d="M-12 -30L-5.5 -24L1 -30" stroke="#8b1a1a" stroke-width="2.5" fill="none"/>
    </g></g>
    <g id="archer"><g>
      <animateTransform attributeName="transform" type="translate" values="0 0;0 -1.6;0 0" dur="0.45s" repeatCount="indefinite"/>
      <rect x="-3" y="-18" width="6" height="18" rx="1.5" fill="#2a2418"><animateTransform attributeName="transform" type="rotate" values="-22 0 -18;22 0 -18;-22 0 -18" dur="0.9s" repeatCount="indefinite"/></rect>
      <rect x="-3" y="-18" width="6" height="18" rx="1.5" fill="#3a3222"><animateTransform attributeName="transform" type="rotate" values="22 0 -18;-22 0 -18;22 0 -18" dur="0.9s" repeatCount="indefinite"/></rect>
      <path d="M-9 -40L-4 -42L-2 -20L-7 -18Z" fill="#6b4a24"/>
      <path d="M-8 -38H8L10 -16H-10Z" fill="#2e5a2a"/><rect x="-7" y="-23" width="14" height="3" fill="#6b4a24"/>
      <path d="M9 -50Q20 -32 9 -14" stroke="#8a6a3a" stroke-width="2" fill="none"/>
      <line x1="9" y1="-50" x2="9" y2="-14" stroke="#e8d5a8" stroke-width="0.8"/>
      <rect x="-1" y="-37" width="11" height="4" rx="2" fill="#2e5a2a"/>
      <path d="M-7 -40Q-7 -54 0 -54Q7 -54 7 -40Z" fill="#244a20"/><circle cx="2" cy="-44" r="4" fill="#d9b48a"/>
    </g></g>
"""


DRAGON_DEFS = """
    <linearGradient id="dragon-fire" x1="1" y1="0" x2="0" y2="0">
      <stop offset="0%" stop-color="#fff3c4"/><stop offset="35%" stop-color="#ffb347"/>
      <stop offset="75%" stop-color="#ff5a1f"/><stop offset="100%" stop-color="#c62828" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="dragon-belly" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#7a1c1c"/><stop offset="100%" stop-color="#c0742e"/>
    </linearGradient>
    <!-- dragon facing left, origin at the shoulder -->
    <g id="dragon">
      <g>
        <animateTransform attributeName="transform" type="translate" values="0 0;0 -4;0 0" dur="0.9s" repeatCount="indefinite"/>
        <!-- far wing -->
        <g transform="translate(4 -4)">
          <path d="M0 0L12 -44L20 -38L27 -48Q31 -28 42 -32Q37 -17 47 -13Q28 -7 22 -1Z" fill="#3e0d0d">
            <animateTransform attributeName="transform" type="scale" values="1 1;1 -0.35;1 1" dur="0.9s" begin="0.08s" repeatCount="indefinite"/>
          </path>
        </g>
        <!-- tail -->
        <path d="M44 0Q70 4 86 -4Q100 -12 112 -8L121 -13L117 -4L123 1L112 -3Q100 -5 88 3Q70 12 44 8Z" fill="#5a1414">
          <animateTransform attributeName="transform" type="rotate" values="-3 44 4;4 44 4;-3 44 4" dur="1.8s" repeatCount="indefinite"/>
        </path>
        <!-- legs tucked -->
        <path d="M6 8L10 16L16 17L12 9Z M28 6L34 14L40 14L34 5Z" fill="#4a1010"/>
        <!-- body -->
        <path d="M-30 0Q-10 -13 20 -7Q40 -3 50 3Q30 11 0 11Q-20 11 -30 0Z" fill="url(#dragon-belly)"/>
        <path d="M-24 -4Q-4 -12 20 -7Q38 -3 48 2Q30 0 0 -2Q-14 -2 -24 -4Z" fill="#5a1414"/>
        <path d="M-14 -8L-11 -14L-8 -9L-4 -15L-1 -10L3 -15L6 -9L10 -14L12 -8" fill="#3a0a0a"/>
        <!-- neck & head -->
        <path d="M-27 -2Q-42 -14 -55 -15L-64 -13L-72 -9L-64 -6L-71 -3L-58 -3Q-45 -2 -25 6Z" fill="#6b1818"/>
        <path d="M-56 -15L-49 -26L-52 -14Z M-50 -14L-42 -22L-46 -12Z" fill="#d9c49a"/>
        <circle cx="-62" cy="-11" r="1.6" fill="#ffd54a"/>
        <!-- near wing -->
        <path d="M0 -2L14 -48L22 -42L30 -52Q34 -30 46 -34Q40 -18 50 -14Q30 -8 24 -2Z" fill="#7a1c1c" stroke="#3a0a0a" stroke-width="1">
          <animateTransform attributeName="transform" type="scale" values="1 1;1 -0.35;1 1" dur="0.9s" repeatCount="indefinite"/>
        </path>
      </g>
      <!-- fire breath (only for a moment each pass) -->
      <path d="M-70 -6Q-88 -16 -112 -10Q-98 -6 -116 -1Q-96 1 -112 8Q-90 6 -70 -3Z" fill="url(#dragon-fire)" opacity="0">
        <animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;0.11;0.12;0.17;0.18;1" dur="28s" repeatCount="indefinite"/>
      </path>
    </g>
"""


def dragon(y, scale=0.85, dur=28):
    """A dragon crossing right-to-left during the first ~30% of each cycle, then out of sight."""
    return f"""<g>
      <animateTransform attributeName="transform" type="translate" values="920 {y};-160 {y - 30};-160 {y - 30}" keyTimes="0;0.3;1" dur="{dur}s" repeatCount="indefinite"/>
      <g transform="scale({scale})"><use href="#dragon"/></g>
    </g>"""


def army(y, scale, dur, begin, span=(-240, 880)):
    members = [("soldier", 200), ("soldier", 172), ("archer", 144), ("soldier", 116),
               ("archer", 88), ("soldier", 60), ("soldier", 32), ("soldier", 4)]
    uses = "\n".join(f'<use href="#{k}" transform="translate({x} {y}) scale({scale})"/>' for k, x in members)
    return f"""<g>
      <animateTransform attributeName="transform" type="translate" values="{span[0]} 0;{span[1]} 0" dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/>
      {uses}
    </g>"""


def frame(w, h):
    return f"""<rect x="10" y="4" width="{w-20}" height="{h-8}" rx="10" fill="url(#bricks)"/>
  <rect x="10" y="4" width="{w-20}" height="{h-8}" rx="10" stroke="#c9a227" stroke-opacity="0.55" stroke-width="2"/>
  <rect x="16" y="10" width="{w-32}" height="{h-20}" rx="7" stroke="#5a4510" stroke-width="1"/>"""


def write(name, svg):
    with open(os.path.join(ASSETS, name), "w", encoding="utf-8", newline="\n") as f:
        f.write(svg.strip() + "\n")
    print("wrote", name)


def num(n):
    return f"{n:,}"


# ------------------------------------------------------------------ war chronicle
def banner(cx, color, value, unit, label, sub, dur, icon):
    x0, x1 = cx - 82, cx + 82
    size = 34 if len(value) <= 5 else 28
    unit_t = f'<tspan font-size="15" fill="#e8d5a8" font-weight="400"> {unit}</tspan>' if unit else ""
    return f"""
  <g>
    <animateTransform attributeName="transform" type="rotate" values="-1 {cx} 78;1 {cx} 78;-1 {cx} 78" dur="{dur}s" repeatCount="indefinite"/>
    <path d="M{x0} 78H{x1}V206L{cx} 236L{x0} 206Z" fill="{color}" filter="url(#drop)"/>
    <path d="M{x0+6} 84H{x1-6}V203L{cx} 229L{x0+6} 203Z" stroke="#e6b84a" stroke-width="1.2"/>
    <g transform="translate({cx} 108)">{icon}</g>
    <text x="{cx}" y="156" text-anchor="middle" class="serif" font-weight="700" font-size="{size}" fill="url(#gold)">{value}{unit_t}</text>
    <text x="{cx}" y="180" text-anchor="middle" class="serif" font-weight="700" font-size="10.5" letter-spacing="1.2" fill="#f6e2a6">{label}</text>
    <text x="{cx}" y="198" text-anchor="middle" class="serif" font-style="italic" font-size="11" fill="#d8c49a">{sub}</text>
  </g>"""


IC_SWORDS = """<g stroke-width="2.5" stroke-linecap="round"><path d="M-11 -11L11 11M11 -11L-11 11" stroke="#d9dde4"/><path d="M-13 5L-5 13M13 5L5 13" stroke="#e6b84a"/></g>"""
IC_FLAME = """<path d="M0 13Q-11 8 -8 -2Q-5 -9 0 -14Q1 -6 6 -3Q10 2 7 8Q5 12 0 13Z" fill="#ff8f2e"/><path d="M0 13Q-5 9 -3 3Q-1 -1 1 -4Q2 2 4 4Q5 9 0 13Z" fill="#ffd36b"/>"""
IC_TOWER = """<path d="M-10 13V-13H-6V-9H-2V-13H2V-9H6V-13H10V13Z" fill="#d9c49a"/><path d="M-3 13V6A3 3 0 0 1 3 6V13Z" fill="#3a2410"/>"""
IC_CROWN = """<path d="M-12 8V-6L-6 0L0 -10L6 0L12 -6V8Z" fill="#e6b84a" stroke="#9c6b1c"/><rect x="-12" y="8" width="24" height="4" fill="#c9a227"/><circle cy="3" r="2" fill="#b71c1c"/>"""


def war_chronicle(created, days, today, cur, cur_rng, longest, long_rng, updated):
    total = sum(days.values())
    year_total = sum(c for d, c in days.items() if d.startswith(str(today.year)))
    day_unit = lambda n: "Day" if n == 1 else "Days"
    cur_sub = fmt_range(*cur_rng) if cur else "Rally the troops!"
    w, h = 850, 260
    return f"""
<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>{DEFS}</defs>
  <style>{STYLE}</style>
  {frame(w, h)}
  <text x="425" y="40" text-anchor="middle" class="serif" font-weight="700" font-size="20" letter-spacing="5" fill="url(#gold)">WAR CHRONICLE</text>
  <text x="425" y="58" text-anchor="middle" class="serif" font-size="10.5" letter-spacing="3" fill="#a8977a">ROYAL ARCHIVES · UPDATED {updated}</text>
  <path d="M250 35H320M530 35H600" stroke="#c9a227" stroke-opacity="0.6"/>
  <path d="M244 35L249 30L254 35L249 40ZM596 35L601 30L606 35L601 40Z" fill="#c9a227"/>
  <rect x="34" y="72" width="782" height="6" rx="3" fill="#5a3a1c"/>
  <circle cx="34" cy="75" r="6" fill="#c9a227"/><circle cx="816" cy="75" r="6" fill="#c9a227"/>
  {banner(128, "#7a1414", num(total), "", "BATTLES WAGED", f"Deeds since {created.year}", 5, IC_SWORDS)}
  {banner(326, "#1c2f6e", str(cur), day_unit(cur), "CURRENT CAMPAIGN", cur_sub, 5.6, IC_FLAME)}
  {banner(524, "#7a1414", str(longest), day_unit(longest), "LONGEST SIEGE", fmt_range(*long_rng), 6.2, IC_TOWER)}
  {banner(722, "#1c2f6e", num(year_total), "", f"{today.year} CONQUESTS", "Deeds this year", 5.3, IC_CROWN)}
</svg>"""


# ------------------------------------------------------------------ battle ledger (contribution grid)
LEVEL = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2, "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}
SHIELD_FILL = ["#2c2a34", "#5e1414", "#9c1f1f", "#d0482a", "url(#gold)"]
SHIELD_EDGE = ["#3a3844", "#7a2020", "#c0392b", "#f07a4a", "#fff1b8"]


def shield(x, y, lvl, extra=""):
    return (f'<path d="M{x} {y}h11v6q0 4.5 -5.5 6.5q-5.5 -2 -5.5 -6.5z" fill="{SHIELD_FILL[lvl]}" '
            f'stroke="{SHIELD_EDGE[lvl]}" stroke-width="0.8"{extra}/>')


def battle_ledger(cal, updated):
    weeks = cal["weeks"]
    step, x0, y0 = 14, 74, 84
    cells, months = [], []
    last_month, last_label_wi = None, -9
    best = (0, None)
    active = 0
    total_days = 0
    for wi, w in enumerate(weeks):
        for d in w["contributionDays"]:
            date = dt.date.fromisoformat(d["date"])
            row = (date.weekday() + 1) % 7  # Sunday first, like GitHub
            lvl = LEVEL[d["contributionLevel"]]
            x, y = x0 + wi * step, y0 + row * step
            extra = ""
            if lvl == 4:
                extra = f' class="glory" style="animation-delay:{(wi * 7 + row) % 13 * 0.23:.2f}s"'
            cells.append(shield(x, y, lvl, extra))
            total_days += 1
            if d["contributionCount"]:
                active += 1
            if d["contributionCount"] > best[0]:
                best = (d["contributionCount"], date)
        first = dt.date.fromisoformat(w["contributionDays"][0]["date"])
        if first.month != last_month:
            if wi - last_label_wi >= 3 and wi < len(weeks) - 2:
                months.append(f'<text x="{x0 + wi * step}" y="{y0 - 8}" class="serif" font-size="10" fill="#a8977a">{first.strftime("%b")}</text>')
                last_label_wi = wi
            last_month = first.month

    grid_w = len(weeks) * step
    w, h = 850, 290
    labels = "".join(
        f'<text x="{x0 - 8}" y="{y0 + r * step + 9.5}" text-anchor="end" class="serif" font-size="9.5" fill="#8c7c62">{n}</text>'
        for r, n in ((1, "Mon"), (3, "Wed"), (5, "Fri")))
    legend_x = x0 + grid_w - 150
    legend = "".join(shield(legend_x + 42 + i * 15, 192, i) for i in range(5))
    best_txt = f"Mightiest day: {best[0]} deeds on {best[1].strftime('%b %d, %Y')}" if best[1] else "The realm awaits its first deed"
    return f"""
<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>{DEFS}{ARMY_DEFS}
    <clipPath id="road"><rect x="18" y="214" width="814" height="64" rx="6"/></clipPath>
  </defs>
  <style>{STYLE}
    .glory {{ animation: glory 2.6s ease-in-out infinite; }}
    @keyframes glory {{ 0%,100% {{ opacity: 1; }} 50% {{ opacity: 0.55; }} }}
  </style>
  {frame(w, h)}
  <text x="36" y="40" class="serif" font-weight="700" font-size="16" letter-spacing="4" fill="url(#gold)">ROLL OF DEEDS</text>
  <text x="36" y="58" class="serif" font-style="italic" font-size="11.5" fill="#d8c49a"><tspan font-weight="700" font-style="normal" fill="#f6e2a6">{num(cal["totalContributions"])}</tspan> deeds of valor in the last year · {active} of {total_days} days on the battlefield</text>
  <circle cx="702" cy="36" r="4" fill="#e53935" class="pulse"/>
  <text x="714" y="40" class="serif" font-size="10.5" letter-spacing="2" fill="#a8977a">{updated}</text>
  {''.join(months)}
  {labels}
  {''.join(cells)}
  <text x="{x0}" y="202" class="serif" font-style="italic" font-size="11" fill="#a8977a">{best_txt}</text>
  <text x="{legend_x + 36}" y="202" text-anchor="end" class="serif" font-size="10" fill="#8c7c62">Peace</text>
  {legend}
  <text x="{legend_x + 120}" y="202" class="serif" font-size="10" fill="#e6b84a">Glory</text>
  <g clip-path="url(#road)">
    <rect x="18" y="214" width="814" height="64" fill="#17130f"/>
    <rect x="18" y="214" width="814" height="3" fill="#2a2418"/>
    <rect x="18" y="248" width="814" height="22" fill="#221c15"/>
    {army(268, 0.72, 26, -12)}
  </g>
</svg>"""


# ------------------------------------------------------------------ battle activity (weekly towers)
def battle_activity(cal, updated):
    weeks = [sum(d["contributionCount"] for d in w["contributionDays"]) for w in cal["weeks"]][-26:]
    all_days = [d for w in cal["weeks"] for d in w["contributionDays"]]
    active_pct = round(100 * sum(1 for d in all_days if d["contributionCount"]) / max(1, len(all_days)))
    peak = max(weeks) or 1
    base, tw = 196, 22
    gap = (760 - 26 * tw) / 25
    towers = []
    for i, c in enumerate(weeks):
        x = 45 + i * (tw + gap)
        hgt = 10 if c == 0 else round(24 + 92 * c / peak)
        top = base - hgt
        if c == 0:  # ruins
            towers.append(f'<path d="M{x:.1f} {base}V{top+3}L{x+5:.1f} {top}L{x+9:.1f} {top+4}L{x+15:.1f} {top+1}L{x+22:.1f} {top+5}V{base}Z" fill="#2e2d36"/>')
            continue
        t = f'<rect x="{x:.1f}" y="{top}" width="{tw}" height="{hgt}" fill="url(#bricks-lit)"/>'
        t += (f'<path d="M{x-1:.1f} {top}V{top-7}H{x+5:.1f}V{top-3}H{x+8.5:.1f}V{top-7}H{x+13.5:.1f}V{top-3}'
              f'H{x+17:.1f}V{top-7}H{x+23:.1f}V{top}Z" fill="#3a3a46"/>')
        if hgt > 56:
            cls = "flicker" if i % 2 else "flicker2"
            t += f'<path class="{cls}" d="M{x+7:.1f} {top+24}V{top+16}A4 4 0 0 1 {x+15:.1f} {top+16}V{top+24}Z" fill="#ffb347" filter="url(#glow)"/>'
        if c >= 0.75 * peak:
            t += (f'<line x1="{x+11:.1f}" y1="{top-7}" x2="{x+11:.1f}" y2="{top-30}" stroke="#6b5232" stroke-width="1.5"/>'
                  f'<path fill="#a51c1c" transform="translate({x+12:.1f} {top-30})"><animate attributeName="d" dur="1.5s" repeatCount="indefinite" '
                  f'values="M0 0Q6 -2 12 0T24 0V11Q18 9 12 11T0 11Z;M0 0Q6 2 12 0T24 0V11Q18 13 12 11T0 11Z;M0 0Q6 -2 12 0T24 0V11Q18 9 12 11T0 11Z"/></path>')
        t += f'<text x="{x+11:.1f}" y="{base-4}" text-anchor="middle" class="serif" font-size="8" fill="#e8d5a8" opacity="0.75">{c}</text>'
        towers.append(t)

    def plaque(x, value, label, color="#3a2410"):
        return f"""<g>
    <rect x="{x}" y="251" width="180" height="40" rx="4" fill="url(#parch)" stroke="#8a6a3a"/>
    <text x="{x+90}" y="270" text-anchor="middle" class="serif" font-weight="700" font-size="16" fill="{color}">{value}</text>
    <text x="{x+90}" y="284" text-anchor="middle" class="serif" font-size="9" letter-spacing="1.8" fill="#6b4a24">{label}</text></g>"""

    w, h = 850, 300
    return f"""
<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>{DEFS}
    <linearGradient id="dusk" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#0b1022"/><stop offset="70%" stop-color="#2a2340"/><stop offset="100%" stop-color="#5a3528"/>
    </linearGradient>
    <clipPath id="scene"><rect x="18" y="12" width="814" height="232" rx="6"/></clipPath>
    {ARMY_DEFS}{DRAGON_DEFS}
  </defs>
  <style>{STYLE}</style>
  {frame(w, h)}
  <g clip-path="url(#scene)">
    <rect x="18" y="12" width="814" height="232" fill="url(#dusk)"/>
    <g fill="#fff6dc" opacity="0.7">
      <circle cx="80" cy="30" r="1"/><circle cx="220" cy="58" r="0.8"/><circle cx="380" cy="26" r="1.1"/>
      <circle cx="520" cy="48" r="0.9"/><circle cx="660" cy="24" r="1"/><circle cx="780" cy="54" r="0.8"/>
    </g>
    <text x="36" y="40" class="serif" font-weight="700" font-size="13" letter-spacing="3" fill="url(#gold)">CONTRIBUTION RAMPARTS</text>
    <text x="36" y="56" class="serif" font-style="italic" font-size="11" fill="#a8977a">Each tower rises with the deeds of one week · last 26 weeks</text>
    <circle cx="668" cy="36" r="4" fill="#e53935" class="pulse"/>
    <text x="680" y="40" class="serif" font-size="11" letter-spacing="2" fill="#e8d5a8">WATCHTOWER LIVE</text>
    <path d="M18 {base}Q200 188 425 192T832 190V244H18Z" fill="#1c1d2c"/>
    {''.join(towers)}
    {dragon(120)}
    <rect x="18" y="{base}" width="814" height="48" fill="#17130f"/>
    <rect x="18" y="{base}" width="814" height="3" fill="#2a2418"/>
    <rect x="18" y="214" width="814" height="26" fill="#221c15"/>
    {army(236, 0.85, 22, -9)}
  </g>
  {plaque(30, num(sum(weeks)), "LAST 26 WEEKS")}
  {plaque(232, num(max(weeks)), "MIGHTIEST WEEK", "#7a1414")}
  {plaque(434, f"{active_pct}%", "DAYS IN BATTLE", "#2e6b2a")}
  {plaque(636, updated, "LAST DISPATCH")}
</svg>"""


# ------------------------------------------------------------------ main
def main():
    created, days, cal = fetch()
    today = dt.datetime.now(dt.timezone.utc).date()
    updated = today.strftime("%b %d, %Y").upper()
    cur, cur_rng, longest, long_rng = streaks(days, today)
    print(f"total={sum(days.values())} current={cur} longest={longest} last_year={cal['totalContributions']}")
    write("war-chronicle.svg", war_chronicle(created, days, today, cur, cur_rng, longest, long_rng, updated))
    write("battle-ledger.svg", battle_ledger(cal, updated))
    write("battle-activity.svg", battle_activity(cal, updated))


if __name__ == "__main__":
    main()
