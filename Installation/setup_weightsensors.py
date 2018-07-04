import time
from Client_Prototype.HardwareControl.Sensors.WeightSensor import WeightSensor


# define reference unit
# read value of last two plates
last_plate = input("Type the value (weight) of the last plate: ")
seconds_last_plate = input("Type the value (weight) of the plate above the last plate: ")
if last_plate <= seconds_last_plate:
    raise Exception("Value of the last plate must be greater than the value of the plate above!")
# measure weight
print("Please lift the whole weight stack except the last plate.")
time.sleep(5)
print("Start measuring... keep lifting!")
measures = []
for i in range(0,5):
    pass
# calculate and set reference unit

# create translation table
# get number of plates
# for each plate, take measures to define the intervals
# create translation table
# update config-file