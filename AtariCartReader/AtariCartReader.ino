/*
 Atari 2600 Cartridge Reader for Arduino Mega 2560 / Uno
 Based on ideas from retrocartdumper (SvOlli) and Cart Reader (sanni), GPLv3.

 Serial 115200 baud, commands terminated by newline:
   L                list bankswitching schemes
   D <scheme> [kb]  dump ROM, answer "OK <bytes>\n" followed by raw data
   P <hexaddr>      read single byte (debug)
*/
#include "hal.h"

const uint16_t ROM = 0x1000;

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
  for (uint16_t i = 0; i < len; i++) Serial.write(peek(from + i));
}

void sendFill(uint16_t len) {
  for (uint16_t i = 0; i < len; i++) Serial.write(0xFF);
}

// F8/F6/F4 (+SC): 4K banks, hotspots at the end of ROM space
void dumpFx(uint16_t hot, uint8_t banks, bool superchip) {
  for (uint8_t b = 0; b < banks; b++) {
    for (uint16_t a = ROM; a < ROM + 0x1000; a++) {
      if (superchip && a < ROM + 0x100) { Serial.write(0xFF); continue; }  // RAM
      peek(hot + b);
      Serial.write(peek(a));
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
    Serial.write(peek(a));
  }
}

// FA (CBS RAM+): 3 banks of 4K, hotspots $1FF8-$1FFA, RAM at $1000-$11FF
void dumpFA() {
  for (uint8_t b = 0; b < 3; b++) {
    sendFill(0x200);
    for (uint16_t a = ROM + 0x200; a < ROM + 0x1000; a++) {
      peek(0x1FF8 + b);
      Serial.write(peek(a));
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

struct Scheme { const char *name; uint8_t kb; };
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
}

void setup() {
  Serial.begin(115200);
  halInit();
  Serial.println(F("READY Atari 2600 Cart Reader"));
}

void loop() {
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
    dump(s, kb);
  } else if (cmd == 'P') {
    uint16_t a = strtol(arg.c_str(), nullptr, 16);
    Serial.println(peek(a), HEX);
  } else {
    Serial.println(F("ERR cmd"));
  }
}
