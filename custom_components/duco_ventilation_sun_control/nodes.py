from custom_components.duco_ventilation_sun_control.ducoboxc_classes import DucoboxNodeSensorEntityDescription
from common import (
    _process_node_co2, 
    _process_node_humidity, 
    _process_node_iaq, 
    _process_node_temperature
)
from homeassistant.components.sensor import (
    SensorDeviceClass,
)
from homeassistant.const import (
    UnitOfTemperature,
    PERCENTAGE,
    CONCENTRATION_PARTS_PER_MILLION,

)

NODE_SENSORS: dict[str, list[DucoboxNodeSensorEntityDescription]] = {
    'UCCO2': [
        DucoboxNodeSensorEntityDescription(
            key='Temp',
            name='Temperature',
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            device_class=SensorDeviceClass.TEMPERATURE,
            value_fn=lambda node: _process_node_temperature(
                node.get('node_data').get('Sensor', {}).get('data', {}).get('Temp')
            ),
            sensor_key='Temp',
            node_type='UCCO2',
        ),
        DucoboxNodeSensorEntityDescription(
            key='Co2',
            name='CO₂',
            native_unit_of_measurement=CONCENTRATION_PARTS_PER_MILLION,
            device_class=SensorDeviceClass.CO2,
            value_fn=lambda node: _process_node_co2(
                node.get('node_data').get('Sensor', {}).get('data', {}).get('Co2')
            ),
            sensor_key='Co2',
            node_type='UCCO2',
        ),
        DucoboxNodeSensorEntityDescription(
            key='IaqCo2',
            name='CO₂ Air Quality',
            native_unit_of_measurement=PERCENTAGE,
            icon="mdi:crosshairs",
            value_fn=lambda node: _process_node_iaq(
                node.get('node_data').get('Sensor', {}).get('data', {}).get('IaqCo2')
            ),
            sensor_key='IaqCo2',
            node_type='UCCO2',
        ),
    ],
    'BSRH': [
        DucoboxNodeSensorEntityDescription(
            key='Temp',
            name='Temperature',
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            device_class=SensorDeviceClass.TEMPERATURE,
            value_fn=lambda node: _process_node_temperature(
                node.get('node_data').get('Sensor', {}).get('data', {}).get('Temp')
            ),
            sensor_key='Temp',
            node_type='BSRH',
        ),
        DucoboxNodeSensorEntityDescription(
            key='Rh',
            name='Relative Humidity',
            native_unit_of_measurement=PERCENTAGE,
            device_class=SensorDeviceClass.HUMIDITY,
            value_fn=lambda node: _process_node_humidity(
                node.get('node_data').get('Sensor', {}).get('data', {}).get('Rh')
            ),
            sensor_key='Rh',
            node_type='BSRH',
        ),
        DucoboxNodeSensorEntityDescription(
            key='IaqRh',
            name='Humidity Air Quality',
            native_unit_of_measurement=PERCENTAGE,
            icon="mdi:crosshairs",
            value_fn=lambda node: _process_node_iaq(
                node.get('node_data').get('Sensor', {}).get('data', {}).get('IaqRh')
            ),
            sensor_key='IaqRh',
            node_type='BSRH',
        ),
    ],
    'VLVRH': [
        DucoboxNodeSensorEntityDescription(
            key='Mode',
            name='Ventilation Mode',
            value_fn=lambda node: node.get('node_data').get('Ventilation', {}).get('Mode'),
            icon="mdi:fan-auto",
            sensor_key='Mode',
            node_type='VLVRH',
        ),
        DucoboxNodeSensorEntityDescription(
            key='FlowLvlTgt',
            name='Flow Level Target',
            native_unit_of_measurement=PERCENTAGE,
            value_fn=lambda node: node.get('node_data').get('Ventilation', {}).get('FlowLvlTgt'),
            icon="mdi:fan-chevron-up",
            sensor_key='FlowLvlTgt',
            node_type='VLVRH',
        ),
        DucoboxNodeSensorEntityDescription(
            key='IaqRh',
            name='Humidity Air Quality',
            native_unit_of_measurement=PERCENTAGE,
            icon="mdi:crosshairs",
            value_fn=lambda node: _process_node_iaq(
                node.get('node_data').get('Sensor', {}).get('data', {}).get('IaqRh')
            ),
            sensor_key='IaqRh',
            node_type='VLVRH',
        ),
        DucoboxNodeSensorEntityDescription(
            key='Rh',
            name='Humidity',
            native_unit_of_measurement=PERCENTAGE,
            device_class=SensorDeviceClass.HUMIDITY,
            value_fn=lambda node: _process_node_iaq(
                node.get('node_data').get('Sensor', {}).get('data', {}).get('Rh')
            ),
            sensor_key='Rh',
            node_type='VLVRH',
        ),
        DucoboxNodeSensorEntityDescription(
            key='Temp',
            name='Temperature',
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            device_class=SensorDeviceClass.TEMPERATURE,
            value_fn=lambda node: _process_node_temperature(
                node.get('node_data').get('Sensor', {}).get('data', {}).get('Temp')
            ),
            sensor_key='Temp',
            node_type='BSRH',
        ),
    ],
}