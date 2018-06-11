
class StatusLed:
    """
    Representation of the Client's status LED.
    """

    def __init__(self, client):
        client.listen_to_statechange(self)
        self.turn_off()
        self.__is_on__ = False

    def update(self, update):
        print("update led: %s" % update)
        if update['Object'] == "ClientState":
            if update['Attribute'] == 'recording':
                if update['Value']:
                    self.turn_on()
                else:
                    self.turn_off()

    def turn_off(self):
        print("LED OFF")

    def turn_on(self):
        print("LED ON")

    def is_on(self):
        return self.__is_on__
