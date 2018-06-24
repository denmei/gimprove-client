import os
from shutil import copy2

# load required packages and install
os.system("sudo pip3 install numpy")
os.system("sudo pip3 install twisted")
os.system("sudo apt-get -y install libatlas3-base")
os.system("sudo pip3 install matplotlib")
os.system("sudo pip3 install tkinter")
os.system("sudo pip3 install pandas")
os.system("sudo pip3 install pytz")
os.system("sudo pip3 install requests")
os.system("sudo pip3 install cairocffi")
os.system("sudo pip3 install websocket-client")
os.system("sudo pip3 install boto3")
os.system("sudo apt-get -y install python-smbus")
os.system("sudo apt-get -y install i2c-tools")
os.system("sudo apt-get -y install python-dev python3-dev")
os.system("sudo apt-get -y install python-rpi.gpio python3-rpi.gpio")
os.system("git config --global user.email 'none'")
os.system("git config --global user.name 'pi'")

# maybe necessary for tkinter-problems: sudo apt-get install python3-tk

# configure aws
#TODO: .aws/credentials + .aws/config
# os.system("pip install awscli --upgrade --user")
# os.system("complete -C aws_completer aws")
aws_path = os.path.join(os.path.expanduser("~"), ".aws")
os.mkdir(aws_path)
copy2("credentials", os.path.join(aws_path, "credentials"))
copy2("config", os.path.join(aws_path, "config"))

os.system("sudo reboot now")

#TODO: If installation successfull, add file. If file not there, every time execeute.py is used the installation will be done first
# TODO: ABFRAGE FÜR EQUIPMENT ID