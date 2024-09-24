from machine import Pin
import time

# Pin Constants
BLUE_BUTTON_PIN = 17
BLUE_LED_PIN = 16
GREEN_BUTTON_PIN = 19
GREEN_LED_PIN = 18
RED_BUTTON_PIN = 21
RED_LED_PIN = 20
BUBBLE_VALVE_RELAY_PIN = 13
TRANSFER_VALVE_RELAY_PIN = 12
FIRE_VALVE_RELAY_PIN = 11
ENCODER_PIN = 15

# Timing Constants
BUBBLE_SLEEP = 20
TRANSFER_SLEEP = 4
FIRE_DURATION = 1.5

TIMEOUT_DURATION = 30

# Misc Constants
ROTATION_COUNT_TO_START = 4

class Button:
    def __init__(self, button_pin, led_pin, debounce_time=25):
        self.button = Pin(button_pin, Pin.IN, Pin.PULL_DOWN)
        self.led = Pin(led_pin, Pin.OUT)
        self.debounce_time = debounce_time / 1000

    def is_pressed(self):
        if self.button.value():
            time.sleep(self.debounce_time)
            if self.button.value():
                return True
        return False

    def blink_led(self, interval=0.5):
        self.led.on()
        time.sleep(interval)
        self.led.off()
        time.sleep(interval)

class Encoder:
    def __init__(self, encoder_pin, pulses_per_rotation=2, debounce_time=0.001):
        self.encoder = Pin(encoder_pin, Pin.IN, Pin.PULL_DOWN)
        self.pulses_per_rotation = pulses_per_rotation
        self.debounce_time = debounce_time
        self.pulse_count = 0
        self.activated = False
        self.last_trigger_time = 0
        self.encoder.irq(trigger=Pin.IRQ_RISING, handler=self._irq_handler)

    def _irq_handler(self, pin):
        current_time = time.ticks_us() / 1_000_000
        if (current_time - self.last_trigger_time) > self.debounce_time:
            self.pulse_count += 1
            self.last_trigger_time = current_time
            if self.pulse_count >= self.pulses_per_rotation:
                self.activated = True
                self.pulse_count = 0

    def is_activated(self):
        if self.activated:
            self.activated = False
            return True
        return False

class Relay:
    def __init__(self, relay_pin):
        self.relay_pin = relay_pin
        self.relay = Pin(relay_pin, Pin.OUT)
        self.turn_off()

    def turn_on(self):
        self.relay.on()
        print(f"Relay on pin {self.relay_pin} turned ON.")

    def turn_off(self):
        self.relay.off()
        print(f"Relay on pin {self.relay_pin} turned OFF.")

def generate_fuel(bubble_valve, duration=BUBBLE_SLEEP):
    print("Generating fuel: Activating bubble valve.")
    bubble_valve.turn_on()
    time.sleep(duration)
    bubble_valve.turn_off()
    print("Fuel generation completed.")

def transfer_fuel(transfer_valve, duration=TRANSFER_SLEEP):
    print("Transferring fuel: Turning on transfer valve.")
    transfer_valve.turn_on()
    time.sleep(duration)
    transfer_valve.turn_off()
    print("Fuel transfer completed.")

def fire_rocket(fire_valve, duration=FIRE_DURATION):
    print("Firing rocket: Turning on fire valve.")
    fire_valve.turn_on()
    time.sleep(duration)
    fire_valve.turn_off()
    print("Rocket fired.")

def wait_for_button_press(button, timeout=TIMEOUT_DURATION):
    start_time = time.time()
    while not button.is_pressed():
        button.blink_led()
        if (time.time() - start_time) > timeout:
            print(f"Timeout waiting for button press.")
            return False
    button.led.on()
    print("Button pressed.")
    return True

def leds_off(leds):
    for led in leds:
        led.off()

def main():
    blue_button = Button(BLUE_BUTTON_PIN, BLUE_LED_PIN)
    green_button = Button(GREEN_BUTTON_PIN, GREEN_LED_PIN)
    red_button = Button(RED_BUTTON_PIN, RED_LED_PIN)
    encoder = Encoder(ENCODER_PIN, pulses_per_rotation=(ROTATION_COUNT_TO_START * 2))
    bubble_valve_relay = Relay(BUBBLE_VALVE_RELAY_PIN)
    transfer_valve_relay = Relay(TRANSFER_VALVE_RELAY_PIN)
    fire_valve_relay = Relay(FIRE_VALVE_RELAY_PIN)

    leds_off([blue_button.led, green_button.led, red_button.led])

    while True:
        if encoder.is_activated():

            print("Activation signal received. Starting sequence.")
            generate_fuel(bubble_valve_relay)
            
            print("Waiting for green button press...")
            if not wait_for_button_press(green_button):
                print("Green button not pressed in time. Resetting system.")
                transfer_fuel(transfer_valve_relay)
                leds_off([blue_button.led, green_button.led, red_button.led])
                print("Aborting sequence.")
                continue
            
            print("Waiting for blue button press...")
            if not wait_for_button_press(blue_button):
                print("Blue button not pressed in time. Resetting system.")
                transfer_fuel(transfer_valve_relay)
                leds_off([blue_button.led, green_button.led, red_button.led])
                print("Aborting sequence.")
                continue
            
            print("Transferring fuel...")
            transfer_fuel(transfer_valve_relay)
            
            print("Waiting for red button press...")
            if not wait_for_button_press(red_button):
                print("Red button not pressed in time. Aborting sequence.")
                leds_off([blue_button.led, green_button.led, red_button.led])
                continue
            
            print("Firing rocket...")
            fire_rocket(fire_valve_relay)

            print("Sequence completed. Resetting system.\n")

            leds_off([blue_button.led, green_button.led, red_button.led])
            time.sleep(30)


        time.sleep(0.1)

if __name__ == "__main__":
    main()
