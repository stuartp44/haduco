from homeassistant.components.select import SelectEntity
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN
from .coordinator import DucoboxCoordinator  # Ensure this is the correct module where DucoboxCoordinator is defined
import logging

_LOGGER = logging.getLogger(__name__)

class DucoboxModeSelect(CoordinatorEntity[DucoboxCoordinator], SelectEntity):
    def __init__(
        self,
        coordinator: DucoboxCoordinator,
        device_info: DeviceInfo,
        unique_id: str,
        node_id: int,
        options: list[str],
    ) -> None:
        super().__init__(coordinator)
        self._attr_device_info = device_info
        self._attr_unique_id = unique_id
        self._node_id = node_id
        self._attr_name = "Ducobox Mode"
        self._attr_options = options
        self._current_mode = self._get_mode_from_data()

    def _get_mode_from_data(self) -> str:
        nodes = self.coordinator.data.get("Nodes", [])
        for node in nodes:
            if node.get("Node") == self._node_id:
                return node.get("Mode", {}).get("Val", "Unknown")
        return "Unknown"

    @property
    def current_option(self) -> str:
        return self._get_mode_from_data()

    async def async_select_option(self, option: str) -> None:
        """Change the ventilation mode on the DucoBox node."""
        try:
            # Use the Duco client from the coordinator
            duco_client = self.coordinator.client
            await self.coordinator.hass.async_add_executor_job(
                duco_client.change_action_node, "Mode", option, self._node_id
            )
            await self.coordinator.async_request_refresh()
        except Exception as e:
            _LOGGER.error(f"Failed to set mode '{option}' for node {self._node_id}: {e}")