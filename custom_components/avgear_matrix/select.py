"""Select platform for AVGear Matrix."""

import logging

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity


_LOGGER = logging.getLogger(__name__)


SELECT_DESCRIPTION = SelectEntityDescription(
    key="matrix_output",
    # name="Matrix Output",
    # translation_key="matrix_output",
    entity_category=EntityCategory.CONFIG,
)


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
        entities.append(AvgearMatrixSelect(coordinator, SELECT_DESCRIPTION, output_num))

    async_add_entities(entities)


class AvgearMatrixSelect(CoordinatorEntity, SelectEntity):
    """Select entity for matrix output."""

    def __init__(
        self, coordinator, description: SelectEntityDescription, output_num
    ) -> None:
        """Set up the AVGear Select platform."""
        super().__init__(coordinator)
        self.entity_description = description

        _LOGGER.info(f"OutputNum: {output_num}")

        self.output_num = output_num
        self._attr_unique_id = f"{coordinator.device_id}_{description.key}_{output_num}"
        self._attr_has_entity_name = True
        self._attr_translation_key = "matrix_output"
        self._attr_translation_placeholders = {"number": str(output_num)}

        # Define available inputs (adjust based on your matrix)
        self._attr_options = ["1", "2", "3", "4"]  # Input options

        self._attr_device_info = coordinator.ha_device_info

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

            # Use coordinator method instead of direct matrix access
            result = await self.coordinator.async_route_input_to_output(
                input_num, self.output_num
            )

            if result:
                # Trigger state update for this entity and any others watching the same data
                self.async_write_ha_state()
            else:
                _LOGGER.warning(
                    "Failed to route input %s to output %s", input_num, self.output_num
                )

        except ValueError:
            _LOGGER.error("Invalid input option: %s", option)
        except Exception as err:
            _LOGGER.error(
                "Failed to route input %s to output %s: %s",
                option,
                self.output_num,
                err,
            )
