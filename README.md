# SmartGym_Client_Prototype

## Description
This program is designed to turn a raspberry pi into a GImprove-component. The functionalities include:
* User authentification
* Record the data coming from different sensors
* Analyzing the sensor data to identify repetitions and weights
* Sending results to the GImprove-server using the GImprove-API

### Client-Prototype:
Contains all of the logic and the corresponding tests.

### Configuration-Dir: 
Contains files with necessary information to run the application.

* api-links.json: Links to the GImprove-API (testing and production).
* config.json: Configuration data for the device (name, id etc.).
* logging.log: Applikations-Logs.

## Usage
To start the client, run the `execute.py` file.

To test the client, execute the following command from the `sm_gym_client` directory: `python3 -m unittest`.

## Contributing
**Dennis Meisner:** meisnerdennis@web.de.

Find more detailed information in the Wiki.
