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
        info: dict[str, str],  # Todo - likely not using
        host: str,
    ) -> None:
        """Initialize global AVGear data updater."""
        self.matrix = matrix
        self.info = info

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
