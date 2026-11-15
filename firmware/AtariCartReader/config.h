#pragma once
#include <Arduino.h>

// All user settings of the firmware.
// Bus wiring is fixed by the boards and read through whole port registers (one access per byte) in hal.h,
// so it is listed here for reference only; changing it needs a change in hal.h:
//   Mega:       A0-A7 = PA0-PA7 (D22-D29), A8-A12 = PC0-PC4 (D37-D33), D0-D7 = PL0-PL7 (D49-D42)
//   Uno / Nano: D0-D7 = D2-D9 (PD2-PD7, PB0-PB1); address bus via 74HC595 (SPI) or MCP23017 (I2C, GPA0-7, GPB0-4)

// Uno / Nano address bus: comment out for the 74HC595 boards, keep for the MCP23017 boards.
// #define ADDR_MCP23017

const unsigned long SERIAL_BAUD = 115200;

// ADC thresholds, to be calibrated on hardware with the S command.
const int SENSE_ORIENTATION = 40;  // ~0.2 V: D2 back-feeds the cartridge rail
const int SENSE_POWERED = 900;     // ~4.4 V: supply is on and not overloaded

const uint8_t READ_BUTTON = A1;    // LOW = pressed (button to GND, internal pull-up)
const uint8_t CART_SENSE = A0;     // switched cartridge rail via 10 kOhm

#if defined(__AVR_ATmega2560__)
const uint8_t CART_PWR = 8;        // PH5, LOW = cartridge on (BC327)
#else
const uint8_t CART_PWR = 10;       // PB2, LOW = cartridge on (BC327)
#endif

const uint8_t MCP_ADDR = 0x20;            // MCP23017 boards: A0-A2 to GND
const uint32_t I2C_CLOCK = 400000;
const uint8_t SR_LATCH = A2;              // 74HC595 boards: RCLK
const uint32_t SPI_CLOCK = 4000000;
