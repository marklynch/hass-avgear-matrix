"""Switch platform for AVGear Matrix."""

import logging

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity


_LOGGER = logging.getLogger(__name__)

POWER_SWITCH_DESCRIPTION = SwitchEntityDescription(
    key="power",
    translation_key="power",
)

HDBT_POWER_SWITCH_DESCRIPTION = SwitchEntityDescription(
    key="hdbt_power",
    translation_key="hdbt_power",
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the AVGear Switch platform."""
    coordinator = config_entry.runtime_data

    entities: list = [
        AvgearMatrixPowerSwitch(coordinator, POWER_SWITCH_DESCRIPTION),
        AvgearMatrixHdbtPowerSwitch(coordinator, HDBT_POWER_SWITCH_DESCRIPTION),
    ]
    for output_num in range(1, coordinator.num_outputs + 1):
        entities.append(AvgearMatrixOutputSwitch(coordinator, output_num))

    async_add_entities(entities)


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


class AvgearMatrixHdbtPowerSwitch(CoordinatorEntity, SwitchEntity):
    """Switch entity for HdBT power state."""

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
        """Return true if HdBT is powered on."""
        return self.coordinator.is_hdbt_powered_on

    async def async_turn_on(self, **kwargs) -> None:
        """Turn HdBT on."""
        result = await self.coordinator.async_hdbt_power_on()
        if result:
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.warning("Failed to power on HdBT")

    async def async_turn_off(self, **kwargs) -> None:
        """Turn HdBT off."""
        result = await self.coordinator.async_hdbt_power_off()
        if result:
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.warning("Failed to power off HdBT")


class AvgearMatrixOutputSwitch(CoordinatorEntity, SwitchEntity):
    """Switch entity for an individual output power state."""

    def __init__(self, coordinator, output_num: int) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self.output_num = output_num
        self._attr_has_entity_name = True
        self._attr_unique_id = f"{coordinator.device_id}_output_{output_num}_power"
        self._attr_translation_key = "output_power"
        self._attr_translation_placeholders = {"number": str(output_num)}
        self._attr_device_info = coordinator.ha_device_info

    @property
    def is_on(self) -> bool | None:
        """Return true if this output is powered on."""
        return self.coordinator.output_power_status.get(self.output_num)

    async def async_turn_on(self, **kwargs) -> None:
        """Turn this output on."""
        result = await self.coordinator.async_output_on(self.output_num)
        if result:
            self.async_write_ha_state()
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.warning("Failed to power on output %s", self.output_num)

    async def async_turn_off(self, **kwargs) -> None:
        """Turn this output off."""
        result = await self.coordinator.async_output_off(self.output_num)
        if result:
            self.async_write_ha_state()
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.warning("Failed to power off output %s", self.output_num)
