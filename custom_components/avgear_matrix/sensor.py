"""Sensor platform for AVGear Matrix."""

import logging

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

_LOGGER = logging.getLogger(__name__)

SENSOR_DESCRIPTIONS = [
    SensorEntityDescription(
        key="device_name",
        translation_key="device_name",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="device_type",
        translation_key="device_type",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="num_inputs",
        translation_key="num_inputs",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="num_outputs",
        translation_key="num_outputs",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the AVGear Sensor platform."""
    coordinator = config_entry.runtime_data
    async_add_entities(
        AvgearMatrixSensor(coordinator, description)
        for description in SENSOR_DESCRIPTIONS
    )


class AvgearMatrixSensor(CoordinatorEntity, SensorEntity):
    """Sensor entity for AVGear Matrix device information."""

    def __init__(self, coordinator, description: SensorEntityDescription) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_has_entity_name = True
        self._attr_unique_id = f"{coordinator.device_id}_{description.key}"
        self._attr_translation_key = description.key
        self._attr_device_info = coordinator.ha_device_info

    @property
    def native_value(self):
        """Return the sensor value."""
        info = self.coordinator.device_info or {}
        if self.entity_description.key == "device_name":
            return info.get("model")
        if self.entity_description.key == "device_type":
            return info.get("type")
        if self.entity_description.key == "num_inputs":
            return self.coordinator.num_inputs
        if self.entity_description.key == "num_outputs":
            return self.coordinator.num_outputs
        return None
