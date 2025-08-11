"""Config flow to configure AVGear Matrix."""

from __future__ import annotations

import logging

from typing import Any

from hdmimatrix import AsyncHDMIMatrix

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import callback

from .const import DEFAULT_PORT, DOMAIN

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
    }
)


async def _validate_connection(host: str) -> bool:
    matrix = AsyncHDMIMatrix(host, DEFAULT_PORT)

    # Using async context manager
    async with matrix:
        name = await matrix.get_device_name()
        # check the name
        _LOGGER.debug(f"Device found: {name}")
        if "TMX44PRO" in name:
            return True

    _LOGGER.warning(f"Device not supported: {name}")
    return False


class AVGearMatrixConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a AVGear Matrix config flow."""

    VERSION = 1

    @callback
    def _async_get_entry(self, data: dict[str, Any]) -> ConfigFlowResult:
        _LOGGER.warning("_async_get_entry")
        return self.async_create_entry(
            title=data[CONF_HOST],
            data={
                CONF_HOST: data[CONF_HOST],
                CONF_PORT: DEFAULT_PORT,
            },
        )

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle a flow initialized by the user."""
        if user_input is None:
            return self.async_show_form(step_id="user", data_schema=DATA_SCHEMA)

        errors = {}

        host = user_input[CONF_HOST]

        try:
            result = await _validate_connection(host)
            if not result:
                errors["base"] = "unsupported_model"
        except OSError:
            errors["base"] = "cannot_connect"

        if errors:
            return self.async_show_form(
                step_id="user", data_schema=DATA_SCHEMA, errors=errors
            )

        _LOGGER.warning("No errors")
        return self._async_get_entry(user_input)
