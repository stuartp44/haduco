"""The Duco integration."""

"""The Duco integration."""
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from .const import DOMAIN


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Duco component."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry) -> bool:
    """Set up Duco from a config entry."""
    return True


async def async_unload_entry(hass: HomeAssistant, entry) -> bool:
    """Unload a Duco config entry."""
    return True
