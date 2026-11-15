# 2D-Massskizze der Cartridge-Fuehrung (3D-Druck), Entwurf 5: Kappe ueber Slot B (Stefan 15.11.2026)
import sys
# --- gemessen (Stefan 14.11.2026) ---
SLOT_TOP = 25.0                          # Oberkante Slot B ueber Platine (auf Stiftleisten)
SHELL_IN_L, SHELL_IN_W = 75.0, 15.5      # Cartridge innen
SL_L, SL_W, SL_UP = 37.0, 9.5, 10.0      # Slot B, Oberteil 10 hoch
SL_LOW_W, SL_H = 7.5, 15.5
# --- aus vcsslot.stl (Thingiverse 618065) ---
CAP_L, CAP_W = 74.2, 15.2                # Huelse
OFF = 2.1                                # Slotmitte neben der Huelsenmitte (Seite B)
PIN_X, PIN_H = 24.75, 6.75               # Klappen-Oeffner
# --- Entwurf ---
PLATE = 1.2                              # geschlossene Deckflaeche ueber dem Slot
TOP = SLOT_TOP + PLATE
CLR = 0.3                                # Luft um den Slot
CAV_L, CAV_W = SL_L + 2 * CLR, SL_W + 2 * CLR
SLIT_L, SLIT_W = 34.0, 2.6               # Schlitz fuer die Cartridge-Platine
HOLE_X, SCREW_D, SCREW_DEPTH = 22.75, 2.2, 10.0   # M2,5 von unten durch die Platine
FOOT_X = HOLE_X + 2.7 / 2 + 1.4          # Fuss endet knapp hinter der Lochaussenkante
FULL_Z = 15.0                            # darueber volle Laenge (Fuehrung in der Cartridge)
PIN_D, PIN_DEPTH = 3.0, 8.0              # Stift 3 x 15, 8 tief eingepresst
BAND = 8.5                               # unten max. 8,5 neben der Slotmitte (freie Flaeche 61 x 17)
STEP_Z = 7.7                             # Unterkante Cartridge mit Kappe (6,5 + 1,2)
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
def poly(pts, fill='#dfe9f7', c='#222'):
    out.append('<polygon points="' + ' '.join(f'{x*S},{y*S}' for x, y in pts) + f'" fill="{fill}" stroke="{c}" stroke-width="1.6"/>')

# --- Draufsicht (Deckflaeche) ---
ox, oy = 16, 24
cx, cy = ox + CAP_L / 2, oy + CAP_W / 2
sy = cy + OFF
txt(cx, oy - 10, 'Draufsicht', 15, bold=True)
rect(ox, oy, CAP_L, CAP_W, fill='#dfe9f7')
rect(cx - CAV_L / 2, sy - CAV_W / 2, CAV_L, CAV_W, fill='none', c='#888', dash='4,3')
rect(cx - SLIT_L / 2, sy - SLIT_W / 2, SLIT_L, SLIT_W, fill='white')
for s in (-1, 1):
    circ(cx + s * PIN_X, sy, PIN_D, '#7aa0d8')
    circ(cx + s * HOLE_X, sy, SCREW_D, 'none', '#999')
hline(cy, ox - 2, ox + CAP_L + 2)
dimh(ox, ox + CAP_L, oy - 3, f(CAP_L))
dimh(cx - SLIT_L / 2, cx + SLIT_L / 2, oy + CAP_W + 3.5, f(SLIT_L) + ' × ' + f(SLIT_W) + ' Schlitz')
dimh(cx - PIN_X, cx + PIN_X, oy + CAP_W + 7, f(2 * PIN_X) + ' Stifte Ø3')
dimh(cx - HOLE_X, cx + HOLE_X, oy + CAP_W + 10.5, f(2 * HOLE_X) + ' Schrauben M2,5 (von unten)')
dimv(ox + CAP_L + 3, oy, oy + CAP_W, f(CAP_W), left=False)
dimv(ox - 2.5, cy, sy, f(OFF), RED)
txt(ox + 1, oy + 1.8, 'Seite A', 11, '#555', 'start')
txt(ox + 1, oy + CAP_W - .8, 'Seite B', 11, '#555', 'start')
txt(cx, sy - 3.2, 'Slot B darunter (gestrichelt)', 10, '#888')

# --- Ansicht laengs ---
lx, base = 16, 100
lcx = lx + CAP_L / 2
txt(lcx, base - TOP - PIN_H - 6, 'Ansicht von Seite A (Schnitt durch Slotmitte)', 15, bold=True)
ln(lx - 4, base, lx + CAP_L + 4, base, '#2e7d32', 2.2)
poly([(lcx - FOOT_X, base), (lcx - CAP_L / 2, base - FULL_Z), (lcx - CAP_L / 2, base - TOP),
      (lcx + CAP_L / 2, base - TOP), (lcx + CAP_L / 2, base - FULL_Z), (lcx + FOOT_X, base)])
rect(lcx - CAV_L / 2, base - SLOT_TOP, CAV_L, SLOT_TOP, fill='white')
rect(lcx - SL_L / 2, base - SLOT_TOP, SL_L, SL_UP, fill='#e8e8e8', c='#777')
rect(lcx - SL_L / 2, base - SLOT_TOP + SL_UP, SL_L, SL_H - SL_UP, fill='#e8e8e8', c='#777')
rect(lcx - 15.24, base - (SLOT_TOP - SL_H), 30.48, SLOT_TOP - SL_H, fill='#555', c='#333')
rect(lcx - SLIT_L / 2, base - TOP - .05, SLIT_L, PLATE + .1, fill='white', c='white')
ln(lcx - SLIT_L / 2, base - TOP, lcx - SLIT_L / 2, base - SLOT_TOP); ln(lcx + SLIT_L / 2, base - TOP, lcx + SLIT_L / 2, base - SLOT_TOP)
for s in (-1, 1):
    rect(lcx + s * PIN_X - PIN_D / 2, base - TOP - PIN_H, PIN_D, PIN_H + PIN_DEPTH, fill='#7aa0d8')
    rect(lcx + s * HOLE_X - SCREW_D / 2, base - SCREW_DEPTH, SCREW_D, SCREW_DEPTH, fill='white', c='#999', dash='3,2')
    ln(lcx + s * HOLE_X, base + 4, lcx + s * HOLE_X, base - SCREW_DEPTH + 1, '#555', 1.2, '2,2')
txt(lcx, base - SLOT_TOP + 5.5, 'Slot B', 11, '#555')
txt(lcx, base - (SLOT_TOP - SL_H) / 2 + .5, 'Stiftleisten', 10, 'white')
dimv(lx - 9, base - TOP, base, f(TOP))
dimv(lx - 5, base - FULL_Z, base, f(FULL_Z))
dimv(lx + CAP_L + 4, base - TOP - PIN_H, base - TOP, f(PIN_H), left=False)
dimv(lx + CAP_L + 4, base - TOP, base - SLOT_TOP, f(PLATE), RED, left=False)
dimh(lcx - FOOT_X, lcx + FOOT_X, base + 6, f(2 * FOOT_X) + ' Fuß')
txt(lcx + PIN_X + 3, base - TOP - 3, 'Stift', 10, '#555', 'start')
txt(lcx + HOLE_X + 2.5, base + 3.5, 'Schraube', 10, '#555', 'start')

# --- Schnitt quer ---
qx, qb = 26, 150
qcx = qx + CAP_W / 2
qsy = qcx + OFF
txt(qcx + 30, qb - TOP - 9, 'Schnitt quer', 15, bold=True)
ln(qx - 12, qb, qx + CAP_W + 12, qb, '#2e7d32', 2.2)
poly([(qsy - BAND, qb), (qsy - BAND, qb - STEP_Z), (qcx - CAP_W / 2, qb - STEP_Z), (qcx - CAP_W / 2, qb - TOP),
      (qcx + CAP_W / 2, qb - TOP), (qcx + CAP_W / 2, qb - SLOT_TOP), (qsy + CAV_W / 2, qb - SLOT_TOP), (qsy + CAV_W / 2, qb),
      (qsy - CAV_W / 2, qb), (qsy - CAV_W / 2, qb - SLOT_TOP), (qsy - SLIT_W / 2, qb - SLOT_TOP), (qsy - SLIT_W / 2, qb - TOP),
      (qsy + SLIT_W / 2, qb - TOP), (qsy + SLIT_W / 2, qb - SLOT_TOP)], fill='none', c='none')
# Seite A massiv, Deckflaeche, Seite B offen
poly([(qsy - BAND, qb), (qsy - BAND, qb - STEP_Z), (qcx - CAP_W / 2, qb - STEP_Z), (qcx - CAP_W / 2, qb - TOP),
      (qsy - SLIT_W / 2, qb - TOP), (qsy - SLIT_W / 2, qb - SLOT_TOP), (qsy - CAV_W / 2, qb - SLOT_TOP), (qsy - CAV_W / 2, qb)])
poly([(qsy + SLIT_W / 2, qb - TOP), (qcx + CAP_W / 2, qb - TOP), (qcx + CAP_W / 2, qb - SLOT_TOP), (qsy + SLIT_W / 2, qb - SLOT_TOP)])
rect(qsy - SL_W / 2, qb - SLOT_TOP, SL_W, SL_UP, fill='#e8e8e8', c='#777')
rect(qsy - SL_LOW_W / 2, qb - SLOT_TOP + SL_UP, SL_LOW_W, SL_H - SL_UP, fill='#e8e8e8', c='#777')
rect(qsy - 2.5 - 1.27, qb - (SLOT_TOP - SL_H), 7.62 - 1.27, SLOT_TOP - SL_H, fill='#555', c='#333')
rect(qcx - SHELL_IN_W / 2, qb - TOP - 10, SHELL_IN_W, TOP + 10 - STEP_Z, fill='none', c='#aaa', dash='4,3')
dimh(qcx - CAP_W / 2, qcx + CAP_W / 2, qb - TOP - 3, f(CAP_W))
dimv(qx - 8, qb - STEP_Z, qb, f(STEP_Z))
dimv(qx - 8, qb - TOP, qb - STEP_Z, f(TOP - STEP_Z))
txt(qcx + CAP_W / 2 + 1.5, qb - 18, 'Seite B neben dem', 10, RED, 'start')
txt(qcx + CAP_W / 2 + 1.5, qb - 16, 'Slot offen (0,4 Wand)', 10, RED, 'start')
txt(qcx - SHELL_IN_W / 2, qb - TOP - 11, 'Cartridge innen', 10, '#888', 'start')

# --- Hinweise ---
nx, ny = 62, 116
notes = [('Prinzip (Stefan 15.11.2026):', '#222', True),
         ('Kappe wird über Slot B gesteckt, oben geschlossen,', '#222', False),
         ('nur der Schlitz für die Cartridge-Platine.', '#222', False),
         ('Deckfläche 1,2 über dem Slot: die Kontakte', '#222', False),
         ('sind lang genug (Toleranz laut Standard).', '#222', False),
         ('Volle Länge 74,2 nur oben (Führung in der', '#222', False),
         ('Cartridge), seitlich schräg zum Fuß 51,6.', '#222', False),
         ('2 Schrauben M2,5 von unten durch die Platine.', '#222', False),
         ('Stifte Ø3 separat, nach dem Druck eingepresst', '#222', False),
         ('(Druck kopfüber auf der Deckfläche).', '#222', False),
         ('Offen (rot):', RED, True),
         ('Löcher für die Nasen der Cartridge:', RED, False),
         ('Lage und Größe fehlen, bitte messen.', RED, False),
         ('Versatz 2,1 aus vcsslot, nicht gemessen.', RED, False),
         ('Stifte: Stahl-Passstift 3 × 15 oder gedruckt.', RED, False)]
for i, (t, c, b) in enumerate(notes):
    txt(nx, ny + i * 2.3, t, 12, c, 'start', bold=b)
w, h = 112 * S, 160 * S
svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><rect width="100%" height="100%" fill="white"/>' + \
      f'<text x="{w/2}" y="30" font-family="DejaVu Sans, sans-serif" font-size="20" font-weight="bold" text-anchor="middle">Cartridge-Führung für Slot B – Entwurf 5 (Kappe)</text>' + \
      f'<text x="{w/2}" y="54" font-family="DejaVu Sans, sans-serif" font-size="13" fill="#555" text-anchor="middle">Maße in mm. Idee Stefan 15.11.2026, Hülse nach vcsslot.stl (Thingiverse 618065). Rot = Annahme/offen.</text>' + ''.join(out) + '</svg>'
open(sys.argv[1], 'w').write(svg)
