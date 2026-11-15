// Switched cartridge supply and orientation check (Mega, Uno, Nano; 74HC595 or MCP23017).
// Serial monitor: 115200 baud, line ending "Newline". Start WITHOUT a cartridge.
#include "config.h"
#if defined(__AVR_ATmega2560__)
#elif defined(ADDR_MCP23017)
#include <Wire.h>
#else
#include <SPI.h>
#endif

uint8_t errors = 0;

void addressLow() {  // keeps the ROM disabled in either orientation, as in the firmware
#if defined(__AVR_ATmega2560__)
  PORTA = 0x00; DDRA = 0xFF;
  PORTC &= 0xE0; DDRC |= 0x1F;
#elif defined(ADDR_MCP23017)
  Wire.beginTransmission(MCP_ADDR); Wire.write(0x12); Wire.write(0); Wire.write(0); Wire.endTransmission();
  Wire.beginTransmission(MCP_ADDR); Wire.write(0x00); Wire.write(0); Wire.write(0); Wire.endTransmission();
#else
  SPI.transfer(0); SPI.transfer(0);
  digitalWrite(SR_LATCH, HIGH); digitalWrite(SR_LATCH, LOW);
#endif
}

void addressRelease() {
#if defined(__AVR_ATmega2560__)
  DDRA = 0x00; PORTA = 0x00;
  DDRC &= 0xE0; PORTC &= 0xE0;
#elif defined(ADDR_MCP23017)
  Wire.beginTransmission(MCP_ADDR); Wire.write(0x00); Wire.write(0xFF); Wire.write(0xFF); Wire.endTransmission();
#endif  // 74HC595 outputs cannot float; they stay low
}

void supplyOff() {
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
  delay(5);
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
  delay(5);
  int v = analogRead(CART_SENSE);
  pinMode(DATA_D2_PIN, INPUT);
  addressRelease();
  Serial.print(F("orientation reading ")); printSense(v);
  Serial.println(v >= SENSE_ORIENTATION ? F(" -> cartridge correct, firmware would switch on")
                                        : F(" -> none or reversed, supply stays off"));
}

void powerWithCartridge() {
  supplyOff();
  addressLow();
  pinMode(DATA_D2_PIN, INPUT_PULLUP);
  delay(5);
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

void help() {
  Serial.println(F("Commands: t = test without cartridge, o = orientation reading (cartridge in), p = power with cartridge (only if orientation OK)"));
}

void setup() {
  digitalWrite(CART_PWR, HIGH);
  pinMode(CART_PWR, OUTPUT);
  pinMode(DATA_D2_PIN, INPUT);
  Serial.begin(SERIAL_BAUD);
#if defined(__AVR_ATmega2560__)
#elif defined(ADDR_MCP23017)
  Wire.begin();
#else
  pinMode(SR_LATCH, OUTPUT);
  digitalWrite(SR_LATCH, LOW);
  SPI.begin();
  SPI.beginTransaction(SPISettings(4000000, MSBFIRST, SPI_MODE0));
#endif
  testWithoutCartridge();
}

void loop() {
  if (!Serial.available()) return;
  String cmd = Serial.readStringUntil('\n');
  cmd.trim();
  if (cmd == "t") testWithoutCartridge();
  else if (cmd == "o") orientationWithCartridge();
  else if (cmd == "p") powerWithCartridge();
  else if (cmd.length()) help();
}
