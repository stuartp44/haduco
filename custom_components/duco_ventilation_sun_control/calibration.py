from custom_components.duco_ventilation_sun_control.ducobox_classes import DucoboxSensorEntityDescription, DucoboxNodeSensorEntityDescription
from common import ( 
    _process_calibration_state, 
    _process_calibration_status
)
from homeassistant.const import (
    EntityCategory,
)

CALIBRATION_SENSORS: tuple[DucoboxSensorEntityDescription, ...] = {
    DucoboxNodeSensorEntityDescription(
        key='CalibrationStatus',
        name='Calibration Status',
        value_fn=lambda data: _process_calibration_status(
            data.get('general_data').get("Ventilation", {}).get("Calibration", {}).get("Valid", {}).get("Val"),
        ),
        icon="mdi:progress-wrench",
        sensor_key='CalibrationStatus',
        node_type='BOX',
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    DucoboxNodeSensorEntityDescription(
        key='CalibrationState',
        name='Calibration State',
        value_fn=lambda data: _process_calibration_state(
            data.get('general_data').get("Ventilation", {}).get("Calibration", {}).get("State", {}).get("Val"),
        ),
        icon="mdi:progress-wrench",
        sensor_key='CalibrationState',
        node_type='BOX',
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
}