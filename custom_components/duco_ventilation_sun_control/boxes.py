from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    UnitOfPressure,
    UnitOfTemperature,
    UnitOfTime,
)

from .common import (
    _process_bypass_position,
    _process_pressure,
    _process_speed,
    _process_temperature,
    _process_timefilterremain,
)
from .ducobox_classes import (
    DucoboxNodeSensorEntityDescription,
    DucoboxSensorEntityDescription,
)

# Common sensors for all BOX types
COMMON_BOX_SENSORS: list[DucoboxNodeSensorEntityDescription] = [
    DucoboxNodeSensorEntityDescription(
        key="Mode",
        value_fn=lambda node: node.get("node_data", {}).get("Ventilation", {}).get("Mode"),
        icon="mdi:fan",
        sensor_key="Mode",
        node_type="BOX",
    ),
    DucoboxNodeSensorEntityDescription(
        key="State",
        value_fn=lambda node: node.get("node_data", {}).get("Ventilation", {}).get("State"),
        icon="mdi:fan-auto",
        sensor_key="State",
        node_type="BOX",
    ),
    DucoboxNodeSensorEntityDescription(
        key="FlowLvlTgt",
        native_unit_of_measurement=PERCENTAGE,
        value_fn=lambda node: node.get("node_data", {}).get("Ventilation", {}).get("FlowLvlTgt"),
        icon="mdi:fan-chevron-up",
        sensor_key="FlowLvlTgt",
        node_type="BOX",
    ),
]

BOX_SENSORS: dict[str, list[DucoboxSensorEntityDescription | DucoboxNodeSensorEntityDescription]] = {
    "FOCUS": [],
    "NOT_SURE": [
        # Temperature sensors
        # relevant ducobox documentation: https://www.duco.eu/Wes/CDN/1/Attachments/installation-guide-DucoBox-Energy-Comfort-(Plus)-(en)_638635518879333838.pdf
        # Oda = outdoor -> box
        DucoboxSensorEntityDescription(
            key="TempOda",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            device_class=SensorDeviceClass.TEMPERATURE,
            value_fn=lambda data: _process_temperature(
                data.get("node_data", {}).get("Ventilation", {}).get("Sensor", {}).get("TempOda")
            ),
        ),
        # Sup = box -> house
        DucoboxSensorEntityDescription(
            key="TempSup",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            device_class=SensorDeviceClass.TEMPERATURE,
            value_fn=lambda data: _process_temperature(
                data.get("node_data", {}).get("Ventilation", {}).get("Sensor", {}).get("TempSup")
            ),
        ),
        # Eta = house -> box
        DucoboxSensorEntityDescription(
            key="TempEta",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            device_class=SensorDeviceClass.TEMPERATURE,
            value_fn=lambda data: _process_temperature(
                data.get("node_data", {}).get("Ventilation", {}).get("Sensor", {}).get("TempEta")
            ),
        ),
        # Eha = box -> outdoor
        DucoboxSensorEntityDescription(
            key="TempEha",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            device_class=SensorDeviceClass.TEMPERATURE,
            value_fn=lambda data: _process_temperature(
                data.get("node_data", {}).get("Ventilation", {}).get("Sensor", {}).get("TempEha")
            ),
        ),
        # Fan speed sensors
        DucoboxSensorEntityDescription(
            key="SpeedSup",
            native_unit_of_measurement="RPM",
            state_class=SensorStateClass.MEASUREMENT,
            device_class=SensorDeviceClass.SPEED,
            value_fn=lambda data: _process_speed(
                data.get("node_data", {}).get("Ventilation", {}).get("Fan", {}).get("SpeedSup")
            ),
        ),
        DucoboxSensorEntityDescription(
            key="SpeedEha",
            native_unit_of_measurement="RPM",
            state_class=SensorStateClass.MEASUREMENT,
            device_class=SensorDeviceClass.SPEED,
            value_fn=lambda data: _process_speed(
                data.get("node_data", {}).get("Ventilation", {}).get("Fan", {}).get("SpeedEha")
            ),
        ),
        # Pressure sensors
        DucoboxSensorEntityDescription(
            key="PressSup",
            native_unit_of_measurement=UnitOfPressure.PA,
            state_class=SensorStateClass.MEASUREMENT,
            device_class=SensorDeviceClass.PRESSURE,
            value_fn=lambda data: _process_pressure(
                data.get("node_data", {}).get("Ventilation", {}).get("Fan", {}).get("PressSup")
            ),
        ),
        DucoboxSensorEntityDescription(
            key="PressEha",
            native_unit_of_measurement=UnitOfPressure.PA,
            state_class=SensorStateClass.MEASUREMENT,
            device_class=SensorDeviceClass.PRESSURE,
            value_fn=lambda data: _process_pressure(
                data.get("node_data", {}).get("Ventilation", {}).get("Fan", {}).get("PressEha")
            ),
        ),
        # Filter time remaining
        DucoboxSensorEntityDescription(
            key="TimeFilterRemain",
            native_unit_of_measurement=UnitOfTime.DAYS,
            state_class=SensorStateClass.MEASUREMENT,
            device_class=SensorDeviceClass.DURATION,
            value_fn=lambda data: _process_timefilterremain(
                data.get("node_data", {}).get("HeatRecovery", {}).get("General", {}).get("TimeFilterRemain")
            ),
        ),
        # Bypass position
        DucoboxSensorEntityDescription(
            key="BypassPos",
            native_unit_of_measurement=PERCENTAGE,
            state_class=SensorStateClass.MEASUREMENT,
            value_fn=lambda data: _process_bypass_position(
                data.get("node_data", {}).get("HeatRecovery", {}).get("Bypass", {}).get("Pos")
            ),
        ),
    ],
}
