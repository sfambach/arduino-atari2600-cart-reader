#pragma once
#include <Arduino.h>

// All settings of the firmware. The board is detected from the selected Arduino board;
// for Uno / Nano choose the address bus variant below.

// ---------------------------------------------------------------- general
const unsigned long SERIAL_BAUD = 115200;

// ADC thresholds, to be calibrated on hardware with the S command.
const int SENSE_ORIENTATION = 40;  // ~0.2 V: D2 back-feeds the cartridge rail
const int SENSE_POWERED = 900;     // ~4.4 V: supply is on and not overloaded

// ---------------------------------------------------------------- Mega 2560 shield
#if defined(__AVR_ATmega2560__)
const uint8_t CART_PWR = 8;        // PH5, LOW = cartridge on (BC327)
const uint8_t CART_SENSE = A0;     // switched cartridge rail via 10 kOhm
const uint8_t READ_BUTTON = A1;    // LOW = pressed (button to GND, internal pull-up)
// Buses are whole ports (one access per byte), so they are given as port registers.
#define ADDR_LO_PORT PORTA         // A0-A7  = PA0-PA7 (D22-D29)
#define ADDR_LO_DDR  DDRA
#define ADDR_HI_PORT PORTC         // A8-A12 = PC0-PC4 (D37-D33)
#define ADDR_HI_DDR  DDRC
#define DATA_PORT    PORTL         // D0-D7  = PL0-PL7 (D49-D42)
#define DATA_PIN     PINL
#define DATA_DDR     DDRL

// ---------------------------------------------------------------- Uno / Nano boards
#elif defined(__AVR_ATmega328P__)
// Address bus variant: comment out for the 74HC595 boards, keep for the MCP23017 boards.
// #define ADDR_MCP23017

const uint8_t CART_PWR = 10;       // PB2, LOW = cartridge on (BC327)
const uint8_t CART_SENSE = A0;     // switched cartridge rail via 10 kOhm
const uint8_t READ_BUTTON = A1;    // LOW = pressed (button to GND, internal pull-up)
// Data bus D0-D7 = D2-D9 (PD2-PD7, PB0-PB1): split over two ports, fixed in hal.h.
#if defined(ADDR_MCP23017)
const uint8_t MCP_ADDR = 0x20;     // A0-A2 to GND; GPA0-7 = A0-A7, GPB0-4 = A8-A12
const uint32_t I2C_CLOCK = 400000; // SDA = A4, SCL = A5
#else
const uint8_t SR_LATCH = A2;       // RCLK of both 74HC595; MOSI D11, SCK D13; U1 = A0-A7, U2 = A8-A12
const uint32_t SPI_CLOCK = 4000000;
#endif

#else
#error "Board not supported (Mega 2560, Uno or Nano)"
#endif
