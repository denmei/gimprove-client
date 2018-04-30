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
* weight_translation.csv: Helps converting measured weight to the weight stack on the machine if option is activated.
* client_cache.txt: If there are connection problems, all HTTP-Requests from the client will be cached here and sent later.

## Usage
To start the client, run the `execute.py` file.

To test the client, execute the following command from the root-directory: `python3 -m unittest`.

## Contributing
**Dennis Meisner:** meisnerdennis@web.de.

Find more detailed information in the Wiki.
