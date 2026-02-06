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


def _detect_board_type_from_info(info: dict) -> str:
    """Detect the board type from a communication board info payload."""
    board = info.get("General", {}).get("Board", {})

    comm_subtype = board.get("CommSubTypeName", {}).get("Val", "")
    if comm_subtype:
        comm_subtype_lower = str(comm_subtype).lower()
        if "connectivity" in comm_subtype_lower:
            return "Connectivity Board"
        if "communication" in comm_subtype_lower or "print" in comm_subtype_lower:
            return "Communication and Print Board"
        return f"{comm_subtype} Board"

    board_name = (
        board.get("Type", {}).get("Val")
        or board.get("Name", {}).get("Val")
        or board.get("BoardType", {}).get("Val")
        or board.get("BoardTypeName", {}).get("Val")
    )
    if isinstance(board_name, str) and board_name:
        board_name_lower = board_name.lower()
        if "connectivity" in board_name_lower:
            return "Connectivity Board"
        if "communication" in board_name_lower or "print" in board_name_lower:
            return "Communication and Print Board"

    api_version = board.get("PublicApiVersion", {}).get("Val") or board.get(
        "ApiVersion", {}
    ).get("Val")
    try:
        return (
            "Connectivity Board"
            if float(api_version) >= 2.0
            else "Communication and Print Board"
        )
    except (TypeError, ValueError):
        return "DUCO Board"


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
    }
)


class DucoboxConnectivityBoardConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Ducobox Connectivity Board."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, str] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is not None:
            return await self._handle_user_input(user_input)
        return self._show_user_form()

    async def async_step_zeroconf(
        self, discovery_info: ZeroconfServiceInfo
    ) -> FlowResult:
        """Handle mDNS discovery."""
        _LOGGER.debug(
            "Zeroconf discovery triggered! Service: %s, Name: %s, Type: %s",
            discovery_info,
            discovery_info.name,
            discovery_info.type,
        )
        if not self._is_valid_discovery(discovery_info):
            _LOGGER.debug(
                "Discovery rejected - device name '%s' doesn't match required pattern",
                discovery_info.name,
            )
            return self.async_abort(reason="not_duco_air_device")

        _LOGGER.debug("Discovery validated successfully")
        host, unique_id, scheme = self._extract_discovery_info(discovery_info)
        _LOGGER.debug(
            "Extracted: host=%s, unique_id=%s, scheme=%s", host, unique_id, scheme
        )

        # For Connectivity Boards, prefer HTTPS over HTTP
        # Check ApiVersion to determine if it's a modern board
        api_version = discovery_info.properties.get("ApiVersion", "")
        is_modern_board = api_version and float(api_version) >= 2.0

        if scheme == "http" and is_modern_board:
            _LOGGER.debug(
                "Modern board (ApiVersion %s) detected via HTTP, aborting to allow HTTPS discovery",
                api_version,
            )
            return self.async_abort(reason="prefer_https")

        await self.async_set_unique_id(unique_id)
        _LOGGER.debug("Unique ID set: %s", unique_id)

        # Check if device already exists and update IP if changed
        existing_entry = await self._update_ip_if_changed(unique_id, host, scheme)
        if existing_entry:
            return self.async_abort(reason="already_configured")

        # If HTTP discovery but device already exists with HTTPS, prefer HTTPS
        if scheme == "http" and self._is_existing_entry(unique_id, host, "https"):
            _LOGGER.debug(
                "Device already configured with HTTPS, preferring that over HTTP"
            )
            return self.async_abort(reason="already_configured")

        if self._is_existing_entry(unique_id, host, scheme):
            _LOGGER.debug("Device already configured, aborting")
            return self.async_abort(reason="already_configured")

        _LOGGER.debug("Proceeding to confirmation step")
        self.context["discovery"] = {
            "host": host,
            "unique_id": unique_id,
            "scheme": scheme,
        }
        return await self.async_step_confirm()

    async def async_step_confirm(
        self, user_input: dict[str, str] | None = None
    ) -> FlowResult:
        """Ask user to confirm adding the discovered device."""
        discovery = self.context.get("discovery", {})
        host = discovery.get("host", "unknown")
        scheme = discovery.get("scheme", "http")
        unique_id = discovery.get("unique_id", "unknown")
        board_type = "DUCO Board"  # Generic fallback

        if user_input is not None:
            return await self._create_entry_from_discovery(discovery)

        try:
            base_url = f"{scheme}://{host}"
            comm_info = await self._get_duco_comm_board_info(base_url)
            board_type = _detect_board_type_from_info(
                comm_info["communication_board_info"]
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
            # Store detected board_type in discovery context
            self.context["discovery"]["board_type"] = board_type
        except Exception as e:
            _LOGGER.warning("Failed to fetch board info for confirm step: %s", e)

        _LOGGER.debug(
            "Setting title_placeholders: board_type=%s, unique_id=%s",
            board_type,
            unique_id,
        )
        _LOGGER.debug(
            "Setting description_placeholders: host=%s, unique_id=%s", host, unique_id
        )

        self.context["title_placeholders"] = {
            "board_type": board_type,
            "unique_id": unique_id,
        }

        return self.async_show_form(
            step_id="confirm",
            description_placeholders={
                "host": host,
                "unique_id": unique_id,
                "board_type": board_type,
            },
        )

    async def _handle_user_input(self, user_input: dict) -> FlowResult:
        """Handle manual input."""
        host = user_input["host"]
        try:
            comm_info, scheme, host_value = await self._get_comm_board_info_with_scheme(
                host
            )
            # Extract MAC from the communication board info
            info = comm_info["communication_board_info"]
            mac = info.get("General", {}).get("Lan", {}).get("Mac", {}).get("Val", "")
            if mac:
                unique_id = mac.replace(":", "").lower()
            else:
                raise ValueError("Could not extract MAC address from device")

            product_entry_info, _ = await self._get_entry_info(
                comm_info, host_value, unique_id, scheme
            )
            board_type = product_entry_info["data"].get("board_type", "Duco")

            await self.async_set_unique_id(unique_id)
            if self._is_existing_entry(unique_id):
                return self.async_abort(reason="already_configured")

            self.context["title_placeholders"] = {
                "board_type": board_type,
                "unique_id": unique_id,
            }

            return self.async_create_entry(
                title="",
                data=product_entry_info["data"],
            )

        except ValueError:
            return self._show_user_form(errors={"host": "invalid_url"})
        except ConnectionError:
            return self._show_user_form(errors={"host": "cannot_connect"})
        except RuntimeError:
            return self._show_user_form(errors={"host": "unknown_error"})

    async def _get_comm_board_info_with_scheme(
        self, host: str
    ) -> tuple[dict, str, str]:
        """Get communication board info and determine the best scheme to use."""
        parsed_url = requests.utils.urlparse(host)

        if parsed_url.scheme:
            if parsed_url.scheme not in ("http", "https"):
                raise ValueError("Invalid URL scheme")
            host_value = parsed_url.netloc or parsed_url.path
            comm_info = await self._get_duco_comm_board_info(host)

            if parsed_url.scheme == "http" and self._is_connectivity_board(
                comm_info["communication_board_info"]
            ):
                try:
                    https_info = await self._get_duco_comm_board_info(
                        f"https://{host_value}"
                    )
                    return https_info, "https", host_value
                except Exception:
                    return comm_info, "http", host_value

            return comm_info, parsed_url.scheme, host_value

        host_value = host
        try:
            comm_info = await self._get_duco_comm_board_info(f"https://{host_value}")
            return comm_info, "https", host_value
        except Exception:
            comm_info = await self._get_duco_comm_board_info(f"http://{host_value}")
            if self._is_connectivity_board(comm_info["communication_board_info"]):
                try:
                    https_info = await self._get_duco_comm_board_info(
                        f"https://{host_value}"
                    )
                    return https_info, "https", host_value
                except Exception:
                    return comm_info, "http", host_value
            return comm_info, "http", host_value

    def _is_connectivity_board(self, info: dict) -> bool:
        """Detect connectivity boards to ensure HTTPS is used when required."""
        return _detect_board_type_from_info(info) == "Connectivity Board"

    def _show_user_form(self, errors: dict[str, str] | None = None) -> FlowResult:
        return self.async_show_form(
            step_id="user",
            data_schema=CONFIG_SCHEMA,
            errors=errors or {},
        )

    def _is_valid_discovery(self, discovery_info: ZeroconfServiceInfo) -> bool:
        return discovery_info.name.lower().startswith("duco")

    def _extract_discovery_info(
        self, discovery_info: ZeroconfServiceInfo
    ) -> tuple[str, str, str]:
        host = discovery_info.addresses[0]
        unique_id = (discovery_info.properties.get("MAC") or "").replace(":", "")
        # Determine scheme from service type
        scheme = "https" if "_https._tcp" in discovery_info.type else "http"
        return host, unique_id, scheme

    async def _update_ip_if_changed(
        self, unique_id: str, new_host: str, scheme: str
    ) -> bool:
        """Check if device exists and update IP if changed. Returns True if device exists."""
        entries = self.hass.config_entries.async_entries(DOMAIN)
        for entry in entries:
            if entry.unique_id == unique_id:
                current_base_url = entry.data.get("base_url")
                new_base_url = f"{scheme}://{new_host}"

                if current_base_url != new_base_url:
                    _LOGGER.info(
                        "Device %s IP changed from %s to %s, updating configuration",
                        unique_id,
                        current_base_url,
                        new_base_url,
                    )
                    self.hass.config_entries.async_update_entry(
                        entry, data={**entry.data, "base_url": new_base_url}
                    )
                    # Reload the entry to apply the new IP
                    await self.hass.config_entries.async_reload(entry.entry_id)
                return True
        return False

    def _is_existing_entry(
        self, unique_id: str, host: str | None = None, scheme: str = "http"
    ) -> bool:
        entries = self.hass.config_entries.async_entries(DOMAIN)
        _LOGGER.debug(
            "Checking if device exists. unique_id=%s, entries=%s",
            unique_id,
            len(entries),
        )
        for entry in entries:
            _LOGGER.debug(
                "Comparing with entry: unique_id=%s, base_url=%s",
                entry.unique_id,
                entry.data.get("base_url"),
            )
            if entry.unique_id == unique_id:
                return True
        return False

    async def _create_entry_from_discovery(self, discovery: dict) -> FlowResult:
        """Create a config entry from discovery data."""
        scheme = discovery.get("scheme", "http")
        host = discovery["host"]
        unique_id = discovery["unique_id"]  # Use MAC from discovery
        board_type = discovery.get("board_type")  # Use detected board type if available
        base_url = f"{scheme}://{host}"
        comm_info = await self._get_duco_comm_board_info(base_url)
        product_entry_info, _ = await self._get_entry_info(
            comm_info, host, unique_id, scheme, board_type
        )

        # Set placeholders for flow_title
        board_type = product_entry_info["data"].get("board_type", "Duco")

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
        self,
        result: dict,
        host: str,
        unique_id: str,
        scheme: str = "http",
        board_type: str | None = None,
        discovery_context: dict | None = None,
    ) -> tuple[dict[str, str | dict], dict | None]:
        info = result["communication_board_info"]
        # Use provided unique_id instead of trying to extract from API
        # (Communication/Print board doesn't return MAC in /info endpoint)
        mac = unique_id
        # Use provided board_type if available, otherwise try to detect from API
        if not board_type:
            board_type = _detect_board_type_from_info(info)

        return {
            "title": f"{board_type} ({mac})",  # only used if flow_title not applied
            "data": {
                "base_url": f"{scheme}://{host}",
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
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> "DucoboxOptionsFlowHandler":
        return DucoboxOptionsFlowHandler()


class DucoboxOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow."""

    async def async_step_init(
        self, user_input: dict[str, int] | None = None
    ) -> FlowResult:
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        # Get current refresh time or use default
        current_refresh_time = self.config_entry.options.get(
            "refresh_time", SCAN_INTERVAL.total_seconds()
        )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required("refresh_time", default=current_refresh_time): vol.All(
                        vol.Coerce(int), vol.Range(min=10, max=3600)
                    ),
                }
            ),
        )
