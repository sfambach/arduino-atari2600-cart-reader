# 2D-Massskizze Atari-2600-Cartridge-Slot nach Stefans Messung (25.10.2026)
import sys
L, W, H = 51.2, 9.0, 19.0          # Gesamtlaenge, -breite, Hoehe ueber Platine
INNER = 37.0                        # Steckleiste ohne Laschen
EAR = (L - INNER) / 2               # Laschenlaenge (gemessen 7, Summe passt nur mit 7,1)
EAR_W = 6.4                         # Laschenbreite (Annahme: "6,4 dick" = Breite)
HOLE_D, HOLE_EDGE = 2.8, 1.5        # Loch, Abstand Lochrand zur Aussenkante
HOLE_X = HOLE_EDGE + HOLE_D / 2
EAR_Z0, EAR_TOP_GAP = 10.4, 3.4     # Lasche ab Platine, Absatz bis Oberkante
EAR_Z1 = H - EAR_TOP_GAP
PITCH, ROW, NPIN, PIN_D = 2.54, 5.5, 12, 0.5
S = 9                               # px pro mm
out = []
def ln(x1, y1, x2, y2, c='#222', w=1.6, dash=None):
    out.append(f'<line x1="{x1*S:.1f}" y1="{y1*S:.1f}" x2="{x2*S:.1f}" y2="{y2*S:.1f}" stroke="{c}" stroke-width="{w}"' + (f' stroke-dasharray="{dash}"' if dash else '') + '/>')
def rect(x, y, w, h, fill='#e8e8e8', c='#222', dash=None):
    out.append(f'<rect x="{x*S:.1f}" y="{y*S:.1f}" width="{w*S:.1f}" height="{h*S:.1f}" fill="{fill}" stroke="{c}" stroke-width="1.6"' + (f' stroke-dasharray="{dash}"' if dash else '') + '/>')
def circ(x, y, d, fill='white', c='#222'):
    out.append(f'<circle cx="{x*S:.1f}" cy="{y*S:.1f}" r="{d/2*S:.1f}" fill="{fill}" stroke="{c}" stroke-width="1.4"/>')
def txt(x, y, t, size=13, c='#222', anchor='middle', rot=0, bold=False):
    tr = f' transform="rotate({rot} {x*S:.1f} {y*S:.1f})"' if rot else ''
    out.append(f'<text x="{x*S:.1f}" y="{y*S:.1f}" font-family="DejaVu Sans, sans-serif" font-size="{size}" fill="{c}" text-anchor="{anchor}"' + (' font-weight="bold"' if bold else '') + f'{tr}>{t}</text>')
DIM = '#1f5fbf'
def dimh(x1, x2, y, t, c=DIM):
    ln(x1, y, x2, y, c, 1.1); ln(x1, y - .8, x1, y + .8, c, 1.1); ln(x2, y - .8, x2, y + .8, c, 1.1)
    txt((x1 + x2) / 2, y - .5, t, 12, c)
def dimv(x, y1, y2, t, c=DIM, left=True):
    ln(x, y1, x, y2, c, 1.1); ln(x - .8, y1, x + .8, y1, c, 1.1); ln(x - .8, y2, x + .8, y2, c, 1.1)
    txt(x - .6 if left else x + .6, (y1 + y2) / 2, t, 12, c, 'middle', -90 if left else 90)

pin_x0 = (L - (NPIN - 1) * PITCH) / 2
# --- Draufsicht ---
ox, oy = 8, 12
txt(ox + L / 2, oy - 6, 'Draufsicht (von oben, Cartridge-Seite)', 15, bold=True)
rect(ox, oy + (W - EAR_W) / 2, EAR, EAR_W); rect(ox + L - EAR, oy + (W - EAR_W) / 2, EAR, EAR_W)
rect(ox + EAR, oy, INNER, W)
rect(ox + EAR + 2, oy + W / 2 - 1.2, INNER - 4, 2.4, fill='#fafafa', dash='5,3')
txt(ox + L / 2, oy + W / 2 + .45, 'Schlitz (Maße offen)', 10, '#888')
for xh in (ox + HOLE_X, ox + L - HOLE_X):
    circ(xh, oy + W / 2, HOLE_D)
for i in range(NPIN):
    circ(ox + pin_x0 + i * PITCH, oy + W / 2 + ROW / 2, PIN_D, '#c47a00', '#c47a00')
    circ(ox + pin_x0 + i * PITCH, oy + W / 2 - ROW / 2, PIN_D, '#c47a00', '#c47a00')
txt(ox + pin_x0, oy + W / 2 + ROW / 2 + 2.3, '1', 11, '#c47a00'); txt(ox + pin_x0 + 11 * PITCH, oy + W / 2 + ROW / 2 + 2.3, '12', 11, '#c47a00')
txt(ox + pin_x0, oy + W / 2 - ROW / 2 - 1.2, '24', 11, '#c47a00'); txt(ox + pin_x0 + 11 * PITCH, oy + W / 2 - ROW / 2 - 1.2, '13', 11, '#c47a00')
dimh(ox, ox + L, oy + W + 7, f'{L:.1f}'.replace('.', ','))
dimh(ox, ox + EAR, oy + W + 4, f'{EAR:.1f}'.replace('.', ','))
dimh(ox + EAR, ox + L - EAR, oy + W + 4, f'{INNER:.0f}')
dimh(ox + L - EAR, ox + L, oy + W + 4, f'{EAR:.1f}'.replace('.', ','))
dimh(ox, ox + HOLE_X, oy - 2.5, f'{HOLE_X:.1f}'.replace('.', ','))
txt(ox + HOLE_X, oy + W / 2 - 2.2, 'Ø2,8', 11, DIM)
dimv(ox + L + 3, oy, oy + W, '9', left=False)
dimv(ox + L + 6.5, oy + (W - EAR_W) / 2, oy + (W + EAR_W) / 2, '6,4 ?', c='#c0392b', left=False)
dimv(ox - 2.5, oy + W / 2 - ROW / 2, oy + W / 2 + ROW / 2, '5,5')
dimh(ox + pin_x0, ox + pin_x0 + PITCH, oy + W + 1.6, '2,54')
# --- Vorderansicht ---
fx, fy = 8, 52
txt(fx + L / 2, fy - 22, 'Vorderansicht (lange Seite)', 15, bold=True)
base = fy
ln(fx - 4, base, fx + L + 4, base, '#2e7d32', 2.2); txt(fx + L + 4.5, base + .4, 'Platine', 11, '#2e7d32', 'start')
rect(fx + EAR, base - H, INNER, H)
for x0 in (fx, fx + L - EAR):
    rect(x0, base - EAR_Z1, EAR, EAR_Z1 - EAR_Z0)
    xh = x0 + (HOLE_X if x0 == fx else EAR - HOLE_X)
    ln(xh - HOLE_D / 2, base - EAR_Z1, xh - HOLE_D / 2, base - EAR_Z0, '#666', 1, '3,2'); ln(xh + HOLE_D / 2, base - EAR_Z1, xh + HOLE_D / 2, base - EAR_Z0, '#666', 1, '3,2')
for i in range(NPIN):
    ln(fx + pin_x0 + i * PITCH, base, fx + pin_x0 + i * PITCH, base + 3, '#c47a00', 1.6)
dimv(fx - 2.5, base - H, base, '19')
dimv(fx + L + 2.5, base - EAR_Z0, base, '10,4', left=False)
dimv(fx + L + 2.5, base - H, base - EAR_Z1, '3,4', left=False)
dimv(fx + L + 6, base - EAR_Z1, base - EAR_Z0, f'{EAR_Z1-EAR_Z0:.1f} ?'.replace('.', ','), c='#c0392b', left=False)
# --- Seitenansicht ---
sx, sy = 8, 82
txt(sx + 12, sy - 22, 'Seitenansicht (kurze Seite)', 15, bold=True)
rect(sx + (W - EAR_W) / 2, sy - EAR_Z1, EAR_W, EAR_Z1 - EAR_Z0)
rect(sx, sy - H, W, H, fill='#e8e8e8')
ln(sx + (W - EAR_W) / 2, sy - EAR_Z1, sx + (W - EAR_W) / 2, sy - EAR_Z0, '#222', 1.2)
ln(sx + (W + EAR_W) / 2, sy - EAR_Z1, sx + (W + EAR_W) / 2, sy - EAR_Z0, '#222', 1.2)
ln(sx - 4, sy, sx + W + 4, sy, '#2e7d32', 2.2)
for yy in (W / 2 - ROW / 2, W / 2 + ROW / 2):
    ln(sx + yy, sy, sx + yy, sy + 3, '#c47a00', 1.6)
dimh(sx, sx + W, sy + 6, '9')
dimh(sx + W / 2 - ROW / 2, sx + W / 2 + ROW / 2, sy + 3.8, '5,5')
txt(sx + W / 2, sy - H - 1, '24 … 13', 10, '#c47a00')
# --- Hinweise ---
nx, ny = 32, 63
notes = [('Offene Punkte (rot):', '#c0392b', True),
         ('1. 7 + 37 + 7 = 51 mm, gemessen 51,2 mm.', '#222', False),
         ('   Gezeichnet mit Laschen je 7,1 mm.', '#222', False),
         ('2. „6,4 dick“ als Laschenbreite gelesen:', '#222', False),
         ('   (6,4 − 2,8) / 2 = 1,8 mm ≈ deine 2 mm.', '#222', False),
         ('3. Laschenhöhe: 19 − 10,4 − 3,4 = 5,2 mm.', '#222', False),
         ('   Ist die Lasche 5,2 oder 6,4 mm hoch?', '#222', False),
         ('4. Lochmitte = 1,5 + 1,4 = 2,9 mm von außen.', '#222', False),
         ('5. Schlitz für die Cartridge-Platine:', '#222', False),
         ('   Länge und Breite fehlen noch.', '#222', False),
         ('Maße in mm. Pins Ø0,5, Raster 2,54.', '#666', False)]
for i, (t, c, b) in enumerate(notes):
    txt(nx, ny + i * 2.3, t, 12, c, 'start', bold=b)
w, h = 78 * S, 100 * S
svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><rect width="100%" height="100%" fill="white"/>' + \
      f'<text x="{w/2}" y="34" font-family="DejaVu Sans, sans-serif" font-size="20" font-weight="bold" text-anchor="middle">Atari 2600 Cartridge-Slot – Maßskizze v1 (25.10.2026)</text>' + ''.join(out) + '</svg>'
open(sys.argv[1], 'w').write(svg)
