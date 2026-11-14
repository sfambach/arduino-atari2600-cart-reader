# 2D-Massskizze der Cartridge-Fuehrung (3D-Druck) fuer Slot B auf Stiftleisten, Entwurf 1 (Stefan misst 14.11.2026)
import sys
# --- Messwerte Stefan 14.11.2026 ---
SHELL_IN_L, SHELL_IN_W = 75.0, 15.5      # Cartridge-Gehaeuse innen (Steckende)
SHELL_OUT_L, SHELL_OUT_W = 82.5, 20.4    # aussen
PCB_A, PCB_B = 9.0, 6.0                  # Innenwand -> Cartridge-Platine, Seite A / Seite B
PCB_T = 0.5                              # unsicher (Stefan: 0,5-0,6); 9 + 6 + 0,5 = 15,5 passt
SLOT_TOP = 25.0                          # Oberkante Slot ueber Platine (Slot B auf Stiftleisten)
SHELL_Z = 6.5                            # Unterkante Gehaeuse ueber Platine, Cartridge gesteckt
# --- Slot B ---
SL_L, SL_W = 37.0, 9.5
# --- Entwurf ---
CLR = 0.3                                # Luft je Seite zum Gehaeuse
SLV_L, SLV_W = SHELL_IN_L - 2 * CLR, SHELL_IN_W - 2 * CLR   # Huelse aussen
CAV_L, CAV_W = 52.0, 10.0                # Aussparung fuer den Slot (passt auch fuer Slot A mit Laschen 51,3 x 9)
OFF = (PCB_A + PCB_T / 2) - SHELL_IN_W / 2  # Versatz Slotmitte gegen Huelsenmitte = Verpolschutz
BASE_L, BASE_W = 61.0, 17.0              # Grundplatte = freie Flaeche auf allen Platinen
HOLE_X, HOLE_D = 22.75, 2.7              # M2,5-Loecher der Platine (Abstand 45,5)
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
ox, oy = 10, 20
cx, cy = ox + SLV_L / 2, oy + SLV_W / 2
txt(cx, oy - 7.5, 'Draufsicht', 15, bold=True)
rect(cx - BASE_L / 2, cy + OFF - BASE_W / 2, BASE_L, BASE_W, fill='#f4f4f4', dash='5,3')
rect(ox, oy, SLV_L, SLV_W, fill='#dfe9f7')
rect(cx - CAV_L / 2, cy + OFF - CAV_W / 2, CAV_L, CAV_W, fill='white')
rect(cx - SL_L / 2, cy + OFF - SL_W / 2, SL_L, SL_W, fill='#e8e8e8', c='#777')
ln(cx - 16.65, cy + OFF, cx + 16.65, cy + OFF, PIN, 2)
for s in (-1, 1):
    circ(cx + s * HOLE_X, cy + OFF, HOLE_D, '#fff', DIM)
hline(cy, ox - 2, ox + SLV_L + 2)
dimh(ox, ox + SLV_L, oy - 2, f(SLV_L))
dimh(cx - BASE_L / 2, cx + BASE_L / 2, cy + OFF + BASE_W / 2 + 3, f(BASE_L) + ' Grundplatte')
dimh(cx - CAV_L / 2, cx + CAV_L / 2, cy + OFF + BASE_W / 2 + 6.5, f(CAV_L) + ' Aussparung')
dimh(cx - HOLE_X, cx + HOLE_X, cy + OFF + BASE_W / 2 + 10, f(2 * HOLE_X) + ' Löcher M2,5')
dimv(ox + SLV_L + 3, oy, oy + SLV_W, f(SLV_W), left=False)
dimv(ox + SLV_L + 7, cy + OFF - BASE_W / 2, cy + OFF + BASE_W / 2, f(BASE_W), left=False)
dimv(ox - 2.5, cy, cy + OFF, f(OFF), RED)
txt(ox + 1, oy + 1.8, 'Seite A (9 mm)', 11, RED, 'start')
txt(ox + 1, oy + SLV_W - .8, 'Seite B (6 mm)', 11, RED, 'start')

# --- Schnitt quer (kurze Seite) ---
sx, base = 18, 108
scx = sx + SLV_W / 2
txt(scx + 8, base - SLOT_TOP - 21, 'Schnitt quer, Cartridge gesteckt', 15, bold=True)
ln(sx - 12, base, sx + SLV_W + 14, base, '#2e7d32', 2.2); txt(sx + SLV_W + 14.5, base + .4, 'Platine', 11, '#2e7d32', 'start')
# Gehaeuse
for s in (-1, 1):
    x_in = scx + s * SHELL_IN_W / 2; x_out = scx + s * SHELL_OUT_W / 2
    rect(min(x_in, x_out), base - SLOT_TOP - 12, abs(x_out - x_in), SLOT_TOP + 12 - SHELL_Z, fill='none', c='#aaa', dash='4,3')
# Grundplatte
rect(scx + OFF - BASE_W / 2, base - SHELL_Z, BASE_W, SHELL_Z, fill='#f4f4f4')
# Huelse
rect(scx - SLV_W / 2, base - SLOT_TOP, SLV_W, SLOT_TOP - SHELL_Z, fill='#dfe9f7')
rect(scx + OFF - CAV_W / 2, base - SLOT_TOP, CAV_W, SLOT_TOP, fill='white')
# Slot + Leisten
rect(scx + OFF - SL_W / 2, base - SLOT_TOP, SL_W, 10, fill='#e8e8e8', c='#777')
rect(scx + OFF - 7.5 / 2, base - SLOT_TOP + 10, 7.5, 5.5, fill='#e8e8e8', c='#777')
for s in (-1, 1):
    ln(scx + OFF + s * 2.75, base - SLOT_TOP + 15.5, scx + OFF + s * 2.75, base + 2, PIN, 1.6)
# Cartridge-Platine
rect(scx + OFF - PCB_T / 2, base - SLOT_TOP - 12, PCB_T, 12 + 7, fill='#7cb36b', c='#2e7d32')
dimv(sx - 9, base - SLOT_TOP, base, f(SLOT_TOP))
dimv(sx - 5, base - SHELL_Z, base, f(SHELL_Z))
dimh(scx - SHELL_IN_W / 2, scx + SHELL_IN_W / 2, base - SLOT_TOP - 13.5, f(SHELL_IN_W) + ' innen')
dimh(scx - SHELL_OUT_W / 2, scx + SHELL_OUT_W / 2, base - SLOT_TOP - 16.5, f(SHELL_OUT_W) + ' außen')
dimh(scx - SHELL_IN_W / 2, scx + OFF - PCB_T / 2, base - SLOT_TOP - 4, f(PCB_A), RED)
dimh(scx + OFF + PCB_T / 2, scx + SHELL_IN_W / 2, base - SLOT_TOP - 4, f(PCB_B), RED)
txt(scx + OFF + 7, base - SLOT_TOP + 5, 'Slot B', 10, '#777', 'start')
txt(scx + OFF + 12, base - SLOT_TOP + 22, 'Stiftleisten', 10, '#777', 'start')

# --- Hinweise ---
nx, ny = 46, 70
notes = [('Prinzip:', '#222', True),
         ('Grundplatte 61 × 17 × 6,5 auf der Platine, an den M2,5-Löchern verschraubt.', '#222', False),
         ('Darauf die Hülse 74,4 × 14,9: das Gehäuse rutscht darüber und sitzt', '#222', False),
         ('auf der Grundplatte auf (Unterkante 6,5 wie gemessen).', '#222', False),
         ('Verpolschutz: Die Cartridge-Platine sitzt nicht mittig (9 / 6 mm),', '#222', False),
         ('deshalb liegt der Slot 1,75 mm neben der Hülsenmitte.', '#222', False),
         ('Verkehrt herum passt das Gehäuse nicht über die Hülse.', '#222', False),
         ('Hülse ragt über die Grundplatte und bei Uno/Mega über die', '#222', False),
         ('Platinenkante (ab 6,5 mm Höhe, dort ist nichts).', '#222', False),
         ('Offen (rot):', RED, True),
         ('Welche Seite (A = 9 mm) ist die Etikettseite?', RED, False),
         ('Platinendicke 0,5 (Summe passt) oder 1,6 (Standard)?', RED, False),
         ('Für Slot A (16,1 hoch, Laschen) eigene, niedrigere Variante.', RED, False)]
for i, (t, c, b) in enumerate(notes):
    txt(nx, ny + i * 2.3, t, 12, c, 'start', bold=b)
w, h = 100 * S, 118 * S
svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><rect width="100%" height="100%" fill="white"/>' + \
      f'<text x="{w/2}" y="30" font-family="DejaVu Sans, sans-serif" font-size="20" font-weight="bold" text-anchor="middle">Cartridge-Führung für Slot B – Entwurf 1</text>' + \
      f'<text x="{w/2}" y="54" font-family="DejaVu Sans, sans-serif" font-size="13" fill="#555" text-anchor="middle">Maße in mm, Cartridge von Stefan gemessen (14.11.2026). Rot = offen. Blau = Hülse, grau gestrichelt = Grundplatte.</text>' + ''.join(out) + '</svg>'
open(sys.argv[1], 'w').write(svg)
