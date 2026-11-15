#pragma once
#include <Arduino.h>
#include "config.h"

// Hardware abstraction: address bus A0-A12, data bus D0-D7, switched cartridge supply.
//
// Address changes must not pass through a third address with A12 high: on the Mega and the MCP23017 boards
// the low and the high byte change one after the other, and the brief mix (new A0-A7, old A8-A12) can hit a
// bankswitch hotspot ($1FF4-$1FFB, E0/E7 at $1FE0-$1FEB) and switch the bank by accident (seen 2026-11-15:
// RealSports Tennis, an F8 cartridge, read as F6). So when the high byte changes, A12 goes low first.
void halInit();                    // bus released, cartridge supply off
void halRelease();                 // all cartridge lines to input without pull-ups
void halDrive();                   // address bus to output
void halPullupData(bool on);       // weak pull-ups on D0-D7 for the orientation check
void halSetAddr(uint16_t addr);
uint8_t halReadData();
void halWriteData(uint8_t data);   // drives the data bus
void halReleaseData();             // data bus back to input

#if defined(__AVR_ATmega2560__)
// Arduino Mega 2560, 40-pin connector; ports in config.h.
inline void halRelease() {
  ADDR_LO_DDR = 0x00; ADDR_LO_PORT = 0x00;
  ADDR_HI_DDR &= 0xE0; ADDR_HI_PORT &= 0xE0;
  DATA_DDR = 0x00; DATA_PORT = 0x00;
}
inline void halDrive() {
  ADDR_LO_PORT = 0x00; ADDR_LO_DDR = 0xFF;
  ADDR_HI_PORT &= 0xE0; ADDR_HI_DDR |= 0x1F;
}
inline void halPullupData(bool on) { DATA_PORT = on ? 0xFF : 0x00; }
inline void halInit() { halRelease(); }
inline void halSetAddr(uint16_t addr) {
  uint8_t hi = (addr >> 8) & 0x1F;
  if ((ADDR_HI_PORT & 0x1F) != hi) ADDR_HI_PORT = (ADDR_HI_PORT & 0xE0) | (hi & 0x0F);  // A12 low first
  ADDR_LO_PORT = addr & 0xFF;
  ADDR_HI_PORT = (ADDR_HI_PORT & 0xE0) | hi;
  delayMicroseconds(2);
}
inline uint8_t halReadData() { return DATA_PIN; }  // PINx, not PORTx!
inline void halWriteData(uint8_t data) { DATA_PORT = data; DATA_DDR = 0xFF; }
inline void halReleaseData() { DATA_DDR = 0x00; DATA_PORT = 0x00; }

#elif defined(__AVR_ATmega328P__)
// Arduino Uno / Nano: data bus D0-D7 = D2-D9 (PD2-PD7, PB0-PB1).
// Address bus: two 74HC595 on SPI (MOSI D11, SCK D13, latch A2; U1 = A0-A7, U2 = A8-A12),
// or with ADDR_MCP23017 defined in config.h the MCP23017 boards (I2C 0x20, GPA0-7 = A0-A7, GPB0-4 = A8-A12).
inline void halReleaseDataPins() {
  DDRD &= 0x03; PORTD &= 0x03;
  DDRB &= 0xFC; PORTB &= 0xFC;
}
#if defined(ADDR_MCP23017)
#include <Wire.h>
inline void mcpWrite(uint8_t reg, uint8_t a, uint8_t b) {
  Wire.beginTransmission(MCP_ADDR);
  Wire.write(reg); Wire.write(a); Wire.write(b);
  Wire.endTransmission();
}
inline void halRelease() {
  mcpWrite(0x00, 0xFF, 0xFF);  // IODIRA/IODIRB: all inputs
  halReleaseDataPins();
}
uint8_t mcpHi = 0;  // last value written to GPIOB (A8-A12)
inline void halDrive() {
  mcpWrite(0x12, 0x00, 0x00);  // GPIOA/GPIOB low before switching to output
  mcpWrite(0x00, 0x00, 0x00);
  mcpHi = 0;
}
inline void halInit() {
  Wire.begin();
  Wire.setClock(I2C_CLOCK);
  halRelease();
}
inline void halSetAddr(uint16_t addr) {
  uint8_t hi = (addr >> 8) & 0x1F;
  if (hi != mcpHi) {  // A12 low first, then GPIOA and GPIOB in one transfer (GPIOA changes first)
    Wire.beginTransmission(MCP_ADDR);
    Wire.write(0x13); Wire.write(hi & 0x0F);
    Wire.endTransmission();
    mcpWrite(0x12, addr & 0xFF, hi);
    mcpHi = hi;
  } else {
    Wire.beginTransmission(MCP_ADDR);
    Wire.write(0x12); Wire.write(addr & 0xFF);
    Wire.endTransmission();
  }
}
#else
#include <SPI.h>
inline void halSetAddr(uint16_t addr) {
  SPI.transfer((addr >> 8) & 0x1F);  // shifted on into U2 (A8-A12)
  SPI.transfer(addr & 0xFF);         // stays in U1 (A0-A7)
  digitalWrite(SR_LATCH, HIGH);
  digitalWrite(SR_LATCH, LOW);
}
// The 74HC595 outputs cannot float (OE is tied low); LOW does not feed an unpowered cartridge.
inline void halRelease() {
  halSetAddr(0);
  halReleaseDataPins();
}
inline void halDrive() { halSetAddr(0); }
inline void halInit() {
  pinMode(SR_LATCH, OUTPUT);
  digitalWrite(SR_LATCH, LOW);
  SPI.begin();
  SPI.beginTransaction(SPISettings(SPI_CLOCK, MSBFIRST, SPI_MODE0));
  halRelease();
}
#endif
inline void halPullupData(bool on) {
  if (on) { PORTD |= 0xFC; PORTB |= 0x03; } else { PORTD &= 0x03; PORTB &= 0xFC; }
}
inline uint8_t halReadData() { return (PIND >> 2) | ((PINB & 0x03) << 6); }
inline void halWriteData(uint8_t data) {
  PORTD = (PORTD & 0x03) | (data << 2);
  PORTB = (PORTB & 0xFC) | (data >> 6);
  DDRD |= 0xFC;
  DDRB |= 0x03;
}
inline void halReleaseData() { halReleaseDataPins(); }
#else
#error "Board not supported (Mega 2560, Uno or Nano)"
#endif
