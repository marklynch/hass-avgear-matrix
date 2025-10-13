"""The AVGear Matrix integration."""

import asyncio
from hdmimatrix import AsyncHDMIMatrix

from homeassistant.const import CONF_HOST, CONF_PORT, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.device_registry import DeviceEntry
import logging
from .const import DOMAIN
from .coordinator import AVGearMatrixConfigEntry, AVGearMatrixDataUpdateCoordinator

PLATFORMS = [Platform.SELECT, Platform.BUTTON]

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: AVGearMatrixConfigEntry
) -> bool:
    """Set up AVGear Matrix from a config entry."""

    _LOGGER.warning("Setup Entry")
    host = entry.data[CONF_HOST]
    port = entry.data[CONF_PORT]
    _LOGGER.warning("Setup Entry %s %s", host, port)

    matrix = AsyncHDMIMatrix(
        host,
        port,
    )
    try:
        # Using async context manager
        async with matrix:
            # Power on the device during initial setup
            _LOGGER.debug("Powering on device during setup")
            await matrix.power_on()

            # Wait 2 seconds to ensure device is fully available
            await asyncio.sleep(2)

            name = await matrix.get_device_name()
            if not name:
                raise ConfigEntryNotReady
    except OSError as error:
        raise ConfigEntryNotReady from error

    # TODO - what should we pass through instead of name?
    coordinator = AVGearMatrixDataUpdateCoordinator(hass, entry, matrix, host)
    # Load static device info once during setup
    await coordinator.async_get_device_info()

    # Do first data refresh for dynamic data
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: AVGearMatrixConfigEntry
) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_remove_config_entry_device(
    hass: HomeAssistant,
    config_entry: AVGearMatrixConfigEntry,
    device_entry: DeviceEntry,
) -> bool:
    """Remove a config entry from a device."""
    # TODO fix unloading device for AVGear
    # Are there any checks that should be run?
    return True
