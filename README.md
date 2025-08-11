# hass-avgear-matrix
Homeassistant integration for AVGear Matrix to allow control and routing of HDMI inputs.

It uses the [hdmimatrix python library](https://github.com/marklynch/hdmimatrix) to control the hdmi matrix.

## Install
* Ensure Home Assistant is updated to version 2025.2.0 or newer.
* Use HACS and add as a custom repo; or download and manually move to the custom_components folder.
* Once the integration is installed follow the standard process to setup via UI and search for AVgear.
* Follow the prompts.

## Currently working
* Setup of AVGear Matrix TMX44PRO AVK
* Creation of device and entities
* Select button to switch input and outputs.

## Future work
* Add more models (need assistance for testing)
* Add version and other info support
