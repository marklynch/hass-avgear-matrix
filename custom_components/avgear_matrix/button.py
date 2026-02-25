"""Button platform for AVGear Matrix."""

import logging

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity


_LOGGER = logging.getLogger(__name__)

BUTTON_DESCRIPTIONS = [
    ButtonEntityDescription(
        key="power_on",
        translation_key="power_on",
        entity_category=EntityCategory.CONFIG,
    ),
    ButtonEntityDescription(
        key="power_off",
        translation_key="power_off",
        entity_category=EntityCategory.CONFIG,
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the AVGear Button platform."""
    coordinator = config_entry.runtime_data

    entities = []
    for description in BUTTON_DESCRIPTIONS:
        entities.append(AvgearMatrixButton(coordinator, description))

    async_add_entities(entities)


class AvgearMatrixButton(CoordinatorEntity, ButtonEntity):
    """Button entity for matrix power control."""

    def __init__(self, coordinator, description: ButtonEntityDescription) -> None:
        """Initialize the button."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_has_entity_name = True
        self._attr_unique_id = f"{coordinator.device_id}_{description.key}"
        self._attr_translation_key = description.key

        self._attr_device_info = coordinator.ha_device_info

    async def async_press(self) -> None:
        """Handle the button press."""
        try:
            if self.entity_description.key == "power_on":
                result = await self.coordinator.async_power_on()
            elif self.entity_description.key == "power_off":
                result = await self.coordinator.async_power_off()
            else:
                _LOGGER.error("Unknown button action: %s", self.entity_description.key)
                return

            if result:
                # Refresh coordinator data after power operations since they may affect overall device state
                await self.coordinator.async_request_refresh()
            else:
                _LOGGER.warning(
                    "Power operation %s failed", self.entity_description.key
                )

        except Exception as err:
            _LOGGER.error("Failed to execute %s: %s", self.entity_description.key, err)
