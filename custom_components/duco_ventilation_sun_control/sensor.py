from __future__ import annotations
import logging
from typing import Any
from retrying import retry
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)
from homeassistant.components.sensor import (
    SensorEntity,
)
from .const import DOMAIN, SCAN_INTERVAL
import asyncio
from .comm_boards import COMMBOARD_SENSORS
from .network import DUCONETWORK_SENSORS
from .nodes import NODE_SENSORS
from .boxes import BOX_SENSORS
from .calibration import CALIBRATION_SENSORS
from .ducobox_classes import (
    DucoboxSensorEntityDescription, 
    DucoboxNodeSensorEntityDescription,
    DucoboxCommsBoardInfo
)
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
        # Use retrying library to retry fetching data
        
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

async def get_mac_address(hass: HomeAssistant) -> str:
    """Get the MAC address of the Ducobox device."""
    coordinator = hass.data[DOMAIN]
    mac_address = (
        coordinator.data.get("General", {})
        .get("Lan", {})
        .get("Mac", {})
        .get("Val")
    )
    if not mac_address:
        _LOGGER.error("No MAC address found in data")
        raise ConfigEntryNotReady(f"Not able to get a MAC Address")
    return mac_address.replace(":", "").lower()

async def build_comms_board_information(
    hass: HomeAssistant,
    entry: ConfigEntry,
    ) -> tuple[str, str]:
        """Build the communication board information."""
        coordinator = hass.data[DOMAIN]
        name = coordinator.data.get("General", {}).get("Lan", {}).get("HostName", {}).get("Val", "")
        serial_number = coordinator.data.get("General", {}).get("Board", {}).get("SerialBoardComm", {}).get("Val", "")
        subtype = coordinator.data.get("General", {}).get("Board", {}).get("CommSubTypeName", {}).get("Val", "")
        
        commsboard_info = DucoboxCommsBoardInfo(
            name=name,
            serial_number=serial_number,
            subtype=subtype,
        )
        
        return commsboard_info

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Ducobox sensors from a config entry."""
    coordinator = DucoboxCoordinator(hass)
    await coordinator.async_config_entry_first_refresh()
    
    # Retrieve MAC address and format device ID and name
    mac_address = await get_mac_address(hass)
    
    comms_board_info = await build_comms_board_information(hass, entry)
    
    if mac_address and mac_address is not None:
        device_id = mac_address
        
        comms_name = comms_board_info.name
        comms_serial_number = comms_board_info.serial_number
        comms_subtype = comms_board_info.subtype

        device_info = DeviceInfo(
            identifiers={(DOMAIN, device_id)},
            name=comms_name,
            manufacturer="DUCO Ventilation & Sun Control",
            model=comms_subtype,
            serial_number=comms_serial_number,
            sw_version=coordinator.data.get("General", {}).get("Board", {}).get("SwVersionComm", {}).get("Val", "Unknown Version"),
        )

        entities: list[SensorEntity] = []

        # Add main Ducobox sensors
        for description in COMMBOARD_SENSORS:
            unique_id = f"{device_id}-{description.key}"
            entities.append(
                DucoboxSensorEntity(
                    coordinator=coordinator,
                    description=description,
                    device_info=device_info,
                    unique_id=unique_id,
                )
            )
        
        # Add node sensors
        nodes = coordinator.data.get('Nodes', [])
        for node in nodes:
            node_id = node.get('Node')
            box_name = coordinator.data.get("General", {}).get("Board", {}).get("BoxName", {}).get("Val", "")
            node_type = node.get('General', {}).get('Type', {}).get('Val', 'Unknown')
            box_sw_version = coordinator.data.get("General", {}).get("Board", {}).get("SwVersionBox", {}).get("Val", "")
            box_serial_number = coordinator.data.get("General", {}).get("Board", {}).get("SerialBoardBox", {}).get("Val", "")

            # Create device info for the node
            node_device_id = f"{device_id}-{node_id}"

            if node.get('General', {}).get('Type', {}).get('Val') == 'BOX':
                node_device_info = DeviceInfo(
                    identifiers={(DOMAIN, node_device_id)},
                    name=box_name,
                    manufacturer="DUCO Ventilation & Sun Control",
                    model=box_name,
                    sw_version=box_sw_version,
                    serial_number=box_serial_number,
                    via_device=(DOMAIN, device_id),
                )
                if box_name in BOX_SENSORS:
                    for description in BOX_SENSORS[box_name]:
                        unique_id = f"{node_device_id}-{description.key}"
                        entities.append(
                            DucoboxNodeSensorEntity(
                                coordinator=coordinator,
                                node_id=node_id,
                                description=description,
                                device_info=node_device_info,
                                unique_id=unique_id,
                                device_id=device_id,
                                node_name=box_name,
                            )
                        )
                    if coordinator.data.get('General', {}).get('NetworkDuco', {}).get('State', {}).get('Val', ""):
                        for description in DUCONETWORK_SENSORS:
                            unique_id = f"{node_device_id}-{description.key}"
                            entities.append(
                                DucoboxNodeSensorEntity(
                                    coordinator=coordinator,
                                    node_id=node_id,
                                    description=description,
                                    device_info=node_device_info,
                                    unique_id=unique_id,
                                    device_id=device_id,
                                    node_name=box_name,
                                )
                            )
                    val = coordinator.data.get('Ventilation', {}).get('Calibration', {}).get('Valid', {}).get('Val', None)
                    if val is not None:
                        for description in CALIBRATION_SENSORS:
                            unique_id = f"{node_device_id}-{description.key}"
                            entities.append(
                                DucoboxNodeSensorEntity(
                                    coordinator=coordinator,
                                    node_id=node_id,
                                    description=description,
                                    device_info=node_device_info,
                                    unique_id=unique_id,
                                    device_id=device_id,
                                    node_name=box_name,
                                )
                            )
                    
                else:
                    _LOGGER.debug(f"No sensors found for node type {box_name}")
            else:
                if node_type != 'UC':
                    node_device_info = DeviceInfo(
                        identifiers={(DOMAIN, node_device_id)},
                        name=node_type,
                        manufacturer="DUCO Ventilation & Sun Control",
                        model=node_type,
                        via_device=(DOMAIN, f"{device_id}-1"),
                    )
                    node_sensors = NODE_SENSORS.get(node_type, [])
                    for description in node_sensors:
                        unique_id = f"{node_device_id}-{description.key}"
                        entities.append(
                            DucoboxNodeSensorEntity(
                                coordinator=coordinator,
                                node_id=node_id,
                                description=description,
                                device_info=node_device_info,
                                unique_id=unique_id,
                                device_id=device_id,
                                node_name=node_type,
                            )
                        )

        if entities:
            async_add_entities(entities, update_before_add=True)
    else:
        _LOGGER.error("No MAC address found in data, unable to create sensors")
        _LOGGER.debug(f"Data received: {coordinator.data}")

class DucoboxSensorEntity(CoordinatorEntity[DucoboxCoordinator], SensorEntity):
    """Representation of a Ducobox sensor entity."""
    entity_description: DucoboxSensorEntityDescription

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
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success
    
    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        return self.entity_description.value_fn(self.coordinator.data)

class DucoboxNodeSensorEntity(CoordinatorEntity[DucoboxCoordinator], SensorEntity):
    """Representation of a Ducobox node sensor entity."""
    entity_description: DucoboxNodeSensorEntityDescription

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
        # Updated entity name
        self._attr_name = description.name
        # self._attr_suggested_object_id = f"{device_id}_{node_name}_{description.name}".lower().replace(' ', '_')

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        # Fetch the latest data for this node
        nodes = self.coordinator.data.get('Nodes', [])
        for node in nodes:
            if node.get('Node') == self._node_id:
                return self.entity_description.value_fn({'node_data': node, 'general_data': self.coordinator.data})
        return None
