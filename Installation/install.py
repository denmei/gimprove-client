import os

# load required packages and install
os.system("pip3 install numpy==1.14.2")
os.system("pip3 install twisted==18.4.0")
os.system("pip3 install matplotlib==2.1.1")
os.system("pip3 install pandas==0.22.0")
os.system("pip3 install pytz==2018.3")
os.system("pip3 install requests==2.18.4")
os.system("pip3 install autobahn==0.6.0.5")
os.system("pip3 install websocket-client==0.47.0")
os.system("pip3 install boto3==1.7.23")
os.system("sudo apt-get install python-smbus")
os.system("sudo apt-get install i2c-tools")
os.system("sudo reboot now")

# configure aws
os.system("pip install awscli --upgrade --user")
os.system("complete -C aws_completer aws")
os.system("aws configure")

