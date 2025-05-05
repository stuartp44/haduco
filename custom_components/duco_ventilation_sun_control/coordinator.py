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


    async def _async_update_data(self):
        """Fetch and enrich data from the DucoBox."""
        data = await self.hass.async_add_executor_job(self.client.get_info)

        # Enrich node data with detailed info
        nodes = data.get("Nodes", [])
        enriched_nodes = []
        for node in nodes:
            node_id = node.get("Node")
            if node_id is None:
                continue

            try:
                detailed_info = await self.hass.async_add_executor_job(
                    self.client.get_node_info, node_id
                )
                # Merge or replace node data with detailed info
                if isinstance(detailed_info, dict):
                    node.update(detailed_info)
            except Exception as e:
                _LOGGER.warning(f"Failed to enrich node {node_id} with get_node_info: {e}")

            enriched_nodes.append(node)

        data["Nodes"] = enriched_nodes
        return data

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