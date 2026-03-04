# hass-avgear-matrix
Homeassistant integration for AVGear Matrix to allow control and routing of HDMI inputs.

It uses the [hdmimatrix python library](https://github.com/marklynch/hdmimatrix) to control the hdmi matrix.

## Install
* Ensure Home Assistant is updated to version 2025.2.0 or newer.
* Use HACS and add as a custom repo:

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=marklynch&repository=hass-avgear-matrix&category=integration)

* Once installed, set up the integration:

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=avgear_matrix)

* Follow the prompts.

## Currently working
* Setup of AVGear Matrix TMX44PRO AVK
* Creation of device and entities
* Select button to switch input and outputs.
* Reads name, type and version numbers

## Future work
* Add more models (need assistance for testing)

