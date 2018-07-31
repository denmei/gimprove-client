# Gimprove-Client

Gimprove is a lightweight system built to digitalize fitness equipment. Once installed on regular machines, Gimprove
allows users to automatically track all relevant keyfigures of their activities such as the number of repetitions
or the weight used. Users get feedback in realtime and can analyze their progress in the Gimprove App.

Related respositories are:
1) [Gimprove Backend](https://bitbucket.org/den_mei/gimprove_backend/src/master/): 
Gimprove Plattform hosting the Gimprove Website and providing the Gimprove-API.
2) [Gimprove-App](https://bitbucket.org/den_mei/gimprove_app/src/master/): User Interface.

This program is designed to turn a Raspberry Pi into a Gimprove-component that can be used to upgrade any fitness machine.
 The functionalities include:
* User authentification
* Record the data coming from different sensors
* Analyzing the sensor data to identify repetitions and weights
* Sending results to the GImprove-server using the GImprove-API (HTTP) and via a Websocket-Connection

![Raspberry Pi-powered Gimprove Terminal in a Gym.](readme/client_terminal.JPG)

## Install
### Raspberry set up (if necessary)
1) Set up wifi: follow [this instruction](https://www.raspberrypi.org/documentation/configuration/wireless/wireless-cli.md)

2) Configure booting without login: type `sudo raspi-config` to open the menu. Go to `Boot Options` &rarr; `Desktop/CLI` and select `Console Autologin` (should be B2)

After going back to the console:
3) ```sudo apt-get update```

4) ```sudo apt-get upgrade```

5) ```sudo apt-get install git```

6) ```sudo apt-get install python3-pip```

7) ```sudo apt-get install python-pip```

8) ```sudo pip3 install RPi.GPIO```

9) Clone this repository: ```git clone https://den_mei@bitbucket.org/den_mei/gimprove_client.git```

Once the previous steps are completed, start the program with the command `python3 sync_and_start.py`. If 
the script is used for the first time, it will process through the remaining steps including:
* Install required python-packages
* Setup AWS
* Setup Gimprove-Account
* Modify .bashrc

### Not on Raspberry Pi
If you're not using a Raspberry Pi, you might have to execute the following steps (since the Pi's RPi package might 
be missing):

1) In the root directory, add a python-package named `RPi`
2) In the package, add a module named `GPIO.py`
3) Add the following code to the new module:

```
BCM = 1
OUT = 1
HIGH = 1
LOW = 1


def setup(self, a):
    pass


def setmode(self):
    pass


def output(self, a):
    pass
```

## Usage
### Running the client
Be aware that the `sync_and_start.py`-script is always executed once the pi is rebooted! In this process, the current
code base is updated from the related Gimprove-S3 bucket. Then, the client is started automatically.

There are various possibilities to **stop the client**:
1) Type `quit`, press a key combination such as `ctrl + c` or use the quit-rfid-tag defined in the client's config file 
when the client is asking for a rfid to shutdown the client.
2) Type `abort` to stop the client and to access the normal Raspberry Pi terminal (useful for maintenance).

**Exceptions** in the normal program flow will cause the client to restart.

### Testing the client
To test the client, execute the following command from the root-directory: `python3 -m unittest`. The server must be
running locally on 127.0.0.1:8000.

## Built with
* <a href="https://github.com/johnbryanmoore/VL53L0X_rasp_python">VL53L0X_rasp_python</a>: Python interface to the 
VL53L0X.
* 

## Contributing
**Dennis Meisner:** meisnerdennis@web.de.


You can find more detailed information in the Wiki.
