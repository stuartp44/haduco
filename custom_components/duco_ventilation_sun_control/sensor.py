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

from .boxes import BOX_SENSORS, COMMON_BOX_SENSORS
from .calibration import CALIBRATION_SENSORS
from .comm_boards import COMMBOARD_SENSORS
from .const import DOMAIN, MANUFACTURER, SCAN_INTERVAL
from .coordinator import DucoboxCoordinator
from .ducobox_classes import (
    DucoboxNodeSensorEntityDescription,
    DucoboxSensorEntityDescription,
)
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

    coordinator = DucoboxCoordinator(
        hass, update_interval=timedelta(seconds=refresh_time)
    )
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

    # Create main board entities first to ensure the device exists
    main_entities = create_main_sensors(coordinator, device_info, device_id, entry)
    if main_entities:
        async_add_entities(main_entities, update_before_add=True)

    # Now create node entities - they can reference the main board via via_device
    node_entities = create_node_sensors(coordinator, device_id, entry)
    if node_entities:
        async_add_entities(node_entities, update_before_add=True)


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


def create_device_info(
    coordinator: DucoboxCoordinator, entry: ConfigEntry, device_id: str
) -> DeviceInfo:
    """Create device info for the main Ducobox."""
    # Library normalizes board info across both board types
    data = coordinator.data
    board_type = entry.data.get("board_type", "DUCO Board")
    if not board_type or board_type == "DUCO Board":
        board_type = _detect_board_type_from_data(data)
    hostname = data.get("General", {}).get("Lan", {}).get("HostName", {}).get("Val")
    base_url = entry.data.get("base_url")

    # Get sw_version and serial from BoardInfo (library normalizes for all board types)
    board_info = data.get("BoardInfo", {})
    sw_version = _normalize_device_info_value(board_info.get("SwVersion"))
    serial_number = _normalize_device_info_value(board_info.get("Serial"))

    # Fallback: If library normalization didn't provide sw_version, get it from General.Board
    if not sw_version:
        # For Connectivity boards, use SwVersionComm; for others, use SwVersionBox
        if "Connectivity" in board_type:
            sw_version = _normalize_device_info_value(
                data.get("General", {})
                .get("Board", {})
                .get("SwVersionComm", {})
                .get("Val")
            )
        else:
            # Communication/Print boards might use different field
            sw_version = _normalize_device_info_value(
                data.get("General", {})
                .get("Board", {})
                .get("SwVersionBox", {})
                .get("Val")
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


def _normalize_device_info_value(value: object | None) -> str | None:
    """Normalize device info values, ignoring placeholders."""
    if value is None:
        return None
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped or stripped.lower() == "n/a":
            return None
        return stripped
    return str(value)


def _detect_board_type_from_data(data: dict) -> str:
    """Detect the board type from coordinator data."""
    board_info = data.get("BoardInfo")

    comm_subtype = (
        data.get("General", {})
        .get("Board", {})
        .get("CommSubTypeName", {})
        .get("Val", "")
    )
    if isinstance(comm_subtype, str) and comm_subtype:
        if "connectivity" in comm_subtype.lower():
            return "Connectivity Board"
        if "communication" in comm_subtype.lower() or "print" in comm_subtype.lower():
            return "Communication and Print Board"
        return f"{comm_subtype} Board"

    api_version = data.get("General", {}).get("Board", {}).get("ApiVersion", {}).get(
        "Val"
    ) or data.get("General", {}).get("Board", {}).get("PublicApiVersion", {}).get("Val")
    if api_version:
        try:
            return (
                "Connectivity Board"
                if float(api_version) >= 2.0
                else "Communication and Print Board"
            )
        except (TypeError, ValueError):
            return "DUCO Board"

    if board_info:
        return "Communication and Print Board"

    return "DUCO Board"


def create_main_sensors(
    coordinator: DucoboxCoordinator,
    device_info: DeviceInfo,
    device_id: str,
    entry: ConfigEntry,
) -> list[SensorEntity]:
    """Create main Ducobox sensors only for available data structures."""
    entities = []
    data = coordinator.data
    board_type = entry.data.get("board_type", "")
    is_comm_print_board = _is_comm_print_board(board_type, data)

    # Filter out Wi-Fi sensor for Communication/Print boards (Ethernet only)
    sensors = COMMBOARD_SENSORS
    if is_comm_print_board:
        sensors = [s for s in sensors if "Wifi" not in s.key]

    # Only create sensors if their parent data structure exists
    # For example, Wi-Fi sensor needs General.Lan, uptime needs General.Board
    for description in sensors:
        # Check if the parent data structure exists by attempting to navigate the path
        # This is a heuristic: try to get one level before the final value
        try:
            # Try calling the value function - if it fails, the structure doesn't exist
            # We check if the path exists, not if the value is None
            description.value_fn(data)
            # If we can call it without error, create the sensor
            # The sensor will be unavailable if the value is None
            entities.append(
                DucoboxSensorEntity(
                    coordinator=coordinator,
                    description=description,
                    device_info=device_info,
                    unique_id=f"{device_id}-{description.key}",
                )
            )
        except (KeyError, AttributeError):
            # Structure doesn't exist, skip this sensor
            _LOGGER.debug(
                f"Skipping sensor {description.key} - required data structure not available on this board type"
            )

    return entities


def _is_comm_print_board(board_type: str, data: dict) -> bool:
    """Return True when the board does not support Wi-Fi signal strength."""
    if "Communication" in board_type or "Print" in board_type:
        return True

    board_info = data.get("BoardInfo")
    if board_info:
        return True

    board_name = (
        data.get("General", {}).get("Board", {}).get("Type", {}).get("Val")
        or data.get("General", {}).get("Board", {}).get("Name", {}).get("Val")
        or data.get("General", {}).get("Board", {}).get("BoardType", {}).get("Val")
    )
    return isinstance(board_name, str) and (
        "Communication" in board_name or "Print" in board_name
    )


def _is_box_node(node: dict, node_type: str) -> bool:
    """Return True when the node should be treated as a box."""
    if node_type == "BOX" or node_type in BOX_SENSORS:
        return True

    return (
        node.get("Calibration") is not None
        or node.get("EnergyCalib") is not None
        or node.get("Ventilation", {}).get("Calibration") is not None
        or node.get("Ventilation", {}).get("EnergyCalib") is not None
        or node.get("HeatRecovery", {}).get("EnergyCalib") is not None
    )


def create_node_sensors(
    coordinator: DucoboxCoordinator, device_id: str, entry: ConfigEntry
) -> list[SensorEntity]:
    """Create sensors for each node, connecting them via the box."""
    entities = []
    nodes = coordinator.data.get("Nodes", [])
    box_device_ids = {}

    # First, create box sensors and store their device IDs
    for node in nodes:
        node_type = node.get("General", {}).get("Type", {}).get("Val", "Unknown")
        if _is_box_node(node, node_type):
            node_id = node.get("Node")
            node_device_id = f"{device_id}-{node_id}"
            box_device_ids[node_id] = node_device_id
            entities.extend(
                create_box_sensors(coordinator, node, node_device_id, device_id, entry)
            )

    # Then, create sensors for other nodes, linking them via their box
    for node in nodes:
        node_id = node.get("Node")
        _LOGGER.debug(f"Processing node ID: {node_id}")
        _LOGGER.debug(f"Node data: {node}")
        node_type = node.get("General", {}).get("Type", {}).get("Val", "Unknown")
        _LOGGER.debug(f"Node ID: {node_id}, Type: {node_type}")
        parent_box_id = find_box_addr(nodes)
        _LOGGER.debug(f"Parent Box ID: {parent_box_id}")

        if node_type not in {"BOX", "UC"} and node_type not in BOX_SENSORS:
            # Use the parent box's device ID as the via_device
            via_device_id = box_device_ids.get(parent_box_id, device_id)
            _LOGGER.debug(
                f"Using via_device_id: {via_device_id} for node ID: {node_id}"
            )
            node_device_id = f"{device_id}-{node_id}"
            entities.extend(
                create_generic_node_sensors(
                    coordinator, node, node_device_id, node_type, via_device_id, entry
                )
            )

    return entities


def create_box_sensors(
    coordinator: DucoboxCoordinator,
    node: dict,
    node_device_id: str,
    device_id: str,
    entry: ConfigEntry,
) -> list[SensorEntity]:
    """Create sensors for a BOX node, including calibration and network sensors."""
    entities = []
    dev_type = node.get("General", {}).get("Type", {}).get("Val", "BOX")
    box_name = (
        coordinator.data.get("General", {})
        .get("Board", {})
        .get("BoxName", {})
        .get("Val", "")
    )

    # Fallback to node type if box_name is empty or "Unknown"
    if not box_name or box_name.lower() == "unknown":
        box_name = dev_type

    # Get sw_version and serial from node data (library normalizes for all board types)
    sw_version_data = node.get("General", {}).get("SwVersion")
    box_sw_version = _normalize_device_info_value(
        sw_version_data.get("Val")
        if isinstance(sw_version_data, dict)
        else sw_version_data
    )
    box_serial_number = _normalize_device_info_value(
        node.get("General", {}).get("SerialBoard")
    )

    # BOX is connected via the main board (Communication/Print or Connectivity)
    box_device_info = DeviceInfo(
        identifiers={(DOMAIN, node_device_id)},
        name=box_name,
        manufacturer=MANUFACTURER,
        model=box_name,
        sw_version=box_sw_version,
        serial_number=box_serial_number,
        via_device=(DOMAIN, device_id),
    )

    # Add common BOX sensors (available for all BOX types)
    entities.extend(
        [
            DucoboxNodeSensorEntity(
                coordinator=coordinator,
                node_id=node.get("Node"),
                description=description,
                device_info=box_device_info,
                unique_id=f"{node_device_id}-{description.key}",
                device_id=device_id,
                node_name=box_name,
            )
            for description in COMMON_BOX_SENSORS
        ]
    )

    # Add box-specific sensors
    if box_name in BOX_SENSORS:
        entities.extend(
            [
                DucoboxNodeSensorEntity(
                    coordinator=coordinator,
                    node_id=node.get("Node"),
                    description=description,
                    device_info=box_device_info,
                    unique_id=f"{node_device_id}-{description.key}",
                    device_id=device_id,
                    node_name=box_name,
                )
                for description in BOX_SENSORS[box_name]
            ]
        )

    # Add Duco network sensors as diagnostic sensors (only for Connectivity boards)
    board_type = entry.data.get("board_type", "")
    if "Connectivity" in board_type:
        # Only add network sensor if NetworkDuco.State data exists
        if (
            coordinator.data.get("General", {}).get("NetworkDuco", {}).get("State")
            is not None
        ):
            entities.extend(
                [
                    DucoboxNodeSensorEntity(
                        coordinator=coordinator,
                        node_id=node.get("Node"),
                        description=description,
                        device_info=box_device_info,
                        unique_id=f"{node_device_id}-{description.key}",
                        device_id=device_id,
                        node_name=box_name,
                    )
                    for description in DUCONETWORK_SENSORS
                ]
            )

    # Add calibration sensors as diagnostic sensors when data exists
    calibration_payload = {"node_data": node, "general_data": coordinator.data}
    calibration_descriptions = [
        description
        for description in CALIBRATION_SENSORS
        if description.value_fn(calibration_payload) is not None
    ]
    if calibration_descriptions:
        entities.extend(
            [
                DucoboxCalibrationSensorEntity(
                    coordinator=coordinator,
                    node_data=node,
                    description=description,
                    device_info=box_device_info,
                    unique_id=f"{node_device_id}-{description.key}",
                )
                for description in calibration_descriptions
            ]
        )

    return entities


def create_generic_node_sensors(
    coordinator: DucoboxCoordinator,
    node: dict,
    node_device_id: str,
    node_type: str,
    via_device_id: str,
    entry: ConfigEntry,
) -> list[SensorEntity]:
    """Create sensors for a generic node, linking them via the specified device."""
    # Get node-specific sw_version and serial from the node data
    sw_version_data = node.get("General", {}).get("SwVersion")
    node_sw_version = _normalize_device_info_value(
        sw_version_data.get("Val")
        if isinstance(sw_version_data, dict)
        else sw_version_data
    )
    node_serial = _normalize_device_info_value(
        node.get("General", {}).get("SerialBoard")
    )

    node_device_info = DeviceInfo(
        identifiers={(DOMAIN, node_device_id)},
        name=node_type,
        manufacturer=MANUFACTURER,
        model=node_type,
        sw_version=node_sw_version,
        serial_number=node_serial,
        via_device=(DOMAIN, via_device_id),
    )

    node_id = node.get("Node")
    board_type = entry.data.get("board_type", "")

    # Filter out IAQ sensors for Communication/Print boards (only available on Connectivity boards)
    sensors = NODE_SENSORS.get(node_type, [])
    if "Communication" in board_type or "Print" in board_type:
        sensors = [s for s in sensors if "Iaq" not in s.key]

    # Only create sensors for fields that actually exist in the node's sensor data
    # This prevents creating sensors that will always show "Unknown"
    sensor_section = node.get("Sensor") or {}
    sensor_data = (
        sensor_section.get("data", {}) if isinstance(sensor_section, dict) else {}
    )
    if sensor_data:
        # Filter to only sensors whose sensor_key exists in the actual data
        sensors = [
            s
            for s in sensors
            if hasattr(s, "sensor_key") and s.sensor_key in sensor_data
        ]

    return [
        DucoboxNodeSensorEntity(
            coordinator=coordinator,
            node_id=node_id,
            description=description,
            device_info=node_device_info,
            unique_id=f"{node_device_id}-{description.key}",
            device_id=via_device_id,
            node_name=node_type,
        )
        for description in sensors
    ]


def create_duco_network_sensors(
    coordinator: DucoboxCoordinator, device_info: DeviceInfo, device_id: str
) -> list[SensorEntity]:
    """Create Duco network sensors."""
    return [
        DucoboxSensorEntity(
            coordinator=coordinator,
            description=description,
            device_info=device_info,
            unique_id=f"{device_id}-{description.key}",
        )
        for description in DUCONETWORK_SENSORS
    ]


def create_calibration_sensors(
    coordinator: DucoboxCoordinator, device_info: DeviceInfo, device_id: str
) -> list[SensorEntity]:
    """Create calibration sensors."""
    return [
        DucoboxSensorEntity(
            coordinator=coordinator,
            description=description,
            device_info=device_info,
            unique_id=f"{device_id}-{description.key}",
        )
        for description in CALIBRATION_SENSORS
    ]


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
        self._attr_has_entity_name = True
        self._attr_translation_key = description.key.lower()

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
        self._attr_has_entity_name = True
        self._attr_translation_key = description.key.lower()

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        nodes = self.coordinator.data.get("Nodes", [])
        for node in nodes:
            if node.get("Node") == self._node_id:
                return self.entity_description.value_fn(
                    {"node_data": node, "general_data": self.coordinator.data}
                )
        return None


class DucoboxCalibrationSensorEntity(
    CoordinatorEntity[DucoboxCoordinator], SensorEntity
):
    """Representation of a Ducobox calibration sensor entity."""

    def __init__(
        self,
        coordinator: DucoboxCoordinator,
        node_data: dict,
        description: DucoboxNodeSensorEntityDescription,
        device_info: DeviceInfo,
        unique_id: str,
    ) -> None:
        """Initialize a Ducobox calibration sensor entity."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_device_info = device_info
        self._attr_unique_id = unique_id
        self._node_data = node_data
        self._attr_has_entity_name = True
        self._attr_translation_key = description.key.lower()

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        return self.entity_description.value_fn(
            {"node_data": self._node_data, "general_data": self.coordinator.data}
        )
