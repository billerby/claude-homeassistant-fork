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
out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
       '<style>',
       '.room{fill:#f4f1ea;stroke:#3a3a3a;stroke-width:8}',
       '.outdoor{fill:#e6efe1;stroke:#7a8a72;stroke-width:4;stroke-dasharray:14 10}',
       '.label{font:600 30px sans-serif;fill:#3a3a3a;text-anchor:middle;dominant-baseline:middle;pointer-events:none}',
       '.outdoor-label{font:italic 26px sans-serif;fill:#6b7a63}',
       '.camera circle{fill:#ffffff;stroke:#3a3a3a;stroke-width:4}',
       '.camera rect,.camera polygon{fill:#3a3a3a}',
       '.appliance circle{fill:#ffffff;stroke:#3a3a3a;stroke-width:4}',
       '.appliance path{fill:#3a3a3a}',
       '.appliance path.handle{fill:none;stroke:#3a3a3a;stroke-width:3}',
       '.small-value{font-size:20px}',
       '.value{font:500 26px sans-serif;fill:#5a5a5a;text-anchor:middle;dominant-baseline:middle;pointer-events:none}',
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
CAMERAS = [("camera_c120", 618, 500)]  # C120 on the outside of the living-room wall by the entrance, aimed at the ground
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
out.append('</svg>')
open(sys.argv[1], "w").write("\n".join(out) + "\n")
