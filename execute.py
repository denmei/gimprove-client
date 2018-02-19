from Client_Prototype.Client import Equipment
import os

equipment = Equipment(exercise_name='Lat Pulldown', equipment_id="fded5e7ff5044992bb70949f3aec172c",
                      link_path=os.path.dirname(os.path.realpath(__file__)) + "/api-links.json")
equipment.run()