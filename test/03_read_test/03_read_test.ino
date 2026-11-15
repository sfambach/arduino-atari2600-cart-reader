// Read test: reads the first 4K bank of a cartridge and checks it (all five boards, see config.h).
// Serial monitor: baud rate from config.h (SERIAL_BAUD), line ending "Newline". Insert the cartridge
// the right way round (label towards pins 13-24) BEFORE starting; the supply is off while you insert it.
#include "config.h"
#if defined(ADDR_MCP23017)
#include <Wire.h>
#elif defined(ADDR_74HC595)
#include <SPI.h>
#endif

const uint16_t ROM = 0x1000;        // A12 high = cartridge selected
const uint16_t HOTSPOTS = 0x0FF0;   // 0x1FF0-0x1FFB switch banks on many cartridges: skipped in the checks
uint8_t errors = 0;

// ---------------------------------------------------------------- address bus, per board variant
#if defined(ADDR_MCP23017)
void mcpWrite(uint8_t reg, uint8_t a, uint8_t b) {
  Wire.beginTransmission(MCP_ADDR);
  Wire.write(reg); Wire.write(a); Wire.write(b);
  Wire.endTransmission();
}
void addrBegin() { Wire.begin(); Wire.setClock(I2C_CLOCK); }
void addrDrive() { mcpWrite(0x0C, 0, 0); mcpWrite(0x14, 0, 0); mcpWrite(0x00, 0x00, 0xE0); }  // no pull-ups, low, output
void addrRelease() { mcpWrite(0x00, 0xFF, 0xFF); }
void setAddr(uint16_t a) { mcpWrite(0x14, a & 0xFF, (a >> 8) & 0x1F); }
#elif defined(ADDR_DIRECT)
void addrBegin() {}
void addrDrive() { for (uint8_t i = 0; i < ADDR_LINES; i++) { pinMode(ADDR_ARDUINO_PIN[i], OUTPUT); digitalWrite(ADDR_ARDUINO_PIN[i], LOW); } }
void addrRelease() { for (uint8_t i = 0; i < ADDR_LINES; i++) pinMode(ADDR_ARDUINO_PIN[i], INPUT); }
void setAddr(uint16_t a) { for (uint8_t i = 0; i < ADDR_LINES; i++) digitalWrite(ADDR_ARDUINO_PIN[i], (a >> i) & 1); }
#else  // ADDR_74HC595
void setAddr(uint16_t a) {
  SPI.transfer((a >> 8) & 0x1F);
  SPI.transfer(a & 0xFF);
  digitalWrite(SR_LATCH, HIGH);
  digitalWrite(SR_LATCH, LOW);
}
void addrBegin() {
  pinMode(SR_LATCH, OUTPUT);
  digitalWrite(SR_LATCH, LOW);
  SPI.begin();
  SPI.beginTransaction(SPISettings(SPI_CLOCK, MSBFIRST, SPI_MODE0));
}
void addrDrive() { setAddr(0); }
void addrRelease() { setAddr(0); }  // outputs cannot float; low does not feed an unpowered cartridge
#endif

// ---------------------------------------------------------------- data bus and supply
void dataInput(bool pullup) { for (uint8_t i = 0; i < DATA_LINES; i++) pinMode(DATA_ARDUINO_PIN[i], pullup ? INPUT_PULLUP : INPUT); }

uint8_t readData() {
  uint8_t v = 0;
  for (uint8_t i = 0; i < DATA_LINES; i++) if (digitalRead(DATA_ARDUINO_PIN[i])) v |= 1 << i;
  return v;
}

uint8_t peek(uint16_t a) {
  setAddr(a);
  delayMicroseconds(5);
  return readData();
}

void cartOff() {
  addrRelease();
  dataInput(false);
  digitalWrite(CART_PWR, HIGH);
}

// Orientation check as in the firmware: supply off, pull-ups on D0-D7; D2 low = reversed cartridge.
bool cartOn() {
  cartOff();
  dataInput(true);
  delay(5);
  bool reversed = !(readData() & 0x04);
  dataInput(false);
#if !defined(SKIP_ORIENTATION_CHECK)
  if (reversed) { Serial.println(F("  FAIL cartridge reversed (D2 low), supply stays off")); errors++; return false; }
#endif
  addrDrive();
  digitalWrite(CART_PWR, LOW);
  delay(20);
  int v = analogRead(CART_SENSE);
  if (v < SENSE_POWERED) { cartOff(); Serial.print(F("  FAIL supply too low: ")); Serial.println(v); errors++; return false; }
  Serial.print(F("  OK   orientation and supply (")); Serial.print(v); Serial.println(F(")"));
  return true;
}

// ---------------------------------------------------------------- checks
void hex2(uint8_t v) { if (v < 0x10) Serial.print('0'); Serial.print(v, HEX); }

uint16_t checksum() {  // over the bank without the hotspot area
  uint16_t sum = 0;
  for (uint16_t a = 0; a < HOTSPOTS; a++) sum = (sum << 1 | sum >> 15) ^ peek(ROM + a);
  return sum;
}

void runTest() {
  errors = 0;
  Serial.println(F("\n=== Read test (cartridge the right way round) ==="));
  if (!cartOn()) { Serial.println(F("RESULT: FAIL")); return; }

  Serial.println(F("First 64 bytes at 0x1000:"));
  for (uint16_t r = 0; r < 64; r += 16) {
    Serial.print(F("  ")); Serial.print(ROM + r, HEX); Serial.print(':');
    for (uint8_t i = 0; i < 16; i++) { Serial.print(' '); hex2(peek(ROM + r + i)); }
    Serial.println();
  }

  // 6502 reset vector: points into the cartridge (high byte 0x10-0x1F or 0xF0-0xFF)
  uint8_t lo = peek(ROM + 0xFFC), hi = peek(ROM + 0xFFD);
  bool vecOk = (hi & 0x10) && ((hi & 0xF0) == 0x10 || (hi & 0xF0) == 0xF0);
  Serial.print(vecOk ? F("  OK   ") : F("  FAIL ")); Serial.print(F("reset vector ")); hex2(hi); hex2(lo); Serial.println();
  if (!vecOk) errors++;

  // stuck data bits: every bit must be 0 somewhere and 1 somewhere
  uint8_t orAll = 0, andAll = 0xFF;
  for (uint16_t a = 0; a < HOTSPOTS; a++) { uint8_t v = peek(ROM + a); orAll |= v; andAll &= v; }
  for (uint8_t b = 0; b < DATA_LINES; b++) {
    if (!(orAll >> b & 1)) { Serial.print(F("  FAIL D")); Serial.print(b); Serial.println(F(" always 0")); errors++; }
    if (andAll >> b & 1) { Serial.print(F("  FAIL D")); Serial.print(b); Serial.println(F(" always 1")); errors++; }
  }
  if (orAll == 0xFF && andAll == 0x00) Serial.println(F("  OK   all data bits change"));

  // address lines: if flipping A_k never changes the data, A_k is probably open or stuck
  // (A11 mirrored = 2K cartridge, which is fine)
  for (uint8_t k = 0; k < 12; k++) {
    bool differs = false;
    for (uint16_t a = 0; a < HOTSPOTS && !differs; a++) {
      uint16_t b = a ^ (1 << k);
      if (b >= HOTSPOTS) continue;
      if (peek(ROM + a) != peek(ROM + b)) differs = true;
    }
    if (!differs) {
      Serial.print(k == 11 ? F("  NOTE ") : F("  FAIL ")); Serial.print(F("A")); Serial.print(k);
      Serial.println(k == 11 ? F(" mirrors: 2K cartridge") : F(" has no effect: open or stuck address line?"));
      if (k != 11) errors++;
    }
  }

  // reading twice must give the same result (contacts, timing)
  uint16_t c1 = checksum(), c2 = checksum();
  Serial.print(c1 == c2 ? F("  OK   ") : F("  FAIL ")); Serial.print(F("stable read, checksum ")); Serial.println(c1, HEX);
  if (c1 != c2) errors++;

  cartOff();
  Serial.println(errors ? F("RESULT: FAIL") : F("RESULT: PASS"));
  Serial.println(F("Commands: t = run again, P<hex> = read one byte (0000-1FFF), h = hex dump of 4K"));
}

void dump4k() {
  if (!cartOn()) return;
  for (uint16_t r = 0; r < 0x1000; r += 16) {
    Serial.print(ROM + r, HEX); Serial.print(':');
    for (uint8_t i = 0; i < 16; i++) { Serial.print(' '); hex2(peek(ROM + r + i)); }
    Serial.println();
  }
  cartOff();
}

void setup() {
  digitalWrite(CART_PWR, HIGH);
  pinMode(CART_PWR, OUTPUT);
  dataInput(false);
  Serial.begin(SERIAL_BAUD);
  addrBegin();
  cartOff();
  runTest();
}

void loop() {
  if (!Serial.available()) return;
  String cmd = Serial.readStringUntil('\n');
  cmd.trim();
  if (cmd == "t") runTest();
  else if (cmd == "h") dump4k();
  else if (cmd.length() > 1 && (cmd[0] == 'P' || cmd[0] == 'p')) {
    uint16_t a = strtoul(cmd.c_str() + 1, nullptr, 16) & 0x1FFF;
    if (cartOn()) { hex2(peek(a)); Serial.println(); cartOff(); }
  } else if (cmd.length()) Serial.println(F("? t / P<hex> / h"));
}
