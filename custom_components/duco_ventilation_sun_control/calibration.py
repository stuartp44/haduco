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
            # Connectivity: Ventilation.Calibration.Valid, Communication/Print: Calibration.CalibIsValid
            data.get("general_data", {}).get("Ventilation", {}).get("Calibration", {}).get("Valid", {}).get("Val")
            or data.get("general_data", {}).get("Calibration", {}).get("CalibIsValid", {}).get("Val")
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
            # Connectivity: Ventilation.Calibration.State, Communication/Print: Calibration.CalibState
            data.get("general_data", {}).get("Ventilation", {}).get("Calibration", {}).get("State", {}).get("Val")
            or data.get("general_data", {}).get("Calibration", {}).get("CalibState", {}).get("Val")
        ),
        icon="mdi:progress-wrench",
        sensor_key="CalibrationState",
        node_type="BOX",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)
