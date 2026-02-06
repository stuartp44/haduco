from __future__ import annotations

import asyncio
import logging
from datetime import timedelta

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, SCAN_INTERVAL
from .coordinator import DucoboxCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Ducobox select entities from a config entry."""
    refresh_time = entry.options.get("refresh_time", SCAN_INTERVAL.total_seconds())

    coordinator = DucoboxCoordinator(
        hass,
        entry.runtime_data,
        update_interval=timedelta(seconds=refresh_time),
        config_entry=entry,
    )
    await coordinator.async_config_entry_first_refresh()

    # Try to get MAC from coordinator data (library should normalize this)
    # Fall back to config entry for backward compatibility
    mac_address = get_mac_from_coordinator(coordinator) or entry.data.get("unique_id")
    if not mac_address:
        _LOGGER.error("No MAC address found in coordinator data or config entry")
        return

    device_id = mac_address.lower()
    nodes = coordinator.data.get("Nodes", [])
    box_device_ids = get_box_device_ids(device_id, nodes)
    board_type = entry.data.get("board_type", "")

    entities = await create_select_entities(hass, coordinator, device_id, nodes, box_device_ids, board_type)
    if entities:
        async_add_entities(entities, update_before_add=True)


def get_mac_from_coordinator(coordinator: DucoboxCoordinator) -> str | None:
    """Get MAC address from coordinator data (library should normalize this)."""
    # Try to get MAC from General.Lan.Mac (normalized by library)
    mac = coordinator.data.get("General", {}).get("Lan", {}).get("Mac", {}).get("Val")
    if mac:
        return mac.replace(":", "").lower()
    return None


def get_box_device_ids(device_id: str, nodes: list[dict]) -> dict[int, str]:
    """Extract BOX node device IDs."""
    box_ids = {}
    for node in nodes:
        if node.get("General", {}).get("Type", {}).get("Val") == "BOX":
            node_id = int(node.get("Node"))
            box_ids[node_id] = f"{device_id}-{node_id}"
    _LOGGER.debug(f"[SELECT] BOX device IDs: {box_ids}")
    return box_ids


async def create_select_entities(
    hass: HomeAssistant,
    coordinator: DucoboxCoordinator,
    device_id: str,
    nodes: list[dict],
    box_device_ids: dict[int, str],
    board_type: str,
) -> list[SelectEntity]:
    """Create all select entities for Ducobox nodes."""
    entities = []
    is_comm_print_board = _is_comm_print_board(board_type, coordinator.data)

    # Default options for Communication/Print boards (standard DUCO ventilation states)
    default_options = [
        "AUTO",
        "AUT1",
        "AUT2",
        "AUT3",
        "MAN1",
        "MAN2",
        "MAN3",
        "EMPT",
        "CNT1",
        "CNT2",
        "CNT3",
        "MANx2",
        "MAN2x2",
        "MAN3x2",
        "MAN1x3",
        "MAN2x3",
        "MAN3x3",
    ]

    for node in nodes:
        node_id = node.get("Node")
        node_type = node.get("General", {}).get("Type", {}).get("Val", "Unknown")
        ventilation = node.get("Ventilation", {})
        mode = ventilation.get("Mode")

        if mode in (None, "-"):
            _LOGGER.debug(f"[SELECT] Skipping node {node_id}: no ventilation mode")
            continue

        parent_val = node.get("General", {}).get("Parent", {}).get("Val")
        try:
            parent_box_id = int(parent_val)
        except (TypeError, ValueError):
            parent_box_id = None

        if parent_box_id is not None and isinstance(parent_box_id, int):
            via_device_id = box_device_ids.get(parent_box_id)
        else:
            via_device_id = None
        via_device = (DOMAIN, via_device_id) if via_device_id else None

        if node_type == "BOX":
            box_name = coordinator.data.get("General", {}).get("Board", {}).get("BoxName", {}).get("Val", "")
            # Fallback to node type if box_name is empty or "Unknown"
            if not box_name or box_name.lower() == "unknown":
                model = node_type
            else:
                model = box_name
        else:
            model = node_type

        node_device_id = f"{device_id}-{node_id}"

        # For Communication/Print boards, use default options without API call
        if is_comm_print_board:
            options = default_options
            _LOGGER.debug(f"[SELECT] Using default options for node {node_id} (Communication/Print board)")
        else:
            # For Connectivity boards, query available actions from API
            try:
                actions_response = await hass.async_add_executor_job(coordinator.client.get_actions_node, node_id)
                ventilation_action = next(
                    (a for a in actions_response.Actions if a.Action == "SetVentilationState" and hasattr(a, "Enum")),
                    None,
                )
                if not ventilation_action or not ventilation_action.Enum:
                    _LOGGER.debug(f"[SELECT] No ventilation action found for node {node_id}")
                    continue
                options = [opt.strip() for opt in ventilation_action.Enum if isinstance(opt, str)]
            except Exception as e:
                if _is_comm_print_exception(e):
                    options = default_options
                    _LOGGER.debug(
                        f"[SELECT] Falling back to default options for node {node_id} (Communication/Print board)"
                    )
                else:
                    _LOGGER.warning(f"[SELECT] Failed to retrieve ventilation actions for node {node_id}: {e}")
                    continue

        device_info = DeviceInfo(
            identifiers={(DOMAIN, node_device_id)},
            name=node_type,
            manufacturer=MANUFACTURER,
            model=model,
            via_device=via_device,
        )
        unique_id = f"{node_device_id}-select-ventilation_mode"

        entity = DucoboxModeSelect(
            coordinator=coordinator,
            device_info=device_info,
            unique_id=unique_id,
            node_id=node_id if isinstance(node_id, int) else int(node_id) if node_id else 0,
            options=options,
        )
        entities.append(entity)

        _LOGGER.debug(f"[SELECT] Created select for node {node_id} with options {options}")

    return entities


class DucoboxModeSelect(CoordinatorEntity[DucoboxCoordinator], SelectEntity):
    """Select entity for Ducobox ventilation mode."""

    def __init__(
        self,
        coordinator: DucoboxCoordinator,
        device_info: DeviceInfo,
        unique_id: str,
        node_id: int,
        options: list[str],
    ) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator)
        self._attr_device_info = device_info
        self._attr_unique_id = unique_id
        self._attr_has_entity_name = True
        self._attr_translation_key = "ventilation_mode"
        self._attr_options = options
        self._node_id = node_id

    @property
    def current_option(self) -> str | None:
        """Return the current ventilation mode."""
        nodes = self.coordinator.data.get("Nodes", [])
        for node in nodes:
            if node.get("Node") == self._node_id:
                state = node.get("Ventilation", {}).get("State")
                if isinstance(state, str) and state in self._attr_options:
                    return state
                _LOGGER.warning(f"[SELECT] Invalid current state '{state}' for node {self._node_id}")
                return None
        _LOGGER.warning(f"[SELECT] Node {self._node_id} not found")
        return None

    async def async_select_option(self, option: str) -> None:
        """Change the ventilation mode."""
        _LOGGER.debug(f"[SELECT] Setting node {self._node_id} to {option}")
        try:
            await self.coordinator.hass.async_add_executor_job(
                self.coordinator.client.change_action_node,
                "SetVentilationState",
                option,
                self._node_id,
            )
            _LOGGER.debug("[SELECT] Successfully sent command, waiting for device to process")
            await asyncio.sleep(3.0)  # Give device 3 seconds to process the change
            _LOGGER.debug("[SELECT] Refreshing coordinator data and waiting for completion")
            await self.coordinator.async_refresh()  # Wait for refresh to complete
            _LOGGER.debug("[SELECT] Coordinator refresh completed, all entities should update")
        except Exception as e:
            _LOGGER.error(f"[SELECT] Failed to set mode '{option}' for node {self._node_id}: {e}")


def _is_comm_print_board(board_type: str, data: dict) -> bool:
    """Return True when the board does not support node actions."""
    if "Communication" in board_type or "Print" in board_type:
        return True

    board_name = (
        data.get("General", {}).get("Board", {}).get("Type", {}).get("Val")
        or data.get("General", {}).get("Board", {}).get("Name", {}).get("Val")
        or data.get("General", {}).get("Board", {}).get("BoardType", {}).get("Val")
    )
    return isinstance(board_name, str) and ("Communication" in board_name or "Print" in board_name)


def _is_comm_print_exception(err: Exception) -> bool:
    """Return True when the error indicates node actions are unsupported."""
    message = str(err)
    return "Node actions are not available" in message or "Communication and Print Board" in message
