import asyncio
import logging

import requests
import voluptuous as vol
from ducopy import DucoPy
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.service_info.zeroconf import ZeroconfServiceInfo

from .const import DOMAIN, SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema(
    {
        vol.Required("host"): str,
    }
)

OPTIONS_SCHEMA = vol.Schema(
    {
        vol.Required("refresh_time", default=SCAN_INTERVAL.total_seconds()): vol.All(
            vol.Coerce(int), vol.Range(min=10, max=3600)
        ),
        vol.Optional("debug_verbosity", default=0): vol.All(vol.Coerce(int), vol.Range(min=0, max=3)),
    }
)


class DucoboxConnectivityBoardConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Ducobox Connectivity Board."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, str] | None = None) -> FlowResult:
        """Handle the initial step."""
        if user_input is not None:
            return await self._handle_user_input(user_input)
        return self._show_user_form()

    async def async_step_zeroconf(self, discovery_info: ZeroconfServiceInfo) -> FlowResult:
        """Handle mDNS discovery."""
        _LOGGER.debug(
            "Zeroconf discovery triggered! Service: %s, Name: %s, Type: %s",
            discovery_info,
            discovery_info.name,
            discovery_info.type,
        )
        if not self._is_valid_discovery(discovery_info):
            _LOGGER.debug("Discovery rejected - device name '%s' doesn't match required pattern", discovery_info.name)
            return self.async_abort(reason="not_duco_air_device")

        host, unique_id, scheme = self._extract_discovery_info(discovery_info)
        await self.async_set_unique_id(unique_id)

        if self._is_existing_entry(unique_id, host, scheme):
            return self.async_abort(reason="already_configured")

        self.context["discovery"] = {"host": host, "unique_id": unique_id, "scheme": scheme}
        return await self.async_step_confirm()

    async def async_step_confirm(self, user_input: dict[str, str] | None = None) -> FlowResult:
        """Ask user to confirm adding the discovered device."""
        discovery = self.context.get("discovery", {})
        host = discovery.get("host", "unknown")
        unique_id = discovery.get("unique_id", "unknown")
        board_type = "Connectivity Board"

        if user_input is not None:
            return await self._create_entry_from_discovery(discovery)

        try:
            comm_info = await self._get_duco_comm_board_info(host)
            board_type = (
                comm_info["communication_board_info"]
                .get("General", {})
                .get("Board", {})
                .get("CommSubTypeName", {})
                .get("Val", board_type)
                .capitalize()
            )
            unique_id = (
                comm_info["communication_board_info"]
                .get("General", {})
                .get("Lan", {})
                .get("Mac", {})
                .get("Val", "")
                .replace(":", "")
                or unique_id
            )
        except Exception as e:
            _LOGGER.warning("Failed to fetch board info for confirm step: %s", e)

        _LOGGER.debug("Setting title_placeholders: board_type=%s, unique_id=%s", board_type, unique_id)
        _LOGGER.debug("Setting description_placeholders: host=%s, unique_id=%s", host, unique_id)

        self.context["title_placeholders"] = {
            "board_type": board_type,
            "unique_id": unique_id,
        }

        return self.async_show_form(
            step_id="confirm",
            description_placeholders={"host": host, "unique_id": unique_id, "board_type": board_type},
        )

    async def _handle_user_input(self, user_input: dict) -> FlowResult:
        """Handle manual input."""
        host = user_input["host"]
        try:
            comm_info = await self._get_duco_comm_board_info(host)
            product_entry_info, _ = await self._get_entry_info(comm_info)
            unique_id = product_entry_info["data"]["unique_id"]
            board_type = product_entry_info["data"].get("board_type", "Duco")

            await self.async_set_unique_id(unique_id)
            if self._is_existing_entry(unique_id):
                return self.async_abort(reason="already_configured")

            self.context["title_placeholders"] = {
                "board_type": board_type,
                "unique_id": unique_id,
            }

            return self.async_create_entry(
                data=product_entry_info["data"],  # No title
            )

        except ValueError:
            return self._show_user_form(errors={"host": "invalid_url"})
        except ConnectionError:
            return self._show_user_form(errors={"host": "cannot_connect"})
        except RuntimeError:
            return self._show_user_form(errors={"host": "unknown_error"})

    def _show_user_form(self, errors: dict[str, str] | None = None) -> FlowResult:
        return self.async_show_form(
            step_id="user",
            data_schema=CONFIG_SCHEMA,
            errors=errors or {},
        )

    def _is_valid_discovery(self, discovery_info: ZeroconfServiceInfo) -> bool:
        valid_names = ["duco_", "duco "]
        return any(discovery_info.name.lower().startswith(x) for x in valid_names)

    def _extract_discovery_info(self, discovery_info: ZeroconfServiceInfo) -> tuple[str, str, str]:
        host = discovery_info.addresses[0]
        unique_id = (discovery_info.properties.get("MAC") or "").replace(":", "")
        # Determine scheme from service type
        scheme = "https" if "_https._tcp" in discovery_info.type else "http"
        return host, unique_id, scheme

    def _is_existing_entry(self, unique_id: str, host: str | None = None, scheme: str = "http") -> bool:
        for entry in self.hass.config_entries.async_entries(DOMAIN):
            if entry.unique_id == unique_id:
                if host and entry.data.get("base_url") != f"{scheme}://{host}":
                    self.hass.config_entries.async_update_entry(
                        entry, data={**entry.data, "base_url": f"{scheme}://{host}"}
                    )
                return True
        return False

    async def _create_entry_from_discovery(self, discovery: dict) -> FlowResult:
        """Create a config entry from discovery data."""
        scheme = discovery.get("scheme", "http")
        base_url = f"{scheme}://{discovery['host']}"
        comm_info = await self._get_duco_comm_board_info(base_url)
        product_entry_info, _ = await self._get_entry_info(comm_info, scheme)

        # Set placeholders for flow_title
        board_type = product_entry_info["data"].get("board_type", "Duco")
        unique_id = product_entry_info["data"]["unique_id"]

        self.context["title_placeholders"] = {
            "board_type": board_type,
            "unique_id": unique_id,
        }

        return self.async_create_entry(
            title="",
            data=product_entry_info["data"],  # No title provided
        )

    def _show_confirm_form(self, discovery: dict) -> FlowResult:
        self._set_confirm_only()
        return self.async_show_form(
            step_id="confirm",
            description_placeholders={
                "host": discovery["host"],
                "unique_id": discovery["unique_id"],
            },
        )

    async def _get_entry_info(
        self, result: dict, scheme: str = "http", discovery_context: dict | None = None
    ) -> tuple[dict[str, str | dict], dict | None]:
        info = result["communication_board_info"]
        mac = info.get("General", {}).get("Lan", {}).get("Mac", {}).get("Val", "").replace(":", "")
        ip = info.get("General", {}).get("Lan", {}).get("Ip", {}).get("Val", "")
        board_type = (
            info.get("General", {}).get("Board", {}).get("CommSubTypeName", {}).get("Val", "Connectivity Board")
        )

        return {
            "title": f"{board_type} ({mac})",  # only used if flow_title not applied
            "data": {
                "base_url": f"{scheme}://{ip}",
                "unique_id": mac,
                "board_type": board_type,  # ← ensure this is present
            },
        }, {"name": f"{board_type} ({mac})"} if discovery_context else None

    async def _get_duco_comm_board_info(self, url: str) -> dict:
        try:
            base_url = self._format_base_url(url)

            def _get_info():
                # Use WARNING level for config flow to avoid cluttering logs during setup
                client = DucoPy(base_url=base_url, verify=False, log_level="WARNING")
                try:
                    return client.get_info()
                finally:
                    client.close()

            info = await asyncio.get_running_loop().run_in_executor(None, _get_info)
            return {"base_url": base_url, "communication_board_info": info}
        except ValueError as err:
            raise ValueError("invalid_url") from err
        except requests.exceptions.RequestException as err:
            raise ConnectionError("cannot_connect") from err
        except Exception as err:
            raise RuntimeError("unknown_error") from err

    def _format_base_url(self, host: str) -> str:
        parsed_url = requests.utils.urlparse(host)
        if not parsed_url.scheme:
            return f"http://{host}"
        if parsed_url.scheme not in ("http", "https"):
            raise ValueError("Invalid URL scheme")
        return host

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> "DucoboxOptionsFlowHandler":
        return DucoboxOptionsFlowHandler(config_entry)


class DucoboxOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, int] | None = None) -> FlowResult:
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=OPTIONS_SCHEMA,
        )
