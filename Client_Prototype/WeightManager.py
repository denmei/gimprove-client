import random
from hx711py.hx711 import HX711


class WeightManager(HX711):

    def __init__(self):
        super(WeightManager, self).__init__(5, 6)

    def get_weight_fake(self):
        return random.randint(5, 100)
