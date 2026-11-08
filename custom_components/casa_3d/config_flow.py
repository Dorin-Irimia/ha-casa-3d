"""Configurare din interfață pentru Casa 3D."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    CONF_ICON,
    CONF_NTC_PANEL,
    CONF_REQUIRE_ADMIN,
    CONF_TITLE,
    DEFAULT_ICON,
    DEFAULT_TITLE,
    DOMAIN,
)


def _schema(values: dict[str, Any]) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(
                CONF_TITLE, default=values.get(CONF_TITLE, DEFAULT_TITLE)
            ): selector.TextSelector(),
            vol.Required(
                CONF_ICON, default=values.get(CONF_ICON, DEFAULT_ICON)
            ): selector.IconSelector(),
            vol.Required(
                CONF_REQUIRE_ADMIN, default=values.get(CONF_REQUIRE_ADMIN, False)
            ): selector.BooleanSelector(),
            vol.Required(
                CONF_NTC_PANEL, default=values.get(CONF_NTC_PANEL, False)
            ): selector.BooleanSelector(),
        }
    )


class Casa3DConfigFlow(ConfigFlow, domain=DOMAIN):
    """Adăugarea integrării (o singură instanță, vezi manifest.json)."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(
                title=DEFAULT_TITLE, data={}, options=user_input
            )
        return self.async_show_form(step_id="user", data_schema=_schema({}))

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return Casa3DOptionsFlow()


class Casa3DOptionsFlow(OptionsFlow):
    """Titlul, pictograma și panourile se pot schimba oricând."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(data=user_input)
        return self.async_show_form(
            step_id="init", data_schema=_schema(dict(self.config_entry.options))
        )
