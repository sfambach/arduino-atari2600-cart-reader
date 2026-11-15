#pragma once
#include <Arduino.h>

// Shared settings of the firmware and all test sketches.
// MASTER COPY: firmware/AtariCartReader/config.h. Edit only this file, then run
//   python3 tools/sync_config.py
// to copy it into every test sketch (the Arduino IDE cannot include files from outside a sketch folder).

// ================================================================ board selection
// Enable exactly ONE board.
// #define BOARD_MEGA            // Mega 2560 shield
// #define BOARD_UNO             // Uno shield, address bus via 2 x 74HC595
#define BOARD_UNO_MCP23017       // Uno shield, address bus via MCP23017
// #define BOARD_NANO            // Nano carrier, address bus via 2 x 74HC595
// #define BOARD_NANO_MCP23017   // Nano carrier, address bus via MCP23017

// ================================================================ general (all boards)
const unsigned long SERIAL_BAUD = 115200;

// ADC thresholds, to be calibrated on hardware with the S command.
const int SENSE_ORIENTATION = 40;  // ~0.2 V: D2 back-feeds the cartridge rail
const int SENSE_POWERED = 900;     // ~4.4 V: supply is on and not overloaded

// Orientation check before switching the cartridge on. Uncomment ONLY if you are sure the cartridge sits
// the right way round (label towards pins 13-24): the supply is then switched on without the check.
// #define SKIP_ORIENTATION_CHECK

// Tests
const unsigned long WALK_STEP_MS = 2000;    // bus test: time per address line in the walk command
const unsigned long OFF_TIMEOUT_MS = 3000;  // supply test: rail must fall below SENSE_ORIENTATION within this time

// Cartridge slot (same on all boards)
const uint8_t ADDR_LINES = 13, DATA_LINES = 8;
const uint8_t ADDR_SLOT_PIN[ADDR_LINES] = {8, 7, 6, 5, 4, 3, 2, 1, 22, 21, 19, 20, 18};  // slot pin of A0-A12
const uint8_t DATA_SLOT_PIN[DATA_LINES] = {9, 10, 11, 13, 14, 15, 16, 17};              // slot pin of D0-D7

// ================================================================ Mega 2560 shield
#if defined(BOARD_MEGA)
#if !defined(__AVR_ATmega2560__)
#error "BOARD_MEGA selected, but the Arduino IDE board is not a Mega 2560"
#endif
#define ADDR_DIRECT                // address lines are Arduino pins
const uint8_t CART_PWR = 8;        // PH5, LOW = cartridge on (BC327)
const uint8_t CART_SENSE = A0;     // switched cartridge rail via 10 kOhm
const uint8_t READ_BUTTON = A1;    // LOW = pressed (button to GND, internal pull-up)
const uint8_t ADDR_ARDUINO_PIN[ADDR_LINES] = {22, 23, 24, 25, 26, 27, 28, 29, 37, 36, 35, 34, 33};  // PA0-7, PC0-4
const uint8_t DATA_ARDUINO_PIN[DATA_LINES] = {49, 48, 47, 46, 45, 44, 43, 42};                      // PL0-7
const uint8_t DATA_D2_PIN = 47;    // PL2, weak pull-up for the orientation check
// The firmware reads the buses as whole ports (one access per byte):
#define ADDR_LO_PORT PORTA         // A0-A7
#define ADDR_LO_DDR  DDRA
#define ADDR_HI_PORT PORTC         // A8-A12 = PC0-PC4
#define ADDR_HI_DDR  DDRC
#define DATA_PORT    PORTL         // D0-D7
#define DATA_PIN     PINL
#define DATA_DDR     DDRL

// ================================================================ Uno shield / Nano carrier (same circuit)
#elif defined(BOARD_UNO) || defined(BOARD_UNO_MCP23017) || defined(BOARD_NANO) || defined(BOARD_NANO_MCP23017)
#if !defined(__AVR_ATmega328P__)
#error "Uno / Nano board selected, but the Arduino IDE board is not an Uno or Nano"
#endif
const uint8_t CART_PWR = 10;       // PB2, LOW = cartridge on (BC327)
const uint8_t CART_SENSE = A0;     // switched cartridge rail via 10 kOhm
const uint8_t READ_BUTTON = A1;    // LOW = pressed (button to GND, internal pull-up)
const uint8_t DATA_ARDUINO_PIN[DATA_LINES] = {2, 3, 4, 5, 6, 7, 8, 9};  // PD2-PD7, PB0-PB1 (firmware: fixed split in hal.h)
const uint8_t DATA_D2_PIN = 4;     // PD4, weak pull-up for the orientation check
#if defined(BOARD_UNO_MCP23017) || defined(BOARD_NANO_MCP23017)
#define ADDR_MCP23017              // GPA0-7 = A0-A7, GPB0-4 = A8-A12
const uint8_t MCP_ADDR = 0x20;     // A0-A2 to GND
const uint32_t I2C_CLOCK = 400000; // SDA = A4, SCL = A5
#else
#define ADDR_74HC595               // U1 = A0-A7, U2 = A8-A12; outputs cannot be read back
const uint8_t SR_LATCH = A2;       // RCLK of both 74HC595; MOSI D11, SCK D13
const uint32_t SPI_CLOCK = 4000000;
#endif

#else
#error "No board selected in config.h"
#endif
