from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.core import HomeAssistant
from datetime import timedelta
import asyncio
import logging
from retrying import retry
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

    async def _async_update_data(self) -> dict:
        """Fetch data from the Ducobox API with a timeout."""
        try:
            return await asyncio.wait_for(
                self.hass.async_add_executor_job(self._fetch_data),
                timeout=30
            )
        except asyncio.TimeoutError:
            _LOGGER.error("Timeout occurred while fetching data from Ducobox API")
            return {}
        except Exception as e:
            _LOGGER.error("Failed to fetch data from Ducobox API: %s", e)
            return {}

    @retry(wait_exponential_multiplier=1000, wait_exponential_max=10000)
    def _fetch_data(self) -> dict:
        """Fetch data from the Duco API."""
        duco_client = self.hass.data[DOMAIN]
        data = duco_client.get_info()
        _LOGGER.debug(f"Data received from /info: {data}")

        nodes_response = duco_client.get_nodes()
        _LOGGER.debug(f"Data received from /nodes: {nodes_response}")

        # Convert nodes_response.Nodes (which is a list of NodeInfo objects) to list of dicts
        data['Nodes'] = [node.dict() for node in nodes_response.Nodes]
        return data

    @property
    def client(self):
        return self.hass.data[DOMAIN]