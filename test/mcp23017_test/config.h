#pragma once
#include <Arduino.h>

// Settings of the MCP23017 board test.
const unsigned long SERIAL_BAUD = 115200;
const uint8_t MCP_ADDR = 0x20;            // A0-A2 to GND
const uint32_t I2C_CLOCK = 100000;
const uint8_t CART_PWR = 10;              // LOW = cartridge supply on; kept HIGH (off) the whole time
const unsigned long WALK_STEP_MS = 2000;  // time per address line in the walk command
