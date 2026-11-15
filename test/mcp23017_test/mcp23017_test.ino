// MCP23017 board test for the Uno / Nano MCP23017 boards. Run WITHOUT a cartridge in the slot.
// Serial monitor: 115200 baud, line ending "Newline".
#include <Wire.h>
#include "config.h"

const uint8_t REG_IODIRA = 0x00, REG_GPPUA = 0x0C, REG_GPIOA = 0x12, REG_OLATA = 0x14;
const uint8_t ADDR_LINES = 13, DATA_LINES = 8;
const uint8_t ADDR_SLOT_PIN[ADDR_LINES] = {8, 7, 6, 5, 4, 3, 2, 1, 22, 21, 19, 20, 18};
const uint8_t DATA_SLOT_PIN[DATA_LINES] = {9, 10, 11, 13, 14, 15, 16, 17};
const uint8_t DATA_ARDUINO_PIN[DATA_LINES] = {2, 3, 4, 5, 6, 7, 8, 9};

uint8_t errors = 0;

void mcpWrite(uint8_t reg, uint8_t a, uint8_t b) {
  Wire.beginTransmission(MCP_ADDR);
  Wire.write(reg); Wire.write(a); Wire.write(b);
  Wire.endTransmission();
}

uint16_t mcpRead(uint8_t reg) {
  Wire.beginTransmission(MCP_ADDR);
  Wire.write(reg);
  if (Wire.endTransmission(false) != 0) return 0xFFFF;
  if (Wire.requestFrom(MCP_ADDR, (uint8_t)2) != 2) return 0xFFFF;
  uint8_t a = Wire.read();
  return a | (Wire.read() << 8);
}

uint16_t readAddrLines() { return mcpRead(REG_GPIOA) & 0x1FFF; }  // GPB5-7 are unused

uint8_t readDataLines() {
  uint8_t v = 0;
  for (uint8_t i = 0; i < DATA_LINES; i++) if (digitalRead(DATA_ARDUINO_PIN[i])) v |= 1 << i;
  return v;
}

void releaseAll() {
  mcpWrite(REG_IODIRA, 0xFF, 0xFF);
  mcpWrite(REG_GPPUA, 0xFF, 0x1F);  // weak pull-ups on A0-A12
  mcpWrite(REG_OLATA, 0x00, 0x00);
  for (uint8_t i = 0; i < DATA_LINES; i++) pinMode(DATA_ARDUINO_PIN[i], INPUT_PULLUP);
}

void fail(const __FlashStringHelper *msg) { errors++; Serial.print(F("  FAIL ")); Serial.println(msg); }

void printAddr(uint8_t i) { Serial.print(F("A")); Serial.print(i); Serial.print(F(" (slot ")); Serial.print(ADDR_SLOT_PIN[i]); Serial.print(F(")")); }
void printData(uint8_t i) { Serial.print(F("D")); Serial.print(i); Serial.print(F(" (slot ")); Serial.print(DATA_SLOT_PIN[i]); Serial.print(F(")")); }

bool testScan() {
  Serial.println(F("1. I2C scan"));
  bool found = false;
  for (uint8_t a = 1; a < 0x7F; a++) {
    Wire.beginTransmission(a);
    if (Wire.endTransmission() == 0) {
      Serial.print(F("  device at 0x")); Serial.println(a, HEX);
      if (a == MCP_ADDR) found = true;
    }
  }
  if (!found) {
    fail(F("no MCP23017 at 0x20. Check: A0-A2 to GND, RESET to +5V, VDD/VSS, SDA = A4, SCL = A5, pull-ups."));
    return false;
  }
  Serial.println(F("  OK"));
  return true;
}

void testRegisters() {
  Serial.println(F("2. Register write / read back"));
  const uint8_t pattern[] = {0x55, 0xAA, 0x00, 0xFF};
  for (uint8_t p : pattern) {
    mcpWrite(REG_OLATA, p, p);
    if (mcpRead(REG_OLATA) != (uint16_t)(p | (p << 8))) { fail(F("OLAT read back differs")); return; }
  }
  mcpWrite(REG_OLATA, 0x00, 0x00);
  Serial.println(F("  OK"));
}

void testIdle() {
  Serial.println(F("3. All lines high with pull-ups (short to GND?)"));
  releaseAll();
  delay(5);
  uint16_t addr = readAddrLines();
  uint8_t data = readDataLines();
  for (uint8_t i = 0; i < ADDR_LINES; i++) if (!(addr & (1 << i))) { Serial.print(F("  ")); printAddr(i); fail(F("is low")); }
  for (uint8_t i = 0; i < DATA_LINES; i++) if (!(data & (1 << i))) { Serial.print(F("  ")); printData(i); fail(F("is low")); }
  if (addr == 0x1FFF && data == 0xFF) Serial.println(F("  OK"));
}

void reportShorts(bool isAddr, uint8_t line, uint16_t addr, uint8_t data) {
  for (uint8_t j = 0; j < ADDR_LINES; j++) {
    bool self = isAddr && j == line;
    bool low = !(addr & (1 << j));
    if (self != low) {
      Serial.print(F("  ")); isAddr ? printAddr(line) : printData(line);
      if (self) fail(F("does not go low"));
      else { Serial.print(F(" -> ")); printAddr(j); fail(F("short")); }
    }
  }
  for (uint8_t j = 0; j < DATA_LINES; j++) {
    bool self = !isAddr && j == line;
    bool low = !(data & (1 << j));
    if (self != low) {
      Serial.print(F("  ")); isAddr ? printAddr(line) : printData(line);
      if (self) fail(F("does not go low"));
      else { Serial.print(F(" -> ")); printData(j); fail(F("short")); }
    }
  }
}

void testShorts() {
  Serial.println(F("4. Walking low: one line low, all others must stay high"));
  uint8_t before = errors;
  for (uint8_t i = 0; i < ADDR_LINES; i++) {
    releaseAll();
    uint16_t dir = ~(1 << i);
    mcpWrite(REG_IODIRA, dir & 0xFF, dir >> 8);
    delay(2);
    uint16_t addr = readAddrLines();
    uint8_t data = readDataLines();
    releaseAll();
    reportShorts(true, i, addr, data);
  }
  for (uint8_t i = 0; i < DATA_LINES; i++) {
    releaseAll();
    pinMode(DATA_ARDUINO_PIN[i], OUTPUT);
    digitalWrite(DATA_ARDUINO_PIN[i], LOW);
    delay(2);
    uint16_t addr = readAddrLines();
    uint8_t data = readDataLines();
    releaseAll();
    reportShorts(false, i, addr, data);
  }
  if (errors == before) Serial.println(F("  OK"));
}

void runTests() {
  errors = 0;
  Serial.println(F("\n=== MCP23017 board test (no cartridge in the slot!) ==="));
  if (testScan()) {
    testRegisters();
    testIdle();
    testShorts();
  }
  releaseAll();
  Serial.println(errors ? F("RESULT: FAIL") : F("RESULT: PASS"));
  Serial.println(F("Commands: t = run tests, w = walk address lines (measure at the slot), aXXXX = set address (hex), r = release"));
}

void walk() {
  Serial.println(F("Walking one: each address line HIGH in turn, measure against slot pin 12/24 (GND). Any key stops."));
  mcpWrite(REG_GPPUA, 0x00, 0x00);
  mcpWrite(REG_OLATA, 0x00, 0x00);
  mcpWrite(REG_IODIRA, 0x00, 0xE0);
  while (true) {
    for (uint8_t i = 0; i < ADDR_LINES; i++) {
      uint16_t v = 1 << i;
      mcpWrite(REG_OLATA, v & 0xFF, v >> 8);
      Serial.print(F("  HIGH: ")); printAddr(i); Serial.println();
      for (unsigned long t = 0; t < WALK_STEP_MS / 100; t++) {
        delay(100);
        if (Serial.available()) { while (Serial.available()) Serial.read(); releaseAll(); Serial.println(F("stopped, lines released")); return; }
      }
    }
  }
}

void setAddress(uint16_t value) {
  value &= 0x1FFF;
  mcpWrite(REG_GPPUA, 0x00, 0x00);
  mcpWrite(REG_OLATA, value & 0xFF, value >> 8);
  mcpWrite(REG_IODIRA, 0x00, 0xE0);
  Serial.print(F("address 0x")); Serial.print(value, HEX); Serial.println(F(" on A0-A12 (r = release)"));
}

void setup() {
  pinMode(CART_PWR, OUTPUT);
  digitalWrite(CART_PWR, HIGH);
  Serial.begin(SERIAL_BAUD);
  Wire.begin();
  Wire.setClock(I2C_CLOCK);
  releaseAll();
  runTests();
}

void loop() {
  if (!Serial.available()) return;
  String cmd = Serial.readStringUntil('\n');
  cmd.trim();
  if (cmd == "t") runTests();
  else if (cmd == "w") walk();
  else if (cmd == "r") { releaseAll(); Serial.println(F("released")); }
  else if (cmd.length() > 1 && cmd[0] == 'a') setAddress(strtoul(cmd.c_str() + 1, nullptr, 16));
  else if (cmd.length()) Serial.println(F("? t / w / aXXXX / r"));
}
