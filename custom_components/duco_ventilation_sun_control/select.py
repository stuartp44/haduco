from __future__ import annotations

import logging
from typing import Any
from homeassistant.components.select import SelectEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import DeviceInfo
from .const import DOMAIN
from .coordinator import DucoboxCoordinator

_LOGGER = logging.getLogger(__name__)


class DucoboxModeSelect(CoordinatorEntity[DucoboxCoordinator], SelectEntity):
    """Select entity to change ventilation mode on a DucoBox node."""

    def __init__(
        self,
        coordinator: DucoboxCoordinator,
        device_info: DeviceInfo,
        unique_id: str,
        node_id: int,
        options: list[str],
    ) -> None:
        """Initialize the mode select entity."""
        super().__init__(coordinator)
        self._attr_device_info = device_info
        self._attr_unique_id = unique_id
        self._attr_name = f"{device_info['name']} Ventilation Mode"
        self._attr_options = options
        self._node_id = node_id

    @property
    def current_option(self) -> str | None:
        """Return the currently selected ventilation mode."""
        nodes = self.coordinator.data.get("Nodes", [])
        _LOGGER.debug(f"Current nodes data: {nodes}")
        for node in nodes:
            if node.get("Node") == self._node_id:
                return node.get("Ventilation", {}).get("State", {}).get("Val")
        return None

    async def async_select_option(self, option: str) -> None:
        """Send request to change ventilation mode on the node."""
        _LOGGER.debug(f"Setting ventilation mode for node {self._node_id} to {option}")
        try:
            await self.coordinator.hass.async_add_executor_job(
                self.coordinator.client.change_action_node,
                "SetVentilationState",
                option,
                self._node_id,
            )
            await self.coordinator.async_request_refresh()
        except Exception as e:
            _LOGGER.error(f"Failed to set ventilation mode '{option}' for node {self._node_id}: {e}")