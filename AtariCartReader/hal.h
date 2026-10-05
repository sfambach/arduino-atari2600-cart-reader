#pragma once
#include <Arduino.h>

// Hardware abstraction: address bus A0-A12, data bus D0-D7.
void halInit();
void halSetAddr(uint16_t addr);
uint8_t halReadData();
void halWriteData(uint8_t data);   // drives the data bus
void halReleaseData();             // data bus back to input

#if defined(__AVR_ATmega2560__)
// Arduino Mega 2560, 40-pin connector:
// A0-A7 = PA0-PA7, A8-A12 = PC0-PC4, D0-D7 = PL0-PL7
inline void halInit() {
  DDRA = 0xFF;
  DDRC |= 0x1F;
  DDRL = 0x00;
  PORTL = 0x00;
}
inline void halSetAddr(uint16_t addr) {
  PORTA = addr & 0xFF;
  PORTC = (PORTC & 0xE0) | ((addr >> 8) & 0x1F);
  delayMicroseconds(2);
}
inline uint8_t halReadData() { return PINL; }  // PINx, not PORTx!
inline void halWriteData(uint8_t data) { PORTL = data; DDRL = 0xFF; }
inline void halReleaseData() { DDRL = 0x00; PORTL = 0x00; }

#elif defined(__AVR_ATmega328P__)
// Arduino Uno: address bus via MCP23017 (I2C 0x20, GPA0-7 = A0-A7, GPB0-4 = A8-A12),
// data bus D0-D7 = Uno D2-D9 (PD2-PD7, PB0-PB1)
#include <Wire.h>
const uint8_t MCP_ADDR = 0x20;
inline void mcpWrite(uint8_t reg, uint8_t a, uint8_t b) {
  Wire.beginTransmission(MCP_ADDR);
  Wire.write(reg); Wire.write(a); Wire.write(b);
  Wire.endTransmission();
}
inline void halInit() {
  Wire.begin();
  Wire.setClock(400000);
  mcpWrite(0x00, 0x00, 0x00);  // IODIRA/IODIRB: all outputs
  DDRD &= 0x03;
  DDRB &= 0xFC;
}
inline void halSetAddr(uint16_t addr) {
  mcpWrite(0x12, addr & 0xFF, (addr >> 8) & 0x1F);  // GPIOA/GPIOB
}
inline uint8_t halReadData() { return (PIND >> 2) | ((PINB & 0x03) << 6); }
inline void halWriteData(uint8_t data) {
  PORTD = (PORTD & 0x03) | (data << 2);
  PORTB = (PORTB & 0xFC) | (data >> 6);
  DDRD |= 0xFC;
  DDRB |= 0x03;
}
inline void halReleaseData() {
  DDRD &= 0x03; PORTD &= 0x03;
  DDRB &= 0xFC; PORTB &= 0xFC;
}
#else
#error "Board not supported (Mega 2560 or Uno)"
#endif
