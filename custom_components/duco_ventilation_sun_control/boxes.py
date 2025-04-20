from custom_components.duco_ventilation_sun_control.ducobox_classes import DucoboxSensorEntityDescription, DucoboxNodeSensorEntityDescription
from homeassistant.const import (
    UnitOfTemperature,
    UnitOfTime,
    PERCENTAGE,
    UnitOfPressure
)
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorStateClass,
)
from common import (
    _process_bypass_position, 
    _process_pressure, 
    _process_speed, 
    _process_temperature, 
    _process_timefilterremain,
)

BOX_SENSORS: tuple[DucoboxSensorEntityDescription, ...] = {
    'FOCUS': [
        DucoboxNodeSensorEntityDescription(
            key='Mode',
            name='Ventilation Mode',
            value_fn=lambda node: node.get('node_data').get('Ventilation', {}).get('Mode'),
            icon="mdi:fan",
            sensor_key='Mode',
            node_type='BOX',
        ),
        DucoboxNodeSensorEntityDescription(
            key='State',
            name='Ventilation State',
            value_fn=lambda node: node.get('node_data').get('Ventilation', {}).get('State'),
            icon="mdi:fan-auto",
            sensor_key='State',
            node_type='BOX',
        ),
        DucoboxNodeSensorEntityDescription(
            key='FlowLvlTgt',
            name='Flow Level Target',
            native_unit_of_measurement=PERCENTAGE,
            value_fn=lambda node: node.get('node_data').get('Ventilation', {}).get('FlowLvlTgt'),
            icon="mdi:fan-chevron-up",
            sensor_key='FlowLvlTgt',
            node_type='BOX',
        ),
        DucoboxNodeSensorEntityDescription(
            key='TimeStateRemain',
            name='Time State Remaining',
            native_unit_of_measurement=UnitOfTime.SECONDS,
            value_fn=lambda node: node.get('node_data').get('Ventilation', {}).get('TimeStateRemain'),
            icon="mdi:fan-clock",
            sensor_key='TimeStateRemain',
            node_type='BOX',
        ),
        DucoboxNodeSensorEntityDescription(
            key='TimeStateEnd',
            name='Time State End',
            native_unit_of_measurement=UnitOfTime.SECONDS,
            value_fn=lambda node: node.get('node_data').get('Ventilation', {}).get('TimeStateEnd'),
            icon="mdi:fan-off",
            sensor_key='TimeStateEnd',
            node_type='BOX',
        ),
    ],
    'NOT_SURE': [
        # Temperature sensors
        # relevant ducobox documentation: https://www.duco.eu/Wes/CDN/1/Attachments/installation-guide-DucoBox-Energy-Comfort-(Plus)-(en)_638635518879333838.pdf
        # Oda = outdoor -> box
        DucoboxSensorEntityDescription(
            key="TempOda",
            name="Outdoor Temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            device_class=SensorDeviceClass.TEMPERATURE,
            value_fn=lambda data: _process_temperature(
                data.get('node_data').get('Ventilation', {}).get('Sensor', {}).get('TempOda', {}).get('Val')
            ),
        ),
        # Sup = box -> house
        DucoboxSensorEntityDescription(
            key="TempSup",
            name="Supply Temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            device_class=SensorDeviceClass.TEMPERATURE,
            value_fn=lambda data: _process_temperature(
                data.get('node_data').get('Ventilation', {}).get('Sensor', {}).get('TempSup', {}).get('Val')
            ),
        ),
        # Eta = house -> box
        DucoboxSensorEntityDescription(
            key="TempEta",
            name="Extract Temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            device_class=SensorDeviceClass.TEMPERATURE,
            value_fn=lambda data: _process_temperature(
                data.get('node_data').get('Ventilation', {}).get('Sensor', {}).get('TempEta', {}).get('Val')
            ),
        ),
        # Eha = box -> outdoor
        DucoboxSensorEntityDescription(
            key="TempEha",
            name="Exhaust Temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            device_class=SensorDeviceClass.TEMPERATURE,
            value_fn=lambda data: _process_temperature(
                data.get('node_data').get('Ventilation', {}).get('Sensor', {}).get('TempEha', {}).get('Val')
            ),
        ),
        # Fan speed sensors
        DucoboxSensorEntityDescription(
            key="SpeedSup",
            name="Supply Fan Speed",
            native_unit_of_measurement="RPM",
            state_class=SensorStateClass.MEASUREMENT,
            device_class=SensorDeviceClass.SPEED,
            value_fn=lambda data: _process_speed(
                data.get('node_data').get('Ventilation', {}).get('Fan', {}).get('SpeedSup', {}).get('Val')
            ),
        ),
        DucoboxSensorEntityDescription(
            key="SpeedEha",
            name="Exhaust Fan Speed",
            native_unit_of_measurement="RPM",
            state_class=SensorStateClass.MEASUREMENT,
            device_class=SensorDeviceClass.SPEED,
            value_fn=lambda data: _process_speed(
                data.get('node_data').get('Ventilation', {}).get('Fan', {}).get('SpeedEha', {}).get('Val')
            ),
        ),
        # Pressure sensors
        DucoboxSensorEntityDescription(
            key="PressSup",
            name="Supply Pressure",
            native_unit_of_measurement=UnitOfPressure.PA,
            state_class=SensorStateClass.MEASUREMENT,
            device_class=SensorDeviceClass.PRESSURE,
            value_fn=lambda data: _process_pressure(
                data.get('node_data').get('Ventilation', {}).get('Fan', {}).get('PressSup', {}).get('Val')
            ),
        ),
        DucoboxSensorEntityDescription(
            key="PressEha",
            name="Exhaust Pressure",
            native_unit_of_measurement=UnitOfPressure.PA,
            state_class=SensorStateClass.MEASUREMENT,
            device_class=SensorDeviceClass.PRESSURE,
            value_fn=lambda data: _process_pressure(
                data.get('Ventilation', {}).get('Fan', {}).get('PressEha', {}).get('Val')
            ),
        ),

        # Filter time remaining
        DucoboxSensorEntityDescription(
            key="TimeFilterRemain",
            name="Filter Time Remaining",
            native_unit_of_measurement=UnitOfTime.DAYS,  # Assuming the value is in days
            state_class=SensorStateClass.MEASUREMENT,
            device_class=SensorDeviceClass.DURATION,
            value_fn=lambda data: _process_timefilterremain(
                data.get('node_data').get('HeatRecovery', {}).get('General', {}).get('TimeFilterRemain', {}).get('Val')
            ),
        ),
        # Bypass position
        DucoboxSensorEntityDescription(
            key="BypassPos",
            name="Bypass Position",
            native_unit_of_measurement=PERCENTAGE,
            state_class=SensorStateClass.MEASUREMENT,
            value_fn=lambda data: _process_bypass_position(
                data.get('HeatRecovery', {}).get('Bypass', {}).get('Pos', {}).get('Val')
            ),
        ),
    ]
}