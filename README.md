# Gimprove-Client
A project where my colleagues and I digitized fitness machines. Unfortunately we had to
stop the project for personal and business reasons. Landing Page is still available here:
[Gimprove-Website](http://www.gimprove.com).

## Project Overview
Gimprove is a lightweight system built to digitize fitness equipment. Once installed on regular machines, Gimprove
allows users to automatically track all relevant keyfigures of their activities such as the number of repetitions
or the weight used. Users get feedback in realtime and can analyze their progress in the Gimprove App. For more
information about Gimprove, visit the [Gimprove-Website](http://www.gimprove.com).

Here's an overview over the Gimprove system and it's components:
![Overview over the single components of the Gimprove System](photos/ReadMe/GimproveSystem.png)

There are three respositories for this project:
1) [Gimprove Backend](https://github.com/denmei/gimprove-backend):
Gimprove Plattform hosting the Gimprove Website and providing the Gimprove-API.

2) [Gimprove-App](https://github.com/denmei/gimprove-app): User Interface.

3) [Gimprove-Client](https://github.com/denmei/gimprove-client): Client that is attached on the machines.

## Repository Overview
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

Optional: Follow [this instruction] (https://www.waveshare.com/wiki/5inch_HDMI_LCD) to install the AddOn for the Mini-Display.

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
* <a href="https://github.com/tatobari/hx711py">hx711py</a>: Python interface for the HX711-sensor (weight-measurement).

## Contributing
**Dennis Meisner:** meisnerdennis@web.de.

## Team Members
* **Lennard Rügauf:** l.ruegauf@gmx.de (Business, Hardware)
* **Matthias Schuhbauer:** matthias_schuhbauer@web.de (Hardware)
* **Dennis Meisner:** meisnerdennis@web.de (Business, Software)

You can find more detailed information in the Wiki.
