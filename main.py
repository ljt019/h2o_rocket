from machine import Pin
import time
import logging

# =========================
# Configuration and Setup
# =========================

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# =========================
# Pin Constants
# =========================

# Button and LED Pins
BLUE_BUTTON_PIN = 2
BLUE_LED_PIN = 16

GREEN_BUTTON_PIN = 0
GREEN_LED_PIN = 17

RED_BUTTON_PIN = 4
RED_LED_PIN = 18

# Valve Relay Pins
SHARED_RELAY_PIN = 19  # Controls both Air Compressor and Bubble Valve
TRANSFER_VALVE_RELAY_PIN = 21
FIRE_VALVE_RELAY_PIN = 22

# Encoder Pin
ENCODER_PIN = 5

# =========================
# Classes
# =========================

class Button:
    """Class to handle button inputs and associated LEDs with debouncing."""
    def __init__(self, button_pin, led_pin, debounce_time=50):
        self.button = Pin(button_pin, Pin.IN, Pin.PULL_DOWN)
        self.led = Pin(led_pin, Pin.OUT)
        self.debounce_time = debounce_time / 1000  # Convert to seconds

    def is_pressed(self):
        """Check if the button is pressed with debouncing."""
        if self.button.value():
            time.sleep(self.debounce_time)
            if self.button.value():
                return True
        return False

    def blink_led(self, interval=0.5):
        """Blink the associated LED with the given interval."""
        self.led.on()
        time.sleep(interval)
        self.led.off()
        time.sleep(interval)


class Encoder:
    """Class to handle encoder input with debounce."""
    def __init__(self, encoder_pin, debounce_time=50):
        self.encoder = Pin(encoder_pin, Pin.IN, Pin.PULL_DOWN)
        self.debounce_time = debounce_time / 1000  # Convert to seconds
        self.activated = False
        self.last_trigger_time = 0
        self.encoder.irq(trigger=Pin.IRQ_RISING, handler=self._irq_handler)

    def _irq_handler(self, pin):
        """Interrupt handler for the encoder."""
        current_time = time.time()
        if (current_time - self.last_trigger_time) > self.debounce_time:
            self.activated = True
            self.last_trigger_time = current_time

    def is_activated(self):
        """Check if the encoder was activated."""
        if self.activated:
            self.activated = False  # Reset the flag
            return True
        return False


class Relay:
    """Class to control relay outputs."""
    def __init__(self, relay_pin):
        self.relay_pin = relay_pin
        self.relay = Pin(relay_pin, Pin.OUT)
        self.turn_off()  # Initialize relay to OFF state

    def turn_on(self):
        """Activate the relay."""
        self.relay.on()
        logging.info(f"Relay on pin {self.relay_pin} turned ON.")

    def turn_off(self):
        """Deactivate the relay."""
        self.relay.off()
        logging.info(f"Relay on pin {self.relay_pin} turned OFF.")

    def activate_both(self):
        """Activate both Air Compressor and Bubble Valve."""
        self.turn_on()

    def deactivate_both(self):
        """Deactivate both Air Compressor and Bubble Valve."""
        self.turn_off()


# =========================
# Valve Control Functions
# =========================

def generate_fuel(shared_relay, duration=5):
    """Activate air compressor and bubble valve to generate fuel."""
    logging.info("Generating fuel: Activating air compressor and bubble valve.")
    shared_relay.activate_both()
    time.sleep(duration)  # Duration to generate fuel
    shared_relay.deactivate_both()
    logging.info("Fuel generation completed.")


def transfer_fuel(transfer_valve, duration=5):
    """Activate transfer valve to transfer fuel."""
    logging.info("Transferring fuel: Turning on transfer valve.")
    transfer_valve.turn_on()
    time.sleep(duration)  # Duration to transfer fuel
    transfer_valve.turn_off()
    logging.info("Fuel transfer completed.")


def fire_rocket(fire_valve, duration=2):
    """Activate fire valve to fire the rocket."""
    logging.info("Firing rocket: Turning on fire valve.")
    fire_valve.turn_on()
    time.sleep(duration)  # Duration to fire the rocket
    fire_valve.turn_off()
    logging.info("Rocket fired.")


def wait_for_button_press(button, timeout=30):
    """Wait for a button press with a timeout."""
    start_time = time.time()
    while not button.is_pressed():
        button.blink_led()
        if (time.time() - start_time) > timeout:
            logging.warning("Timeout waiting for button press.")
            return False
    button.led.off()
    logging.info("Button pressed.")
    return True


# =========================
# Main Function
# =========================

def main():
    # Initialize Buttons with their LEDs
    blue_button = Button(BLUE_BUTTON_PIN, BLUE_LED_PIN)
    green_button = Button(GREEN_BUTTON_PIN, GREEN_LED_PIN)
    red_button = Button(RED_BUTTON_PIN, RED_LED_PIN)

    # Initialize Encoder
    encoder = Encoder(ENCODER_PIN)

    # Initialize Relays for Valves
    bubble_and_compressor_relay = Relay(SHARED_RELAY_PIN)  # Controls both Air Compressor and Bubble Valve
    transfer_valve_relay = Relay(TRANSFER_VALVE_RELAY_PIN)
    fire_valve_relay = Relay(FIRE_VALVE_RELAY_PIN)

    while True:
        # Wait until the encoder is activated
        if encoder.is_activated():
            logging.info("Activation signal received. Starting sequence.")

            # Generate fuel
            generate_fuel(bubble_and_compressor_relay)

            # Blink the green LED until the green button is pressed or timeout
            logging.info("Waiting for green button press...")
            if not wait_for_button_press(green_button):
                logging.error("Green button not pressed in time. Aborting sequence.")
                continue  # Restart the loop or handle accordingly

            # Blink the blue LED until the blue button is pressed or timeout
            logging.info("Waiting for blue button press...")
            if not wait_for_button_press(blue_button):
                logging.error("Blue button not pressed in time. Aborting sequence.")
                continue

            # Transfer fuel
            transfer_fuel(transfer_valve_relay)

            # Blink the red LED until the red button is pressed or timeout
            logging.info("Waiting for red button press...")
            if not wait_for_button_press(red_button):
                logging.error("Red button not pressed in time. Aborting sequence.")
                continue

            # Fire the rocket
            fire_rocket(fire_valve_relay)

            logging.info("Sequence completed. Resetting system.\n")

        # Small delay to prevent CPU overutilization
        time.sleep(0.1)


# =========================
# Entry Point
# =========================

if __name__ == "__main__":
    main()
