class Observable:

    def __init__(self, object_name):
        self.__listeners__ = []
        self.__object_name__ = object_name

    def register_listener(self, listener):
        self.__listeners__ += [listener]
        return True

    def release_listener(self, listener):
        if listener in self.__listeners__:
            new_listeners = []
            for old_listener in self.__listeners__:
                if old_listener != listener:
                    new_listeners += old_listener
            self.__listeners__ = new_listeners
        return True

    def update_listeners(self, attribute, value):
        for listener in self.__listeners__:
            try:
                listener.update({'Object': self.__object_name__, 'Attribute': attribute, 'Value': value})
            except Exception as e:
                print("Exception: %s" % e)
