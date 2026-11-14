# 2D-Massskizze der Cartridge-Fuehrung (3D-Druck), Entwurf 4: nur der Innenteil (Huelse) nach vcsslot.stl, angepasst an Slot B
import sys
# --- gemessen (Stefan 14.11.2026) ---
SLOT_TOP = 25.0                          # Oberkante Slot B ueber Platine (auf Stiftleisten)
SHELL_Z = 6.5                            # Unterkante Cartridge-Gehaeuse ueber Platine, gesteckt
SHELL_IN_L, SHELL_IN_W = 75.0, 15.5      # Cartridge innen
SL_L, SL_W = 37.0, 9.5                   # Slot B
# --- aus vcsslot.stl (RabbitEngineering, Thingiverse 618065) ---
SLV_L, SLV_W = 74.2, 15.2                # Huelse an der Spitze
OFF = 2.1                                # Platinenschlitz neben der Mitte
PIN_X, PIN_L, PIN_T, PIN_H = 24.75, 6.5, 2.0, 6.75   # Klappen-Oeffner (Laschen ueber der Spitze)
# --- Entwurf ---
WALL, TIP_T = 1.2, 1.2
OPEN_L, OPEN_W = SL_L + 1.0, SL_W + 0.7  # Durchbruch in der Spitze fuer den Slot
BASE_L, BASE_W = 61.0, 17.0              # Sockel = freie Flaeche auf allen Platinen
HOLE_X, HOLE_D = 22.75, 2.7              # M2,5-Loecher der Platine
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

def hline(y, x0, x1, c='#999'): ln(x0, y, x1, y, c, 1, '4,3')

# --- Draufsicht ---
ox, oy = 14, 22
cx, cy = ox + SLV_L / 2, oy + SLV_W / 2
txt(cx, oy - 9, 'Draufsicht', 15, bold=True)
rect(cx - BASE_L / 2, cy + OFF - BASE_W / 2, BASE_L, BASE_W, fill='#f4f4f4', dash='5,3')
rect(ox, oy, SLV_L, SLV_W, fill='#dfe9f7')
rect(cx - OPEN_L / 2, cy + OFF - OPEN_W / 2, OPEN_L, OPEN_W, fill='white')
rect(cx - SL_L / 2, cy + OFF - SL_W / 2, SL_L, SL_W, fill='#e8e8e8', c='#777')
ln(cx - 16.65, cy + OFF, cx + 16.65, cy + OFF, PIN, 2)
for s in (-1, 1):
    rect(cx + s * PIN_X - PIN_L / 2, cy + OFF - PIN_T / 2, PIN_L, PIN_T, fill='#7aa0d8')
    circ(cx + s * HOLE_X, cy + OFF, HOLE_D, '#fff', DIM)
hline(cy, ox - 2, ox + SLV_L + 2)
dimh(ox, ox + SLV_L, oy - 3, f(SLV_L))
dimh(cx - PIN_X, cx + PIN_X, oy + SLV_W + 5, f(2 * PIN_X) + ' Öffner')
dimh(cx - BASE_L / 2, cx + BASE_L / 2, oy + SLV_W + 8.5, f(BASE_L) + ' Sockel (gestrichelt)')
dimh(cx - OPEN_L / 2, cx + OPEN_L / 2, oy + SLV_W + 12, f(OPEN_L) + ' Durchbruch')
dimh(cx - HOLE_X, cx + HOLE_X, oy + SLV_W + 15.5, f(2 * HOLE_X) + ' Löcher M2,5')
dimv(ox + SLV_L + 3, oy, oy + SLV_W, f(SLV_W), left=False)
dimv(ox + SLV_L + 7, cy + OFF - BASE_W / 2, cy + OFF + BASE_W / 2, f(BASE_W), left=False)
dimv(ox - 2.5, cy, cy + OFF, f(OFF), RED)
txt(ox + 1, oy + 1.8, 'Seite A', 11, '#555', 'start')
txt(ox + 1, oy + SLV_W - .8, 'Seite B', 11, '#555', 'start')

# --- Schnitt laengs ---
lx, base = 14, 100
lcx = lx + SLV_L / 2
txt(lcx, base - SLOT_TOP - PIN_H - 6, 'Schnitt längs', 15, bold=True)
ln(lx - 4, base, lx + SLV_L + 4, base, '#2e7d32', 2.2)
rect(lcx - BASE_L / 2, base - SHELL_Z, BASE_L, SHELL_Z, fill='#f4f4f4')
for s in (-1, 1):
    x0 = lx if s < 0 else lx + SLV_L - WALL
    rect(x0, base - SLOT_TOP, WALL, SLOT_TOP - SHELL_Z, fill='#dfe9f7')
    rect(lcx + s * PIN_X - PIN_L / 2, base - SLOT_TOP - PIN_H, PIN_L, PIN_H, fill='#7aa0d8')
rect(lx, base - SLOT_TOP, SLV_L, TIP_T, fill='#dfe9f7')
rect(lcx - OPEN_L / 2, base - SLOT_TOP - .1, OPEN_L, TIP_T + .2, fill='white', c='white')
rect(lcx - SL_L / 2, base - SLOT_TOP, SL_L, 10, fill='#e8e8e8', c='#777')
rect(lcx - SL_L / 2, base - SLOT_TOP + 10, SL_L, 5.5, fill='#e8e8e8', c='#777')
for i in range(12):
    x = lcx - 13.97 + i * 2.54
    ln(x, base - SLOT_TOP + 15.5, x, base - SHELL_Z, PIN, 1.2)
rect(lx + (SLV_L - SHELL_IN_L) / 2, base - SLOT_TOP - PIN_H - 3, SHELL_IN_L, SLOT_TOP + PIN_H + 3 - SHELL_Z, fill='none', c='#aaa', dash='4,3')
dimv(lx - 9, base - SLOT_TOP, base, f(SLOT_TOP))
dimv(lx - 5, base - SHELL_Z, base, f(SHELL_Z))
dimv(lx + SLV_L + 5, base - SLOT_TOP - PIN_H, base - SLOT_TOP, f(PIN_H), left=False)
txt(lcx, base - SLOT_TOP + 5.5, 'Slot B', 11, '#555')
txt(lx + 3, base - SLOT_TOP - PIN_H - 1, 'Cartridge-Gehäuse innen (gestrichelt)', 10, '#888', 'start')

# --- Schnitt quer ---
qx = 30
qcx = qx + SLV_W / 2
txt(qcx + 22, 112, 'Schnitt quer', 15, bold=True)
qb = 150
ln(qx - 14, qb, qx + SLV_W + 14, qb, '#2e7d32', 2.2)
rect(qcx + OFF - BASE_W / 2, qb - SHELL_Z, BASE_W, SHELL_Z, fill='#f4f4f4')
rect(qcx - SLV_W / 2, qb - SLOT_TOP, WALL, SLOT_TOP - SHELL_Z, fill='#dfe9f7')
rect(qcx - SLV_W / 2, qb - SLOT_TOP, (qcx + OFF - OPEN_W / 2) - (qcx - SLV_W / 2), TIP_T, fill='#dfe9f7')
rect(qcx + OFF + OPEN_W / 2, qb - SLOT_TOP, (qcx + SLV_W / 2) - (qcx + OFF + OPEN_W / 2), TIP_T, fill='#dfe9f7')
rect(qcx + OFF - SL_W / 2, qb - SLOT_TOP, SL_W, 10, fill='#e8e8e8', c='#777')
rect(qcx + OFF - 7.5 / 2, qb - SLOT_TOP + 10, 7.5, 5.5, fill='#e8e8e8', c='#777')
ln(qcx + SLV_W / 2 - WALL / 2, qb - SLOT_TOP, qcx + SLV_W / 2 - WALL / 2, qb - SHELL_Z, RED, 1.2, '3,2')
dimh(qcx - SLV_W / 2, qcx + SLV_W / 2, qb - SLOT_TOP - 4, f(SLV_W))
dimh(qcx - SHELL_IN_W / 2, qcx + SHELL_IN_W / 2, qb - SLOT_TOP - 8, f(SHELL_IN_W) + ' Cartridge innen')
dimv(qx - 8, qb - SLOT_TOP, qb, f(SLOT_TOP))
txt(qcx + SLV_W / 2 + 1.5, qb - 12, 'Seite B: Wand neben', 10, RED, 'start')
txt(qcx + SLV_W / 2 + 1.5, qb - 10, 'dem Slot ausgespart', 10, RED, 'start')

# --- Hinweise ---
nx, ny = 64, 122
notes = [('Prinzip (Innenteil von vcsslot.stl):', '#222', True),
         ('Hülse 74,2 × 15,2 geht in die Cartridge, Spitze', '#222', False),
         ('bündig mit der Slot-Oberkante (25).', '#222', False),
         ('Die Spitze schiebt den Schieber hoch, die zwei', '#222', False),
         ('Laschen (6,75 hoch) öffnen die Klappe.', '#222', False),
         ('Kein Außenrahmen: nur der Sockel 61 × 17', '#222', False),
         ('steht auf der Platine (M2,5-Löcher).', '#222', False),
         ('Offen (rot):', RED, True),
         ('Versatz 2,1 aus vcsslot, nicht an Slot B gemessen.', RED, False),
         ('Seite B: neben dem Slot nur 0,75 Platz,', RED, False),
         ('dort Wand ausgespart.', RED, False),
         ('Laschen bei Nachbau-Gehäusen mit Halter prüfen.', RED, False)]
for i, (t, c, b) in enumerate(notes):
    txt(nx, ny + i * 2.3, t, 12, c, 'start', bold=b)
w, h = 112 * S, 156 * S
svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><rect width="100%" height="100%" fill="white"/>' + \
      f'<text x="{w/2}" y="30" font-family="DejaVu Sans, sans-serif" font-size="20" font-weight="bold" text-anchor="middle">Cartridge-Führung für Slot B – Entwurf 4 (nur Innenteil)</text>' + \
      f'<text x="{w/2}" y="54" font-family="DejaVu Sans, sans-serif" font-size="13" fill="#555" text-anchor="middle">Maße in mm. Vorlage vcsslot.stl (Thingiverse 618065), Slot und Höhen von Stefan gemessen. Rot = Annahme/offen.</text>' + ''.join(out) + '</svg>'
open(sys.argv[1], 'w').write(svg)
