"""Config flow for Duco integration."""
from homeassistant import config_entries
from homeassistant.components import zeroconf
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from .const import DOMAIN
from duco import DucoDevice


class DucoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Duco."""

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return DucoOptionsFlowHandler(config_entry)

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle the initial step."""
        return self.async_show_form(step_id="user")

    async def async_step_zeroconf(self, discovery_info: zeroconf.ZeroconfServiceInfo) -> FlowResult:
        """Handle a flow initiated by zeroconf discovery."""
        # Access the attributes directly
        name = discovery_info.name
        host = discovery_info.host
        port = discovery_info.port
        properties = discovery_info.properties
        duco_device = DucoDevice(host, port)
        
        # Filter only devices with "DUCO" in the name
        if "DUCO" not in name:
            return self.async_abort(reason="not_duco_device")

        try:
            mac_address = name.split('[')[1].split(']')[0]
        except IndexError:
            return self.async_abort(reason="invalid_name_format")
        
        # Extract a unique ID from the properties or use the MAC address
        unique_id = properties.get("id", mac_address)
        board_data = await hass.async_add_executor_job(duco_device.get_cap_board_info())

        # Set the unique ID and check if already configured
        await self.async_set_unique_id(unique_id)
        self._abort_if_unique_id_configured()

        # Store the device info in the config entry
        return self.async_create_entry(
            title=f"Duco Communication and Print Board - {board_data['serial']}",
            data={
                "host": host,
                "port": port,
                "name": name,
                "unique_id": f"{board_data['mac']}",
            },
            options = {
                "serial": board_data['serial'],
                "version": board_data['swversion'],
            }
        )

class DucoOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle an options flow for Duco."""
    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None) -> FlowResult:
        """Manage the options."""
        return self.async_show_form(step_id="init")