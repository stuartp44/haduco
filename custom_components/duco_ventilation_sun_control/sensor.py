from __future__ import annotations
import logging
from typing import Any
from retrying import retry
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator
from homeassistant.components.sensor import SensorEntity
from .const import DOMAIN, SCAN_INTERVAL
import asyncio
from .comm_boards import COMMBOARD_SENSORS
from .network import DUCONETWORK_SENSORS
from .nodes import NODE_SENSORS
from .boxes import BOX_SENSORS
from .calibration import CALIBRATION_SENSORS
from .ducobox_classes import DucoboxSensorEntityDescription, DucoboxNodeSensorEntityDescription

_LOGGER = logging.getLogger(__name__)


class DucoboxCoordinator(DataUpdateCoordinator):
    """Coordinator to manage data updates for Ducobox sensors."""

    def __init__(self, hass: HomeAssistant):
        super().__init__(
            hass,
            _LOGGER,
            name="Ducobox Connectivity Board",
            update_interval=SCAN_INTERVAL,
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
        duco_client = self.hass.data[DOMAIN]
        data = duco_client.get_info()
        _LOGGER.debug(f"Data received from /info: {data}")

        nodes_response = duco_client.get_nodes()
        _LOGGER.debug(f"Data received from /nodes: {nodes_response}")

        # Convert nodes_response.Nodes (which is a list of NodeInfo objects) to list of dicts
        data['Nodes'] = [node.dict() for node in nodes_response.Nodes]
        return data


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Ducobox sensors from a config entry."""
    coordinator = DucoboxCoordinator(hass)
    await coordinator.async_config_entry_first_refresh()

    mac_address = get_mac_address(coordinator)
    if not mac_address:
        _LOGGER.error("No MAC address found in data, unable to create sensors")
        _LOGGER.debug(f"Data received: {coordinator.data}")
        return

    device_id = mac_address.replace(":", "").lower()
    device_info = create_device_info(coordinator, device_id)

    entities = []
    entities.extend(create_main_sensors(coordinator, device_info, device_id))
    entities.extend(create_node_sensors(coordinator, device_id))
    entities.extend(create_duco_network_sensors(coordinator, device_info, device_id))
    entities.extend(create_calibration_sensors(coordinator, device_info, device_id))

    if entities:
        async_add_entities(entities, update_before_add=True)


def get_mac_address(coordinator: DucoboxCoordinator) -> str | None:
    """Retrieve the MAC address from the coordinator data."""
    return (
        coordinator.data.get("General", {})
        .get("Lan", {})
        .get("Mac", {})
        .get("Val")
    )


def create_device_info(coordinator: DucoboxCoordinator, device_id: str) -> DeviceInfo:
    """Create device info for the main Ducobox."""
    data = coordinator.data
    return DeviceInfo(
        identifiers={(DOMAIN, device_id)},
        name=data.get("General", {}).get("Lan", {}).get("HostName", {}).get("Val", "Unknown"),
        manufacturer="DUCO Ventilation & Sun Control",
        model=data.get("General", {}).get("Board", {}).get("CommSubTypeName", {}).get("Val", "Unknown"),
        serial_number=data.get("General", {}).get("Board", {}).get("SerialBoardComm", {}).get("Val", "Unknown"),
        sw_version=data.get("General", {}).get("Board", {}).get("SwVersionComm", {}).get("Val", "Unknown"),
    )


def create_main_sensors(coordinator: DucoboxCoordinator, device_info: DeviceInfo, device_id: str) -> list[SensorEntity]:
    """Create main Ducobox sensors."""
    return [
        DucoboxSensorEntity(
            coordinator=coordinator,
            description=description,
            device_info=device_info,
            unique_id=f"{device_id}-{description.key}",
        )
        for description in COMMBOARD_SENSORS
    ]


def create_node_sensors(coordinator: DucoboxCoordinator, device_id: str) -> list[SensorEntity]:
    """Create sensors for each node."""
    entities = []
    nodes = coordinator.data.get("Nodes", [])
    for node in nodes:
        node_id = node.get("Node")
        node_type = node.get("General", {}).get("Type", {}).get("Val", "Unknown")
        node_device_id = f"{device_id}-{node_id}"

        if node_type == "BOX":
            entities.extend(create_box_sensors(coordinator, node, node_device_id, device_id))
        elif node_type != "UC":
            entities.extend(create_generic_node_sensors(coordinator, node, node_device_id, node_type, device_id))

    return entities


def create_box_sensors(coordinator: DucoboxCoordinator, node: dict, node_device_id: str, device_id: str) -> list[SensorEntity]:
    """Create sensors for a BOX node, including calibration and network sensors."""
    entities = []
    box_name = coordinator.data.get("General", {}).get("Board", {}).get("BoxName", {}).get("Val", "")
    box_device_info = DeviceInfo(
        identifiers={(DOMAIN, node_device_id)},
        name=box_name,
        manufacturer="DUCO Ventilation & Sun Control",
        model=box_name,
        via_device=(DOMAIN, device_id),
    )

    # Add box-specific sensors
    if box_name in BOX_SENSORS:
        for description in BOX_SENSORS[box_name]:
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
    coordinator: DucoboxCoordinator, node: dict, node_device_id: str, node_type: str, device_id: str
) -> list[SensorEntity]:
    """Create sensors for a generic node."""
    node_device_info = DeviceInfo(
        identifiers={(DOMAIN, node_device_id)},
        name=node_type,
        manufacturer="DUCO Ventilation & Sun Control",
        model=node_type,
        via_device=(DOMAIN, device_id),
    )

    return [
        DucoboxNodeSensorEntity(
            coordinator=coordinator,
            node_id=node.get("Node"),
            description=description,
            device_info=node_device_info,
            unique_id=f"{node_device_id}-{description.key}",
            device_id=device_id,
            node_name=node_type,
        )
        for description in NODE_SENSORS.get(node_type, [])
    ]


def create_duco_network_sensors(coordinator: DucoboxCoordinator, device_info: DeviceInfo, device_id: str) -> list[SensorEntity]:
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


def create_calibration_sensors(coordinator: DucoboxCoordinator, device_info: DeviceInfo, device_id: str) -> list[SensorEntity]:
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
                return self.entity_description.value_fn({'node_data': node, 'general_data': self.coordinator.data})
        return None