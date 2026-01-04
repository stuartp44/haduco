import asyncio
import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class DucoboxCoordinator(DataUpdateCoordinator):
    """Coordinator to manage data updates for Ducobox sensors."""

    def __init__(self, hass: HomeAssistant, update_interval: timedelta):
        super().__init__(
            hass,
            _LOGGER,
            name="Ducobox Connectivity Board",
            update_interval=update_interval,
        )
        self._last_successful_data = {}

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
        duco_client = self.hass.data[DOMAIN]
        data = duco_client.get_info()
        _LOGGER.debug(f"Data received from /info: {data}")

        nodes_response = duco_client.get_nodes()
        _LOGGER.debug(f"Data received from /nodes: {nodes_response}")

        # Convert nodes_response.Nodes (which is a list of NodeInfo objects) to list of dicts
        data["Nodes"] = [node.dict() for node in nodes_response.Nodes]
        _LOGGER.debug(f"Data after processing nodes: {data}")
        return data

    @property
    def client(self) -> object:
        return self.hass.data[DOMAIN]
