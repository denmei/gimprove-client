# Gimprove-Client

This program is designed to turn a Raspberry Pi into a Gimprove-component. The functionalities include:
* User authentification
* Record the data coming from different sensors
* Analyzing the sensor data to identify repetitions and weights
* Sending results to the GImprove-server using the GImprove-API (HTTP) and via a Websocket-Connection

## Install
To install all required packages, run `python3 install.py` from the root directory.

### Setup User
Communication with the Gimprove-server requires the client to authenticate with his credentials. When setting up the 
client, you have to enter the credentials in the corresponding file under ```test/Configuration/.credentials.json```.

At the moment, you'll also have to update your equipment-id in ```Configuration/config.json```.

### Setup AWS
To setup AWS for uploading the log-Files to S3:
* Create `/.aws`: `mkdir /.aws` and cd into the new directory
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

## Usage
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
* logging.log: Applikations-Logs.
* weight_translation.csv: Helps converting measured weight to the weight stack on the machine if option is activated.
* client_cache.txt: If there are connection problems, all HTTP-Requests from the client will be cached here and sent later.


You can find more detailed information in the Wiki.
