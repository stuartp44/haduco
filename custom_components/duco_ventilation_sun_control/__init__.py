import asyncio
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
    debug_verbosity = entry.options.get("debug_verbosity", 0)
    _LOGGER.debug(f"Base URL from config entry: {base_url}")
    _LOGGER.debug(f"Debug verbosity: {debug_verbosity}")

    # Map verbosity level to log level string
    log_level_map = {0: "WARNING", 1: "INFO", 2: "DEBUG", 3: "DEBUG"}
    log_level = log_level_map.get(debug_verbosity, "WARNING")

    try:
        # Initialize DucoPy in executor to avoid blocking the event loop
        # The library auto-detects board generation (Connectivity vs Communication/Print)
        def _init_client():
            return DucoPy(base_url=base_url, verify=False, log_level=log_level)
        
        duco_client = await asyncio.get_running_loop().run_in_executor(None, _init_client)
        _LOGGER.info(f"DucoPy initialized with base URL: {base_url}")
        
        # Log detected board information
        if hasattr(duco_client.client, '_board_type') and duco_client.client._board_type:
            _LOGGER.info(f"Detected board type: {duco_client.client._board_type}")
            _LOGGER.info(f"API generation: {duco_client.client._generation}")
        
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
