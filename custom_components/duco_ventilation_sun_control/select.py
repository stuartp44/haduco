from __future__ import annotations

import logging
from typing import Any
from datetime import timedelta
from homeassistant.components.select import SelectEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, SCAN_INTERVAL, MANUFACTURER
from .coordinator import DucoboxCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Ducobox select entities."""
    refresh_time = entry.options.get("refresh_time", SCAN_INTERVAL.total_seconds())

    coordinator = DucoboxCoordinator(hass, update_interval=timedelta(seconds=refresh_time))
    await coordinator.async_config_entry_first_refresh()

    mac_address = coordinator.data.get("General", {}).get("Lan", {}).get("Mac", {}).get("Val")
    if not mac_address:
        _LOGGER.error("No MAC address found; skipping select entities.")
        return

    device_id = mac_address.replace(":", "").lower()
    entities = []

    for node in coordinator.data.get("Nodes", []):
        node_id = node.get("Node")
        node_type = node.get("General", {}).get("Type", {}).get("Val", "Unknown")
        mode = node.get("Ventilation", {}).get("Mode")

        if mode in (None, "-"):
            _LOGGER.info(f"Skipping node {node_id}: no valid ventilation mode")
            continue

        try:
            actions_response = await hass.async_add_executor_job(
                coordinator.client.get_actions_node, node_id
            )
            ventilation_action = next(
                (a for a in actions_response.Actions if a.Action == "SetVentilationState" and hasattr(a, "Enum")),
                None
            )
            if not ventilation_action or not ventilation_action.Enum:
                continue

            mode_options = [opt.strip() for opt in ventilation_action.Enum if isinstance(opt, str)]
            node_device_id = f"{device_id}-{node_id}"

            # Build device_info per node
            device_info = DeviceInfo(
                identifiers={(DOMAIN, node_device_id)},
                name=f"{node_type} Node {node_id}",
                manufacturer=MANUFACTURER,
                model=node_type,
                via_device=(DOMAIN, device_id),
            )

            unique_id = f"{node_device_id}-select-ventilation_mode"
            entities.append(
                DucoboxModeSelect(
                    coordinator=coordinator,
                    device_info=device_info,
                    unique_id=unique_id,
                    node_id=node_id,
                    options=mode_options,
                )
            )

            _LOGGER.debug(f"Added select entity for node {node_id} with options: {mode_options}")

        except Exception as e:
            _LOGGER.warning(f"Failed to retrieve SetVentilationState actions for node {node_id}: {e}")

    if entities:
        async_add_entities(entities, update_before_add=True)


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
        for node in nodes:
            if node.get("Node") == self._node_id:
                ventilation = node.get("Ventilation", {})
                mode = ventilation.get("Mode")

                _LOGGER.debug(
                    f"[SELECT] Node {self._node_id} current mode: {mode} | Allowed options: {self._attr_options}"
                )

                if isinstance(mode, str) and mode in self._attr_options:
                    return mode

                _LOGGER.warning(
                    f"[SELECT] Current mode '{mode}' is not in allowed options for node {self._node_id}"
                )
                return None

        _LOGGER.warning(f"[SELECT] No matching node for ID {self._node_id}")
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
            _LOGGER.debug(f"Mode set successfully for node {self._node_id} to {option}")
            await self.coordinator.async_request_refresh()
        except Exception as e:
            _LOGGER.error(f"Failed to set ventilation mode '{option}' for node {self._node_id}: {e}")