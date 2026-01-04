from homeassistant.const import (
    EntityCategory,
)

from .common import _process_calibration_state, _process_calibration_status
from .ducobox_classes import DucoboxNodeSensorEntityDescription, DucoboxSensorEntityDescription

CALIBRATION_SENSORS: tuple[DucoboxSensorEntityDescription, ...] = (
    DucoboxNodeSensorEntityDescription(
        key="CalibrationStatus",
        name="Calibration Status",
        value_fn=lambda data: _process_calibration_status(
            data.get("general_data", {}).get("Calibration", {}).get("CalibIsValid", {}).get("Val"),
        ),
        icon="mdi:progress-wrench",
        sensor_key="CalibrationStatus",
        node_type="BOX",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    DucoboxNodeSensorEntityDescription(
        key="CalibrationState",
        name="Calibration State",
        value_fn=lambda data: _process_calibration_state(
            data.get("general_data", {}).get("Calibration", {}).get("CalibState", {}).get("Val"),
        ),
        icon="mdi:progress-wrench",
        sensor_key="CalibrationState",
        node_type="BOX",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)
