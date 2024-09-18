# H2O Rocket Exhibit

## Overview

This project simulates a rocket fuel generation and launch sequence using a Raspberry Pi Pico. It's designed as an educational exhibit to demonstrate the concept of separating hydrogen and oxygen from H2O to create fuel. The actual demonstration uses a series of simulated steps involving bubble generation, fluid transfer, and a model rocket launch.

## Hardware Requirements

- Raspberry Pi Pico
- 3 buttons (Blue, Green, Red) with corresponding LEDs
- 1 encoder
- 3 relay modules
- Air compressor (simulated)
- Bubble valve (simulated)
- Transfer valve (simulated)
- Fire valve (simulated)
- Model rocket (for demonstration purposes)

## Pin Configuration

- Blue Button: GPIO 2
- Blue LED: GPIO 16
- Green Button: GPIO 0
- Green LED: GPIO 17
- Red Button: GPIO 4
- Red LED: GPIO 18
- Encoder: GPIO 5
- Shared Relay (Air Compressor & Bubble Valve): GPIO 19
- Transfer Valve Relay: GPIO 21
- Fire Valve Relay: GPIO 22

## Software Dependencies

- MicroPython firmware for Raspberry Pi Pico

## Setup Instructions

1. Flash MicroPython firmware onto your Raspberry Pi Pico.
2. Connect the hardware components according to the pin configuration.
3. Copy the `main.py` file to your Raspberry Pi Pico.

## Usage

1. Power on the Raspberry Pi Pico.
2. The system will wait for an activation signal from the encoder.
3. Once activated, the sequence begins:
   a. Fuel generation (simulated by bubble creation)
   b. Wait for green button press
   c. Wait for blue button press
   d. Fuel transfer
   e. Wait for red button press
   f. Rocket launch
4. The sequence can be repeated by activating the encoder again.

## Code Structure

- `Button` class: Handles button inputs and LED control with debouncing.
- `Encoder` class: Manages encoder input with debounce mechanism.
- `Relay` class: Controls relay outputs for various valves.
- Main sequence functions:
  - `generate_fuel()`: Simulates fuel generation.
  - `transfer_fuel()`: Simulates fuel transfer.
  - `fire_rocket()`: Simulates rocket launch.
  - `wait_for_button_press()`: Waits for a specific button press with timeout.
- `main()` function: Orchestrates the entire demo sequence.

## Customization

You can adjust the duration of each step by modifying the `time.sleep()` values in the respective functions. The debounce time for buttons and encoder can also be adjusted in their class initializations.

## Troubleshooting

- Ensure all connections are secure and correctly wired.
- Check that the MicroPython firmware is properly installed on the Raspberry Pi Pico.
- If buttons are not responsive, try adjusting the debounce time.
- For any issues with relay activation, verify the relay module connections and power supply.
