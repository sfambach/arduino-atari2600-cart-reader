# Schaltplan: schaltbare Cartridge-Versorgung (BC327, Polyfuse, Spannungsmessung)
import sys
W, H = 1100, 640
o = []
def ln(pts, c='#222', w=2.2):
    o.append('<polyline points="' + ' '.join(f'{x},{y}' for x, y in pts) + f'" fill="none" stroke="{c}" stroke-width="{w}"/>')
def t(x, y, s, size=16, c='#222', a='middle', b=False):
    o.append(f'<text x="{x}" y="{y}" font-family="DejaVu Sans, sans-serif" font-size="{size}" fill="{c}" text-anchor="{a}"' + (' font-weight="bold"' if b else '') + f'>{s}</text>')
def dot(x, y): o.append(f'<circle cx="{x}" cy="{y}" r="5" fill="#222"/>')
def res_v(x, y1, y2, label, val):
    m = (y1 + y2) / 2
    ln([(x, y1), (x, m - 30)]); ln([(x, m + 30), (x, y2)])
    o.append(f'<rect x="{x-11}" y="{m-30}" width="22" height="60" fill="white" stroke="#222" stroke-width="2.2"/>')
    t(x + 18, m - 4, label, 15, a='start', b=True); t(x + 18, m + 16, val, 15, a='start')
def res_h(x1, x2, y, label, val):
    m = (x1 + x2) / 2
    ln([(x1, y), (m - 30, y)]); ln([(m + 30, y), (x2, y)])
    o.append(f'<rect x="{m-30}" y="{y-11}" width="60" height="22" fill="white" stroke="#222" stroke-width="2.2"/>')
    t(m, y - 18, label, 15, b=True); t(m, y + 32, val, 15)
def gnd(x, y):
    ln([(x, y), (x, y + 12)]); ln([(x - 16, y + 12), (x + 16, y + 12)]); ln([(x - 10, y + 18), (x + 10, y + 18)]); ln([(x - 4, y + 24), (x + 4, y + 24)])
def port(x, y, text, side, c):
    w = 9 * len(text) + 24
    x0 = x - w if side == 'left' else x
    o.append(f'<rect x="{x0}" y="{y-16}" width="{w}" height="32" rx="6" fill="{c}" stroke="#555" stroke-width="1.5"/>')
    t(x0 + w / 2, y + 6, text, 15, b=True)
ARD, SLOT = '#dbe8f7', '#f3e6c4'
t(W / 2, 40, 'Schaltbare Cartridge-Versorgung', 24, b=True)
t(W / 2, 68, 'Arduino-Pin LOW = Cartridge an, HIGH = aus', 16, '#555')
Y5 = 140
port(60, Y5, 'Arduino 5V', 'right', ARD)
ln([(172, Y5), (230, Y5)])
o.append(f'<rect x="230" y="{Y5-12}" width="70" height="24" fill="white" stroke="#222" stroke-width="2.2"/>')
ln([(240, Y5 + 12), (290, Y5 - 12)], w=1.6)
t(265, Y5 - 22, 'F1', 15, b=True); t(265, Y5 + 36, 'Polyfuse 200 mA', 14)
ln([(300, Y5), (520, Y5)]); dot(420, Y5)
EX, BX, BY = 520, 470, 250
ln([(EX, Y5), (EX, 205)])
o.append(f'<circle cx="{EX-12}" cy="{BY}" r="44" fill="none" stroke="#222" stroke-width="2.2"/>')
ln([(BX + 18, BY - 26), (BX + 18, BY + 26)], w=4)
ln([(BX + 18, BY - 12), (EX, 205)]); ln([(BX + 18, BY + 12), (EX, 295)])
o.append(f'<polygon points="{BX+20},{BY-13} {BX+36},{BY-30} {BX+40},{BY-18}" fill="#222"/>')
t(EX + 14, 215, 'E', 14, a='start'); t(EX + 14, 300, 'C', 14, a='start'); t(BX + 4, BY + 44, 'B', 14, a='end')
t(EX + 50, BY - 4, 'Q1', 16, a='start', b=True); t(EX + 50, BY + 18, 'BC327 (PNP)', 15, a='start')
ln([(BX + 18, BY), (420, BY)]); dot(420, BY)
res_v(420, Y5, BY, 'R4', '10 kΩ')
res_h(220, 420, BY, 'R3', '1 kΩ')
port(220, BY, 'Arduino Schaltpin', 'left', ARD)
t(130, BY + 40, 'Mega D8 · Uno/Nano D10', 14, '#555')
YC = 400
ln([(EX, 295), (EX, YC)]); dot(EX, YC)
ln([(EX, YC), (880, YC)]); dot(640, YC); dot(760, YC)
port(880, YC, 'Slot Pin 23 (+5 V)', 'right', SLOT)
for x, lab, val in ((640, 'C2', '100 nF'), (760, 'R6', '100 kΩ')):
    if lab == 'C2':
        ln([(x, YC), (x, 470)]); ln([(x - 22, 470), (x + 22, 470)], w=3); ln([(x - 22, 482), (x + 22, 482)], w=3); ln([(x, 482), (x, 530)])
        t(x + 30, 470, lab, 15, a='start', b=True); t(x + 30, 492, val, 15, a='start')
    else:
        res_v(x, YC, 530, lab, val)
    gnd(x, 530)
dot(EX, YC)
res_h(320, EX, YC, 'R5', '10 kΩ')
port(320, YC, 'Arduino A0 (Messung)', 'left', ARD)
# TO-92 from the front (flat side facing the viewer, legs down)
TX, TY = 760, 215
o.append(f'<path d="M {TX-38} {TY} A 38 38 0 0 1 {TX+38} {TY} Z" fill="#eee" stroke="#222" stroke-width="2.2"/>')
ln([(TX - 38, TY), (TX + 38, TY)], w=4)
for i, pin in enumerate('CBE'):
    x = TX - 20 + 20 * i
    ln([(x, TY), (x, TY + 40)], c='#888', w=3)
    t(x, TY + 60, pin, 16, b=True)
t(TX, TY - 50, 'BC327: flache Seite zu dir, Beine unten', 14, '#555')
t(TX, TY + 84, 'links C · Mitte B · rechts E', 14, '#222', b=True)
port(880, 560, 'Slot Pin 12 + 24', 'right', SLOT); gnd(860, 560); ln([(860, 560), (880, 560)])
t(W / 2, 612, 'Pinbelegung des BC327 je nach Hersteller im Datenblatt prüfen. Andere Arduino-/Slot-Pins wie in den Tabellen.', 14, '#555')
svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><rect width="100%" height="100%" fill="white"/>' + ''.join(o) + '</svg>'
open(sys.argv[1], 'w').write(svg)
