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

        _LOGGER.debug(f"CONF_HOST: {host}")

        # Create a unique device identifier
        self.device_id = f"avgear_matrix_{host.replace('.', '_')}"

    async def _async_update_data(self) -> dict[str, AsyncHDMIMatrix]:
        """Fetch data from AVGear Matrix."""
        _LOGGER.warning("_async_update_data coordinator")

        try:
            async with self.matrix:
                video_status = await self.matrix.get_video_status_parsed()
                _LOGGER.debug(f"Video Status: {video_status}")
                return video_status
        except OSError as error:
            raise UpdateFailed from error
