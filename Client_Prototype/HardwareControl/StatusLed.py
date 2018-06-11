import RPi.GPIO as GPIO
import time


class StatusLed:
    """
    Representation of the Client's status LED.
    """

    def __init__(self, client, gpio_nr=17):
        # TODO: in settings! also number
        GPIO.setmode(GPIO.BCM)
        client.listen_to_statechange(self)
        GPIO.setup(gpio_nr, GPIO.OUT)
        self.gpio_nr = gpio_nr
        self.__is_on__ = False
        self.turn_off()

    def update(self, update):
        print("update led: %s" % update)
        if update['Object'] == "ClientState":
            if update['Attribute'] == 'recording':
                if update['Value']:
                    self.turn_on()
                else:
                    self.turn_off()

    def turn_off(self):
        GPIO.output(self.gpio_nr, GPIO.LOW)
        print("OFF LED")

    def turn_on(self):
        i = 0
        while i < 20:
            GPIO.output(self.gpio_nr, GPIO.HIGH)
            time.sleep(0.1)
            GPIO.output(self.gpio_nr, GPIO.LOW)
            i = i + 1
        GPIO.output(self.gpio_nr, GPIO.HIGH)
        print("ON LED")

    def is_on(self):
        return self.__is_on__
