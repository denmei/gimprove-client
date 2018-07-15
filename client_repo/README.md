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

![alt text](readme/client_terminal.JPG)

## Install
### Raspberry set up (if necessary)
1) Set up wifi: follow [this instruction](https://www.raspberrypi.org/documentation/configuration/wireless/wireless-cli.md)
2) ```sudo apt-get update```
3) ```sudo apt-get upgrade```
4) ```sudo apt-get install git```
5) ```sudo apt-get install python3-pip```
6) ```sudo apt-get install python-pip```
7) ```sudo pip3 install RPi.GPIO```
8) Clone this repository: ```git clone https://den_mei@bitbucket.org/den_mei/gimprove_client.git```

Once the previous steps are completed, start the program with the command `python3 sync_and_start.py`. If 
the script is used for the first time, it will guide through the remaining steps including:
* Install required python-packages
* Setup AWS
* Setup Gimprove-Account
* Modify .bashrc

### Not on Raspberry Pi
If you're not using a Raspberry Pi, you might have to execute the following steps:

UPDATE!!


## Usage
**Running the client:** Be aware that the `sync_and_start.py`-script is always executed once the pi is rebooted! In this process, the current
code base is updated from the related Gimprove-S3 bucket. The proceeding behavior of the client depends on the environment defined in the `config.json`-file:
* *Production*: The client starts automatically.
* *Test/Local*: The client is not started by the sync_and_start-script. Start the client manually by executing the `gimprove_client/execute.py`-script.

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
