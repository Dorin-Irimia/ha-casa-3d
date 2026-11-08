"""Casa 3D: casa ta în 3D, cu senzorii din Home Assistant pe ea.

Integrarea:
  * servește paginile din `frontend/` la URL_BASE;
  * adaugă în bara laterală panoul „Casa 3D” (și, opțional, configuratorul
    display-ului NTC);
  * păstrează schița casei în `.storage/casa_3d.config` și o expune prin
    comenzile WebSocket `casa_3d/config/get` și `casa_3d/config/save`.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
from urllib.parse import urlencode

import voluptuous as vol

from homeassistant.components import frontend, panel_custom, websocket_api
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.storage import Store
from homeassistant.helpers.typing import ConfigType

from .const import (
    CONF_ICON,
    CONF_NTC_PANEL,
    CONF_NTC_TITLE,
    CONF_REQUIRE_ADMIN,
    CONF_TITLE,
    DEFAULT_ICON,
    DEFAULT_NTC_TITLE,
    DEFAULT_TITLE,
    DOMAIN,
    NTC_ICON,
    PANEL_3D,
    PANEL_ELEMENT,
    PANEL_NTC,
    STORAGE_KEY,
    STORAGE_VERSION,
    URL_BASE,
    VERSION,
)

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

FRONTEND_DIR = Path(__file__).parent / "frontend"

# Schița trebuie să aibă măcar etajele și dispozitivele; restul câmpurilor
# sunt validate de pagină (normalizeCfg).
SCHITA_SCHEMA = vol.Schema(
    {
        vol.Required("floors"): vol.All(list, vol.Length(min=1)),
        vol.Required("devices"): list,
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Servește fișierele paginilor și înregistrează comenzile WebSocket."""
    await hass.http.async_register_static_paths(
        [StaticPathConfig(URL_BASE, str(FRONTEND_DIR), cache_headers=False)]
    )
    hass.data[DOMAIN] = {
        "store": Store[dict[str, Any]](hass, STORAGE_VERSION, STORAGE_KEY),
    }
    websocket_api.async_register_command(hass, ws_get_config)
    websocket_api.async_register_command(hass, ws_save_config)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Adaugă panourile în bara laterală."""
    opts = {**entry.data, **entry.options}
    title = opts.get(CONF_TITLE) or DEFAULT_TITLE
    require_admin = bool(opts.get(CONF_REQUIRE_ADMIN, False))
    ntc = bool(opts.get(CONF_NTC_PANEL, False))

    params = {"v": VERSION, "title": title}
    if ntc:
        params["ntc"] = f"/{PANEL_NTC}"
    await _register_panel(
        hass,
        PANEL_3D,
        title,
        opts.get(CONF_ICON) or DEFAULT_ICON,
        f"{URL_BASE}/apartament/index.html?{urlencode(params)}",
        require_admin,
    )
    if ntc:
        await _register_panel(
            hass,
            PANEL_NTC,
            opts.get(CONF_NTC_TITLE) or DEFAULT_NTC_TITLE,
            NTC_ICON,
            f"{URL_BASE}/ntc-display.html?{urlencode({'v': VERSION})}",
            require_admin,
        )

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Scoate panourile. Schița rămâne salvată pentru o reinstalare."""
    frontend.async_remove_panel(hass, PANEL_3D, warn_if_unknown=False)
    frontend.async_remove_panel(hass, PANEL_NTC, warn_if_unknown=False)
    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Opțiunile s-au schimbat: refă panourile."""
    await hass.config_entries.async_reload(entry.entry_id)


async def _register_panel(
    hass: HomeAssistant,
    url_path: str,
    title: str,
    icon: str,
    page: str,
    require_admin: bool,
) -> None:
    await panel_custom.async_register_panel(
        hass,
        frontend_url_path=url_path,
        webcomponent_name=PANEL_ELEMENT,
        sidebar_title=title,
        sidebar_icon=icon,
        module_url=f"{URL_BASE}/{PANEL_ELEMENT}.js?v={VERSION}",
        config={"page": page, "title": title},
        require_admin=require_admin,
    )


async def _async_load(hass: HomeAssistant) -> dict[str, Any] | None:
    data = hass.data[DOMAIN]
    if "config" not in data:
        data["config"] = await data["store"].async_load()
    return data["config"]


@websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/config/get"})
@websocket_api.async_response
async def ws_get_config(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Trimite schița salvată (sau null dacă nu există încă)."""
    connection.send_result(msg["id"], await _async_load(hass))


@websocket_api.require_admin
@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/config/save",
        vol.Required("config"): SCHITA_SCHEMA,
    }
)
@websocket_api.async_response
async def ws_save_config(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Salvează schița (doar administratorii)."""
    data = hass.data[DOMAIN]
    data["config"] = msg["config"]
    await data["store"].async_save(msg["config"])
    connection.send_result(msg["id"], {"saved": True})
