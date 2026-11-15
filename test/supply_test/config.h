#pragma once
#include <Arduino.h>

// Settings of the supply and orientation test. Thresholds as in the firmware's config.h.

// ================================================================ board selection
// Enable exactly ONE board.
// #define BOARD_MEGA
// #define BOARD_UNO
#define BOARD_UNO_MCP23017
// #define BOARD_NANO
// #define BOARD_NANO_MCP23017

// ================================================================ general
const unsigned long SERIAL_BAUD = 115200;
const int SENSE_ORIENTATION = 40;  // ~0.2 V: D2 back-feeds the cartridge rail
const int SENSE_POWERED = 900;     // ~4.4 V: supply is on and not overloaded
const unsigned long OFF_TIMEOUT_MS = 3000;  // rail must fall below SENSE_ORIENTATION within this time

// ================================================================ Mega 2560 shield
#if defined(BOARD_MEGA)
#if !defined(__AVR_ATmega2560__)
#error "BOARD_MEGA selected, but the Arduino IDE board is not a Mega 2560"
#endif
const uint8_t CART_PWR = 8;        // LOW = cartridge on (BC327)
const uint8_t CART_SENSE = A0;
const uint8_t DATA_D2_PIN = 47;    // PL2

// ================================================================ Uno shield / Nano carrier
#elif defined(BOARD_UNO) || defined(BOARD_UNO_MCP23017) || defined(BOARD_NANO) || defined(BOARD_NANO_MCP23017)
#if !defined(__AVR_ATmega328P__)
#error "Uno / Nano board selected, but the Arduino IDE board is not an Uno or Nano"
#endif
const uint8_t CART_PWR = 10;       // LOW = cartridge on (BC327)
const uint8_t CART_SENSE = A0;
const uint8_t DATA_D2_PIN = 4;     // PD4
#if defined(BOARD_UNO_MCP23017) || defined(BOARD_NANO_MCP23017)
#define ADDR_MCP23017
const uint8_t MCP_ADDR = 0x20;
#else
const uint8_t SR_LATCH = A2;
#endif

#else
#error "No board selected in config.h"
#endif
