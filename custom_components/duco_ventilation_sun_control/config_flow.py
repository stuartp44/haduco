import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.components.zeroconf import ZeroconfServiceInfo
from homeassistant.data_entry_flow import FlowResult
from homeassistant.core import callback
from ducopy import DucoPy
from .const import DOMAIN
import requests
import asyncio

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema({
    vol.Required("host"): str,
})

class DucoboxConnectivityBoardConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Ducobox Connectivity Board."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step for config flow."""
        errors = {}

        if user_input is not None:
            host = user_input["host"]

            try:
                communication_board_info = await self.get_duco_comm_board_info(host)
                product_entry_info, _ = await self.get_entry_info(communication_board_info)

                # Check if the device has already been configured
                await self.async_set_unique_id(product_entry_info["data"]["unique_id"])
                existing_entry = self.hass.config_entries.async_get_entry(product_entry_info["data"]["unique_id"])
                
                if existing_entry:
                    return self.async_abort(reason="already_configured")
                
                else:
                    return self.async_create_entry(
                        title=product_entry_info["title"],
                        data=product_entry_info["data"],
                    )

            except ValueError:
                errors["host"] = "invalid_url"
            except ConnectionError:
                errors["host"] = "cannot_connect"
            except RuntimeError:
                errors["host"] = "unknown_error"

        return self.async_show_form(
            step_id="user",
            data_schema=CONFIG_SCHEMA,
            errors=errors
        )

    async def async_step_zeroconf(self, discovery_info: ZeroconfServiceInfo) -> FlowResult:
        """Handle discovery via mDNS."""
        _LOGGER.debug(f"Discovery info: {discovery_info}")

        valid_names = ['duco_', 'duco ']

        if not any(discovery_info.name.lower().startswith(x) for x in valid_names):
            return self.async_abort(reason="not_duco_air_device")

        # Extract information from mDNS discovery
        # Use the IP address directly to avoid '.local' issues
        host = discovery_info.addresses[0]
        unique_id = discovery_info.properties.get("MAC").replace(':', '')

        _LOGGER.debug(f"Extracted host: {host}, unique_id: {unique_id}")

        # Check if the device has already been configured
        await self.async_set_unique_id(unique_id)
        existing_entry = self.hass.config_entries.async_get_entry(unique_id)

        if existing_entry:
            # Update the IP address if it has changed
            if existing_entry.data["base_url"] != f"https://{host}":
                self.hass.config_entries.async_update_entry(
                    existing_entry, data={**existing_entry.data, "base_url": f"https://{host}"}
                )
            return self.async_abort(reason="already_configured")

        # Store discovery data in context
        self.context["discovery"] = {
            "host": host,
            "unique_id": unique_id,
        }

        # Ask user for confirmation
        return await self.async_step_confirm()

    async def async_step_confirm(self, user_input=None) -> FlowResult:
        """Ask user to confirm adding the discovered device."""
        discovery = self.context["discovery"]
        _LOGGER.debug(f"Discovery context: {discovery}")
        
        try:
            communication_board_info = await self.get_duco_comm_board_info(discovery["host"])
        except ValueError as ex:
            return self.async_abort(reason=ex)
        product_entry_info,discovery_context = await self.get_entry_info(communication_board_info, discovery_context=True)
        
        self.context["title_placeholders"] = discovery_context
        
        if user_input is not None:
            return self.async_create_entry(
                title=product_entry_info["title"],
                data=product_entry_info["data"],
            )

        self._set_confirm_only()
        # Show confirmation form to the user
        return self.async_show_form(
            step_id="confirm",
            
            description_placeholders={
                "host": discovery["host"],
                "unique_id": discovery["unique_id"],
            },
        )
    
    async def get_entry_info(self, result, discovery_context=None):
        """Renders the product entry information and if required discover context."""
        _LOGGER.debug(f"Result: {result}")
        communication_board_type = result["communication_board_info"].get("General", {}).get("Board", {}).get("CommSubTypeName", {}).get("Val", "")
        _LOGGER.debug(f"Communication board type: {communication_board_type}")
        communication_board_mac = result["communication_board_info"].get("General", {}).get("Lan", {}).get("Mac", {}).get("Val", "").replace(':', '')
        _LOGGER.debug(f"Communication board MAC: {communication_board_mac}")
        communication_board_host = result["communication_board_info"].get("General", {}).get("Lan", {}).get("HostName", {}).get("Val", "")
        _LOGGER.debug(f"Communication board host: {communication_board_host}")
        communication_board_ip = result["communication_board_info"].get("General", {}).get("Lan", {}).get("Ip", {}).get("Val", "")
        _LOGGER.debug(f"Communication board IP: {communication_board_ip}")        
        if communication_board_type == "CONNECTIVITY":
            _LOGGER.debug("Communication board is a Connectivity Board")
            product = {
                "title": f"Connectivity Board ({communication_board_mac})",
                "data": {
                    "base_url": f"https://{communication_board_ip}",
                    "unique_id": communication_board_mac,
                },
            }
            if discovery_context:
                discovery_context = {"name": f"Connectivity Board ({communication_board_mac.replace(':', '')})"}
        
        return product,discovery_context

    async def get_duco_comm_board_info(self, host: str):
                """Attempt to connect to the Duco device and retrieve its information."""
                try:
                    parsed_url = requests.utils.urlparse(host)
                    if not parsed_url.scheme:
                        base_url = f"https://{host}"
                        parsed_url = requests.utils.urlparse(base_url)

                    if parsed_url.scheme != "https":
                        raise ValueError("Invalid URL scheme")

                    duco_client = DucoPy(base_url=base_url, verify=False)
                    _LOGGER.debug(f"DucoPy initialized with base URL: {base_url}")

                    communication_board_info = await asyncio.get_running_loop().run_in_executor(
                        None, duco_client.get_info
                    )
                    _LOGGER.debug(f"Communication board info: {communication_board_info}")
                    duco_client.close()

                    return {"base_url": base_url, "communication_board_info": communication_board_info}

                except ValueError as ex:
                    _LOGGER.error("Invalid URL provided: %s", ex)
                    raise ValueError("invalid_url")
                except requests.exceptions.RequestException as ex:
                    _LOGGER.error("Connection error to Ducobox: %s", ex)
                    raise ConnectionError("cannot_connect")
                except Exception as ex:
                    _LOGGER.error("Unexpected error connecting to Ducobox: %s", ex)
                    raise RuntimeError("unknown_error")
    
    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return DucoboxOptionsFlowHandler(config_entry)


class DucoboxOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Ducobox Connectivity Board."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        return self.async_show_form(step_id="init", data_schema=vol.Schema({}))