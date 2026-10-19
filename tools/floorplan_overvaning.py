"""Generate config/www/floorplan/overvaning.svg (upstairs plan for ha-floorplan).

Room coordinates were measured on a photo of the construction drawing.
usage: python tools/floorplan_overvaning.py config/www/floorplan/overvaning.svg
"""
import sys
OX, OY = -260, -180  # offset so the plan (garage included) starts near 0,0
# id, label, x0, y0, x1, y1, kind
ROOMS = [
    # detached garage up to the left, placed from the basement drawing
    ("garage", "Garage", -186, -165, 394, 159, "building"),
    ("vardagsrum", "Vardagsrum", 652, 80, 1145, 742, "room"),
    ("pizzerian", "Altan / Pizzeria", 1145, 80, 1480, 742, "outdoor"),
    ("entre", "Entré", 440, 560, 652, 742, "room"),
    ("trappa", "Trappa", 285, 555, 440, 742, "outdoor"),
    ("wc", "WC", 175, 745, 290, 930, "room"),
    ("kapprum_hall", "Kapprum/hall", 290, 745, 1482, 935, "room"),
    ("bad", "Bad", 1482, 745, 1700, 935, "room"),
    ("kok", "Kök", 130, 935, 605, 1325, "room"),
    ("pianorum", "Pianorum", 605, 935, 872, 1325, "room"),
    ("fritiofs_rum", "Fritiofs rum", 872, 935, 1112, 1325, "room"),
    ("henriks_rum", "Henriks rum", 1112, 935, 1410, 1325, "room"),
    ("master_bedroom", "Master bedroom", 1410, 935, 1728, 1325, "room"),
]
# non-rectangular areas: id, label, outline as (x, y) points, label position, kind
AREAS = [
    ("parkering", "Parkering", [(-235, 178), (600, 178), (600, 538), (245, 538), (245, 729), (-235, 729)], (420, 480), "outdoor"),
]
TEXT_SLOTS = {"vardagsrum"}
W, H = 2008, 1525
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
       '.building{fill:#1a2333;stroke:#50627e;stroke-width:8}',
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
       '.motion{fill:none;stroke:none;pointer-events:none}',
       '.sensor circle{fill:#121a2a;stroke:#c9d3df;stroke-width:4}',
       '.sensor circle.dot{fill:#c9d3df;stroke:none}',
       '.sensor path{fill:none;stroke:#c9d3df;stroke-width:3;stroke-linecap:round}',
       '.thermometer rect,.thermometer circle.bulb{fill:#c9d3df;stroke:none}',
       '.device circle{fill:#121a2a;stroke:#c9d3df;stroke-width:4}',
       '.device rect{fill:none;stroke:#c9d3df;stroke-width:3}',
       '.device circle.dot{fill:#c9d3df;stroke:none}',
       '.device path.bolt{fill:#c9d3df}',
       '.car .body{fill:#2a3a57;stroke:#c9d3df;stroke-width:4}',
       '.car .glass{fill:#121a2a}',
       '.r5-body,.r5-mirror{fill:#eceef1;stroke:#8a96a6;stroke-width:1.5}',
       '.r5-glass{fill:#1b2330}',
       '.r5-roof{fill:#15171c;stroke:#c0392b;stroke-width:3}',
       '.r5-light{fill:#c9d3df;stroke:#5a6678;stroke-width:1}',
       '.car-name{font:600 19px sans-serif;fill:#e8edf4;paint-order:stroke;stroke:#121a2a;stroke-width:4px;text-anchor:middle;dominant-baseline:middle;pointer-events:none}',
       '.car-value{font:600 19px sans-serif;fill:#e8edf4;paint-order:stroke;stroke:#121a2a;stroke-width:4px;text-anchor:middle;dominant-baseline:middle;pointer-events:none}',
       '.car .bolt{fill:#2f9e8a}',
       '.speaker circle{fill:#121a2a;stroke:#c9d3df;stroke-width:4}',
       '.speaker rect,.speaker circle.cone{fill:none;stroke:#c9d3df;stroke-width:2.5}',
       '.speaker circle.dot{fill:#c9d3df;stroke:none}',
       '.value{font:500 26px sans-serif;fill:#9aa7b8;text-anchor:middle;dominant-baseline:middle;pointer-events:none}',
       '</style>']
for rid, label, x0, y0, x1, y1, kind in ROOMS:
    x, y, w, h = x0 - OX, y0 - OY, x1 - x0, y1 - y0
    out.append(f'<rect id="{rid}" class="{kind}" x="{x}" y="{y}" width="{w}" height="{h}"/>')
for aid, label, pts, (lx, ly), kind in AREAS:
    d = " ".join(f"{x - OX},{y - OY}" for x, y in pts)
    out.append(f'<polygon id="{aid}" class="{kind}" points="{d}"/>')
    out.append(f'<text id="{aid}_label" class="label outdoor-label" x="{lx - OX}" y="{ly - OY}">{label}</text>')
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
# presence sensor (Aqara FP2) in the garage, mid-wall towards the living room and the path behind the house;
# the frame over the garage lights up together with it
GX0, GY0, GX1, GY1 = next((x0, y0, x1, y1) for rid, _, x0, y0, x1, y1, _ in ROOMS if rid == "garage")
out.append(f'<rect id="garage_motion" class="motion" x="{GX0 - OX}" y="{GY0 - OY}" width="{GX1 - GX0}" height="{GY1 - GY0}"/>')
SX, SY = GX1 - 26 - OX, (GY0 + GY1) // 2 - OY
out.append(f'<g id="garage_sensor" class="sensor">'
           f'<circle cx="{SX}" cy="{SY}" r="22"/>'
           f'<circle class="dot" cx="{SX + 7}" cy="{SY}" r="3.5"/>'
           f'<path d="M{SX - 1},{SY - 8} a10,10 0 0 0 0,16 M{SX - 7},{SY - 13} a16,16 0 0 0 0,26"/>'
           '</g>')
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


def car_marker(mid, name, cx, cy, image=None, style=None):
    """Car seen from above in a parking spot, nose to the right; name, charge and a bolt while charging.

    image is a top view with the nose up (the Tesla card's picture); without it the car is drawn.
    """
    x0, y0, w, h = cx - 55, cy - 135, 110, 270  # drawn nose up, then turned a quarter clockwise
    tx = cx - 36  # the texts sit over the roof
    if image:
        iw = h * 357 / 720  # the picture is 357x720 including the mirrors
        body = f'<image href="{image}" x="{cx - iw / 2:.1f}" y="{y0}" width="{iw:.1f}" height="{h}"/>'
    elif style == "r5":
        # white Renault 5 E-Tech, 3.92 x 1.77 m against the Tesla's 4.72 m: black roof with the red trim
        w, h = 100, 224
        x0, y0 = cx - w // 2, cy - h // 2
        tx = cx - 20
        body = (f'<rect x="{x0 - 7}" y="{y0 + 72}" width="{w + 14}" height="12" rx="5" class="r5-mirror"/>'
                f'<rect class="r5-body" x="{x0}" y="{y0}" width="{w}" height="{h}" rx="24"/>'
                f'<rect class="r5-light" x="{x0 + 8}" y="{y0 + 5}" width="20" height="6" rx="3"/>'
                f'<rect class="r5-light" x="{x0 + w - 28}" y="{y0 + 5}" width="20" height="6" rx="3"/>'
                f'<path class="r5-glass" d="M{x0 + 8},{y0 + 62} Q{cx},{y0 + 52} {x0 + w - 8},{y0 + 62} L{x0 + w - 12},{y0 + 86} L{x0 + 12},{y0 + 86} z"/>'
                f'<rect class="r5-roof" x="{x0 + 11}" y="{y0 + 86}" width="{w - 22}" height="92" rx="6"/>'
                f'<path class="r5-glass" d="M{x0 + 12},{y0 + 178} L{x0 + w - 12},{y0 + 178} L{x0 + w - 14},{y0 + 196} Q{cx},{y0 + 201} {x0 + 14},{y0 + 196} z"/>')
    else:
        body = (f'<rect class="body" x="{x0}" y="{y0}" width="{w}" height="{h}" rx="32"/>'
                f'<path class="glass" d="M{x0 + 12},{y0 + 92} Q{cx},{y0 + 70} {x0 + w - 12},{y0 + 92} L{x0 + w - 20},{y0 + 120} Q{cx},{y0 + 108} {x0 + 20},{y0 + 120} z"/>'
                f'<path class="glass" d="M{x0 + 18},{y0 + 222} Q{cx},{y0 + 214} {x0 + w - 18},{y0 + 222} L{x0 + w - 14},{y0 + 244} Q{cx},{y0 + 252} {x0 + 14},{y0 + 244} z"/>')
    return (f'<g id="{mid}_slot" class="slot"><g id="{mid}" class="car">'
            f'<g transform="rotate(90 {cx} {cy})">{body}'
            '</g>'
            f'<text class="car-name" x="{tx}" y="{cy - 24}">{name}</text>'
            f'<text id="{mid}_value" class="car-value" x="{tx}" y="{cy + 2}"></text>'
            f'<path id="{mid}_bolt" class="bolt" d="M{tx + 3},{cy + 16} L{tx - 8},{cy + 32} h8 l-3,12 L{tx + 8},{cy + 27} h-8 z"/>'
            '</g></g>')


# the cars on the parking, shown only while they are at home; a plugged-in car is moved by
# the stylesheet to the spot by the charger, centred at (90, 640)
out.append(car_marker("car_tesla", "Otto", -60 - OX, 265 - OY, image="/local/tesla-card/model3_top.webp?v=2"))
out.append(car_marker("car_jean_luc", "Jean-Luc", -60 - OX, 410 - OY, style="r5"))
# Easee charger on the outside of the WC wall, towards the parking
EX, EY = 140 - OX, 800 - OY
out.append(f'<g id="laddbox" class="device">'
           f'<circle cx="{EX}" cy="{EY}" r="24"/>'
           f'<path class="bolt" d="M{EX + 3},{EY - 14} L{EX - 8},{EY + 2} h8 l-3,12 L{EX + 8},{EY - 3} h-8 z"/>'
           '</g>')
out.append(f'<text id="laddbox_value" class="value small-value" x="{EX}" y="{EY - 40}"></text>')
out.append('</svg>')
open(sys.argv[1], "w").write("\n".join(out) + "\n")
