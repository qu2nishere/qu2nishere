"""Usage: python scripts/header.py assets/header.svg

Winter night header: view from the castle battlements over a distant snowy village."""
import random, sys

random.seed(7)
OUT = sys.argv[1]
SERIF = "Georgia, 'Palatino Linotype', 'Book Antiqua', 'Times New Roman', serif"
W, H = 850, 360

# ---------------------------------------------------------------- helpers
def pine(x, y, s, fill="#13203a"):
    """Snow-covered pine, base at (x,y), height ~ 40*s."""
    return f"""<g transform="translate({x} {y}) scale({s})">
      <rect x="-1.5" y="-6" width="3" height="6" fill="#2a1d14"/>
      <path d="M0 -40L-9 -24H-5L-13 -12H-7L-16 0H16L7 -12H13L5 -24H9Z" fill="{fill}"/>
      <path d="M0 -40L-5 -31Q0 -29 5 -31Z M-5 -24Q0 -21 5 -24L3 -22Q0 -20 -3 -22Z M-7 -12Q0 -9 7 -12L5 -10Q0 -8 -5 -10Z M-16 0Q0 3 16 0L12 -2Q0 1 -12 -2Z" fill="#dfe7f7"/>
    </g>"""

def house(x, y, w, h, roof="#2b1f1a", wall="#4a3426", lit=True, chimney=True, delay=0.0):
    """House with base at (x,y)."""
    rh = h * 0.75
    out = f"""<g>
      <rect x="{x}" y="{y-h}" width="{w}" height="{h}" fill="{wall}"/>
      <path d="M{x-3} {y-h+1}L{x+w/2} {y-h-rh}L{x+w+3} {y-h+1}Z" fill="{roof}"/>
      <path d="M{x-3} {y-h+1}L{x+w/2} {y-h-rh}L{x+w+3} {y-h+1}L{x+w-1} {y-h+1}L{x+w/2} {y-h-rh+4}L{x+1} {y-h+1}Z" fill="#e8eefc"/>
      <path d="M{x+w*0.18} {y-h-rh*0.45}L{x+w/2} {y-h-rh}L{x+w*0.82} {y-h-rh*0.45}Q{x+w/2} {y-h-rh*0.62} {x+w*0.18} {y-h-rh*0.45}Z" fill="#e8eefc"/>"""
    if lit:
        out += f"""<rect class="win" style="animation-delay:{delay:.1f}s" x="{x+w*0.3}" y="{y-h*0.65}" width="{max(2.5, w*0.22):.1f}" height="{max(3, h*0.3):.1f}" fill="#ffc461"/>"""
    if chimney:
        cx = x + w * 0.72
        cy = y - h - rh * 0.5
        out += f"""<rect x="{cx}" y="{cy-6}" width="3.5" height="7" fill="#3a2a22"/><rect x="{cx-0.5}" y="{cy-7}" width="4.5" height="1.8" fill="#e8eefc"/>"""
        for i in range(3):
            out += f"""<circle class="smoke" style="animation-delay:{delay + i*1.3:.1f}s" cx="{cx+1.8}" cy="{cy-9}" r="2.2" fill="#aab4cc"/>"""
    return out + "</g>"

def torch(x, y, s=1.0, cls="flicker"):
    """Torch on a pole, base at (x,y)."""
    return f"""<g transform="translate({x} {y}) scale({s})">
      <circle cy="-22" r="16" fill="url(#torch-glow)" class="{cls}"/>
      <rect x="-1.2" y="-18" width="2.4" height="18" fill="#3a2a1c"/>
      <path class="flame" d="M0 -17Q-4.5 -22 0 -30Q4.5 -22 0 -17Z" fill="#ffcf5a"/>
      <path class="flame" d="M0 -18Q-2 -21 0 -25Q2 -21 0 -18Z" fill="#fff3c4"/>
    </g>"""

# ---------------------------------------------------------------- scene pieces
stars = "".join(
    f'<circle class="tw{random.randint(1,3)}" cx="{random.uniform(0, W):.0f}" cy="{random.uniform(5, 150):.0f}" r="{random.uniform(0.5, 1.4):.1f}"/>'
    for _ in range(45))

# Snowflakes: three depth layers
flakes = []
for layer, (n, rmin, rmax, dmin, dmax, op) in enumerate([(45, 0.5, 1.0, 14, 20, 0.55), (35, 1.0, 1.7, 10, 14, 0.75), (18, 1.8, 2.8, 7, 10, 0.9)]):
    for _ in range(n):
        dur = random.uniform(dmin, dmax)
        flakes.append(
            f'<circle class="fall{random.randint(1,3)}" style="animation-duration:{dur:.1f}s;animation-delay:-{random.uniform(0, dur):.1f}s" '
            f'cx="{random.uniform(-20, W + 20):.0f}" cy="-10" r="{random.uniform(rmin, rmax):.1f}" opacity="{op}"/>')

# Distant trees on the snow fields
far_trees = "".join(pine(x, y, s, "#1a2944") for x, y, s in [
    (175, 268, 0.42), (190, 270, 0.5), (205, 266, 0.38), (330, 262, 0.4), (345, 265, 0.48),
    (420, 252, 0.36), (432, 255, 0.42), (812, 236, 0.4), (826, 240, 0.48), (838, 236, 0.36)])
near_trees = "".join(pine(x, y, s) for x, y, s in [
    (150, 300, 0.95), (172, 304, 1.15), (196, 300, 0.85), (452, 300, 0.9), (476, 304, 1.2), (500, 300, 0.8),
    (790, 302, 1.05), (815, 300, 0.85), (836, 304, 1.15)])

# Village on the far hill (right-center)
village = "".join([
    house(560, 236, 16, 10, delay=0.2), house(582, 240, 20, 12, delay=1.1),
    house(612, 232, 14, 9, delay=0.6, chimney=False), house(640, 238, 22, 13, delay=1.6),
    house(702, 236, 18, 11, delay=0.9), house(726, 240, 15, 9, delay=2.0),
    house(748, 234, 20, 12, delay=0.4), house(776, 238, 14, 9, delay=1.3, chimney=False),
    house(536, 244, 14, 8, delay=1.8, chimney=False),
])
church = """<g>
      <rect x="668" y="200" width="22" height="34" fill="#4a3a30"/>
      <path d="M665 201L679 172L693 201Z" fill="#2b1f1a"/>
      <path d="M665 201L679 172L693 201L689 201L679 179L669 201Z" fill="#e8eefc"/>
      <path d="M679 172V160M675 164H683" stroke="#c9a227" stroke-width="1.6"/>
      <path class="win" style="animation-delay:0.7s" d="M676 222V213A3 3 0 0 1 682 213V222Z" fill="#ffc461"/>
      <circle class="win" style="animation-delay:1.4s" cx="679" cy="191" r="2.5" fill="#ffc461"/>
      <rect x="690" y="216" width="22" height="18" fill="#3e2e24"/>
      <path d="M688 217L701 206L714 217Z" fill="#e8eefc"/>
    </g>"""
village_torches = "".join(torch(x, y, s, c) for x, y, s, c in [
    (552, 246, 0.45, "flicker"), (628, 244, 0.45, "flicker2"), (664, 240, 0.5, "flicker"),
    (698, 242, 0.45, "flicker2"), (744, 244, 0.45, "flicker"), (792, 244, 0.45, "flicker2")])

# Road from the castle gate (bottom-left) to the village, lined with torches
road = "M170 316C240 306 300 300 380 286S500 262 560 252"
road_torches = "".join(torch(x, y, s, c) for x, y, s, c in [
    (238, 314, 0.8, "flicker"), (330, 296, 0.68, "flicker2"), (420, 278, 0.58, "flicker"), (500, 262, 0.5, "flicker2")])

# Torch-bearing patrol walking the road towards the village
patrol = "".join(f"""<g>
      <animateMotion path="{road}" dur="38s" begin="-{b}s" repeatCount="indefinite" keyPoints="0;1" keyTimes="0;1"/>
      <animateTransform attributeName="transform" type="scale" values="0.62;0.3" dur="38s" begin="-{b}s" repeatCount="indefinite" additive="sum"/>
      <use href="#walker"/>
    </g>""" for b in (0, 2.2, 4.4))


# ---------------------------------------------------------------- magic world
def kid(robe, hat, trim):
    """Little wizard, feet at (0,0), facing right."""
    return f"""<path d="M-6 -16L6 -16L8.5 0H-8.5Z" fill="{robe}"/>
      <path d="M-8.5 0H8.5L8 -2H-8Z" fill="{trim}"/>
      <rect x="-5" y="-17" width="10" height="3" rx="1.5" fill="{trim}"/>
      <circle cy="-21" r="4.6" fill="#f1c9a5"/>
      <circle cx="2" cy="-21.5" r="0.8" fill="#2a1d14"/>
      <ellipse cy="-24" rx="8" ry="1.8" fill="{hat}"/>
      <path d="M-5.5 -24L5.5 -24L-1 -40Z" fill="{hat}"/>
      <circle cx="-1" cy="-40" r="1.4" fill="{trim}"/>
      <path d="M0.5 -31L1.3 -29.4L3 -29.2L1.7 -28L2 -26.3L0.5 -27.1L-1 -26.3L-0.7 -28L-2 -29.2L-0.3 -29.4Z" fill="#ffe27a"/>
      <line x1="4" y1="-12" x2="13" y2="-20" stroke="#6b4a24" stroke-width="1.6" stroke-linecap="round"/>"""


def duel_side(x, y, flip, robe, hat, trim, color, begin, target_path, tx, ty, dur=12):
    """One young wizard who casts a spell along target_path every `dur` seconds."""
    sx = -1 if flip else 1
    hop = (f'<animateTransform attributeName="transform" type="translate" values="0 0;0 -4;0 0;0 0" '
           f'keyTimes="0;0.03;0.06;1" dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/>')
    wand = (f'<circle cx="13" cy="-20" r="1.8" fill="{color}" filter="url(#magic-glow)">'
            f'<animate attributeName="r" values="1.8;5;1.8;1.8" keyTimes="0;0.02;0.08;1" dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/></circle>')
    figure = f'<g transform="translate({x} {y}) scale({1.25*sx} 1.25)"><g>{hop}{kid(robe, hat, trim)}{wand}</g></g>'
    trail = ""
    for i, (r, op) in enumerate([(4.2, 1), (3.1, 0.7), (2.3, 0.5), (1.6, 0.35)]):
        b = begin + i * 0.06
        if i == 0:
            core = f'<circle r="{r*2.2:.1f}" fill="{color}" opacity="0.3"/><circle r="{r}" fill="#ffffff"/>'
        else:
            core = f'<circle r="{r}" fill="{color}" opacity="{op}"/>'
        trail += f"""<g opacity="0">
        <animateMotion path="{target_path}" keyPoints="0;1;1" keyTimes="0;0.1;1" calcMode="linear" dur="{dur}s" begin="{b:.2f}s" repeatCount="indefinite"/>
        <animate attributeName="opacity" values="1;0" keyTimes="0;0.1" calcMode="discrete" dur="{dur}s" begin="{b:.2f}s" repeatCount="indefinite"/>
        {core}</g>"""
    rays = "".join(f'<line x1="0" y1="-5" x2="0" y2="-11" transform="rotate({a})" stroke="{color}" stroke-width="1.4" stroke-linecap="round"/>'
                   for a in range(0, 360, 45))
    burst = f"""<g transform="translate({tx} {ty})"><g opacity="0">
        <animate attributeName="opacity" values="0;0;1;0;0" keyTimes="0;0.099;0.1;0.17;1" dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/>
        <animateTransform attributeName="transform" type="scale" values="0.2;0.2;1.6;1.6" keyTimes="0;0.1;0.17;1" dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/>
        <circle r="7" stroke="{color}" stroke-width="1.5" fill="{color}" fill-opacity="0.25"/>{rays}
      </g></g>"""
    return figure, trail + burst


kidA, spellA = duel_side(262, 284, False, "#1f3a8a", "#2b4fb8", "#e6b84a", "#6ff3ff", 1.0, "M278 259Q336 200 396 250", 400, 250)
kidB, spellB = duel_side(404, 268, True, "#5b2a86", "#8b1a1a", "#f1c75b", "#ff7ae0", 7.0, "M388 243Q328 192 266 264", 264, 266)
duel = kidA + kidB + spellA + spellB

motes = "".join(
    f'<circle class="mote" style="animation-duration:{random.uniform(6, 11):.1f}s;animation-delay:-{random.uniform(0, 10):.1f}s" '
    f'cx="{random.uniform(130, 840):.0f}" cy="{random.uniform(215, 300):.0f}" r="{random.uniform(0.9, 1.8):.1f}" '
    f'fill="{random.choice(["#8ff7ff", "#ffe27a", "#ff9ae8", "#a8ffcb"])}"/>'
    for _ in range(22))

aurora = "".join(f"""<path fill="url(#aurora{i})" opacity="{op}">
      <animate attributeName="d" dur="{d}s" repeatCount="indefinite" values="{a};{b};{a}"/>
    </path>""" for i, op, d, a, b in [
    (1, 0.32, 11, "M380 70Q480 30 580 62T780 40T870 58V96Q770 78 680 100T480 92T380 108Z",
                  "M380 60Q480 46 580 48T780 58T870 40V82Q770 96 680 84T480 104T380 96Z"),
    (2, 0.22, 14, "M430 104Q540 70 640 96T850 82V118Q740 112 640 128T430 132Z",
                  "M430 96Q540 92 640 80T850 98V128Q740 122 640 116T430 126Z"),
])

wizard_tower = """<g>
      <rect x="516" y="212" width="14" height="38" fill="#4a4a5e"/>
      <path d="M512 213L523 186L534 213Z" fill="#4b2a7a"/>
      <path d="M512 213L523 186L534 213L531 213L523 193L515 213Z" fill="#e8eefc"/>
      <path class="win" d="M520 232V226A3 3 0 0 1 526 226V232Z" fill="#c08cff"/>
      <circle cx="523" cy="182" r="9" fill="url(#orb-glow)" class="orb"/>
      <circle cx="523" cy="182" r="3" fill="#e2c6ff"/>
    </g>"""

# Foreground battlement (we stand on the wall)
merlons = []
mx = 120
while mx < W:
    merlons.append(f'<rect x="{mx}" y="306" width="34" height="22" fill="url(#bricks)"/>'
                   f'<path d="M{mx-1} 307Q{mx+17} 297 {mx+35} 307V310H{mx-1}Z" fill="#eef3ff"/>')
    mx += 58

svg = f"""<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="{H}" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="#04060f"/><stop offset="50%" stop-color="#111a35"/><stop offset="80%" stop-color="#26315a"/><stop offset="100%" stop-color="#3a4570"/>
    </linearGradient>
    <radialGradient id="moon-glow" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#dfe8ff" stop-opacity="0.5"/><stop offset="100%" stop-color="#dfe8ff" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="torch-glow" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#ffb347" stop-opacity="0.8"/><stop offset="100%" stop-color="#ff6a00" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="village-glow" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#ffb347" stop-opacity="0.28"/><stop offset="100%" stop-color="#ff8a00" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="snow-far" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#7f90b8"/><stop offset="100%" stop-color="#4d5c85"/>
    </linearGradient>
    <linearGradient id="snow-near" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#a9b8d8"/><stop offset="100%" stop-color="#5e6d96"/>
    </linearGradient>
    <linearGradient id="gold" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#fff1b8"/><stop offset="45%" stop-color="#e6b84a"/><stop offset="100%" stop-color="#9c6b1c"/>
    </linearGradient>
    <linearGradient id="roof" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#7a2020"/><stop offset="100%" stop-color="#360a0a"/>
    </linearGradient>
    <linearGradient id="wall-shade" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#000" stop-opacity="0"/><stop offset="100%" stop-color="#000" stop-opacity="0.5"/>
    </linearGradient>
    <pattern id="bricks" width="24" height="12" patternUnits="userSpaceOnUse">
      <rect width="24" height="12" fill="#353646"/>
      <path d="M0 0.5H24M0 6.5H24M0.5 0V6M12.5 6V12" stroke="#23242f" stroke-width="1"/>
    </pattern>
    <linearGradient id="aurora1" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#5dffb0" stop-opacity="0"/><stop offset="40%" stop-color="#5dffb0"/><stop offset="75%" stop-color="#4fd2ff"/><stop offset="100%" stop-color="#4fd2ff" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="aurora2" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#b47aff" stop-opacity="0"/><stop offset="50%" stop-color="#b47aff"/><stop offset="100%" stop-color="#5dffb0" stop-opacity="0"/>
    </linearGradient>
    <radialGradient id="orb-glow" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#c08cff" stop-opacity="0.9"/><stop offset="100%" stop-color="#7a3cff" stop-opacity="0"/>
    </radialGradient>
    <filter id="magic-glow" x="-100%" y="-100%" width="300%" height="300%">
      <feGaussianBlur stdDeviation="1.6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="title-shadow" x="-10%" y="-20%" width="120%" height="150%">
      <feDropShadow dx="0" dy="3" stdDeviation="2" flood-color="#000" flood-opacity="0.85"/>
      <feDropShadow dx="0" dy="0" stdDeviation="8" flood-color="#e6b84a" flood-opacity="0.35"/>
    </filter>

    <!-- tiny torch-bearer for the patrol (feet at 0,0) -->
    <g id="walker">
      <g transform="translate(-12 0)">
        <circle cx="10" cy="-36" r="12" fill="url(#torch-glow)" class="flicker"/>
        <rect x="-3" y="-16" width="6" height="16" fill="#1b1b24"/>
        <path d="M-7 -34H7L9 -14H-9Z" fill="#7a1a1a"/>
        <rect x="-5.5" y="-45" width="11" height="11" rx="3" fill="#9aa2b0"/>
        <line x1="7" y1="-26" x2="10" y2="-38" stroke="#3a2a1c" stroke-width="2"/>
        <path class="flame" d="M10 -38Q6 -42 10 -48Q14 -42 10 -38Z" fill="#ffcf5a"/>
      </g>
      <g transform="translate(12 0)">
        <rect x="-3" y="-16" width="6" height="16" fill="#1b1b24"/>
        <path d="M-7 -34H7L9 -14H-9Z" fill="#1f3a8a"/>
        <rect x="-5.5" y="-45" width="11" height="11" rx="3" fill="#9aa2b0"/>
        <line x1="8" y1="0" x2="8" y2="-58" stroke="#5c4a30" stroke-width="1.6"/>
        <path d="M8 -64L5.5 -57H10.5Z" fill="#cfd5de"/>
      </g>
    </g>

    <!-- castle guard standing at the parapet, looking out (feet at 0,0) -->
    <g id="guard">
      <g>
        <animateTransform attributeName="transform" type="translate" values="0 0;0 -0.8;0 0" dur="3s" repeatCount="indefinite"/>
        <rect x="-4" y="-22" width="8" height="22" fill="#1d1d26"/>
        <path d="M-10 -50H10L13 -20H-13Z" fill="#7a1a1a"/>
        <path d="M-10 -50Q-16 -30 -15 -16L-10 -18Z" fill="#4a1010"/>
        <rect x="-1.5" y="-48" width="3" height="24" fill="#e6b84a"/>
        <rect x="-8" y="-38" width="16" height="3" fill="#e6b84a"/>
        <rect x="-8" y="-66" width="16" height="16" rx="4" fill="#a8afbb"/>
        <path d="M-8 -64Q0 -72 8 -64" stroke="#eef3ff" stroke-width="3"/>
        <rect x="0" y="-60" width="8" height="2.5" fill="#15151a"/>
        <line x1="15" y1="4" x2="15" y2="-92" stroke="#6b5232" stroke-width="2.5"/>
        <path d="M15 -103L11 -91H19Z" fill="#dfe5ee"/>
        <rect x="2" y="-48" width="14" height="6" rx="3" fill="#7d828c"/>
      </g>
    </g>

    <!-- waving flag (origin top of pole) -->
    <g id="flag">
      <line x1="0" y1="-2" x2="0" y2="34" stroke="#6b5232" stroke-width="2.2"/>
      <circle cx="0" cy="-2.5" r="2" fill="#e6b84a"/>
      <path fill="#da251d">
        <animate attributeName="d" dur="1.4s" repeatCount="indefinite"
          values="M1 1Q8.5 -2.5 16 1T31 1V21Q23.5 17.5 16 21T1 21Z;M1 1Q8.5 4.5 16 1T31 1V21Q23.5 24.5 16 21T1 21Z;M1 1Q8.5 -2.5 16 1T31 1V21Q23.5 17.5 16 21T1 21Z"/>
      </path>
      <polygon points="16.00,4.40 17.53,8.90 22.28,8.96 18.47,11.80 19.88,16.34 16.00,13.60 12.12,16.34 13.53,11.80 9.72,8.96 14.47,8.90" fill="#ffde00">
        <animateTransform attributeName="transform" type="translate" values="0 -0.8;0 0.8;0 -0.8" dur="1.4s" repeatCount="indefinite"/>
      </polygon>
    </g>
  </defs>

  <style>
    .tw1 {{ animation: tw 3s ease-in-out infinite; }}
    .tw2 {{ animation: tw 4.5s ease-in-out infinite 1s; }}
    .tw3 {{ animation: tw 2.4s ease-in-out infinite 0.6s; }}
    @keyframes tw {{ 0%,100% {{ opacity: 0.25; }} 50% {{ opacity: 1; }} }}
    .flicker {{ animation: flick 1.8s ease-in-out infinite; }}
    .flicker2 {{ animation: flick 2.3s ease-in-out infinite 0.4s; }}
    @keyframes flick {{ 0%,100% {{ opacity: 1; }} 30% {{ opacity: 0.65; }} 55% {{ opacity: 0.95; }} 75% {{ opacity: 0.75; }} }}
    .win {{ animation: win 3.2s ease-in-out infinite; }}
    @keyframes win {{ 0%,100% {{ opacity: 1; }} 40% {{ opacity: 0.7; }} 60% {{ opacity: 0.9; }} }}
    .flame {{ transform-box: fill-box; transform-origin: 50% 100%; animation: flame 0.45s ease-in-out infinite alternate; }}
    @keyframes flame {{ from {{ transform: scale(1,1); }} to {{ transform: scale(0.82,1.22); }} }}
    .smoke {{ transform-box: fill-box; transform-origin: center; animation: smoke 4s ease-out infinite; opacity: 0; }}
    @keyframes smoke {{ 0% {{ transform: translate(0,0) scale(0.6); opacity: 0.55; }} 100% {{ transform: translate(6px,-22px) scale(2.2); opacity: 0; }} }}
    .mote {{ transform-box: fill-box; animation-name: mote; animation-timing-function: ease-in-out; animation-iteration-count: infinite; }}
    @keyframes mote {{ 0% {{ transform: translate(0,0); opacity: 0; }} 20% {{ opacity: 1; }} 50% {{ transform: translate(8px,-18px); }} 80% {{ opacity: 0.9; }} 100% {{ transform: translate(-4px,-36px); opacity: 0; }} }}
    .orb {{ animation: orb 2.4s ease-in-out infinite; }}
    @keyframes orb {{ 0%,100% {{ opacity: 0.55; }} 50% {{ opacity: 1; }} }}
    .fall1 {{ animation-name: fall1; animation-timing-function: linear; animation-iteration-count: infinite; }}
    .fall2 {{ animation-name: fall2; animation-timing-function: linear; animation-iteration-count: infinite; }}
    .fall3 {{ animation-name: fall3; animation-timing-function: linear; animation-iteration-count: infinite; }}
    @keyframes fall1 {{ 0% {{ transform: translate(0,0); }} 50% {{ transform: translate(14px,190px); }} 100% {{ transform: translate(-4px,380px); }} }}
    @keyframes fall2 {{ 0% {{ transform: translate(0,0); }} 50% {{ transform: translate(-12px,190px); }} 100% {{ transform: translate(8px,380px); }} }}
    @keyframes fall3 {{ 0% {{ transform: translate(0,0); }} 50% {{ transform: translate(22px,190px); }} 100% {{ transform: translate(30px,380px); }} }}
  </style>

  <!-- sky -->
  <rect width="{W}" height="{H}" fill="url(#sky)"/>
  <g fill="#f2f5ff">{stars}</g>

  <!-- aurora -->
  {aurora}

  <!-- moon -->
  <circle cx="770" cy="62" r="78" fill="url(#moon-glow)"/>
  <circle cx="770" cy="62" r="25" fill="#eef3ff"/>
  <circle cx="762" cy="56" r="4" fill="#d6dff2"/><circle cx="779" cy="70" r="5.5" fill="#d6dff2"/><circle cx="777" cy="50" r="2.5" fill="#d6dff2"/>

  <!-- snowy mountains -->
  <path d="M110 230L190 150L240 190L310 120L390 200L450 160L520 210L600 140L680 195L760 150L850 205V260H110Z" fill="#1c2747"/>
  <path d="M190 150L172 168L184 166L192 174L200 162L212 168Z M310 120L290 142L302 138L312 148L322 136L334 142Z M450 160L436 174L446 172L453 179L460 170L468 174Z M600 140L582 160L594 156L602 165L612 154L622 160Z M760 150L744 166L756 163L763 171L770 161L780 166Z" fill="#c4d0ea" opacity="0.85"/>

  <!-- far snow fields & village hill -->
  <path d="M110 268Q260 236 420 250T640 226Q740 214 850 228V300H110Z" fill="url(#snow-far)"/>
  <ellipse cx="672" cy="232" rx="170" ry="48" fill="url(#village-glow)"/>
  {far_trees}

  <!-- the village -->
  {church}
  {village}
  {village_torches}
  {wizard_tower}

  <!-- near snow field, road & torches -->
  <path d="M110 300Q300 270 520 284T850 278V330H110Z" fill="url(#snow-near)"/>
  <path d="{road}" stroke="#c9d5ee" stroke-width="9" stroke-linecap="round" opacity="0.55"/>
  <path d="{road}" stroke="#8d9cc0" stroke-width="2" stroke-dasharray="2 7" stroke-linecap="round" opacity="0.6"/>
  {near_trees}
  {road_torches}
  {patrol}
  {duel}
  <g filter="url(#magic-glow)">{motes}</g>

  <!-- ==================== CASTLE (foreground, left) ==================== -->
  <rect x="0" y="118" width="112" height="242" fill="url(#bricks)"/>
  <rect x="0" y="118" width="112" height="242" fill="url(#wall-shade)"/>
  <path d="M-8 120L56 40L120 120Z" fill="url(#roof)"/>
  <path d="M-8 120L56 40L120 120L108 120L56 54L4 120Z" fill="#eef3ff"/>
  <path d="M33 69L56 40L79 69Q56 60 33 69Z" fill="#eef3ff"/>
  <use href="#flag" transform="translate(56 12)"/>
  <rect x="-2" y="118" width="116" height="6" fill="#eef3ff"/>
  <path class="win" d="M46 170V146A10 10 0 0 1 66 146V170Z" fill="#ffc461" filter="url(#glow)"/>
  <path d="M56 136V170M46 156H66" stroke="#2a1f18" stroke-width="2"/>
  <path d="M44 172H68V176H44Z" fill="#eef3ff"/>
  <path class="win" style="animation-delay:1.2s" d="M50 238V224A6 6 0 0 1 62 224V238Z" fill="#ffc461" filter="url(#glow)"/>

  <!-- guards on the parapet -->
  <use href="#guard" transform="translate(206 336)"/>
  <use href="#guard" transform="translate(612 336) scale(-1 1)"/>

  <!-- battlement we stand on -->
  <rect x="112" y="326" width="{W-112}" height="34" fill="url(#bricks)"/>
  <rect x="112" y="326" width="{W-112}" height="34" fill="url(#wall-shade)"/>
  <path d="M112 327Q400 320 {W} 327V331H112Z" fill="#eef3ff"/>
  {''.join(merlons)}
  {torch(300, 306, 1.0, "flicker")}
  {torch(532, 306, 1.0, "flicker2")}
  {torch(764, 306, 1.0, "flicker")}

  <!-- ==================== TITLE ==================== -->
  <g font-family="{SERIF}">
    <text x="150" y="58" font-size="12" letter-spacing="5" fill="#c9a227">✦ HEAR YE, HEAR YE ✦</text>
    <text x="146" y="118" font-size="56" font-weight="700" fill="url(#gold)" filter="url(#title-shadow)" letter-spacing="1">Sir Quân</text>
    <text x="150" y="148" font-size="19" font-style="italic" fill="#e3e9f7">of House <tspan fill="#f1c75b" font-style="normal" font-weight="700">qu2nishere</tspan></text>
    <path d="M136 166H154V194H136L144 180Z" fill="#5e1010"/>
    <path d="M514 166H496V194H514L506 180Z" fill="#5e1010"/>
    <path d="M150 160H500V188H150Z" fill="#8b1a1a" stroke="#e6b84a" stroke-width="1.5"/>
    <path d="M152 160Q325 155 498 160" stroke="#eef3ff" stroke-width="2.5" stroke-linecap="round"/>
    <text x="325" y="179" text-anchor="middle" font-size="11.5" font-weight="700" letter-spacing="1.4" fill="#f6e2a6">FULL-STACK DEVELOPER · KNIGHT OF CODE</text>
    <text x="152" y="214" font-size="13.5" font-style="italic" fill="#c3cde6">“Keeping the forge warm through the long winter of 2026”</text>
  </g>

  <!-- falling snow (on top of everything) -->
  <g fill="#ffffff">{''.join(flakes)}</g>
</svg>"""

with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    f.write(svg)
print("ok", len(svg))
