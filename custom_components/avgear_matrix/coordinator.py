"""DataUpdateCoordinator for AVGear Matrix integration."""

from __future__ import annotations

import asyncio
import ipaddress
import logging
from importlib.metadata import version as pkg_version

_CROCKFORD_ALPHABET = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"


def _crockford32_encode(n: int) -> str:
    """Encode an integer as a Crockford Base32 string."""
    if n == 0:
        return "0"
    result = []
    while n:
        result.append(_CROCKFORD_ALPHABET[n & 31])
        n >>= 5
    return "".join(reversed(result))

from hdmimatrix import AsyncHDMIMatrix

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DEVICE_NAME, DOMAIN, MANUFACTURER, SCAN_INTERVAL

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
        port: int,
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
        _host_int = int(ipaddress.ip_address(host))
        self.short_id = _crockford32_encode((_host_int << 16) | port)
        self.device_id = f"avgear_matrix_{self.short_id}"
        self.device_info = None
        self.num_inputs: int = 4
        self.num_outputs: int = 4
        self.is_powered_on: bool | None = None
        self.is_hdbt_powered_on: bool | None = None
        self.output_power_status: dict[int, bool] = {}
        self._lock = asyncio.Lock()

    async def _async_update_data(self) -> dict[str, str]:
        """Fetch data from AVGear Matrix."""
        _LOGGER.debug("_async_update_data coordinator")

        try:
            async with self._lock, self.matrix:
                video_status = await self.matrix.get_video_status_parsed()
                _LOGGER.debug("Video Status: %s", video_status)
                self.is_powered_on = await self.matrix.is_powered_on()
                _LOGGER.debug("Is powered on: %s", self.is_powered_on)
                self.is_hdbt_powered_on = await self.matrix.is_hdbt_powered_on()
                _LOGGER.debug("Is HdBT powered on: %s", self.is_hdbt_powered_on)
                self.output_power_status = await self.matrix.get_output_power_status_parsed()
                _LOGGER.debug("Output power status: %s", self.output_power_status)
                return video_status
        except OSError as error:
            raise UpdateFailed from error

    async def async_power_on(self) -> bool:
        """Power on the matrix."""
        try:
            async with self._lock, self.matrix:
                result = await self.matrix.power_on()
                _LOGGER.debug("Power on result: %s", result)
                return result
        except Exception as err:
            _LOGGER.error("Failed to power on matrix: %s", err)
            return False

    async def async_power_off(self) -> bool:
        """Power off the matrix."""
        try:
            async with self._lock, self.matrix:
                result = await self.matrix.power_off()
                _LOGGER.debug("Power off result: %s", result)
                return result
        except Exception as err:
            _LOGGER.error("Failed to power off matrix: %s", err)
            return False

    async def async_hdbt_power_on(self) -> bool:
        """Power on HdBT."""
        try:
            async with self._lock, self.matrix:
                result = await self.matrix.hdbt_power_on()
                _LOGGER.debug("HdBT power on result: %s", result)
                if result:
                    self.is_hdbt_powered_on = True
                return result
        except Exception as err:
            _LOGGER.error("Failed to power on HdBT: %s", err)
            return False

    async def async_hdbt_power_off(self) -> bool:
        """Power off HdBT."""
        try:
            async with self._lock, self.matrix:
                result = await self.matrix.hdbt_power_off()
                _LOGGER.debug("HdBT power off result: %s", result)
                if result:
                    self.is_hdbt_powered_on = False
                return result
        except Exception as err:
            _LOGGER.error("Failed to power off HdBT: %s", err)
            return False

    async def async_output_on(self, output_num: int) -> bool:
        """Power on an individual output."""
        try:
            async with self._lock, self.matrix:
                result = await self.matrix.output_on(output_num)
                _LOGGER.debug("Output %s on result: %s", output_num, result)
                if result:
                    self.output_power_status[output_num] = await self.matrix.is_output_on(output_num)
                return result
        except Exception as err:
            _LOGGER.error("Failed to power on output %s: %s", output_num, err)
            return False

    async def async_output_off(self, output_num: int) -> bool:
        """Power off an individual output."""
        try:
            async with self._lock, self.matrix:
                result = await self.matrix.output_off(output_num)
                _LOGGER.debug("Output %s off result: %s", output_num, result)
                if result:
                    self.output_power_status[output_num] = await self.matrix.is_output_on(output_num)
                return result
        except Exception as err:
            _LOGGER.error("Failed to power off output %s: %s", output_num, err)
            return False

    async def async_route_input_to_output(
        self, input_num: int, output_num: int
    ) -> bool:
        """Route input to output."""
        try:
            async with self._lock, self.matrix:
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
                async with self._lock, self.matrix:
                    name = await self.matrix.get_device_name()
                    device_type = await self.matrix.get_device_type()
                    version = await self.matrix.get_device_version()
                    input_status = await self.matrix.get_input_status_parsed()

                lib_version = await self.hass.async_add_executor_job(pkg_version, "hdmimatrix")
                self.device_info = {
                    "model": name,
                    "type": device_type,
                    "version": version,
                    "lib_version": lib_version,
                }
                if input_status:
                    self.num_inputs = len(input_status)
                    self.num_outputs = len(input_status)
            except Exception as err:
                _LOGGER.warning("Could not get device info: %s", err)
                self.device_info = {
                    "model": "Unknown",
                    "type": "Unknown",
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
            manufacturer=MANUFACTURER,
            name=f"{DEVICE_NAME} {self.short_id}",
            model=info.get("model"),
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
