#pragma once
#include <Arduino.h>

// Settings of the supply and orientation test. Thresholds as in the firmware's config.h.

// Uno / Nano address bus: comment out for the 74HC595 boards, keep for the MCP23017 boards.
// #define ADDR_MCP23017

const unsigned long SERIAL_BAUD = 115200;
const int SENSE_ORIENTATION = 40;  // ~0.2 V: D2 back-feeds the cartridge rail
const int SENSE_POWERED = 900;     // ~4.4 V: supply is on and not overloaded
const unsigned long OFF_TIMEOUT_MS = 3000;  // rail must fall below SENSE_ORIENTATION within this time
const uint8_t CART_SENSE = A0;

#if defined(__AVR_ATmega2560__)
const uint8_t CART_PWR = 8;        // LOW = cartridge on (BC327)
const uint8_t DATA_D2_PIN = 47;    // PL2
#else
const uint8_t CART_PWR = 10;
const uint8_t DATA_D2_PIN = 4;     // PD4
const uint8_t MCP_ADDR = 0x20;
const uint8_t SR_LATCH = A2;
#endif
