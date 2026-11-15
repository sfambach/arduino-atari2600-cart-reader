// Switched cartridge supply and orientation check (all five boards, see config.h).
// Serial monitor: baud rate from config.h (SERIAL_BAUD), line ending "Newline". Start WITHOUT a cartridge.
#include "config.h"
#if defined(ADDR_MCP23017)
#include <Wire.h>
#elif defined(ADDR_74HC595)
#include <SPI.h>
#endif

uint8_t errors = 0;
bool manualOn = false;          // set by the manual switch (1 / 0)
unsigned long lastPrint = 0;

void addressLow() {  // keeps the ROM disabled in either orientation, as in the firmware
#if defined(ADDR_DIRECT)
  for (uint8_t i = 0; i < ADDR_LINES; i++) { pinMode(ADDR_ARDUINO_PIN[i], OUTPUT); digitalWrite(ADDR_ARDUINO_PIN[i], LOW); }
#elif defined(ADDR_MCP23017)
  Wire.beginTransmission(MCP_ADDR); Wire.write(0x12); Wire.write(0); Wire.write(0); Wire.endTransmission();
  Wire.beginTransmission(MCP_ADDR); Wire.write(0x00); Wire.write(0); Wire.write(0); Wire.endTransmission();
#else
  SPI.transfer(0); SPI.transfer(0);
  digitalWrite(SR_LATCH, HIGH); digitalWrite(SR_LATCH, LOW);
#endif
}

void addressRelease() {
#if defined(ADDR_DIRECT)
  for (uint8_t i = 0; i < ADDR_LINES; i++) pinMode(ADDR_ARDUINO_PIN[i], INPUT);
#elif defined(ADDR_MCP23017)
  Wire.beginTransmission(MCP_ADDR); Wire.write(0x00); Wire.write(0xFF); Wire.write(0xFF); Wire.endTransmission();
#endif  // 74HC595 outputs cannot float; they stay low
}

void releaseData() { for (uint8_t i = 0; i < DATA_LINES; i++) pinMode(DATA_ARDUINO_PIN[i], INPUT); }

void supplyOff() {
  manualOn = false;
  digitalWrite(CART_PWR, HIGH);
  releaseData();
  addressRelease();
}

void printSense(int v) {
  Serial.print(v); Serial.print(F(" (")); Serial.print(v * 5.0 / 1023, 2); Serial.print(F(" V)"));
}

void check(bool ok, const __FlashStringHelper *what, int v) {
  Serial.print(ok ? F("  OK   ") : F("  FAIL ")); Serial.print(what); Serial.print(F(": ")); printSense(v); Serial.println();
  if (!ok) errors++;
}

// Orientation check as in the firmware: supply off, pull-ups on D0-D7. A reversed cartridge pulls a data line
// to its own GND pin (measured 2026-11-15: D2), so 0xFF = right way round or empty slot.
uint8_t readOrientation() {
  supplyOff();
  for (uint8_t i = 0; i < DATA_LINES; i++) pinMode(DATA_ARDUINO_PIN[i], INPUT_PULLUP);
  delay(5);
  uint8_t v = 0;
  for (uint8_t i = 0; i < DATA_LINES; i++) if (digitalRead(DATA_ARDUINO_PIN[i])) v |= 1 << i;
  releaseData();
  return v;
}

void printData(uint8_t v) {
  Serial.print(F("data lines with pull-ups (D7..D0): "));
  for (int8_t i = DATA_LINES - 1; i >= 0; i--) Serial.print((v >> i) & 1);
}

void help() {
  Serial.println(F("Commands: t = test without cartridge, o = orientation check (cartridge in), p = power with cartridge (only if the right way round), 1 / 0 = supply on / off"));
}

void testWithoutCartridge() {
  errors = 0;
  Serial.println(F("\n=== Supply test (no cartridge in the slot!) ==="));
  supplyOff();
  delay(OFF_TIMEOUT_MS);
  int v = analogRead(CART_SENSE);
  check(v < SENSE_OFF, F("1. supply off"), v);

  uint8_t d = readOrientation();
  Serial.print(d == 0xFF ? F("  OK   ") : F("  FAIL ")); Serial.print(F("2. empty slot, ")); printData(d); Serial.println();
  if (d != 0xFF) errors++;

  addressLow();
  digitalWrite(CART_PWR, LOW);
  delay(20);
  v = analogRead(CART_SENSE);
  check(v >= SENSE_POWERED, F("3. supply on (BC327, fuse)"), v);

  supplyOff();
  unsigned long t0 = millis();
  while ((v = analogRead(CART_SENSE)) >= SENSE_OFF && millis() - t0 < OFF_TIMEOUT_MS) {}
  check(v < SENSE_OFF, F("4. supply off again"), v);
  Serial.print(F("     fell in ")); Serial.print(millis() - t0); Serial.println(F(" ms"));

  Serial.println(errors ? F("RESULT: FAIL") : F("RESULT: PASS"));
  help();
}

void orientationCheck() {
  uint8_t v = readOrientation();
  printData(v);
  Serial.println(v == 0xFF ? F(" -> right way round or empty slot") : F(" -> REVERSED, supply stays off"));
}

void powerWithCartridge() {
  if (readOrientation() != 0xFF) { Serial.println(F("reversed: supply NOT switched on")); return; }
  addressLow();
  digitalWrite(CART_PWR, LOW);
  delay(20);
  int v = analogRead(CART_SENSE);
  supplyOff();
  Serial.print(F("supply with cartridge ")); printSense(v);
  Serial.println(v >= SENSE_POWERED ? F(" -> OK") : F(" -> too low (short or overload?)"));
}

// Manual switch: 1 = supply on (address lines low), 0 = off. While on, the sense reading is printed every second.
void manualSupply(bool on) {
  if (on) {
    supplyOff();
    addressLow();
    digitalWrite(CART_PWR, LOW);
    manualOn = true;
    Serial.println(F("supply ON (0 = off). Measure slot pin 23 / R6 against GND."));
  } else {
    supplyOff();
    Serial.println(F("supply OFF"));
  }
}

void setup() {
  digitalWrite(CART_PWR, HIGH);
  pinMode(CART_PWR, OUTPUT);
  releaseData();
  Serial.begin(SERIAL_BAUD);
#if defined(ADDR_MCP23017)
  Wire.begin();
  Wire.setClock(I2C_CLOCK);
#elif defined(ADDR_74HC595)
  pinMode(SR_LATCH, OUTPUT);
  digitalWrite(SR_LATCH, LOW);
  SPI.begin();
  SPI.beginTransaction(SPISettings(SPI_CLOCK, MSBFIRST, SPI_MODE0));
#endif
  testWithoutCartridge();
}

void loop() {
  if (manualOn && millis() - lastPrint >= 1000) {
    lastPrint = millis();
    Serial.print(F("  sense ")); printSense(analogRead(CART_SENSE)); Serial.println();
  }
  if (!Serial.available()) return;
  String cmd = Serial.readStringUntil('\n');
  cmd.trim();
  if (cmd == "t") testWithoutCartridge();
  else if (cmd == "o") orientationCheck();
  else if (cmd == "p") powerWithCartridge();
  else if (cmd == "1") manualSupply(true);
  else if (cmd == "0") manualSupply(false);
  else if (cmd.length()) help();
}
