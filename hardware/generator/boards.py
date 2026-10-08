# Netzlisten und Platzierung der beiden Aufsteckplatinen fuer den Atari-2600-Cartridge-Reader.
# Belegung wie Firmware hal.h (sfambach/arduino-atari2600-cart-reader).
NC = None
CART = {1: 'A7', 2: 'A6', 3: 'A5', 4: 'A4', 5: 'A3', 6: 'A2', 7: 'A1', 8: 'A0', 9: 'D0', 10: 'D1', 11: 'D2', 12: 'GND',
        13: 'D3', 14: 'D4', 15: 'D5', 16: 'D6', 17: 'D7', 18: 'A12', 19: 'A10', 20: 'A11', 21: 'A9', 22: 'A8', 23: '+5V', 24: 'GND'}
SLOT = ('Connector_Generic:Conn_02x12_Top_Bottom', 'Atari 2600 Cartridge-Slot', 'atari:Atari2600_Cart_Slot_2x12_P2.54mm_Row5.08mm')
C100N = 'Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm'
C10U = 'Capacitor_THT:CP_Radial_D5.0mm_P2.00mm'
R = 'Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal'
POWER = {'+5V', 'GND'}
X0, Y0 = 100, 153.34  # Ursprung der Shield-Footprints = linke untere Ecke des Arduino


def shield_pins(names, conn):
    return {n: conn.get(n) for n in names}


UNO_PINS = ['3V3', '5V1', '5V2', 'A0', 'A1', 'A2', 'A3', 'A4', 'A5', 'AREF', 'D0', 'D1', 'D10', 'D11', 'D12', 'D13', 'D2', 'D3',
            'D4', 'D5', 'D6', 'D7', 'D8', 'D9', 'GND1', 'GND2', 'GND3', 'GND4', 'IORF', 'MISO', 'MOSI', 'RST1', 'RST2', 'SCK',
            'SCL', 'SDA', 'VIN']
MEGA_PINS = UNO_PINS + ['5V3', '5V4', 'A6', 'A7', 'A8', 'A9', 'A10', 'A11', 'A12', 'A13', 'A14', 'A15', 'GND5', 'GND6'] + \
    ['D%d' % i for i in range(14, 54)]

uno_conn = {'5V1': '+5V', 'GND1': 'GND', 'GND2': 'GND', 'GND3': 'GND', 'A4': 'SDA', 'A5': 'SCL'}
for i in range(8):
    uno_conn['D%d' % (i + 2)] = 'D%d' % i
mcp = {'9': '+5V', '10': 'GND', '11': NC, '12': 'SCL', '13': 'SDA', '14': NC, '15': 'GND', '16': 'GND', '17': 'GND',
       '18': '+5V', '19': NC, '20': NC, '6': NC, '7': NC, '8': NC}
for i in range(8):
    mcp[str(21 + i)] = 'A%d' % i
for i in range(5):
    mcp[str(1 + i)] = 'A%d' % (8 + i)

UNO = dict(
    name='atari2600-cart-reader-uno',
    title='Atari 2600 Cart Reader - Uno-Shield',
    note='Aufsteckplatine fuer Arduino Uno R3. Adressbus A0-A12 ueber MCP23017 (I2C 0x20), Datenbus D0-D7 an Uno D2-D9.\n'
         'Firmware: github.com/sfambach/arduino-atari2600-cart-reader - fambach.net',
    board=(X0, Y0 - 53.34, X0 + 68.58, Y0),
    parts={
        'A1': ('arduino-library:Arduino_Uno_R3_Shield', 'Arduino Uno R3', 'arduino-library:Arduino_Uno_R3_Shield', (60, 100),
               shield_pins(UNO_PINS, uno_conn)),
        'J1': (*SLOT, (215, 100), {str(k): v for k, v in CART.items()}),
        'U1': ('Interface_Expansion:MCP23017_SP', 'MCP23017-E/SP', 'Package_DIP:DIP-28_W7.62mm_Socket', (150, 100), mcp),
        'R1': ('Device:R', '4k7', R, (250, 60), {'1': '+5V', '2': 'SDA'}),
        'R2': ('Device:R', '4k7', R, (265, 60), {'1': '+5V', '2': 'SCL'}),
        'C1': ('Device:C', '100n', C100N, (185, 60), {'1': '+5V', '2': 'GND'}),
        'C2': ('Device:C', '100n', C100N, (250, 150), {'1': '+5V', '2': 'GND'}),
        'C3': ('Device:C_Polarized', '10u', C10U, (265, 150), {'1': '+5V', '2': 'GND'}),
    },
    place={
        'A1': ('origin', (X0, Y0), 0),
        'J1': ('at', (120.32, 126.54), 0),
        'U1': ('at', (117.6, 146.1), 90),
        'R1': ('pads', (153.4, 138.5), (161.02, 138.5)),
        'R2': ('pads', (153.4, 143.5), (161.02, 143.5)),
        'C1': ('pads', (154.5, 110), (159.5, 110)),
        'C2': ('pads', (106, 109), (111, 109)),
        'C3': ('pads', (114.5, 109), (116.5, 109)),
    },
    texts=[('Atari 2600 Cart Reader - Uno v1.0', 134.3, 106.2, 1.2), ('MCP23017', 134, 142.3, 1.0)],
    btexts=[('fambach.net', 134.3, 113.5, 1.0), ('github.com/sfambach/arduino-atari2600-cart-reader', 134.3, 115.5, 0.8)],
)

mega_conn = {'5V1': '+5V', '5V3': '+5V', '5V4': '+5V', 'GND1': 'GND', 'GND2': 'GND', 'GND3': 'GND', 'GND5': 'GND',
             'GND6': 'GND'}
for i in range(8):
    mega_conn['D%d' % (22 + i)] = 'A%d' % i      # PA0-PA7
    mega_conn['D%d' % (49 - i)] = 'D%d' % i      # PL0-PL7
for i in range(5):
    mega_conn['D%d' % (37 - i)] = 'A%d' % (8 + i)  # PC0-PC4

MEGA = dict(
    name='atari2600-cart-reader-mega',
    title='Atari 2600 Cart Reader - Mega-Shield',
    note='Aufsteckplatine fuer Arduino Mega 2560. A0-A7 = PA0-PA7 (D22-D29), A8-A12 = PC0-PC4 (D37-D33), D0-D7 = PL0-PL7 (D49-D42).\n'
         'Firmware: github.com/sfambach/arduino-atari2600-cart-reader - fambach.net',
    board=(X0, Y0 - 53.34, X0 + 101.6, Y0),
    parts={
        'A1': ('arduino-library:Arduino_Mega2560_R3_Shield', 'Arduino Mega 2560 R3', 'arduino-library:Arduino_Mega2560_R3_Shield',
               (60, 100), shield_pins(MEGA_PINS, mega_conn)),
        'J1': (*SLOT, (215, 100), {str(k): v for k, v in CART.items()}),
        'C2': ('Device:C', '100n', C100N, (250, 150), {'1': '+5V', '2': 'GND'}),
        'C3': ('Device:C_Polarized', '10u', C10U, (265, 150), {'1': '+5V', '2': 'GND'}),
    },
    place={
        'A1': ('origin', (X0, Y0), 0),
        'J1': ('at', (175, 110), 270),
        'C2': ('pads', (150, 113), (155, 113)),
        'C3': ('pads', (150, 120), (152, 120)),
    },
    texts=[('Atari 2600 Cart Reader - Mega v1.0', 135, 106.2, 1.2)],
    btexts=[('fambach.net', 135, 128, 1.0), ('github.com/sfambach/arduino-atari2600-cart-reader', 135, 130, 0.8)],
)

BOARDS = {'uno': UNO, 'mega': MEGA}
