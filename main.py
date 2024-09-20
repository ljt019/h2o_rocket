from machine import Pin
import time

# =========================
# Pin Constants
# =========================

# Button and LED Pins
BLUE_BUTTON_PIN = 17
BLUE_LED_PIN = 16

GREEN_BUTTON_PIN = 19
GREEN_LED_PIN = 18

RED_BUTTON_PIN = 21
RED_LED_PIN = 20

# Valve Relay Pins
BUBBLE_VALVE_RELAY_PIN = 13 
TRANSFER_VALVE_RELAY_PIN = 12
FIRE_VALVE_RELAY_PIN = 11

# Encoder Pin
ENCODER_PIN = 15 

# Timing Constants
BUBBLE_SLEEP = 5;
TRANSFER_SLEEP = 5;
FIRE_DURATION = 2;

# =========================
# Classes
# =========================

class Button:
    """Class to handle button inputs and associated LEDs with debouncing."""
    def __init__(self, button_pin, led_pin, debounce_time=50):
        """
        Initialize the Button.

        :param button_pin: GPIO pin connected to the button.
        :param led_pin: GPIO pin connected to the LED.
        :param debounce_time: Debounce time in milliseconds.
        """
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
    """Class to handle encoder input with pulse counting and debounce."""
    def __init__(self, encoder_pin, pulses_per_rotation=2, debounce_time=0.001):
        """
        Initialize the encoder.

        :param encoder_pin: GPIO pin connected to the encoder signal.
        :param pulses_per_rotation: Number of pulses corresponding to one full rotation.
        :param debounce_time: Debounce time in seconds.
        """
        self.encoder = Pin(encoder_pin, Pin.IN, Pin.PULL_DOWN)
        self.pulses_per_rotation = pulses_per_rotation
        self.debounce_time = debounce_time  # in seconds
        self.pulse_count = 0
        self.activated = False
        self.last_trigger_time = 0
        self.encoder.irq(trigger=Pin.IRQ_RISING, handler=self._irq_handler)

    def _irq_handler(self, pin):
        """Interrupt handler for the encoder."""
        current_time = time.ticks_us() / 1_000_000  # Convert microseconds to seconds
        if (current_time - self.last_trigger_time) > self.debounce_time:
            self.pulse_count += 1
            self.last_trigger_time = current_time
            if self.pulse_count >= self.pulses_per_rotation:
                self.activated = True
                self.pulse_count = 0  # Reset count for the next rotation

    def is_activated(self):
        """Check if a full rotation has been detected."""
        if self.activated:
            self.activated = False  # Reset the flag
            return True
        return False


class Relay:
    """Class to control relay outputs."""
    def __init__(self, relay_pin):
        """
        Initialize the Relay.

        :param relay_pin: GPIO pin connected to the relay.
        """
        self.relay_pin = relay_pin
        self.relay = Pin(relay_pin, Pin.OUT)
        self.turn_off()  # Initialize relay to OFF state

    def turn_on(self):
        """Activate the relay."""
        self.relay.on()
        print(f"Relay on pin {self.relay_pin} turned ON.")

    def turn_off(self):
        """Deactivate the relay."""
        self.relay.off()
        print(f"Relay on pin {self.relay_pin} turned OFF.")


# =========================
# Main Sequence Functions
# =========================

def generate_fuel(bubble_valve, duration=BUBBLE_SLEEP):
    """Activate bubble valve to "generate fuel"."""
    print("Generating fuel: Activating bubble valve.")
    bubble_valve.turn_on()
    time.sleep(duration)  # Duration to generate fuel
    bubble_valve.turn_on()
    print("Fuel generation completed.")


def transfer_fuel(transfer_valve, duration=TRANSFER_SLEEP):
    """Activate transfer valve to transfer fuel."""
    print("Transferring fuel: Turning on transfer valve.")
    transfer_valve.turn_on()
    time.sleep(duration)  # Duration to transfer fuel
    transfer_valve.turn_off()
    print("Fuel transfer completed.")


def fire_rocket(fire_valve, duration=FIRE_DURATION):
    """Activate fire valve to fire the rocket."""
    print("Firing rocket: Turning on fire valve.")
    fire_valve.turn_on()
    time.sleep(duration)  # Duration to fire the rocket
    fire_valve.turn_off()
    print("Rocket fired.")


def reset_system(transfer_valve_relay, fire_valve_relay):
    """
    Reset the system by transferring fuel and firing the rocket.

    :param transfer_valve_relay: Relay controlling the transfer valve.
    :param fire_valve_relay: Relay controlling the fire valve.
    """
    print("Resetting system.")
    transfer_fuel(transfer_valve_relay)  # Transfer fuel to reset the system
    fire_rocket(fire_valve_relay)        # Fire the rocket to reset the system
    print("System reset.")


def wait_for_button_press(button, timeout=60):
    """
    Wait for a button press with a timeout.

    :param button: Instance of the Button class.
    :param timeout: Maximum time to wait for a button press in seconds.
    :return: True if button was pressed, False if timeout occurred.
    """
    start_time = time.time()
    while not button.is_pressed():
        button.blink_led()
        if (time.time() - start_time) > timeout:
            print(f"Timeout waiting for {button.led} button press.")
            return False
    button.led.off()
    print("Button pressed.")
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
    encoder = Encoder(ENCODER_PIN, pulses_per_rotation=2)  # Adjust pulses_per_rotation as needed

    # Initialize Relays for Valves
    bubble_valve_relay = Relay(BUBBLE_VALVE_RELAY_PIN)  
    transfer_valve_relay = Relay(TRANSFER_VALVE_RELAY_PIN)
    fire_valve_relay = Relay(FIRE_VALVE_RELAY_PIN)

    while True:
        # Wait until the encoder is activated (full rotation detected)
        if encoder.is_activated():
            print("Activation signal received. Starting sequence.")

            # Generate fuel
            generate_fuel(bubble_valve_relay)

            # Blink the green LED until the green button is pressed or timeout
            print("Waiting for green button press...")
            if not wait_for_button_press(green_button):
                print("Green button not pressed in time. Aborting sequence.")
                reset_system(transfer_valve_relay, fire_valve_relay)
                continue  # Restart the loop or handle accordingly

            # Blink the blue LED until the blue button is pressed or timeout
            print("Waiting for blue button press...")
            if not wait_for_button_press(blue_button):
                print("Blue button not pressed in time. Aborting sequence.")
                reset_system(transfer_valve_relay, fire_valve_relay)
                continue

            # Transfer fuel
            transfer_fuel(transfer_valve_relay)

            # Blink the red LED until the red button is pressed or timeout
            print("Waiting for red button press...")
            if not wait_for_button_press(red_button):
                print("Red button not pressed in time. Aborting sequence.")
                fire_rocket(fire_valve_relay)  # Fire the rocket to reset the system
                continue

            # Fire the rocket
            fire_rocket(fire_valve_relay)

            print("Sequence completed. Resetting system.\n")

        # Small delay to prevent CPU overutilization
        time.sleep(0.1)


# =========================
# Entry Point
# =========================

if __name__ == "__main__":
    main()
