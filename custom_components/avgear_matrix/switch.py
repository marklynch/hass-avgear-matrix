"""Switch platform for AVGear Matrix."""

import logging

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity


_LOGGER = logging.getLogger(__name__)

SWITCH_DESCRIPTION = SwitchEntityDescription(
    key="power",
    translation_key="power",
    entity_category=EntityCategory.CONFIG,
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the AVGear Switch platform."""
    coordinator = config_entry.runtime_data
    async_add_entities([AvgearMatrixPowerSwitch(coordinator, SWITCH_DESCRIPTION)])


class AvgearMatrixPowerSwitch(CoordinatorEntity, SwitchEntity):
    """Switch entity for matrix power state."""

    def __init__(self, coordinator, description: SwitchEntityDescription) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_has_entity_name = True
        self._attr_unique_id = f"{coordinator.device_id}_{description.key}"
        self._attr_translation_key = description.key
        self._attr_device_info = coordinator.ha_device_info

    @property
    def is_on(self) -> bool | None:
        """Return true if the matrix is powered on."""
        return self.coordinator.is_powered_on

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the matrix on."""
        result = await self.coordinator.async_power_on()
        if result:
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.warning("Failed to power on matrix")

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the matrix off."""
        result = await self.coordinator.async_power_off()
        if result:
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.warning("Failed to power off matrix")
