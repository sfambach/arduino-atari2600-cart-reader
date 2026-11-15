/*
 Atari 2600 Cartridge Reader for Arduino Mega 2560 / Uno / Nano
 Based on ideas from retrocartdumper (SvOlli) and Cart Reader (sanni), GPLv3.

 Serial at SERIAL_BAUD (config.h), commands terminated by newline (protocol 1, used by the PC program
 in software/ and by tools/dump.py; every answer line is plain text, so a serial monitor works too):
   H                "HELLO AtariCartReader <version> <board> 1"
   L                list bankswitching schemes, one "<name> <kb>K" per line, then "END"
   D <scheme> [kb]  dump ROM: "OK <bytes>", the raw bytes, then "CRC <crc32 hex>"
   P <hexaddr>      read single byte (debug)
   S                "STATUS <data bits hex> <ok|reversed> <supply ADC or -1>"
 Errors: "ERR <text>".

 The cartridge is only powered while a command runs. Before switching on, the
 firmware checks the orientation with the supply off: a reversed cartridge puts
 its own +5V pin on slot pin 11 (D2), and its unpowered circuit pulls that pin
 low against the pull-up. D2 low keeps the supply off. Other data lines may be
 low on a correct cartridge (measured on a 32-in-1 multicart: D4) and are ignored.
*/
#include "config.h"
#include "hal.h"

const char FW_VERSION[] = "0.2.1";
const uint8_t PROTOCOL = 1;

struct Scheme { const char *name; uint8_t kb; };  // before any function: Arduino inserts prototypes there

const uint16_t ROM = 0x1000;

uint32_t crc;  // CRC-32 (IEEE) of the bytes sent by the running dump

void out(uint8_t b) {
  Serial.write(b);
  crc ^= b;
  for (uint8_t i = 0; i < 8; i++) crc = (crc >> 1) ^ (0xEDB88320UL & (0UL - (crc & 1)));
}

// Data bus with pull-ups, supply off. Bit 2 (D2) low = reversed cartridge.
uint8_t readOrientation() {
  digitalWrite(CART_PWR, HIGH);
  halRelease();
  halPullupData(true);
  delay(5);
  uint8_t v = halReadData();
  halPullupData(false);
  return v;
}

void cartOff() {
  halRelease();
  digitalWrite(CART_PWR, HIGH);
}

bool cartOn() {
#if !defined(SKIP_ORIENTATION_CHECK)
  if (!(readOrientation() & 0x04)) {
    Serial.println(F("ERR cartridge inserted the wrong way round"));
    return false;
  }
#endif
  halDrive();
  digitalWrite(CART_PWR, LOW);
  delay(20);
  if (analogRead(CART_SENSE) < SENSE_POWERED) {
    cartOff();
    Serial.println(F("ERR cartridge supply too low (short?)"));
    return false;
  }
  return true;
}

uint8_t peek(uint16_t addr) {
  halSetAddr(addr);
  return halReadData();
}

// Write with A12 low: cartridge does not drive the bus, Arduino does.
void poke(uint16_t addr, uint8_t data) {
  halWriteData(data);
  halSetAddr(addr);
  halSetAddr(addr & 0x0FFF);
  halReleaseData();
}

void sendRange(uint16_t from, uint16_t len) {
  for (uint16_t i = 0; i < len; i++) out(peek(from + i));
}

void sendFill(uint16_t len) {
  for (uint16_t i = 0; i < len; i++) out(0xFF);
}

// F8/F6/F4 (+SC): 4K banks, hotspots at the end of ROM space
void dumpFx(uint16_t hot, uint8_t banks, bool superchip) {
  for (uint8_t b = 0; b < banks; b++) {
    for (uint16_t a = ROM; a < ROM + 0x1000; a++) {
      if (superchip && a < ROM + 0x100) { out(0xFF); continue; }  // RAM
      if (a == ROM || a - 1 >= 0x1FF4) peek(hot + b);  // select the bank; again after reading a hotspot
      out(peek(a));
    }
  }
}

// E0 (Parker Bros.): 8 slices of 1K, first window at $1000
void dumpE0() {
  for (uint8_t s = 0; s < 8; s++) {
    peek(0x1FE0 + s);
    sendRange(ROM, 0x400);
  }
}

// E7 (M-Network): 2K banks 0-6 at $1000, bank 7 fixed at $1800 (first 512 bytes hidden by RAM)
void dumpE7() {
  for (uint8_t b = 0; b < 7; b++) {
    peek(0x1FE0 + b);
    sendRange(ROM, 0x800);
  }
  sendFill(0x200);
  for (uint16_t a = 0x1A00; a < 0x2000; a++) {
    out(peek(a));
  }
}

// FA (CBS RAM+): 3 banks of 4K, hotspots $1FF8-$1FFA, RAM at $1000-$11FF
void dumpFA() {
  for (uint8_t b = 0; b < 3; b++) {
    sendFill(0x200);
    for (uint16_t a = ROM + 0x200; a < ROM + 0x1000; a++) {
      peek(0x1FF8 + b);
      out(peek(a));
    }
  }
}

// FE (Activision): bank chosen by D5 of the access after $01FE (experimental)
void dumpFE() {
  for (uint8_t b = 0; b < 2; b++) {
    halSetAddr(0x01FE);
    halWriteData(b == 0 ? 0xF0 : 0xD0);
    halSetAddr(0x01FF);
    halReleaseData();
    sendRange(ROM, 0x1000);
  }
}

// 3F (Tigervision): write bank to $003F, 2K window at $1000, last bank fixed at $1800
void dump3F(uint8_t kb) {
  uint8_t banks = kb / 2;
  for (uint8_t b = 0; b < banks; b++) {
    poke(0x003F, b);
    sendRange(ROM, 0x800);
  }
}

const Scheme schemes[] = {
  {"2K", 2}, {"4K", 4}, {"F8", 8}, {"F8SC", 8}, {"F6", 16}, {"F6SC", 16},
  {"F4", 32}, {"F4SC", 32}, {"E0", 8}, {"E7", 16}, {"FA", 12}, {"FE", 8}, {"3F", 8},
};

const Scheme *findScheme(const String &n) {
  for (const Scheme &s : schemes) if (n.equalsIgnoreCase(s.name)) return &s;
  return nullptr;
}

void dump(const Scheme *s, uint8_t kb) {
  String n = s->name;
  Serial.print(F("OK "));
  Serial.println((uint32_t)kb * 1024);
  crc = 0xFFFFFFFFUL;
  if (n == "2K") sendRange(ROM, 0x800);
  else if (n == "4K") sendRange(ROM, 0x1000);
  else if (n.startsWith("F8")) dumpFx(0x1FF8, 2, n.endsWith("SC"));
  else if (n.startsWith("F6")) dumpFx(0x1FF6, 4, n.endsWith("SC"));
  else if (n.startsWith("F4")) dumpFx(0x1FF4, 8, n.endsWith("SC"));
  else if (n == "E0") dumpE0();
  else if (n == "E7") dumpE7();
  else if (n == "FA") dumpFA();
  else if (n == "FE") dumpFE();
  else if (n == "3F") dump3F(kb);
  Serial.print(F("CRC "));
  Serial.println(crc ^ 0xFFFFFFFFUL, HEX);
}

String lastScheme = "4K";
uint8_t lastKb = 4;

// Dumps with the scheme of the last D command (4K until one was given); the host saves it with dump.py listen.
void readButton() {
  if (digitalRead(READ_BUTTON) == HIGH) return;
  delay(20);
  if (digitalRead(READ_BUTTON) == HIGH) return;
  if (cartOn()) {
    dump(findScheme(lastScheme), lastKb);
    cartOff();
  }
  while (digitalRead(READ_BUTTON) == LOW) {}
  delay(20);
}

void hello() {
  Serial.print(F("HELLO AtariCartReader "));
  Serial.print(FW_VERSION);
  Serial.print(' ');
  Serial.print(F(BOARD_NAME));
  Serial.print(' ');
  Serial.println(PROTOCOL);
}

void setup() {
  Serial.begin(SERIAL_BAUD);
  pinMode(READ_BUTTON, INPUT_PULLUP);
  digitalWrite(CART_PWR, HIGH);
  pinMode(CART_PWR, OUTPUT);
  halInit();
  Serial.println(F("READY Atari 2600 Cart Reader"));
  hello();
}

void loop() {
  readButton();
  if (!Serial.available()) return;
  String line = Serial.readStringUntil('\n');
  line.trim();
  if (line.length() == 0) return;
  char cmd = toupper(line[0]);
  String arg = line.substring(1);
  arg.trim();

  if (cmd == 'L') {
    for (const Scheme &s : schemes) {
      Serial.print(s.name); Serial.print(' '); Serial.print(s.kb); Serial.println(F("K"));
    }
    Serial.println(F("END"));
  } else if (cmd == 'D') {
    int sp = arg.indexOf(' ');
    String name = sp < 0 ? arg : arg.substring(0, sp);
    const Scheme *s = findScheme(name);
    if (!s) { Serial.println(F("ERR scheme")); return; }
    uint8_t kb = s->kb;
    if (sp > 0 && s->name[0] == '3') kb = arg.substring(sp + 1).toInt();
    lastScheme = s->name;
    lastKb = kb;
    if (!cartOn()) return;
    dump(s, kb);
    cartOff();
  } else if (cmd == 'P') {
    uint16_t a = strtol(arg.c_str(), nullptr, 16);
    if (!cartOn()) return;
    Serial.println(peek(a), HEX);
    cartOff();
  } else if (cmd == 'S') {
    uint8_t o = readOrientation();
    bool ok = o & 0x04;
    int supply = -1;
    if (ok) {
      digitalWrite(CART_PWR, LOW);
      delay(20);
      supply = analogRead(CART_SENSE);
    }
    cartOff();
    Serial.print(F("STATUS "));
    Serial.print(o, HEX);
    Serial.print(ok ? F(" ok ") : F(" reversed "));
    Serial.println(supply);
  } else if (cmd == 'H') {
    hello();
  } else {
    Serial.println(F("ERR cmd"));
  }
}
