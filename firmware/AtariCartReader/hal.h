#pragma once
#include <Arduino.h>
#include "config.h"

// Hardware abstraction: address bus A0-A12, data bus D0-D7, switched cartridge supply.
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
  ADDR_LO_PORT = addr & 0xFF;
  ADDR_HI_PORT = (ADDR_HI_PORT & 0xE0) | ((addr >> 8) & 0x1F);
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
inline void halDrive() {
  mcpWrite(0x12, 0x00, 0x00);  // GPIOA/GPIOB low before switching to output
  mcpWrite(0x00, 0x00, 0x00);
}
inline void halInit() {
  Wire.begin();
  Wire.setClock(I2C_CLOCK);
  halRelease();
}
inline void halSetAddr(uint16_t addr) {
  mcpWrite(0x12, addr & 0xFF, (addr >> 8) & 0x1F);  // GPIOA/GPIOB
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
