"""Constante pentru integrarea Casa 3D."""

from __future__ import annotations

from typing import Final

DOMAIN: Final = "casa_3d"
VERSION: Final = "1.0.0"

# Fișierele paginilor (custom_components/casa_3d/frontend) sunt servite aici.
URL_BASE: Final = "/casa_3d_static"

PANEL_3D: Final = "casa-3d"
PANEL_NTC: Final = "casa-3d-ntc"
PANEL_ELEMENT: Final = "casa-3d-panel"

STORAGE_KEY: Final = f"{DOMAIN}.config"
STORAGE_VERSION: Final = 1

CONF_TITLE: Final = "title"
CONF_ICON: Final = "icon"
CONF_REQUIRE_ADMIN: Final = "require_admin"
CONF_NTC_PANEL: Final = "ntc_panel"
CONF_NTC_TITLE: Final = "ntc_title"

DEFAULT_TITLE: Final = "Casa 3D"
DEFAULT_ICON: Final = "mdi:floor-plan"
DEFAULT_NTC_TITLE: Final = "Display NTC"
NTC_ICON: Final = "mdi:thermometer-lines"
