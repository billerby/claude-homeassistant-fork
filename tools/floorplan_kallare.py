"""Generate config/www/floorplan/kallare.svg (basement plan for ha-floorplan).

Room outlines were measured on a scan of the construction drawing (garage left out).
usage: python tools/floorplan_kallare.py config/www/floorplan/kallare.svg
"""
import sys
OX, OY = 60, 0  # offset so the plan starts near 0,0
# id, label, outline as (x, y) points, kind
ROOMS = [
    ("pingisrummet", "Pingis / bio", [(430, 10), (800, 10), (800, 335), (1095, 335), (1095, 545), (530, 545), (530, 340), (430, 340)], "room"),
    ("pentry", "Pentry", [(430, 340), (530, 340), (530, 412), (430, 412)], "room"),
    ("toalett_pingisrum", "WC", [(430, 412), (530, 412), (530, 545), (430, 545)], "room"),
    ("trappa", "Trappa", [(1095, 340), (1275, 340), (1275, 545), (1095, 545)], "outdoor"),
    ("bastun", "Bastu", [(80, 545), (237, 545), (237, 677), (80, 677)], "room"),
    ("badrum_kallare", "Badrum", [(237, 545), (475, 545), (475, 677), (237, 677)], "room"),
    ("matkallare", "Matkällare", [(475, 545), (630, 545), (630, 677), (475, 677)], "room"),
    ("korridor", "", [(475, 677), (630, 677), (630, 752), (475, 752)], "room"),
    ("pannrum", "Pannrum", [(80, 677), (287, 677), (287, 945), (80, 945)], "room"),
    ("tvattstuga", "Tvättstuga", [(287, 677), (475, 677), (475, 945), (287, 945)], "room"),
    ("elrum", "Elrum", [(475, 752), (630, 752), (630, 945), (475, 945)], "room"),
    ("familjerum", "Brasrum", [(630, 545), (1000, 545), (1000, 945), (630, 945)], "room"),
    ("tovas_rum", "Tovas rum", [(1000, 545), (1225, 545), (1225, 945), (1000, 945)], "room"),
]
LABEL_AT = {"pingisrummet": (615, 190)}  # label position for non-rectangular rooms
W, H = 1240, 960


def centre(rid, pts):
    if rid in LABEL_AT:
        return LABEL_AT[rid]
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2


def wifi_marker(mid, cx, cy):
    """Ceiling-mounted access point: wifi glyph in a circle."""
    return (f'<g id="{mid}" class="ap">'
            f'<circle cx="{cx}" cy="{cy}" r="24"/>'
            f'<path d="M{cx - 13},{cy - 3} a18,18 0 0 1 26,0 M{cx - 8},{cy + 2} a11,11 0 0 1 16,0"/>'
            f'<circle class="dot" cx="{cx}" cy="{cy + 8}" r="3"/>'
            '</g>'
            f'<text id="{mid}_clients" class="value small-value" x="{cx}" y="{cy + 40}"></text>')


def device_marker(mid, cx, cy, glyph):
    """Network device on the floor: a glyph in a circle with a value line below."""
    return (f'<g id="{mid}" class="device">'
            f'<circle cx="{cx}" cy="{cy}" r="22"/>{glyph}</g>'
            f'<text id="{mid}_value" class="value small-value" x="{cx}" y="{cy + 38}"></text>')


def router_glyph(cx, cy):
    return (f'<rect x="{cx - 12}" y="{cy - 7}" width="24" height="14" rx="2"/>'
            f'<circle class="dot" cx="{cx - 6}" cy="{cy}" r="2"/><circle class="dot" cx="{cx}" cy="{cy}" r="2"/>')


def pi_glyph(cx, cy):
    return f'<text class="glyph" x="{cx}" y="{cy + 1}">π</text>'


def switch_glyph(cx, cy):
    ports = "".join(f'<circle class="dot" cx="{cx + dx}" cy="{cy + 2}" r="1.8"/>' for dx in (-8, -3, 2, 7))
    return f'<rect x="{cx - 13}" y="{cy - 6}" width="26" height="14" rx="2"/>{ports}'


def battery_glyph(cx, cy):
    return (f'<rect x="{cx - 12}" y="{cy - 7}" width="21" height="14" rx="2"/>'
            f'<rect class="solid" x="{cx + 9}" y="{cy - 3}" width="3" height="6" rx="1"/>'
            f'<rect class="solid" x="{cx - 9}" y="{cy - 4}" width="15" height="8" rx="1"/>')


def drop_glyph(cx, cy):
    return f'<path class="fill" d="M{cx},{cy - 13} C{cx + 4},{cy - 5} {cx + 10},{cy} {cx + 10},{cy + 4} a10,10 0 0 1 -20,0 C{cx - 10},{cy} {cx - 4},{cy - 5} {cx},{cy - 13} z"/>'


def speaker_marker(mid, cx, cy, soundbar=False):
    """Sonos speaker on a wall: a speaker (or soundbar) glyph in a circle."""
    if soundbar:
        glyph = (f'<rect x="{cx - 14}" y="{cy - 5}" width="28" height="10" rx="4"/>'
                 + "".join(f'<circle class="dot" cx="{cx + dx}" cy="{cy}" r="1.8"/>' for dx in (-7, 0, 7)))
    else:
        glyph = (f'<rect x="{cx - 8}" y="{cy - 12}" width="16" height="24" rx="3"/>'
                 f'<circle class="cone" cx="{cx}" cy="{cy + 3}" r="5"/>'
                 f'<circle class="dot" cx="{cx}" cy="{cy - 6}" r="1.8"/>')
    return f'<g id="{mid}" class="speaker"><circle cx="{cx}" cy="{cy}" r="24"/>{glyph}</g>'


out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
       '<style>',
       '.room{fill:#1d2b44;stroke:#50627e;stroke-width:6}',
       '.outdoor{fill:#182a2a;stroke:#4f6f62;stroke-width:3;stroke-dasharray:12 8}',
       '.label{font:600 24px sans-serif;fill:#e8edf4;text-anchor:middle;dominant-baseline:middle;pointer-events:none}',
       '.outdoor-label{font:italic 22px sans-serif;fill:#7fa392}',
       '.small{font-size:17px}',
       '.motion{fill:none;stroke:none;pointer-events:none}',
       '.ap circle{fill:#121a2a;stroke:#c9d3df;stroke-width:4}',
       '.ap circle.dot{fill:#c9d3df;stroke:none}',
       '.ap path{fill:none;stroke:#c9d3df;stroke-width:3;stroke-linecap:round}',
       '.small-value{font-size:20px}',
       '.device circle{fill:#121a2a;stroke:#c9d3df;stroke-width:4}',
       '.device rect{fill:none;stroke:#c9d3df;stroke-width:3}',
       '.device circle.dot{fill:#c9d3df;stroke:none}',
       '.device rect.solid{fill:#c9d3df;stroke:none}',
       '.device .glyph{font:700 26px serif;fill:#c9d3df;text-anchor:middle;dominant-baseline:middle}',
       '.device path.fill{fill:#5aa0ff}',
       '.speaker circle{fill:#121a2a;stroke:#c9d3df;stroke-width:4}',
       '.speaker rect,.speaker circle.cone{fill:none;stroke:#c9d3df;stroke-width:2.5}',
       '.speaker circle.dot{fill:#c9d3df;stroke:none}',
       '.value{font:500 22px sans-serif;fill:#9aa7b8;text-anchor:middle;dominant-baseline:middle;pointer-events:none}',
       '</style>']
for rid, label, pts, kind in ROOMS:
    d = " ".join(f"{x - OX},{y - OY}" for x, y in pts)
    out.append(f'<polygon id="{rid}" class="{kind}" points="{d}"/>')
for rid, label, pts, kind in ROOMS:
    if kind == "room":
        d = " ".join(f"{x - OX},{y - OY}" for x, y in pts)
        out.append(f'<polygon id="{rid}_motion" class="motion" points="{d}"/>')
for rid, label, pts, kind in ROOMS:
    if not label:
        continue
    x, y = centre(rid, pts)
    cls = "label outdoor-label" if kind == "outdoor" else "label"
    if max(p[0] for p in pts) - min(p[0] for p in pts) < 120:
        cls += " small"
    # rooms too narrow for the name get it written vertically
    rot = f' transform="rotate(-90 {x - OX:.0f} {y - OY:.0f})"' if max(p[0] for p in pts) - min(p[0] for p in pts) < 100 and len(label) > 4 else ""
    out.append(f'<text id="{rid}_label" class="{cls}" x="{x - OX:.0f}" y="{y - OY:.0f}"{rot}>{label}</text>')
    # placeholder that ha-floorplan fills with live values via floorplan.text_set
    if kind == "room":
        out.append(f'<text id="{rid}_temp" class="value" x="{x - OX:.0f}" y="{y - OY + 34:.0f}"></text>')
out.append(wifi_marker("ap_u6_lite", 815 - OX, 680 - OY))
# Dream Machine and the Raspberry Pi stand together in Pingis / bio, outside the WC towards the food cellar
out.append(device_marker("udm", 560 - OX, 482 - OY, router_glyph(560 - OX, 482 - OY)))
out.append(device_marker("raspberry_pi", 655 - OX, 482 - OY, pi_glyph(655 - OX, 482 - OY)))
# water meter in the boiler room, in the corner towards the sauna
out.append(device_marker("vattenmatare", 140 - OX, 712 - OY, drop_glyph(140 - OX, 712 - OY)))
# USW Lite 8 PoE in the ping-pong room, against the wall of the inner corner
out.append(device_marker("usw_lite_8_poe_pingis", 859 - OX, 372 - OY, switch_glyph(859 - OX, 372 - OY)))
# US 8 60W in Tova's room, against the wall towards the stairs
out.append(device_marker("us_8_60w", 1170 - OX, 584 - OY, switch_glyph(1170 - OX, 584 - OY)))
# home battery on the electrical room wall towards Brasrum
out.append(device_marker("hembatteri", 600 - OX, 790 - OY, battery_glyph(600 - OX, 790 - OY)))
# Sonos: Brasrum on the outer wall, laundry room on the wall to the boiler room
out.append(speaker_marker("sonos_brasrum", 815 - OX, 905 - OY))
out.append(speaker_marker("sonos_tvattstuga", 322 - OX, 718 - OY))
out.append('</svg>')
open(sys.argv[1], "w").write("\n".join(out) + "\n")
