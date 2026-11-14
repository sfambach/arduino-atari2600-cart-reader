# 2D-Massskizze Atari-2600-Cartridge-Slot ohne Laschen (Variante B), von Hand gemessen (Stefan, 14.11.2026)
import sys
L, W = 37.0, 9.5                    # Oberteil, gemessen
H, UP_H = 15.5, 10.0                # Gesamthoehe, Oberteil gemessen
LOW_H = H - UP_H                    # Unterteil = Rest
LOW_W = 7.5                         # Unterteil schmaler, gemessen
LOW_L = L                           # nicht gemessen: angenommen gleich lang wie das Oberteil
SLOT_W, CONTACT_GAP, SLOT_DEPTH, SLOT_L = 2.2, 1.4, 9.0, 33.3   # nicht gemessen: wie Slot A
PITCH, ROW, NPIN, PIN_D = 2.54, 5.5, 12, 0.5                   # Stefan: gleiche Pins, gleiche Abstaende
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

pin_x0 = (L - (NPIN - 1) * PITCH) / 2
def pins(ox, cy):
    for i in range(NPIN):
        for dy in (ROW / 2, -ROW / 2):
            circ(ox + pin_x0 + i * PITCH, cy + dy, PIN_D, PIN, PIN)

# --- Draufsicht ---
ox, oy = 12, 16
txt(ox + L / 2, oy - 5.5, 'Draufsicht (Cartridge-Seite)', 15, bold=True)
rect(ox, oy, L, W)
rect(ox + (L - SLOT_L) / 2, oy + W / 2 - SLOT_W / 2, SLOT_L, SLOT_W, fill='#fafafa', c=RED)
txt(ox + L / 2, oy + W / 2 + .45, 'Schlitz', 10, '#888')
dimh(ox + (L - SLOT_L) / 2, ox + (L + SLOT_L) / 2, oy + 1.4, f(SLOT_L), RED)
dimh(ox, ox + L, oy + W + 3.5, f(L))
dimv(ox + L + 3, oy, oy + W, f(W), left=False)
dimv(ox + L + 6.5, oy + W / 2 - SLOT_W / 2, oy + W / 2 + SLOT_W / 2, '2,2', RED, left=False)

# --- Vorderansicht ---
fx, base = 12, 56
txt(fx + L / 2, base - H - 3, 'Vorderansicht (lange Seite)', 15, bold=True)
ln(fx - 6, base, fx + L + 6, base, '#2e7d32', 2.2); txt(fx + L + 6.5, base + .4, 'Platine', 11, '#2e7d32', 'start')
rect(fx + (L - LOW_L) / 2, base - LOW_H, LOW_L, LOW_H)
rect(fx, base - H, L, UP_H)
for i in range(NPIN):
    ln(fx + pin_x0 + i * PITCH, base, fx + pin_x0 + i * PITCH, base + 3, PIN, 1.6)
dimv(fx - 2.5, base - H, base, f(H))
dimv(fx + L + 2.5, base - H, base - LOW_H, f(UP_H), left=False)
dimv(fx + L + 2.5, base - LOW_H, base, f(LOW_H), left=False)
dimh(fx, fx + L, base - H - 1.2, f(L))

# --- Seitenansicht ---
sx, sb = 12, 88
txt(sx + 16, sb - H - 3, 'Seitenansicht (kurze Seite)', 15, bold=True)
ln(sx - 4, sb, sx + W + 4, sb, '#2e7d32', 2.2)
for yy in (W / 2 - ROW / 2, W / 2 + ROW / 2):
    ln(sx + yy, sb, sx + yy, sb + 3, PIN, 1.6)
rect(sx + (W - LOW_W) / 2, sb - LOW_H, LOW_W, LOW_H)
rect(sx, sb - H, W, UP_H)
dimh(sx, sx + W, sb + 6.5, f(W))
rect(sx + W / 2 - SLOT_W / 2, sb - H, SLOT_W, SLOT_DEPTH, fill='white', c=RED, dash='4,2')
dimh(sx + W / 2 - SLOT_W / 2, sx + W / 2 + SLOT_W / 2, sb - H - 1.5, '2,2', RED)
dimv(sx - 2.5, sb - H, sb - H + SLOT_DEPTH, f(SLOT_DEPTH), RED)
dimh(sx + W / 2 - ROW / 2, sx + W / 2 + ROW / 2, sb + 4.2, '5,5')
dimh(sx + (W - LOW_W) / 2, sx + (W + LOW_W) / 2, sb - LOW_H / 2, f(LOW_W))

# --- Unteransicht ---
ux, uy = 12, 104
txt(ux + L / 2, uy - 3, 'Unteransicht (Platinenseite)', 15, bold=True)
rect(ux, uy, L, W, fill='#f2f2f2')
rect(ux + (L - LOW_L) / 2, uy + (W - LOW_W) / 2, LOW_L, LOW_W)
pins(ux, uy + W / 2)
txt(ux + pin_x0, uy - .6, '1', 11, PIN); txt(ux + pin_x0 + 11 * PITCH, uy - .6, '12', 11, PIN)
txt(ux + pin_x0, uy + W + 1.9, '24', 11, PIN); txt(ux + pin_x0 + 11 * PITCH, uy + W + 1.9, '13', 11, PIN)
dimh(ux + pin_x0, ux + pin_x0 + PITCH, uy + W + 4.2, '2,54')
dimv(ux - 2.5, uy + W / 2 - ROW / 2, uy + W / 2 + ROW / 2, '5,5')

# --- Hinweise ---
nx, ny = 32, 75
notes = [('Unterschiede zu Slot A (mit Laschen):', '#222', True),
         ('Keine Laschen, keine Verschraubung.', '#222', False),
         ('37 × 9,5 statt 36,8 × 9 (ohne Laschen), 15,5 statt 16,1 hoch.', '#222', False),
         ('Pins wie Slot A: 2 × 12, RM 2,54, Reihen 5,5 → passt auf die Platinen.', '#222', False),
         ('Die M2,5-Löcher der Platine bleiben frei (Abstand 45,5 > 37).', '#222', False),
         ('Rot = nicht gemessen, von Slot A übernommen:', RED, True),
         ('Schlitz 33,3 × 2,2, Tiefe 9; Länge Unterteil = 37.', RED, False)]
for i, (t, c, b) in enumerate(notes):
    txt(nx, ny + i * 2.3, t, 12, c, 'start', bold=b)
w, h = 82 * S, 121 * S
svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><rect width="100%" height="100%" fill="white"/>' + \
      f'<text x="{w/2}" y="30" font-family="DejaVu Sans, sans-serif" font-size="20" font-weight="bold" text-anchor="middle">Atari 2600 Cartridge-Slot B (ohne Laschen) – Maßskizze</text>' + \
      f'<text x="{w/2}" y="54" font-family="DejaVu Sans, sans-serif" font-size="13" fill="#555" text-anchor="middle">Von Hand gemessen (Stefan, 14.11.2026), Maße in mm. Rot = nicht gemessen.</text>' + ''.join(out) + '</svg>'
open(sys.argv[1], 'w').write(svg)
