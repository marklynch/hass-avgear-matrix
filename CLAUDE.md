# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a Home Assistant custom integration (HACS-compatible) for controlling AVGear HDMI Matrix switches. It communicates with the device via the [`hdmimatrix`](https://github.com/marklynch/hdmimatrix) Python library over TCP (default port 4001).

The integration uses `local_polling` (30-second interval) and supports the `TMX44PRO AVK` model (4 inputs × 4 outputs). Adding new models requires adding an entry to `SUPPORTED_MODELS` in `const.py`.

## Architecture

All device communication is centralized in `coordinator.py` (`AVGearMatrixDataUpdateCoordinator`). Entities never call the `AsyncHDMIMatrix` object directly — they go through coordinator methods.

The `AsyncHDMIMatrix` object is used as an async context manager for every operation (`async with self.matrix:`), meaning each call opens and closes the connection.

Key data flow:
- `__init__.py`: Entry setup — powers on device, loads static device info, triggers first coordinator refresh, then sets up platforms.
- `coordinator.py`: Manages polling (`_async_update_data` fetches `get_video_status_parsed()`) and exposes action methods (`async_route_input_to_output`, `async_power_on`, `async_power_off`).
- `select.py`: One `AvgearMatrixSelect` entity per output (1–N), reads current routing from `coordinator.data[output_num]`, calls `coordinator.async_route_input_to_output()` on change.
- `button.py`: Power On / Power Off buttons, trigger coordinator refresh after press.
- `switch.py`: Single `AvgearMatrixPowerSwitch` entity; reads `coordinator.is_powered_on` (polled via `is_powered_on()` in `_async_update_data`), calls `coordinator.async_power_on/off()` on toggle.
- `config_flow.py`: Single-step user flow — takes host IP, validates by connecting and checking device name against `SUPPORTED_MODELS`.

## Versioning

Both `manifest.json` and `CHANGELOG.md` must be updated together when releasing. The `hdmimatrix` library version in `requirements` must also match.

## Translations

Entity names and config flow strings live in `translations/`. The `en.json` is the source of truth; `es.json` and `fr.json` mirror its structure. The `matrix_output` select entity uses the `{number}` placeholder.

## Development Setup

This integration runs inside Home Assistant. For local development, copy or symlink `custom_components/avgear_matrix/` into your HA `config/custom_components/` directory and restart HA.

Install the `hdmimatrix` library (used by HA):
```bash
pip install hdmimatrix==0.2.0
```

There are no automated tests in this repo yet (`config-flow-test-coverage` and `test-coverage` are marked `todo` in `quality_scale.yaml`). HA integration tests use `pytest-homeassistant-custom-component` if added in future.
