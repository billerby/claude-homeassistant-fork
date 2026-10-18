"""Generate config/www/floorplan/overvaning.svg (upstairs plan for ha-floorplan).

Room coordinates were measured on a photo of the construction drawing.
usage: python tools/floorplan_overvaning.py config/www/floorplan/overvaning.svg
"""
import sys
OX, OY = 100, 60  # offset so the plan starts near 0,0
# id, label, x0, y0, x1, y1, kind
ROOMS = [
    ("vardagsrum", "Vardagsrum", 652, 80, 1145, 742, "room"),
    ("pizzerian", "Altan / Pizzeria", 1145, 80, 1480, 742, "outdoor"),
    ("entre", "Entré", 440, 560, 652, 742, "room"),
    ("trappa", "Trappa", 285, 555, 440, 742, "outdoor"),
    ("wc", "WC", 175, 745, 290, 930, "room"),
    ("kapprum", "Kapprum", 290, 745, 610, 930, "room"),
    ("hall", "Hall", 610, 745, 1482, 935, "room"),
    ("bad", "Bad", 1482, 745, 1700, 935, "room"),
    ("kok", "Kök", 130, 935, 605, 1325, "room"),
    ("pianorum", "Pianorum", 605, 935, 872, 1325, "room"),
    ("fritiofs_rum", "Fritiofs rum", 872, 935, 1112, 1325, "room"),
    ("henriks_rum", "Henriks rum", 1112, 935, 1410, 1325, "room"),
    ("master_bedroom", "Master bedroom", 1410, 935, 1728, 1325, "room"),
]
TEXT_SLOTS = {"vardagsrum"}
W, H = 1660, 1290
def wifi_marker(mid, cx, cy):
    """Ceiling-mounted access point: wifi glyph in a circle."""
    return (f'<g id="{mid}" class="ap">'
            f'<circle cx="{cx}" cy="{cy}" r="24"/>'
            f'<path d="M{cx - 13},{cy - 3} a18,18 0 0 1 26,0 M{cx - 8},{cy + 2} a11,11 0 0 1 16,0"/>'
            f'<circle class="dot" cx="{cx}" cy="{cy + 8}" r="3"/>'
            '</g>'
            f'<text id="{mid}_clients" class="value small-value" x="{cx}" y="{cy + 40}"></text>')


def switch_marker(mid, cx, cy):
    """Network switch: a box with a row of ports in a circle, client count below."""
    ports = "".join(f'<circle class="dot" cx="{cx + dx}" cy="{cy + 2}" r="1.8"/>' for dx in (-8, -3, 2, 7))
    return (f'<g id="{mid}" class="device">'
            f'<circle cx="{cx}" cy="{cy}" r="24"/>'
            f'<rect x="{cx - 13}" y="{cy - 6}" width="26" height="14" rx="2"/>{ports}'
            '</g>'
            f'<text id="{mid}_clients" class="value small-value" x="{cx}" y="{cy + 40}"></text>')


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
       '.room{fill:#1d2b44;stroke:#50627e;stroke-width:8}',
       '.outdoor{fill:#182a2a;stroke:#4f6f62;stroke-width:4;stroke-dasharray:14 10}',
       '.label{font:600 30px sans-serif;fill:#e8edf4;text-anchor:middle;dominant-baseline:middle;pointer-events:none}',
       '.outdoor-label{font:italic 26px sans-serif;fill:#7fa392}',
       '.camera circle{fill:#121a2a;stroke:#c9d3df;stroke-width:4}',
       '.camera rect,.camera polygon{fill:#c9d3df}',
       '.appliance circle{fill:#121a2a;stroke:#c9d3df;stroke-width:4}',
       '.appliance path{fill:#c9d3df}',
       '.appliance path.handle{fill:none;stroke:#c9d3df;stroke-width:3}',
       '.small-value{font-size:20px}',
       '.ap circle{fill:#121a2a;stroke:#c9d3df;stroke-width:4}',
       '.ap circle.dot{fill:#c9d3df;stroke:none}',
       '.ap path{fill:none;stroke:#c9d3df;stroke-width:3;stroke-linecap:round}',
       '.thermometer circle{fill:#121a2a;stroke:#c9d3df;stroke-width:4}',
       '.thermometer rect,.thermometer circle.bulb{fill:#c9d3df;stroke:none}',
       '.device circle{fill:#121a2a;stroke:#c9d3df;stroke-width:4}',
       '.device rect{fill:none;stroke:#c9d3df;stroke-width:3}',
       '.device circle.dot{fill:#c9d3df;stroke:none}',
       '.speaker circle{fill:#121a2a;stroke:#c9d3df;stroke-width:4}',
       '.speaker rect,.speaker circle.cone{fill:none;stroke:#c9d3df;stroke-width:2.5}',
       '.speaker circle.dot{fill:#c9d3df;stroke:none}',
       '.value{font:500 26px sans-serif;fill:#9aa7b8;text-anchor:middle;dominant-baseline:middle;pointer-events:none}',
       '</style>']
for rid, label, x0, y0, x1, y1, kind in ROOMS:
    x, y, w, h = x0 - OX, y0 - OY, x1 - x0, y1 - y0
    out.append(f'<rect id="{rid}" class="{kind}" x="{x}" y="{y}" width="{w}" height="{h}"/>')
for rid, label, x0, y0, x1, y1, kind in ROOMS:
    cls = "label outdoor-label" if kind == "outdoor" else "label"
    out.append(f'<text id="{rid}_label" class="{cls}" x="{(x0+x1)/2-OX:.0f}" y="{(y0+y1)/2-OY:.0f}">{label}</text>')
# placeholders that ha-floorplan fills with live values via floorplan.text_set
for rid, label, x0, y0, x1, y1, kind in ROOMS:
    if rid in TEXT_SLOTS:
        out.append(f'<text id="{rid}_temp" class="value" x="{(x0+x1)/2-OX:.0f}" y="{(y0+y1)/2-OY+42:.0f}"></text>')
# camera markers outside the walls: id, x, y (drawing coordinates)
CAMERAS = [("camera_c120", 618, 210)]  # C120 on the outside of the living-room wall on the entrance side, aimed at the ground
for cid, cx, cy in CAMERAS:
    x, y = cx - OX, cy - OY
    out.append(f'<g id="{cid}" class="camera">'
               f'<circle cx="{x}" cy="{y}" r="24"/>'
               f'<rect x="{x - 12}" y="{y - 8}" width="17" height="16" rx="2"/>'
               f'<polygon points="{x + 5},{y - 4} {x + 13},{y - 9} {x + 13},{y + 9} {x + 5},{y + 4}"/>'
               '</g>')
# Silvia espresso machine on the kitchen counter along the wall to the piano room
KX, KY = 568 - OX, 1110 - OY
out.append(f'<g id="kaffemaskin" class="appliance">'
           f'<circle cx="{KX}" cy="{KY}" r="24"/>'
           f'<path d="M{KX - 11},{KY - 7} h17 v9 a8,8 0 0 1 -8,8 h-1 a8,8 0 0 1 -8,-8 z"/>'
           f'<path class="handle" d="M{KX + 6},{KY - 4} a5,5 0 0 1 0,9"/>'
           '</g>')
out.append(f'<text id="kaffemaskin_power" class="value small-value" x="{KX}" y="{KY + 42}"></text>')
out.append(wifi_marker("ap_u6_lr", 898 - OX, 330 - OY))
# USW-Lite-8-PoE in the living room against the hall wall, with the piano room behind it
out.append(switch_marker("usw_lite_8_poe", 760 - OX, 680 - OY))
# outdoor temperature (Ngenic controller) outside the house, left of the entrance
TX, TY = 310 - OX, 260 - OY
out.append(f'<g id="utetemp" class="thermometer">'
           f'<circle cx="{TX}" cy="{TY}" r="24"/>'
           f'<rect x="{TX - 3}" y="{TY - 14}" width="6" height="18" rx="3"/>'
           f'<circle class="bulb" cx="{TX}" cy="{TY + 8}" r="6"/>'
           '</g>')
out.append(f'<text id="utetemp_value" class="value" x="{TX}" y="{TY + 44}"></text>')
# Sonos: soundbar under the TV against the hall, kitchen speaker on the wall to the coat room
out.append(speaker_marker("sonos_vardagsrum", 960 - OX, 705 - OY, soundbar=True))
out.append(speaker_marker("sonos_kok", 440 - OX, 972 - OY))
out.append('</svg>')
open(sys.argv[1], "w").write("\n".join(out) + "\n")
