# Gimprove-Client

Gimprove is a lightweight system built to digitalize fitness equipment. Once installed on regular machines, Gimproves
allows users to automatically track all relevant keyfigures of their activities such as the number of the repetitions
or the weight used. Users get feedback in realtime and can analyze their progress in the Gimprove App.

Related respositories are:
1) <a href="">Gimprove Backend</a>: Gimprove Plattform hosting the Gimprove Website and providing the Gimprove-API.
2) <a href="">Gimprove-App</a>: User Interface.

This program is designed to turn a Raspberry Pi into a Gimprove-component that can be used to upgrade any fitness machine.
 The functionalities include:
* User authentification
* Record the data coming from different sensors
* Analyzing the sensor data to identify repetitions and weights
* Sending results to the GImprove-server using the GImprove-API (HTTP) and via a Websocket-Connection

<img src="/readme/client_terminal.JPG">

## Install
To install all required packages, run `python3 install.py` from the root directory.

### Setup User
Communication with the Gimprove-server requires the client to authenticate with his credentials. When setting up the 
client, you have to enter the credentials.

At the moment, you'll also have to update your equipment-id in ```Configuration/config.json```.

### Setup AWS
To setup AWS for uploading the log-Files to S3:
* Go to Home directory by executing `cd`
* Create `/.aws` with the command `mkdir .aws` and cd into the new directory
* Create the configuration file with `touch config`, open the file and paste: 
```
[default]
region = eu-central-1
```
* Create the credentials file with `touch credentials` and enter the following (replace *** with your credentials!):
```
[default]
aws_access_key_id = ***
aws_secret_access_key = ***
```

### Not on Raspberry Pi
If you're not using a Raspberry Pi, you might have to execute the following steps
before executing the `execute.py`-script:

1) In the sm_gym_client-directory, add a new directory named `RPi`

2) In `RPi`, add a new file called `GPIO.py` with the following content:
```python
class GPIO:
    pass
```

3) Add an empty file named `__init__.py` to the `RPi` directory.


## Usage
Before running the client, make sure that you're using the correct environment by checking the config.json-file.
To **run** the client, run the `execute.py` file with `python3 execute.py` from the root-directory.

To **test** the client, execute the following command from the root-directory: `python3 -m unittest`. The server must be
running locally on 127.0.0.1:8000.

## Built with
* <a href="https://github.com/johnbryanmoore/VL53L0X_rasp_python">VL53L0X_rasp_python</a>: Python interface to the 
VL53L0X.
* 

## Contributing
**Dennis Meisner:** meisnerdennis@web.de.

## Configuration: 
The Configuration-folder contains files with necessary information to run the application:

* api-links.json: Links to the GImprove-API (testing and production).
* config.json: Configuration data for the device (name, id etc.).
* logs/logging.log: Applikations-Logs.
* weight_translation.csv: Helps converting measured weight to the weight stack on the machine if option is activated.
* client_cache.txt: If there are connection problems, all HTTP-Requests from the client will be cached here and sent later.
* credentials-template.json: Empty template for the client's credentials.
* .credentials.json: Contains the credentials for the communication with the Gimprove-Server


You can find more detailed information in the Wiki.
