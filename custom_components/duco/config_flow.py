"""Config flow for Duco integration."""

from homeassistant import config_entries
from homeassistant.components import zeroconf
from homeassistant.core import callback
from .const import DOMAIN
import logging

_LOGGER = logging.getLogger(__name__)


class DucoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Duco."""

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return DucoOptionsFlowHandler(config_entry)

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        return self.async_show_form(step_id="user")

    async def async_step_zeroconf(self, discovery_info):
        """Handle a flow initiated by zeroconf discovery."""
        # Extract details from discovery_info
        _LOGGER.debug("Zeroconf discovery: %s", discovery_info)
        name = discovery_info.get("name")
        address = discovery_info.get("host")
        port = discovery_info.get("port")
        unique_id = discovery_info.get("properties", {}).get("id", name)

        await self.async_set_unique_id(unique_id)
        self._abort_if_unique_id_configured()

        # Store the device info in the config entry
        return self.async_create_entry(
            title=f"Duco Device {name}",
            data={
                "host": address,
                "port": port,
                "name": name,
                "unique_id": unique_id,
            },
        )


class DucoOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle an options flow for Duco."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        return self.async_show_form(step_id="init")
