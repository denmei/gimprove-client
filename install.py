import os

os.system("pip install -r requirements.txt --no-index --find-links file: requirements.txt")
os.system("sudo apt-get install python-smbus")
os.system("sudo apt-get install i2c-tools")