import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.service_info.zeroconf import ZeroconfServiceInfo
from homeassistant.data_entry_flow import FlowResult
from homeassistant.core import callback
from ducopy import DucoPy
from .const import DOMAIN, SCAN_INTERVAL
import requests
import asyncio

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema({
    vol.Required("host"): str,
})

OPTIONS_SCHEMA = vol.Schema({
    vol.Required("Refresh Time", default=SCAN_INTERVAL.total_seconds()): vol.All(
        vol.Coerce(int), vol.Range(min=10, max=3600)
    ),
})

class DucoboxConnectivityBoardConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Ducobox Connectivity Board."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step for config flow."""
        if user_input is not None:
            return await self._handle_user_input(user_input)

        return self._show_user_form()

    async def async_step_zeroconf(self, discovery_info: ZeroconfServiceInfo) -> FlowResult:
        """Handle discovery via mDNS."""
        if not self._is_valid_discovery(discovery_info):
            return self.async_abort(reason="not_duco_air_device")

        host, unique_id = self._extract_discovery_info(discovery_info)
        await self.async_set_unique_id(unique_id)

        if self._is_existing_entry(unique_id, host):
            return self.async_abort(reason="already_configured")

        self.context["discovery"] = {"host": host, "unique_id": unique_id}
        return await self.async_step_confirm()

    async def async_step_confirm(self, user_input=None) -> FlowResult:
        """Ask user to confirm adding the discovered device."""
        discovery = self.context["discovery"]

        if user_input is not None:
            return await self._create_entry_from_discovery(discovery)

        # Fetch board info to customize the title
        try:
            comm_info = await self._get_duco_comm_board_info(discovery["host"])
            board_type = comm_info["communication_board_info"].get("General", {}).get("Board", {}).get("CommSubTypeName", {}).get("Val", "Board").capitalize()
            mac_address = comm_info["communication_board_info"].get("General", {}).get("Lan", {}).get("Mac", {}).get("Val", "").replace(':', '')
            self.context["title_placeholders"] = {
                "board_type": board_type,
                "unique_id": mac_address,
                }
        except Exception:
            self.context["title_placeholders"] = {"board_type": "Connectivity Board"}

        return self._show_confirm_form(discovery)

    async def _handle_user_input(self, user_input: dict) -> FlowResult:
        """Handle user input for manual configuration."""
        host = user_input["host"]
        try:
            communication_board_info = await self._get_duco_comm_board_info(host)
            product_entry_info, _ = await self._get_entry_info(communication_board_info)
            unique_id = product_entry_info["data"]["unique_id"]

            await self.async_set_unique_id(unique_id)
            if self._is_existing_entry(unique_id):
                return self.async_abort(reason="already_configured")

            return self.async_create_entry(
                title=product_entry_info["title"],
                data=product_entry_info["data"],
            )
        except ValueError:
            return self._show_user_form(errors={"host": "invalid_url"})
        except ConnectionError:
            return self._show_user_form(errors={"host": "cannot_connect"})
        except RuntimeError:
            return self._show_user_form(errors={"host": "unknown_error"})

    def _show_user_form(self, errors=None) -> FlowResult:
        """Show the user form for manual configuration."""
        return self.async_show_form(
            step_id="user",
            data_schema=CONFIG_SCHEMA,
            errors=errors or {},
        )

    def _is_valid_discovery(self, discovery_info: ZeroconfServiceInfo) -> bool:
        """Check if the discovery info is valid for a Duco device."""
        valid_names = ['duco_', 'duco ']
        return any(discovery_info.name.lower().startswith(x) for x in valid_names)

    def _extract_discovery_info(self, discovery_info: ZeroconfServiceInfo) -> tuple[str, str]:
        """Extract host and unique ID from discovery info."""
        host = discovery_info.addresses[0]
        unique_id = discovery_info.properties.get("MAC").replace(':', '')
        return host, unique_id

    def _is_existing_entry(self, unique_id: str, host: str = None) -> bool:
        """Check if an entry with the given unique ID already exists."""
        for entry in self.hass.config_entries.async_entries(DOMAIN):
            if entry.unique_id == unique_id:
                if host and entry.data["base_url"] != f"https://{host}":
                    self.hass.config_entries.async_update_entry(
                        entry, data={**entry.data, "base_url": f"https://{host}"}
                    )
                return True
        return False

    async def _create_entry_from_discovery(self, discovery: dict) -> FlowResult:
        """Create a config entry from discovery data."""
        communication_board_info = await self._get_duco_comm_board_info(discovery["host"])
        product_entry_info, _ = await self._get_entry_info(communication_board_info)
        return self.async_create_entry(
            title=product_entry_info["title"],
            data=product_entry_info["data"],
        )

    def _show_confirm_form(self, discovery: dict) -> FlowResult:
        """Show the confirmation form for discovered devices."""
        self._set_confirm_only()
        return self.async_show_form(
            step_id="confirm",
            description_placeholders={
                "host": discovery["host"],
                "unique_id": discovery["unique_id"],
            },
        )

    async def _get_entry_info(self, result: dict, discovery_context=None) -> tuple[dict, dict]:
        """Render the product entry information."""
        communication_board_info = result["communication_board_info"]
        mac = communication_board_info.get("General", {}).get("Lan", {}).get("Mac", {}).get("Val", "").replace(':', '')
        ip = communication_board_info.get("General", {}).get("Lan", {}).get("Ip", {}).get("Val", "")
        board_type = communication_board_info.get("General", {}).get("Board", {}).get("CommSubTypeName", {}).get("Val", "Connectivity Board")

        product = {
            "title": f"{board_type} ({mac})",
            "data": {
                "base_url": f"https://{ip}",
                "unique_id": mac,
            },
        }
        discovery_context = {"name": f"{board_type} ({mac})"} if discovery_context else None
        return product, discovery_context

    async def _get_duco_comm_board_info(self, host: str) -> dict:
        """Retrieve information from the Duco device."""
        try:
            base_url = self._format_base_url(host)
            duco_client = DucoPy(base_url=base_url, verify=False)
            communication_board_info = await asyncio.get_running_loop().run_in_executor(
                None, duco_client.get_info
            )
            duco_client.close()
            return {"base_url": base_url, "communication_board_info": communication_board_info}
        except ValueError:
            raise ValueError("invalid_url")
        except requests.exceptions.RequestException:
            raise ConnectionError("cannot_connect")
        except Exception:
            raise RuntimeError("unknown_error")

    def _format_base_url(self, host: str) -> str:
        """Format the base URL for the Duco device."""
        parsed_url = requests.utils.urlparse(host)
        if not parsed_url.scheme:
            return f"https://{host}"
        if parsed_url.scheme != "https":
            raise ValueError("Invalid URL scheme")
        return host

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
        
        current_refresh_time = self.config_entry.options.get("refresh_time", SCAN_INTERVAL.total_seconds())
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required("refresh_time", default=current_refresh_time): vol.All(
                    vol.Coerce(int), vol.Range(min=10, max=3600)
                ),
            }),
        )
