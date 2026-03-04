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

## Features
* Supports any AVGear Matrix device
* Master power switch with all controls automatically disabled when powered off
* Route inputs to outputs via select entities per output
* Per-output power switches
* HdBT power switch (HDBaseT models only)
* Diagnostic sensors for device name, type, firmware version, library version, number of inputs, and number of outputs

