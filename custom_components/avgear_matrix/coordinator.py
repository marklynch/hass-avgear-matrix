"""DataUpdateCoordinator for AVGear Matrix integration."""

from __future__ import annotations

import logging

from hdmimatrix import AsyncHDMIMatrix

from homeassistant.components.climate import SCAN_INTERVAL
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


type AVGearMatrixConfigEntry = ConfigEntry[AVGearMatrixDataUpdateCoordinator]


class AVGearMatrixDataUpdateCoordinator(DataUpdateCoordinator[dict[str, str]]):
    """Class to manage fetching AVGear data."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: AVGearMatrixConfigEntry,
        matrix: AsyncHDMIMatrix,
        host: str,
    ) -> None:
        """Initialize global AVGear data updater."""
        self.matrix = matrix

        _LOGGER.warning("Init coordinator")

        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )

        # host = entry.get("CONF_HOST", "wrong")
        _LOGGER.debug("CONF_HOST: %s", host)

        # Create a unique device identifier
        self.device_id = f"avgear_matrix_{host.replace('.', '_')}"
        self.device_info = None

    async def _async_update_data(self) -> dict[str, AsyncHDMIMatrix]:
        """Fetch data from AVGear Matrix."""
        _LOGGER.warning("_async_update_data coordinator")

        try:
            async with self.matrix:
                video_status = await self.matrix.get_video_status_parsed()
                _LOGGER.debug("Video Status: %s", video_status)
                return video_status
        except OSError as error:
            raise UpdateFailed from error

    async def async_power_on(self) -> bool:
        """Power on the matrix."""
        try:
            async with self.matrix:
                result = await self.matrix.power_on()
                _LOGGER.debug("Power on result: %s", result)
                return result
        except Exception as err:
            _LOGGER.error("Failed to power on matrix: %s", err)
            return False

    async def async_power_off(self) -> bool:
        """Power off the matrix."""
        try:
            async with self.matrix:
                result = await self.matrix.power_off()
                _LOGGER.debug("Power off result: %s", result)
                return result
        except Exception as err:
            _LOGGER.error("Failed to power off matrix: %s", err)
            return False

    async def async_route_input_to_output(
        self, input_num: int, output_num: int
    ) -> bool:
        """Route input to output."""
        try:
            async with self.matrix:
                # Ensure the output is powered on before routing
                result = await self.matrix.output_on(output_num)
                _LOGGER.debug("Turned on output %s: %s", output_num, result)

                # Now route the input to the output
                result = await self.matrix.route_input_to_output(input_num, output_num)
                _LOGGER.debug(
                    "Routed input %s to output %s: %s", input_num, output_num, result
                )
                # Update internal state immediately
                self.update_output_state(output_num, input_num)
                return result
        except Exception as err:
            _LOGGER.error(
                "Failed to route input %s to output %s: %s", input_num, output_num, err
            )
            return False

    async def async_get_device_info(self):
        """Get static device information once."""
        if self.device_info is None:
            try:
                # Load static info from device
                async with self.matrix:
                    name = await self.matrix.get_device_name()
                    device_type = await self.matrix.get_device_type()
                    version = await self.matrix.get_device_version()

                self.device_info = {
                    "name": name,
                    "model": device_type,
                    "manufacturer": "AVGear",
                    "version": version,
                }
            except Exception as err:
                _LOGGER.warning("Could not get device info: %s", err)
                self.device_info = {
                    "name": "Unknown",
                    "model": "Unknown",
                    "manufacturer": "AVGear",
                    "version": "Unknown",
                }
        return self.device_info

    def update_output_state(self, output_num: int, input_num: int) -> None:
        """Update the internal state for a specific output immediately."""
        if self.data is None:
            self.data = {}
        self.data[output_num] = input_num
        _LOGGER.debug(
            "Updated internal state: output %s -> input %s", output_num, input_num
        )
