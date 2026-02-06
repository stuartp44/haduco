import asyncio
import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


class DucoboxCoordinator(DataUpdateCoordinator):
    """Coordinator to manage data updates for Ducobox sensors."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: object,
        update_interval: timedelta,
        config_entry: ConfigEntry,
    ):
        super().__init__(
            hass,
            _LOGGER,
            name="Ducobox Connectivity Board",
            update_interval=update_interval,
            config_entry=config_entry,
        )
        self._last_successful_data: dict[str, Any] = {}
        self._client = client

    async def _async_update_data(self) -> dict:
        """Fetch data from the Ducobox API with a timeout."""
        try:
            data = await asyncio.wait_for(self.hass.async_add_executor_job(self._fetch_data), timeout=30)
            self._last_successful_data = data
            return data
        except TimeoutError:
            _LOGGER.warning("Timeout occurred while fetching data from Ducobox API, using last known data")
            return self._last_successful_data
        except Exception as e:
            _LOGGER.warning("Failed to fetch data from Ducobox API: %s, using last known data", e)
            return self._last_successful_data

    def _fetch_data(self) -> dict[str, list]:
        """Fetch data from the Duco API."""
        data = self._client.get_info()
        _LOGGER.debug(f"Data received from /info: {data}")

        nodes_response = self._client.get_nodes()
        _LOGGER.debug(f"Data received from /nodes: {nodes_response}")

        # Get board info (contains serial, sw version, uptime for Communication/Print boards)
        try:
            board_info = self._client.get_board_info()
            data["BoardInfo"] = board_info
            _LOGGER.debug(f"Data received from board_info: {board_info}")
        except Exception as e:
            _LOGGER.debug(f"Failed to fetch board_info (may not be available on this board type): {e}")

        # Convert nodes_response.Nodes (which is a list of NodeInfo objects) to list of dicts
        data["Nodes"] = [node.dict() for node in nodes_response.Nodes]
        _LOGGER.debug(f"Data after processing nodes: {data}")
        return data

    @property
    def client(self) -> object:
        return self._client
