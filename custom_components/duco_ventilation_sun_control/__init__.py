import logging
from typing import Any

from ducopy import DucoPy
from homeassistant.config_entries import ConfigEntry, ConfigEntryNotReady
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# This integration is configured via config flow only
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Ducobox Connectivity Board integration."""
    _LOGGER.debug("Setting up Ducobox Connectivity Board integration")
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Ducobox from a config entry."""
    base_url = entry.data["base_url"]
    _LOGGER.debug(f"Base URL from config entry: {base_url}")

    try:
        duco_client = DucoPy(base_url=base_url, verify=False)
        _LOGGER.debug(f"DucoPy initialized with base URL: {base_url}")
        hass.data.setdefault(DOMAIN, {})
        hass.data[DOMAIN] = duco_client
    except Exception as ex:
        _LOGGER.error("Could not connect to Ducobox: %s", ex)
        raise ConfigEntryNotReady from ex

    await hass.config_entries.async_forward_entry_setups(entry, ["sensor", "select"])
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor", "select"])
    # if unload_ok:
    # # Retrieve and close the DucoPy instance
    # ducopy = hass.data[DOMAIN].pop(entry.entry_id, None)
    # if ducopy:
    #     ducopy.close()
    return unload_ok
