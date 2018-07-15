from client_repo.Client_Prototype.Helpers.Observable import Observable


class ClientState(Observable):
    """
    State class for the client. Provides information about the current state of the client, including the wifi-connection
    or whether the client is currently recording from the sensors.
    Other classes can subscribe as listeners and react on statechanges.
    """

    def __init__(self, recording):
        super(ClientState, self).__init__("ClientState")
        self.__recording__ = recording

    def set_record_attr(self, new_record):
        self.__recording__ = new_record
        self.update_listeners(attribute='recording', value=self.__recording__)
