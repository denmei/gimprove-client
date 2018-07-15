import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from client_repo.Client_Prototype.Client import Equipment

equipment = Equipment()
equipment.run()
