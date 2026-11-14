# 2D-Massskizze der Cartridge-Fuehrung (3D-Druck), Entwurf 3: Aussenrahmen wie der Konsolenschacht, zwei Oeffner-Stifte
import sys
# --- gemessen (Stefan 14.11.2026) ---
SHELL_OUT_L, SHELL_OUT_W = 82.5, 20.4    # Cartridge aussen
SLOT_TOP = 25.0                          # Oberkante Slot B ueber Platine (auf Stiftleisten)
SHELL_Z = 6.5                            # Unterkante Gehaeuse ueber Platine, Cartridge gesteckt
SL_L, SL_W = 37.0, 9.5                   # Slot B
# --- Schacht-Angaben (Stefan 14.11.2026, Konsolen-Schacht, ca.-Werte) ---
FR_IN_L, FR_IN_W = 83.0, 21.0            # Innenmass Rahmen
WALL = 2.0
FR_L, FR_W = FR_IN_L + 2 * WALL, FR_IN_W + 2 * WALL
PIN_X, PIN_D = 37.0, 3.0                 # Stifte +-37 von der Mitte
# --- Entwurf ---
OFF = 2.2                                # Slot neben der Mitte (Platinenlage aus holder.stl), Verpolschutz
FLOOR_T = 2.0                            # Anschlagboden, Oberkante = Gehaeuseunterkante 6,5
FR_TOP = SHELL_Z + 24.0                  # Schachttiefe 24 (Angabe 22-25)
PIN_TOP = SLOT_TOP + 3.0                 # Annahme: Stifte 3 mm ueber dem Slot, damit die Klappe vor dem Slot aufgeht
BASE_L, BASE_W = 61.0, 17.0              # Sockel = freie Flaeche auf allen Platinen
HOLE_X, HOLE_D = 22.75, 2.7              # M2,5-Loecher der Platine
CUT_L, CUT_W = 52.0, 10.5                # Durchbruch im Boden fuer den Slot
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


def hline(y, x0, x1, c='#999'): ln(x0, y, x1, y, c, 1, '4,3')

# --- Draufsicht ---
ox, oy = 14, 22
cx, cy = ox + FR_L / 2, oy + FR_W / 2
txt(cx, oy - 9, 'Draufsicht', 15, bold=True)
rect(ox, oy, FR_L, FR_W, fill='#dfe9f7')
rect(ox + WALL, oy + WALL, FR_IN_L, FR_IN_W, fill='#eef3fb')
rect(cx - BASE_L / 2, cy + OFF - BASE_W / 2, BASE_L, BASE_W, fill='none', dash='5,3')
rect(cx - CUT_L / 2, cy + OFF - CUT_W / 2, CUT_L, CUT_W, fill='white')
rect(cx - SL_L / 2, cy + OFF - SL_W / 2, SL_L, SL_W, fill='#e8e8e8', c='#777')
ln(cx - 16.65, cy + OFF, cx + 16.65, cy + OFF, PIN, 2)
for s in (-1, 1):
    circ(cx + s * HOLE_X, cy + OFF, HOLE_D, '#fff', DIM)
    circ(cx + s * PIN_X, cy, PIN_D, '#7aa0d8')
hline(cy, ox - 2, ox + FR_L + 2)
dimh(ox, ox + FR_L, oy - 2.5, f(FR_L))
dimh(ox + WALL, ox + WALL + FR_IN_L, oy - 5.5, f(FR_IN_L) + ' innen')
dimh(cx - PIN_X, cx + PIN_X, oy + FR_W + 3, f(2 * PIN_X) + ' Stifte Ø3')
dimh(cx - BASE_L / 2, cx + BASE_L / 2, oy + FR_W + 6.5, f(BASE_L) + ' Sockel (gestrichelt)')
dimh(cx - CUT_L / 2, cx + CUT_L / 2, oy + FR_W + 10, f(CUT_L) + ' Durchbruch')
dimh(cx - HOLE_X, cx + HOLE_X, oy + FR_W + 13.5, f(2 * HOLE_X) + ' Löcher M2,5')
dimv(ox + FR_L + 3, oy, oy + FR_W, f(FR_W), left=False)
dimv(ox + FR_L + 7, oy + WALL, oy + WALL + FR_IN_W, f(FR_IN_W), left=False)
dimv(ox - 2.5, cy, cy + OFF, f(OFF), RED)

# --- Schnitt laengs (durch die Stifte) ---
lx, base = 14, 108
lcx = lx + FR_L / 2
txt(lcx, base - FR_TOP - 6, 'Schnitt längs', 15, bold=True)
ln(lx - 3, base, lx + FR_L + 3, base, '#2e7d32', 2.2)
rect(lcx - BASE_L / 2, base - SHELL_Z + FLOOR_T, BASE_L, SHELL_Z - FLOOR_T, fill='#f4f4f4')
rect(lx, base - SHELL_Z, FR_L, FLOOR_T, fill='#dfe9f7')
for s in (-1, 1):
    x0 = lx if s < 0 else lx + FR_L - WALL
    rect(x0, base - FR_TOP, WALL, FR_TOP - SHELL_Z, fill='#dfe9f7')
    rect(lcx + s * PIN_X - PIN_D / 2, base - PIN_TOP, PIN_D, PIN_TOP - SHELL_Z, fill='#7aa0d8')
rect(lcx - CUT_L / 2, base - SHELL_Z, CUT_L, FLOOR_T + .2, fill='white', c='white')
rect(lcx - CUT_L / 2, base - SHELL_Z, CUT_L, SHELL_Z, fill='white')
rect(lcx - SL_L / 2, base - SLOT_TOP, SL_L, 10, fill='#e8e8e8', c='#777')
rect(lcx - SL_L / 2, base - SLOT_TOP + 10, SL_L, 5.5, fill='#e8e8e8', c='#777')
for i in range(12):
    x = lcx - 13.97 + i * 2.54
    ln(x, base - SLOT_TOP + 15.5, x, base, PIN, 1.2)
rect(lx + WALL + .25, base - FR_TOP - 3, SHELL_OUT_L, FR_TOP - SHELL_Z + 3, fill='none', c='#aaa', dash='4,3')
dimv(lx - 9, base - FR_TOP, base, f(FR_TOP))
dimv(lx - 5, base - SHELL_Z, base, f(SHELL_Z))
dimv(lx + FR_L + 4, base - SLOT_TOP, base, f(SLOT_TOP), left=False)
dimv(lx + FR_L + 9, base - PIN_TOP, base, f(PIN_TOP), RED, left=False)
txt(lcx, base - SLOT_TOP + 5.5, 'Slot B', 11, '#555')
txt(lx + 6, base - FR_TOP + 2, 'Cartridge (gestrichelt)', 10, '#888', 'start')

# --- Hinweise ---
nx, ny = 10, 118
notes = [('Prinzip (wie der Schacht der Konsole):', '#222', True),
         ('Rahmen innen 83 × 21 umfasst das Gehäuse (82,5 × 20,4), Boden bei 6,5 mm = Anschlag.', '#222', False),
         ('Zwei Stifte (Abstand 74) drücken die Klappe der Original-Cartridge auf, der Slot schiebt den Schieber hoch.', '#222', False),
         ('Verpolschutz: Slot 2,2 mm außermittig (Platinenlage). Verkehrt herum trifft der Slot nicht den Schlitz.', '#222', False),
         ('Sockel 61 × 17 trägt den Rahmen, verschraubt an den M2,5-Löchern. Rahmen ragt bei Uno/Mega/Nano über die Platine.', '#222', False),
         ('Offen (rot):', RED, True),
         ('Stifthöhe 28 über Platine angenommen (3 mm über dem Slot); Angabe «12-14 ab Boden» gilt für den Konsolenstecker (8-10 hoch).', RED, False),
         ('Schachtwerte sind ca.-Werte, nicht nachgemessen. Bauteile unter dem Rahmen (bis 6,5 hoch) nicht geprüft.', RED, False)]
for i, (t, c, b) in enumerate(notes):
    txt(nx, ny + i * 2.3, t, 12, c, 'start', bold=b)
w, h = 114 * S, 138 * S
svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><rect width="100%" height="100%" fill="white"/>' + \
      f'<text x="{w/2}" y="30" font-family="DejaVu Sans, sans-serif" font-size="20" font-weight="bold" text-anchor="middle">Cartridge-Führung für Slot B – Entwurf 3</text>' + \
      f'<text x="{w/2}" y="54" font-family="DejaVu Sans, sans-serif" font-size="13" fill="#555" text-anchor="middle">Maße in mm. Schacht und Stifte nach Stefans Angaben (14.11.2026), Rot = Annahme/offen.</text>' + ''.join(out) + '</svg>'
open(sys.argv[1], 'w').write(svg)
