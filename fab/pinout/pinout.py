# Pinbelegung Cartridge-Kontaktleiste, Ansicht von unten, Etikett oben (Quelle: WiringVCS, The Hardware Book)
import sys
SIG = {1:'A7',2:'A6',3:'A5',4:'A4',5:'A3',6:'A2',7:'A1',8:'A0',9:'D0',10:'D1',11:'D2',12:'GND',
       13:'D3',14:'D4',15:'D5',16:'D6',17:'D7',18:'A12',19:'A10',20:'A11',21:'A9',22:'A8',23:'+5V',24:'GND'}
def color(s): return '#c0392b' if s == '+5V' else '#333' if s == 'GND' else '#1f5fbf' if s.startswith('A') else '#2e7d32'
W, H, X0, PW = 900, 470, 90, 60
o = []
def t(x, y, s, size=15, c='#222', b=False, a='middle'):
    o.append(f'<text x="{x}" y="{y}" font-family="DejaVu Sans, sans-serif" font-size="{size}" fill="{c}" text-anchor="{a}"' + (' font-weight="bold"' if b else '') + f'>{s}</text>')
t(W/2, 38, 'Atari 2600 Cartridge – Pinbelegung der Kontaktleiste', 22, b=True)
t(W/2, 64, 'Blick von unten auf die Kontakte, Etikett oben', 15, '#555')
o.append(f'<rect x="{X0-20}" y="95" width="{12*PW+40}" height="40" fill="#f3e6c4" stroke="#8a7a50" stroke-width="2"/>')
t(W/2, 121, 'Etikettseite', 16, '#6b5a2e', True)
o.append(f'<rect x="{X0-20}" y="140" width="{12*PW+40}" height="220" fill="#2f6b3a" stroke="#1d4425" stroke-width="2"/>')
rows = [(range(13, 25), 150, 'Etikettseite: Pins 13–24'), (range(12, 0, -1), 270, 'Rückseite: Pins 1–12')]
for pins, y, label in rows:
    for i, n in enumerate(pins):
        x = X0 + i * PW
        o.append(f'<rect x="{x+8}" y="{y}" width="{PW-16}" height="80" rx="4" fill="#d4af37" stroke="#8c6d1f" stroke-width="1.5"/>')
        t(x + PW/2, y + 30, str(n), 17, '#222', True)
        t(x + PW/2, y + 58, SIG[n], 14, color(SIG[n]), True)
t(W/2, 395, 'Obere Reihe = Etikettseite (Pins 13–24), untere Reihe = Rückseite (Pins 1–12)', 14, '#333')
t(W/2, 420, 'Pin k liegt gegenüber Pin 25 − k. Verkehrt herum gesteckt landen +5 V auf D2 (Pin 11).', 14, '#c0392b')
t(W/2, 450, 'Quellen: WiringVCS (drzaiusx11), The Hardware Book; Gegenprobe: Pin 23 hat Durchgang zu ROM-VCC.', 12, '#666')
svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><rect width="100%" height="100%" fill="white"/>' + ''.join(o) + '</svg>'
open(sys.argv[1], 'w').write(svg)
