# Gimprove-Client

This program is designed to turn a Raspberry Pi into a Gimprove-component. The functionalities include:
* User authentification
* Record the data coming from different sensors
* Analyzing the sensor data to identify repetitions and weights
* Sending results to the GImprove-server using the GImprove-API (HTTP) and via a Websocket-Connection

## Install
All necessary packages are listed in the `requirements.txt`-file. 

## Usage
To **run** the client, run the `execute.py` file with `python3 execute.py` from the root-directory.

To **test** the client, execute the following command from the root-directory: `python3 -m unittest`.

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
* logging.log: Applikations-Logs.
* weight_translation.csv: Helps converting measured weight to the weight stack on the machine if option is activated.
* client_cache.txt: If there are connection problems, all HTTP-Requests from the client will be cached here and sent later.


You can find more detailed information in the Wiki.
