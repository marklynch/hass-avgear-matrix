"""Config flow to configure AVGear Matrix."""

from __future__ import annotations

import logging
import asyncio

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
        vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
    }
)


async def _validate_connection(host: str, port: int) -> bool:
    matrix = AsyncHDMIMatrix(host, port)

    # Using async context manager
    async with matrix:
        # Power on the device during initial setup
        _LOGGER.debug("Powering on device during setup")
        await matrix.power_on()

        # Wait 2 seconds to ensure device is fully available
        await asyncio.sleep(2)

        name = await matrix.get_device_name()
        _LOGGER.debug("Device found: %s", name)
        return bool(name)


class AVGearMatrixConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a AVGear Matrix config flow."""

    VERSION = 1

    @callback
    def _async_get_entry(self, data: dict[str, Any]) -> ConfigFlowResult:
        _LOGGER.debug("_async_get_entry")
        return self.async_create_entry(
            title=f"AVGear Matrix ({data[CONF_HOST]}:{data[CONF_PORT]})",
            data={
                CONF_HOST: data[CONF_HOST],
                CONF_PORT: data[CONF_PORT],
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
        port = user_input[CONF_PORT]

        await self.async_set_unique_id(f"{host}:{port}")
        self._abort_if_unique_id_configured()

        try:
            result = await _validate_connection(host, port)
            if not result:
                errors["base"] = "unsupported_model"
        except OSError:
            errors["base"] = "cannot_connect"

        if errors:
            return self.async_show_form(
                step_id="user", data_schema=DATA_SCHEMA, errors=errors
            )

        _LOGGER.debug("No errors")
        return self._async_get_entry(user_input)
