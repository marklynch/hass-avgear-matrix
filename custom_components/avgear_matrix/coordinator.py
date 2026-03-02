"""DataUpdateCoordinator for AVGear Matrix integration."""

from __future__ import annotations

import logging
from importlib.metadata import version as pkg_version

from hdmimatrix import AsyncHDMIMatrix

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, SCAN_INTERVAL, SUPPORTED_MODELS

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

        _LOGGER.debug("Init coordinator")

        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )

        _LOGGER.debug("CONF_HOST: %s", host)

        # Create a unique device identifier
        self.host = host
        self.device_id = f"avgear_matrix_{host.replace('.', '_')}"
        self.device_info = None
        self.num_inputs: int = 4
        self.num_outputs: int = 4
        self.is_powered_on: bool | None = None

    async def _async_update_data(self) -> dict[str, str]:
        """Fetch data from AVGear Matrix."""
        _LOGGER.debug("_async_update_data coordinator")

        try:
            async with self.matrix:
                video_status = await self.matrix.get_video_status_parsed()
                _LOGGER.debug("Video Status: %s", video_status)
                self.is_powered_on = await self.matrix.is_powered_on()
                _LOGGER.debug("Is powered on: %s", self.is_powered_on)
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
                    version = await self.matrix.get_device_version()

                lib_version = pkg_version("hdmimatrix")
                self.device_info = {
                    "name": "AVGear Matrix",
                    "model": name,
                    "manufacturer": "AVGear",
                    "version": version,
                    "lib_version": lib_version,
                }
                if name in SUPPORTED_MODELS:
                    self.num_inputs = SUPPORTED_MODELS[name]["inputs"]
                    self.num_outputs = SUPPORTED_MODELS[name]["outputs"]
            except Exception as err:
                _LOGGER.warning("Could not get device info: %s", err)
                self.device_info = {
                    "name": "Unknown",
                    "model": "Unknown",
                    "manufacturer": "AVGear",
                    "version": "Unknown",
                    "lib_version": "Unknown",
                }
        return self.device_info

    @property
    def ha_device_info(self) -> DeviceInfo:
        """Return HA DeviceInfo for this device."""
        info = self.device_info or {}
        return DeviceInfo(
            identifiers={(DOMAIN, self.device_id)},
            manufacturer="AVGear",
            name=info.get("name", "AVGear Matrix"),
            model=info.get("model"),
            sw_version=f"{info.get('version', 'Unknown')} (hdmimatrix {info.get('lib_version', 'Unknown')})",
            configuration_url=f"http://{self.host}",
        )

    def update_output_state(self, output_num: int, input_num: int) -> None:
        """Update the internal state for a specific output immediately."""
        if self.data is None:
            self.data = {}
        self.data[output_num] = input_num
        _LOGGER.debug(
            "Updated internal state: output %s -> input %s", output_num, input_num
        )
