import unittest
from Client_Prototype.Client import Equipment


class TestClient(unittest.TestCase):

    def setUp(self):
        self.equipment = Equipment(exercise_name='Lat Pulldown', equipment_id="1b7d032196154bd5a64c7fcfee388ec5")

    def test_test(self):
        self.assertEqual("hallo", "test")

# run tests
if __name__ == '__main__':
    print("Testing")