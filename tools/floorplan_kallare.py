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


out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
       '<style>',
       '.room{fill:#f4f1ea;stroke:#3a3a3a;stroke-width:6}',
       '.outdoor{fill:#e6efe1;stroke:#7a8a72;stroke-width:3;stroke-dasharray:12 8}',
       '.label{font:600 24px sans-serif;fill:#3a3a3a;text-anchor:middle;dominant-baseline:middle;pointer-events:none}',
       '.outdoor-label{font:italic 22px sans-serif;fill:#6b7a63}',
       '.small{font-size:17px}',
       '.motion{fill:none;stroke:none;pointer-events:none}',
       '.value{font:500 22px sans-serif;fill:#5a5a5a;text-anchor:middle;dominant-baseline:middle;pointer-events:none}',
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
out.append('</svg>')
open(sys.argv[1], "w").write("\n".join(out) + "\n")
