"""Select platform for AVGear Matrix."""

import logging
from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.const import EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the AVGear Select platform."""
    coordinator = config_entry.runtime_data

    entities = []

    # TODO - read this from matrix info in future
    for output_num in range(1, 5):  # Outputs 1-4
        entities.append(AvgearMatrixSelect(coordinator, output_num))

    async_add_entities(entities)


class AvgearMatrixSelect(CoordinatorEntity, SelectEntity):
    """Select entity for matrix output."""

    def __init__(self, coordinator, output_num):
        super().__init__(coordinator)
        self.output_num = output_num
        self._attr_unique_id = f"avgear_matrix_output_{output_num}"
        self._attr_name = f"Matrix Output {output_num}"
        # Define available inputs (adjust based on your matrix)
        self._attr_options = ["1", "2", "3", "4"]  # Input options

        # Add device info
        _LOGGER.debug(f"AvgearMatrixSelect: {coordinator.info}")
        _LOGGER.debug(f"AvgearMatrixSelect - device_id: {coordinator.device_id}")
        self._attr_device_info: DeviceInfo = DeviceInfo(
            identifiers={(DOMAIN, f"{coordinator.device_id}")},
            manufacturer="AVGear",
            model="AVGear Model",
            # name=output_num,
            # sw_version=coordinator.info["version"],
            sw_version="0.0.1",  # TODO - read from device
            # configuration_url=f"http://{coordinator.host}",  # Link to device config
        )

    entity_description = SelectEntityDescription(
        key="switch_input",
        translation_key="switch_input",
        entity_category=EntityCategory.CONFIG,
    )

    @property
    def current_option(self):
        """Return the current input for this output."""
        current_input = self.coordinator.data.get(self.output_num)
        return str(current_input) if current_input else "1"

    async def async_select_option(self, option: str) -> None:
        """Change the input for this output."""
        try:
            # Convert option back to int and route to this output
            input_num = int(option)
            async with self.coordinator.matrix:
                result = await self.coordinator.matrix.route_input_to_output(
                    input_num, self.output_num
                )

            # Log the result for debugging
            _LOGGER.debug(
                f"Routed input {input_num} to output {self.output_num}: {result}"
            )

            # Refresh coordinator data to update all entities
            await self.coordinator.async_request_refresh()

        except ValueError:
            _LOGGER.error(f"Invalid input option: {option}")
        except Exception as err:
            _LOGGER.error(
                f"Failed to route input {option} to output {self.output_num}: {err}"
            )
