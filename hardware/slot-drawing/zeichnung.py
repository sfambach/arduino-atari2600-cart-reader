# 2D-Massskizze Atari-2600-Cartridge-Slot, von Hand gemessen (Stefan, 25.10.2026)
import sys
L, W = 51.3, 9.0
SLOT_L = 33.3                       # Schlitzlaenge (Stefan: "Schlitzbreite")
UP_H = 10.1                         # Oberteil (36,8 lang) ueber dem Unterteil
INNER = 36.8                        # Steckleiste ohne Laschen
LOW_L, LOW_H = 35.0, 6.0            # schmaler Unterteil unter den Laschen
H = LOW_H + UP_H                    # Hoehe ab Unterkante Slot
EAR = (L - INNER) / 2
EAR_W = 7.1                         # Laschenbreite quer zu den Pinreihen
HOLE_D, HOLE_EDGE = 2.8, 1.5
HOLE_X = HOLE_EDGE + HOLE_D / 2
EAR_H = 6.5
EAR_Z0 = LOW_H                      # Laschen schliessen unten buendig mit dem Unterteil ab
EAR_Z1 = EAR_Z0 + EAR_H
EAR_TOP_GAP = H - EAR_Z1            # bestaetigt 3,5 bis 3,6
STRIP_W = 2.5                       # Buchsenleiste einreihig, typisch
PITCH, ROW, NPIN, PIN_D = 2.54, 5.5, 12, 0.5
STRIP_L = NPIN * PITCH
S = 9
RED, DIM, PIN, ADPC = '#c0392b', '#1f5fbf', '#c47a00', '#d9c7a0'
out = []
def f(v): return f'{v:.1f}'.replace('.', ',').replace(',0', '') if abs(v - round(v)) < 1e-6 else f'{v:.1f}'.replace('.', ',')
def ln(x1, y1, x2, y2, c='#222', w=1.6, dash=None):
    out.append(f'<line x1="{x1*S:.1f}" y1="{y1*S:.1f}" x2="{x2*S:.1f}" y2="{y2*S:.1f}" stroke="{c}" stroke-width="{w}"' + (f' stroke-dasharray="{dash}"' if dash else '') + '/>')
def rect(x, y, w, h, fill='#e8e8e8', c='#222', dash=None):
    out.append(f'<rect x="{x*S:.1f}" y="{y*S:.1f}" width="{w*S:.1f}" height="{h*S:.1f}" fill="{fill}" stroke="{c}" stroke-width="1.6"' + (f' stroke-dasharray="{dash}"' if dash else '') + '/>')
def circ(x, y, d, fill='white', c='#222'):
    out.append(f'<circle cx="{x*S:.1f}" cy="{y*S:.1f}" r="{d/2*S:.1f}" fill="{fill}" stroke="{c}" stroke-width="1.4"/>')
def txt(x, y, t, size=13, c='#222', anchor='middle', rot=0, bold=False):
    tr = f' transform="rotate({rot} {x*S:.1f} {y*S:.1f})"' if rot else ''
    out.append(f'<text x="{x*S:.1f}" y="{y*S:.1f}" font-family="DejaVu Sans, sans-serif" font-size="{size}" fill="{c}" text-anchor="{anchor}"' + (' font-weight="bold"' if bold else '') + f'{tr}>{t}</text>')
def dimh(x1, x2, y, t, c=DIM):
    ln(x1, y, x2, y, c, 1.1); ln(x1, y - .8, x1, y + .8, c, 1.1); ln(x2, y - .8, x2, y + .8, c, 1.1)
    txt((x1 + x2) / 2, y - .5, t, 12, c)
def dimv(x, y1, y2, t, c=DIM, left=True):
    ln(x, y1, x, y2, c, 1.1); ln(x - .8, y1, x + .8, y1, c, 1.1); ln(x - .8, y2, x + .8, y2, c, 1.1)
    txt(x - .6 if left else x + .6, (y1 + y2) / 2, t, 12, c, 'middle', -90 if left else 90)
pin_x0 = (L - (NPIN - 1) * PITCH) / 2
def pins(ox, cy):
    for i in range(NPIN):
        for dy in (ROW / 2, -ROW / 2):
            circ(ox + pin_x0 + i * PITCH, cy + dy, PIN_D, PIN, PIN)

# --- Draufsicht ---
ox, oy = 8, 13
txt(ox + L / 2, oy - 5.5, 'Draufsicht (Cartridge-Seite)', 15, bold=True)
rect(ox, oy + (W - EAR_W) / 2, EAR, EAR_W); rect(ox + L - EAR, oy + (W - EAR_W) / 2, EAR, EAR_W)
rect(ox + EAR, oy, INNER, W)
rect(ox + (L - SLOT_L) / 2, oy + W / 2 - 1.2, SLOT_L, 2.4, fill='#fafafa', dash='5,3')
txt(ox + L / 2, oy + W / 2 + .45, 'Schlitz (Breite offen)', 10, '#888')
dimh(ox + (L - SLOT_L) / 2, ox + (L + SLOT_L) / 2, oy + 1.4, f(SLOT_L))
for xh in (ox + HOLE_X, ox + L - HOLE_X):
    circ(xh, oy + W / 2, HOLE_D)
dimh(ox, ox + L, oy + W + 6, f(L))
dimh(ox, ox + EAR, oy + W + 3, f(EAR)); dimh(ox + EAR, ox + L - EAR, oy + W + 3, f(INNER)); dimh(ox + L - EAR, ox + L, oy + W + 3, f(EAR))
dimh(ox, ox + HOLE_X, oy - 2.2, f(HOLE_X))
txt(ox + HOLE_X, oy + W / 2 - 2.2, 'Ø2,8', 11, DIM)
dimv(ox + L + 3, oy, oy + W, '9', left=False)
dimv(ox + L + 6.5, oy + (W - EAR_W) / 2, oy + (W + EAR_W) / 2, f(EAR_W), left=False)

# --- Vorderansicht ---
fx, base = 8, 60
txt(fx + L / 2, base - H - 3, 'Vorderansicht (lange Seite)', 15, bold=True)
ln(fx - 4, base, fx + L + 4, base, '#2e7d32', 2.2); txt(fx + L + 4.5, base + .4, 'Platine / Auflage', 11, '#2e7d32', 'start')
rect(fx + (L - LOW_L) / 2, base - LOW_H, LOW_L, LOW_H)
rect(fx + EAR, base - H, INNER, H - LOW_H)
for x0 in (fx, fx + L - EAR):
    rect(x0, base - EAR_Z1, EAR, EAR_Z1 - EAR_Z0)
    xh = x0 + (HOLE_X if x0 == fx else EAR - HOLE_X)
    for s in (-1, 1):
        ln(xh + s * HOLE_D / 2, base - EAR_Z1, xh + s * HOLE_D / 2, base - EAR_Z0, '#666', 1, '3,2')
for i in range(NPIN):
    ln(fx + pin_x0 + i * PITCH, base, fx + pin_x0 + i * PITCH, base + 3, PIN, 1.6)
dimv(fx - 2.5, base - H, base, f(H))
dimv(fx + L + 2.5, base - EAR_Z0, base, f(EAR_Z0), left=False)
dimv(fx + (L - LOW_L) / 2 - 2, base - LOW_H, base, f(LOW_H))
dimv(fx + L + 2.5, base - H, base - EAR_Z1, f(EAR_TOP_GAP), left=False)
dimv(fx - 5.5, base - H, base - LOW_H, f(UP_H))
dimv(fx + L + 6, base - EAR_Z1, base - EAR_Z0, f(EAR_H), left=False)
dimh(fx + (L - LOW_L) / 2, fx + (L + LOW_L) / 2, base - LOW_H + 2.2, '35')

# --- Seitenansicht ---
sx, sb = 8, 92
txt(sx + 14, sb - H - 3, 'Seitenansicht (kurze Seite)', 15, bold=True)
ln(sx - 4, sb, sx + W + 4, sb, '#2e7d32', 2.2)
for yy in (W / 2 - ROW / 2, W / 2 + ROW / 2):
    ln(sx + yy, sb, sx + yy, sb + 3, PIN, 1.6)
rect(sx, sb - LOW_H, W, LOW_H)
rect(sx, sb - H, W, H - LOW_H)
rect(sx + (W - EAR_W) / 2, sb - EAR_Z1, EAR_W, EAR_Z1 - EAR_Z0)
dimh(sx, sx + W, sb + 6.5, '9')
dimh(sx + W / 2 - ROW / 2, sx + W / 2 + ROW / 2, sb + 4.2, '5,5')
txt(sx + W + 1, sb - LOW_H / 2 + .4, 'Breite unten ?', 10, RED, 'start')

# --- Unteransicht ---
ux, uy = 8, 108
txt(ux + L / 2, uy - 3, 'Unteransicht (Platinenseite)', 15, bold=True)
rect(ux, uy + (W - EAR_W) / 2, EAR, EAR_W); rect(ux + L - EAR, uy + (W - EAR_W) / 2, EAR, EAR_W)
rect(ux + EAR, uy, INNER, W, fill='#f2f2f2')
rect(ux + (L - LOW_L) / 2, uy, LOW_L, W)
for yy in (W / 2 - ROW / 2, W / 2 + ROW / 2):
    pass
for xh in (ux + HOLE_X, ux + L - HOLE_X):
    circ(xh, uy + W / 2, HOLE_D)
pins(ux, uy + W / 2)
txt(ux + pin_x0, uy - .6, '1', 11, PIN); txt(ux + pin_x0 + 11 * PITCH, uy - .6, '12', 11, PIN)
txt(ux + pin_x0, uy + W + 1.9, '24', 11, PIN); txt(ux + pin_x0 + 11 * PITCH, uy + W + 1.9, '13', 11, PIN)
dimh(ux + pin_x0, ux + pin_x0 + PITCH, uy + W + 4.2, '2,54')
dimh(ux + (L - LOW_L) / 2, ux + (L + LOW_L) / 2, uy + W + 7, '35')
dimv(ux - 2.5, uy + W / 2 - ROW / 2, uy + W / 2 + ROW / 2, '5,5')

# --- Hinweise ---
nx, ny = 32, 77
notes = [('Offene Punkte (rot):', RED, True),
         ('1. Breite des 35er-Unterteils: gezeichnet 9.', '#222', False),
         ('2. Schlitz: 33,3 lang, Breite (quer) fehlt.', '#222', False),
         ('Passt: 36,8 + 2 × 7,2 = 51,2 ≈ 51,3 gemessen.', '#222', False),
         ('Loch Ø2,8 in 7,1 breiter Lasche: je 2,15 Rand.', '#222', False),
         ('Laschen bündig mit Unterteil (6 + 6,5 = 12,5).', '#222', False),
         ('Höhen ab Unterkante Slot, ohne Rundstift-Adapter.', '#222', False),
         ('Lochmitte 2,9 mm von außen. Pins Ø0,5.', '#666', False)]
for i, (t, c, b) in enumerate(notes):
    txt(nx, ny + i * 2.3, t, 12, c, 'start', bold=b)
w, h = 80 * S, 125 * S
svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><rect width="100%" height="100%" fill="white"/>' + \
      f'<text x="{w/2}" y="30" font-family="DejaVu Sans, sans-serif" font-size="20" font-weight="bold" text-anchor="middle">Atari 2600 Cartridge-Slot – Maßskizze v6</text>' + \
      f'<text x="{w/2}" y="54" font-family="DejaVu Sans, sans-serif" font-size="13" fill="#555" text-anchor="middle">Von Hand gemessen (Stefan, 25.10.2026), Maße in mm. Rot = unsicher oder abgeleitet.</text>' + ''.join(out) + '</svg>'
open(sys.argv[1], 'w').write(svg)
