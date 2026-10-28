# Netzlisten und Platzierung der beiden Aufsteckplatinen fuer den Atari-2600-Cartridge-Reader.
# Belegung wie Firmware hal.h (sfambach/arduino-atari2600-cart-reader).
NC = None
CART = {1: 'A7', 2: 'A6', 3: 'A5', 4: 'A4', 5: 'A3', 6: 'A2', 7: 'A1', 8: 'A0', 9: 'D0', 10: 'D1', 11: 'D2', 12: 'GND',
        13: 'D3', 14: 'D4', 15: 'D5', 16: 'D6', 17: 'D7', 18: 'A12', 19: 'A10', 20: 'A11', 21: 'A9', 22: 'A8', 23: 'CART_5V', 24: 'GND'}
SLOT = ('Connector_Generic:Conn_02x12_Top_Bottom', 'Atari 2600 Cartridge-Slot', 'atari:Atari2600_Cart_Slot_2x12_P2.54mm_Row5.50mm_Guide')
C100N = 'Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm'
C10U = 'Capacitor_THT:CP_Radial_D5.0mm_P2.00mm'
R = 'Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal'
FUSE = 'atari:Fuse_PTC_Radial_P5.08mm'
TO92 = 'Package_TO_SOT_THT:TO-92_Inline'
BUTTON = 'Button_Switch_THT:SW_PUSH_6mm'
POWER = {'+5V', 'GND'}


def cart_power(sch_x, sch_y):
    # Switched cartridge supply: polyfuse, PNP high-side switch (LOW = on), voltage sense for the orientation check.
    return {
        'F1': ('Device:Polyfuse', 'MF-R020 (200 mA)', FUSE, (sch_x, sch_y), {'1': '+5V', '2': '+5V_F'}),
        'Q1': ('Transistor_BJT:BC327', 'BC327', TO92, (sch_x + 20, sch_y), {'1': 'CART_5V', '2': 'Q_BASE', '3': '+5V_F'}),
        'R3': ('Device:R', '1k', R, (sch_x + 35, sch_y), {'1': 'CART_PWR', '2': 'Q_BASE'}),
        'R4': ('Device:R', '10k', R, (sch_x + 50, sch_y), {'1': '+5V_F', '2': 'Q_BASE'}),
        'R5': ('Device:R', '10k', R, (sch_x + 65, sch_y), {'1': 'CART_5V', '2': 'CART_SENSE'}),
        'R6': ('Device:R', '100k', R, (sch_x + 80, sch_y), {'1': 'CART_5V', '2': 'GND'}),
    }


def buttons(sch_x, sch_y):
    # Reset on the Arduino's RESET line, read button on A1 (internal pull-up, LOW = pressed).
    return {
        'SW1': ('Switch:SW_Push', 'Reset', BUTTON, (sch_x, sch_y), {'1': 'RESET', '2': 'GND'}),
        'SW2': ('Switch:SW_Push', 'Read', BUTTON, (sch_x + 20, sch_y), {'1': 'READ', '2': 'GND'}),
    }
X0, Y0 = 100, 153.34  # Ursprung der Shield-Footprints = linke untere Ecke des Arduino


def shield_pins(names, conn):
    return {n: conn.get(n) for n in names}


UNO_PINS = ['3V3', '5V1', '5V2', 'A0', 'A1', 'A2', 'A3', 'A4', 'A5', 'AREF', 'D0', 'D1', 'D10', 'D11', 'D12', 'D13', 'D2', 'D3',
            'D4', 'D5', 'D6', 'D7', 'D8', 'D9', 'GND1', 'GND2', 'GND3', 'GND4', 'IORF', 'MISO', 'MOSI', 'RST1', 'RST2', 'SCK',
            'SCL', 'SDA', 'VIN']
MEGA_PINS = UNO_PINS + ['5V3', '5V4', 'A6', 'A7', 'A8', 'A9', 'A10', 'A11', 'A12', 'A13', 'A14', 'A15', 'GND5', 'GND6'] + \
    ['D%d' % i for i in range(14, 54)]

uno_conn = {'5V1': '+5V', 'GND1': 'GND', 'GND2': 'GND', 'GND3': 'GND', 'A4': 'SDA', 'A5': 'SCL', 'D10': 'CART_PWR', 'A0': 'CART_SENSE',
            'RST1': 'RESET', 'A1': 'READ'}
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
        'C2': ('Device:C', '100n', C100N, (250, 150), {'1': 'CART_5V', '2': 'GND'}),
        'C3': ('Device:C_Polarized', '10u', C10U, (265, 150), {'1': '+5V', '2': 'GND'}),
        **cart_power(150, 175),
        **buttons(150, 200),
    },
    drop={'A1': ['MISO', 'MOSI', 'SCK', 'RST2', '5V2', 'GND4'], 'A1_holes': [(66.04, -35.56)]},
    place={
        'A1': ('origin', (X0, Y0), 0),
        'J1': ('at', (120.32, 126.54), 0),
        'F1': ('pads', (122, 111), (127.08, 111)),
        'Q1': ('at', (132, 111), 0),
        'R3': ('pads', (102, 134), (102, 141.62)),
        'R4': ('pads', (105.2, 134), (105.2, 141.62)),
        'R5': ('pads', (108.4, 134), (108.4, 141.62)),
        'R6': ('pads', (111.6, 134), (111.6, 141.62)),
        'U1': ('at', (117.6, 146.1), 90),
        'R1': ('pads', (153.4, 138.5), (161.02, 138.5)),
        'R2': ('pads', (153.4, 143.5), (161.02, 143.5)),
        'C1': ('pads', (160.5, 110), (165.5, 110)),
        'SW1': ('at', (144, 108.5), 0),
        'SW2': ('at', (154, 108.5), 0),
        'C2': ('pads', (106, 109), (111, 109)),
        'C3': ('pads', (114.5, 109), (116.5, 109)),
    },
    texts=[('Atari 2600 Cart Reader - Uno v1.2 - fambach.net', 139, 105.7, 1.0)],
    btexts=[('fambach.net', 134.3, 113.5, 1.0), ('github.com/sfambach/arduino-atari2600-cart-reader', 134.3, 115.5, 0.8)],
)

mega_conn = {'5V1': '+5V', '5V3': '+5V', '5V4': '+5V', 'GND1': 'GND', 'GND2': 'GND', 'GND3': 'GND', 'GND5': 'GND',
             'GND6': 'GND', 'D8': 'CART_PWR', 'A0': 'CART_SENSE', 'RST1': 'RESET', 'A1': 'READ'}
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
        'C2': ('Device:C', '100n', C100N, (250, 150), {'1': 'CART_5V', '2': 'GND'}),
        'C3': ('Device:C_Polarized', '10u', C10U, (265, 150), {'1': '+5V', '2': 'GND'}),
        **cart_power(150, 175),
        **buttons(150, 200),
    },
    drop={'A1': ['MISO', 'MOSI', 'SCK', 'RST2', '5V2', 'GND4']},
    place={
        'A1': ('origin', (X0, Y0), 0),
        'J1': ('at', (121.03, 130.75), 0),
        'F1': ('pads', (128, 142), (133.08, 142)),
        'Q1': ('at', (122, 142), 0),
        'R3': ('pads', (142, 138.5), (142, 146.12)),
        'R4': ('pads', (145.2, 138.5), (145.2, 146.12)),
        'R5': ('pads', (148.4, 138.5), (148.4, 146.12)),
        'R6': ('pads', (151.6, 138.5), (151.6, 146.12)),
        'C2': ('pads', (140, 111), (145, 111)),
        'C3': ('pads', (150, 111), (152, 111)),
        'SW1': ('at', (178.5, 137), 0),
        'SW2': ('at', (188.5, 137), 0),
    },
    texts=[('Atari 2600 Cart Reader - Mega v1.2 - fambach.net', 135, 106.2, 1.2)],
    btexts=[('fambach.net', 122, 128, 1.0), ('github.com/sfambach/arduino-atari2600-cart-reader', 122, 130, 0.8)],
)

NANO_PINS = {'1': 'D1/TX', '2': 'D0/RX', '3': 'RESET1', '4': 'GND', '5': 'D2', '6': 'D3', '7': 'D4', '8': 'D5', '9': 'D6',
             '10': 'D7', '11': 'D8', '12': 'D9', '13': 'D10', '14': 'D11', '15': 'D12', '16': 'D13', '17': '3V3', '18': 'AREF',
             '19': 'A0', '20': 'A1', '21': 'A2', '22': 'A3', '23': 'A4', '24': 'A5', '25': 'A6', '26': 'A7', '27': '+5V',
             '28': 'RESET2', '29': 'GND', '30': 'VIN'}
nano_by_name = dict(uno_conn, **{'+5V': '+5V', 'GND': 'GND', 'RESET1': 'RESET'})
nano_conn = {num: nano_by_name.get(name) for num, name in NANO_PINS.items()}
NX, NY = 100, 100  # linke obere Ecke der Nano-Platine

NANO = dict(
    name='atari2600-cart-reader-nano',
    title='Atari 2600 Cart Reader - Nano-Platine',
    note='Traegerplatine fuer Arduino Nano (ATmega328P, gesteckt). Gleiche Belegung und Firmware wie die Uno-Variante:\n'
         'Adressbus A0-A12 ueber MCP23017 (I2C 0x20), Datenbus D0-D7 an Nano D2-D9, Versorgung Cartridge D10, Messung A0.\n'
         'Firmware: github.com/sfambach/arduino-atari2600-cart-reader - fambach.net',
    board=(NX, NY, NX + 80, NY + 62),
    parts={
        'A1': ('MCU_Module:Arduino_Nano_v3.x', 'Arduino Nano v3', 'Module:Arduino_Nano', (60, 100), nano_conn),
        'J1': (*SLOT, (215, 100), {str(k): v for k, v in CART.items()}),
        'U1': ('Interface_Expansion:MCP23017_SP', 'MCP23017-E/SP', 'Package_DIP:DIP-28_W7.62mm_Socket', (150, 100), mcp),
        'R1': ('Device:R', '4k7', R, (250, 60), {'1': '+5V', '2': 'SDA'}),
        'R2': ('Device:R', '4k7', R, (265, 60), {'1': '+5V', '2': 'SCL'}),
        'C1': ('Device:C', '100n', C100N, (185, 60), {'1': '+5V', '2': 'GND'}),
        'C2': ('Device:C', '100n', C100N, (250, 150), {'1': 'CART_5V', '2': 'GND'}),
        'C3': ('Device:C_Polarized', '10u', C10U, (265, 150), {'1': '+5V', '2': 'GND'}),
        'H1': ('Mechanical:MountingHole', 'M3', 'MountingHole:MountingHole_3.2mm_M3', (280, 60), {}),
        'H2': ('Mechanical:MountingHole', 'M3', 'MountingHole:MountingHole_3.2mm_M3', (290, 60), {}),
        **cart_power(150, 175),
        **buttons(150, 200),
    },
    place={
        'A1': ('at', (NX + 37.5, NY + 58.24), 90),
        'J1': ('at', (NX + 40 - 13.97, NY + 14.5 + 2.75), 0),
        'U1': ('at', (NX + 13, NY + 35.6), 90),
        'R1': ('pads', (NX + 50, NY + 28), (NX + 57.62, NY + 28)),
        'R2': ('pads', (NX + 50, NY + 32), (NX + 57.62, NY + 32)),
        'C1': ('pads', (NX + 62, NY + 28), (NX + 67, NY + 28)),
        'C2': ('pads', (NX + 18, NY + 53), (NX + 23, NY + 53)),
        'C3': ('pads', (NX + 26, NY + 53), (NX + 28, NY + 53)),
        'F1': ('pads', (NX + 24, NY + 45), (NX + 29.08, NY + 45)),
        'Q1': ('at', (NX + 18, NY + 45), 0),
        'R3': ('pads', (NX + 4, NY + 43), (NX + 4, NY + 50.62)),
        'R4': ('pads', (NX + 7.2, NY + 43), (NX + 7.2, NY + 50.62)),
        'R5': ('pads', (NX + 10.4, NY + 43), (NX + 10.4, NY + 50.62)),
        'R6': ('pads', (NX + 13.6, NY + 43), (NX + 13.6, NY + 50.62)),
        'SW1': ('at', (NX + 67.5, NY + 34), 0),
        'SW2': ('at', (NX + 9.5, NY + 53.5), 0),
        'H1': ('pos', (NX + 3.5, NY + 31), 0),
        'H2': ('pos', (NX + 76.5, NY + 31), 0),
    },
    texts=[('Atari 2600 Cart Reader - Nano v1.2 - fambach.net', NX + 40, NY + 3.5, 1.2)],
    btexts=[('fambach.net', NX + 40, NY + 37.5, 1.0), ('github.com/sfambach/arduino-atari2600-cart-reader', NX + 40, NY + 39.5, 0.8)],
)

BOARDS = {'uno': UNO, 'mega': MEGA, 'nano': NANO}
