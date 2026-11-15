#pragma once
#include <Arduino.h>

// Settings of the MCP23017 board test (Uno shield or Nano carrier with MCP23017, same circuit).
#if !defined(__AVR_ATmega328P__)
#error "This test is for the Uno / Nano MCP23017 boards"
#endif
const unsigned long SERIAL_BAUD = 115200;
const uint8_t MCP_ADDR = 0x20;            // A0-A2 to GND
const uint32_t I2C_CLOCK = 100000;
const uint8_t CART_PWR = 10;              // LOW = cartridge supply on; kept HIGH (off) the whole time
const unsigned long WALK_STEP_MS = 2000;  // time per address line in the walk command

// Wiring of the board (Uno / Nano MCP23017 boards). MCP23017: GPA0-7 = A0-A7, GPB0-4 = A8-A12.
const uint8_t ADDR_LINES = 13, DATA_LINES = 8;
const uint8_t DATA_ARDUINO_PIN[DATA_LINES] = {2, 3, 4, 5, 6, 7, 8, 9};   // D0-D7
const uint8_t ADDR_SLOT_PIN[ADDR_LINES] = {8, 7, 6, 5, 4, 3, 2, 1, 22, 21, 19, 20, 18};  // slot pin of A0-A12, for messages
const uint8_t DATA_SLOT_PIN[DATA_LINES] = {9, 10, 11, 13, 14, 15, 16, 17};              // slot pin of D0-D7, for messages
