// Switched cartridge supply and orientation check (Mega, Uno, Nano; 74HC595 or MCP23017).
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

void supplyOff() {
  manualOn = false;
  digitalWrite(CART_PWR, HIGH);
  pinMode(DATA_D2_PIN, INPUT);
  addressRelease();
}

void printSense(int v) {
  Serial.print(v); Serial.print(F(" (")); Serial.print(v * 5.0 / 1023, 2); Serial.print(F(" V)"));
}

void check(bool ok, const __FlashStringHelper *what, int v) {
  Serial.print(ok ? F("  OK   ") : F("  FAIL ")); Serial.print(what); Serial.print(F(": ")); printSense(v); Serial.println();
  if (!ok) errors++;
}

void testWithoutCartridge() {
  errors = 0;
  Serial.println(F("\n=== Supply test (no cartridge in the slot!) ==="));
  supplyOff();
  delay(OFF_TIMEOUT_MS);
  int v = analogRead(CART_SENSE);
  check(v < SENSE_ORIENTATION, F("1. supply off"), v);

  addressLow();
  pinMode(DATA_D2_PIN, INPUT_PULLUP);
  delay(50);
  v = analogRead(CART_SENSE);
  pinMode(DATA_D2_PIN, INPUT);
  check(v < SENSE_ORIENTATION, F("2. orientation check, empty slot (supply must stay off)"), v);

  digitalWrite(CART_PWR, LOW);
  delay(20);
  v = analogRead(CART_SENSE);
  check(v >= SENSE_POWERED, F("3. supply on (BC327, fuse)"), v);

  supplyOff();
  unsigned long t0 = millis();
  while ((v = analogRead(CART_SENSE)) >= SENSE_ORIENTATION && millis() - t0 < OFF_TIMEOUT_MS) {}
  check(v < SENSE_ORIENTATION, F("4. supply off again"), v);
  Serial.print(F("     fell in ")); Serial.print(millis() - t0); Serial.println(F(" ms"));

  Serial.println(errors ? F("RESULT: FAIL") : F("RESULT: PASS"));
  help();
}

void orientationWithCartridge() {
  supplyOff();
  addressLow();
  pinMode(DATA_D2_PIN, INPUT_PULLUP);
  delay(50);
  int v = analogRead(CART_SENSE);
  pinMode(DATA_D2_PIN, INPUT);
  addressRelease();
  Serial.print(F("orientation reading ")); printSense(v);
  Serial.println(v >= SENSE_ORIENTATION ? F(" -> cartridge correct, firmware would switch on")
                                        : F(" -> none or reversed, supply stays off"));
}

// Alternative check: a reversed cartridge puts its GND (cartridge pin 12) on slot pin 13 = D3.
// Supply off, pull-ups on all data lines: D3 low = reversed; all high = correct or no cartridge.
void groundCheck() {
  supplyOff();
  addressRelease();
  for (uint8_t i = 0; i < DATA_LINES; i++) pinMode(DATA_ARDUINO_PIN[i], INPUT_PULLUP);
  delay(5);
  Serial.print(F("data lines with pull-ups (D7..D0): "));
  for (int8_t i = DATA_LINES - 1; i >= 0; i--) Serial.print(digitalRead(DATA_ARDUINO_PIN[i]));
  bool reversed = digitalRead(DATA_ARDUINO_PIN[3]) == LOW;
  for (uint8_t i = 0; i < DATA_LINES; i++) pinMode(DATA_ARDUINO_PIN[i], INPUT);
  Serial.println(reversed ? F(" -> D3 low: cartridge REVERSED") : F(" -> D3 high: correct or no cartridge"));
}

void powerWithCartridge() {
  supplyOff();
  addressLow();
  pinMode(DATA_D2_PIN, INPUT_PULLUP);
  delay(50);
  int v = analogRead(CART_SENSE);
  pinMode(DATA_D2_PIN, INPUT);
  if (v < SENSE_ORIENTATION) { Serial.println(F("none or reversed: supply NOT switched on")); supplyOff(); return; }
  digitalWrite(CART_PWR, LOW);
  delay(20);
  v = analogRead(CART_SENSE);
  supplyOff();
  Serial.print(F("supply with cartridge ")); printSense(v);
  Serial.println(v >= SENSE_POWERED ? F(" -> OK") : F(" -> too low (short or overload?)"));
}

// Holds the orientation check (supply off, address low, pull-up on D2) so slot pins 11 (D2) and 23 (+5V) can be measured.
void holdOrientation() {
  supplyOff();
  addressLow();
  pinMode(DATA_D2_PIN, INPUT_PULLUP);
  Serial.println(F("holding: supply off, A0-A12 low, pull-up on D2. Measure slot pin 11 and 23 against GND. Any key stops."));
  while (!Serial.available()) {
    Serial.print(F("  sense ")); printSense(analogRead(CART_SENSE));
    Serial.print(F(", D2 reads ")); Serial.println(digitalRead(DATA_D2_PIN));
    delay(500);
  }
  while (Serial.available()) Serial.read();
  supplyOff();
  Serial.println(F("stopped"));
}

// Manual switch: 1 = supply on (address lines low), 0 = off. While on, the sense reading is printed every second.
void manualSupply(bool on) {
  manualOn = on;
  if (on) {
    pinMode(DATA_D2_PIN, INPUT);
    addressLow();
    digitalWrite(CART_PWR, LOW);
    Serial.println(F("supply ON (0 = off). Measure slot pin 23 / R6 against GND."));
  } else {
    supplyOff();
    Serial.println(F("supply OFF"));
  }
}

void help() {
  Serial.println(F("Commands: t = test without cartridge, o = orientation reading (cartridge in), g = ground check (D3 low = reversed), h = hold orientation check for measuring, 1 / 0 = supply on / off, p = power with cartridge (only if orientation OK)"));
}

void setup() {
  digitalWrite(CART_PWR, HIGH);
  pinMode(CART_PWR, OUTPUT);
  pinMode(DATA_D2_PIN, INPUT);
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
  else if (cmd == "o") orientationWithCartridge();
  else if (cmd == "g") groundCheck();
  else if (cmd == "p") powerWithCartridge();
  else if (cmd == "h") holdOrientation();
  else if (cmd == "1") manualSupply(true);
  else if (cmd == "0") manualSupply(false);
  else if (cmd.length()) help();
}
