from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .boxes import BOX_SENSORS
from .calibration import CALIBRATION_SENSORS
from .comm_boards import COMMBOARD_SENSORS
from .const import DOMAIN, MANUFACTURER, SCAN_INTERVAL
from .coordinator import DucoboxCoordinator
from .ducobox_classes import DucoboxNodeSensorEntityDescription, DucoboxSensorEntityDescription
from .network import DUCONETWORK_SENSORS
from .nodes import NODE_SENSORS

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Ducobox sensors from a config entry."""
    refresh_time = entry.options.get("refresh_time", SCAN_INTERVAL.total_seconds())

    coordinator = DucoboxCoordinator(hass, update_interval=timedelta(seconds=refresh_time))
    await coordinator.async_config_entry_first_refresh()

    # Try to get MAC from coordinator data (library should normalize this)
    # Fall back to config entry for backward compatibility
    mac_address = get_mac_from_coordinator(coordinator) or entry.data.get("unique_id")
    if not mac_address:
        _LOGGER.error("No MAC address found in coordinator data or config entry")
        _LOGGER.debug(f"Coordinator data: {coordinator.data}")
        return

    device_id = mac_address.lower()
    device_info = create_device_info(coordinator, entry, device_id)

    entities = []
    entities.extend(create_main_sensors(coordinator, device_info, device_id))
    entities.extend(create_node_sensors(coordinator, device_id))

    if entities:
        async_add_entities(entities, update_before_add=True)


def find_box_addr(nodes: list[dict]) -> int | None:
    """Find the Addr of the first node where the type is BOX."""
    for node in nodes:
        if node.get("General", {}).get("Type", {}).get("Val") == "BOX":
            addr = node.get("General", {}).get("Addr")
            if addr is None:
                # If Addr is None, use the Node ID
                return node.get("Node")
            # Handle both normalized (int) and non-normalized (dict with Val) formats
            if isinstance(addr, dict):
                return addr.get("Val")
            return addr
    return None


def get_mac_from_coordinator(coordinator: DucoboxCoordinator) -> str | None:
    """Get MAC address from coordinator data (library should normalize this)."""
    # Try to get MAC from General.Lan.Mac (normalized by library)
    mac = coordinator.data.get("General", {}).get("Lan", {}).get("Mac", {}).get("Val")
    if mac:
        return mac.replace(":", "").lower()
    return None


def create_device_info(coordinator: DucoboxCoordinator, entry: ConfigEntry, device_id: str) -> DeviceInfo:
    """Create device info for the main Ducobox."""
    # Try to get board info from coordinator (library should normalize this)
    data = coordinator.data
    board_type = data.get("General", {}).get("Board", {}).get("CommSubTypeName", {}).get("Val") or entry.data.get(
        "board_type", "DUCO Board"
    )
    hostname = data.get("General", {}).get("Lan", {}).get("HostName", {}).get("Val")
    base_url = entry.data.get("base_url")

    # Try to get sw_version and serial from BoardInfo (Communication/Print boards)
    # Fall back to General.Board for Connectivity boards
    board_info = data.get("BoardInfo", {})
    sw_version = board_info.get("swversion") or data.get("General", {}).get("Board", {}).get("SwVersionComm", {}).get(
        "Val"
    )
    serial_number = board_info.get("serial") or data.get("General", {}).get("Board", {}).get("SerialBoardComm", {}).get(
        "Val"
    )

    return DeviceInfo(
        identifiers={(DOMAIN, device_id)},
        name=hostname or f"{board_type} ({device_id})",
        manufacturer=MANUFACTURER,
        model=board_type,
        sw_version=sw_version,
        serial_number=serial_number,
        configuration_url=base_url,
    )


def create_main_sensors(coordinator: DucoboxCoordinator, device_info: DeviceInfo, device_id: str) -> list[SensorEntity]:
    """Create main Ducobox sensors only if data exists."""
    entities = []
    data = coordinator.data

    for description in COMMBOARD_SENSORS:
        # Check if the sensor data exists before creating the entity
        value = description.value_fn(data)
        if value is not None:
            entities.append(
                DucoboxSensorEntity(
                    coordinator=coordinator,
                    description=description,
                    device_info=device_info,
                    unique_id=f"{device_id}-{description.key}",
                )
            )

    return entities


def create_node_sensors(coordinator: DucoboxCoordinator, device_id: str) -> list[SensorEntity]:
    """Create sensors for each node, connecting them via the box."""
    entities = []
    nodes = coordinator.data.get("Nodes", [])
    box_device_ids = {}

    # First, create box sensors and store their device IDs
    for node in nodes:
        node_type = node.get("General", {}).get("Type", {}).get("Val", "Unknown")
        if node_type == "BOX":
            node_id = node.get("Node")
            node_device_id = f"{device_id}-{node_id}"
            box_device_ids[node_id] = node_device_id
            entities.extend(create_box_sensors(coordinator, node, node_device_id, device_id))

    # Then, create sensors for other nodes, linking them via their box
    for node in nodes:
        node_id = node.get("Node")
        _LOGGER.debug(f"Processing node ID: {node_id}")
        _LOGGER.debug(f"Node data: {node}")
        node_type = node.get("General", {}).get("Type", {}).get("Val", "Unknown")
        _LOGGER.debug(f"Node ID: {node_id}, Type: {node_type}")
        parent_box_id = find_box_addr(nodes)
        _LOGGER.debug(f"Parent Box ID: {parent_box_id}")

        if node_type != "BOX" and node_type != "UC":
            # Use the parent box's device ID as the via_device
            via_device_id = box_device_ids.get(parent_box_id, device_id)
            _LOGGER.debug(f"Using via_device_id: {via_device_id} for node ID: {node_id}")
            node_device_id = f"{device_id}-{node_id}"
            entities.extend(create_generic_node_sensors(coordinator, node, node_device_id, node_type, via_device_id))

    return entities


def create_box_sensors(
    coordinator: DucoboxCoordinator, node: dict, node_device_id: str, device_id: str
) -> list[SensorEntity]:
    """Create sensors for a BOX node, including calibration and network sensors."""
    entities = []
    box_name = coordinator.data.get("General", {}).get("Board", {}).get("BoxName", {}).get("Val", "")
    # Fallback to node type if box_name is empty (e.g., Communication/Print board doesn't provide BoxName)
    if not box_name:
        node_type = node.get("General", {}).get("Type", {}).get("Val", "BOX")
        box_name = node_type

    box_sw_version = coordinator.data.get("General", {}).get("Board", {}).get("SwVersionBox", {}).get("Val", "")
    box_serial_number = coordinator.data.get("General", {}).get("Board", {}).get("SerialBoardBox", {}).get("Val", "")
    box_device_info = DeviceInfo(
        identifiers={(DOMAIN, node_device_id)},
        name=box_name,
        manufacturer=MANUFACTURER,
        model=box_name.capitalize(),
        sw_version=box_sw_version,
        serial_number=box_serial_number,
        via_device=(DOMAIN, device_id),
    )

    # Add box-specific sensors
    if box_name in BOX_SENSORS:
        for description in BOX_SENSORS[box_name]:
            # Check if the sensor data exists before creating
            value = description.value_fn(coordinator.data)
            if value is not None:
                entities.append(
                    DucoboxNodeSensorEntity(
                        coordinator=coordinator,
                        node_id=node.get("Node"),
                        description=description,
                        device_info=box_device_info,
                        unique_id=f"{node_device_id}-{description.key}",
                        device_id=device_id,
                        node_name=box_name,
                    )
                )

    # Add Duco network sensors as diagnostic sensors
    for description in DUCONETWORK_SENSORS:
        # Check if the sensor data exists before creating
        value = description.value_fn(coordinator.data)
        if value is not None:
            entities.append(
                DucoboxNodeSensorEntity(
                    coordinator=coordinator,
                    node_id=node.get("Node"),
                    description=description,
                    device_info=box_device_info,
                    unique_id=f"{node_device_id}-{description.key}",
                    device_id=device_id,
                    node_name=box_name,
                )
            )

    # Add calibration sensors as diagnostic sensors
    for description in CALIBRATION_SENSORS:
        # Check if the sensor data exists before creating
        value = description.value_fn(coordinator.data)
        if value is not None:
            entities.append(
                DucoboxNodeSensorEntity(
                    coordinator=coordinator,
                    node_id=node.get("Node"),
                    description=description,
                    device_info=box_device_info,
                    unique_id=f"{node_device_id}-{description.key}",
                    device_id=device_id,
                    node_name=box_name,
                )
            )

    return entities


def create_generic_node_sensors(
    coordinator: DucoboxCoordinator, node: dict, node_device_id: str, node_type: str, via_device_id: str
) -> list[SensorEntity]:
    """Create sensors for a generic node, linking them via the specified device."""
    node_device_info = DeviceInfo(
        identifiers={(DOMAIN, node_device_id)},
        name=node_type,
        manufacturer=MANUFACTURER,
        model=node_type,
        via_device=(DOMAIN, via_device_id),
    )

    node_id = node.get("Node")
    entities = []

    for description in NODE_SENSORS.get(node_type, []):
        # Check if the sensor data exists before creating
        value = description.value_fn(coordinator.data)
        if value is not None:
            entities.append(
                DucoboxNodeSensorEntity(
                    coordinator=coordinator,
                    node_id=node_id,
                    description=description,
                    device_info=node_device_info,
                    unique_id=f"{node_device_id}-{description.key}",
                    device_id=via_device_id,
                    node_name=node_type,
                )
            )

    return entities


def create_duco_network_sensors(
    coordinator: DucoboxCoordinator, device_info: DeviceInfo, device_id: str
) -> list[SensorEntity]:
    """Create Duco network sensors."""
    entities = []

    for description in DUCONETWORK_SENSORS:
        # Check if the sensor data exists before creating
        value = description.value_fn(coordinator.data)
        if value is not None:
            entities.append(
                DucoboxSensorEntity(
                    coordinator=coordinator,
                    description=description,
                    device_info=device_info,
                    unique_id=f"{device_id}-{description.key}",
                )
            )

    return entities


def create_calibration_sensors(
    coordinator: DucoboxCoordinator, device_info: DeviceInfo, device_id: str
) -> list[SensorEntity]:
    """Create calibration sensors."""
    entities = []

    for description in CALIBRATION_SENSORS:
        # Check if the sensor data exists before creating
        value = description.value_fn(coordinator.data)
        if value is not None:
            entities.append(
                DucoboxSensorEntity(
                    coordinator=coordinator,
                    description=description,
                    device_info=device_info,
                    unique_id=f"{device_id}-{description.key}",
                )
            )

    return entities


class DucoboxSensorEntity(CoordinatorEntity[DucoboxCoordinator], SensorEntity):
    """Representation of a Ducobox sensor entity."""

    def __init__(
        self,
        coordinator: DucoboxCoordinator,
        description: DucoboxSensorEntityDescription,
        device_info: DeviceInfo,
        unique_id: str,
    ) -> None:
        """Initialize a Ducobox sensor entity."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_device_info = device_info
        self._attr_unique_id = unique_id
        self._attr_name = f"{device_info['name']} {description.name}"

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        return self.entity_description.value_fn(self.coordinator.data)


class DucoboxNodeSensorEntity(CoordinatorEntity[DucoboxCoordinator], SensorEntity):
    """Representation of a Ducobox node sensor entity."""

    def __init__(
        self,
        coordinator: DucoboxCoordinator,
        node_id: int,
        description: DucoboxNodeSensorEntityDescription,
        device_info: DeviceInfo,
        unique_id: str,
        device_id: str,
        node_name: str,
    ) -> None:
        """Initialize a Ducobox node sensor entity."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_device_info = device_info
        self._attr_unique_id = unique_id
        self._node_id = node_id
        self._attr_name = description.name

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        nodes = self.coordinator.data.get("Nodes", [])
        for node in nodes:
            if node.get("Node") == self._node_id:
                return self.entity_description.value_fn({"node_data": node, "general_data": self.coordinator.data})
        return None
