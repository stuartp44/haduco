from homeassistant.const import EntityCategory

from .common import _process_calibration_state, _process_calibration_status
from .ducobox_classes import (
    DucoboxNodeSensorEntityDescription,
    DucoboxSensorEntityDescription,
)


def _get_nested_val(data: dict, *path: str) -> object | None:
    current: object = data
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    if isinstance(current, dict):
        return current.get("Val")
    return current


def _get_calibration_value(data: dict, key: str) -> object | None:
    """Return calibration value from known locations."""
    paths = (
        ("general_data", "Ventilation", "Calibration", key),
        ("general_data", "Calibration", key),
        ("general_data", "EnergyCalib", key),
        ("general_data", "api_info", "EnergyCalib", key),
        ("node_data", "Calibration", key),
        ("node_data", "EnergyCalib", key),
        ("node_data", "Ventilation", "EnergyCalib", key),
        ("node_data", "HeatRecovery", "EnergyCalib", key),
    )
    for path in paths:
        if (value := _get_nested_val(data, *path)) is not None:
            return value
    return None


def _get_calibration_bool(data: dict, primary_key: str, fallback_key: str) -> bool | None:
    value = _get_calibration_value(data, primary_key)
    if value is None:
        value = _get_calibration_value(data, fallback_key)
    return value if isinstance(value, bool) else None


def _get_calibration_str(data: dict, primary_key: str, fallback_key: str) -> str | None:
    value = _get_calibration_value(data, primary_key)
    if value is None:
        value = _get_calibration_value(data, fallback_key)
    return value if isinstance(value, str) else None


CALIBRATION_SENSORS: tuple[DucoboxSensorEntityDescription, ...] = (
    DucoboxNodeSensorEntityDescription(
        key="CalibrationStatus",
        value_fn=lambda data: _process_calibration_status(_get_calibration_bool(data, "Valid", "CalibIsValid")),
        icon="mdi:progress-wrench",
        sensor_key="CalibrationStatus",
        node_type="BOX",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    DucoboxNodeSensorEntityDescription(
        key="CalibrationState",
        value_fn=lambda data: _process_calibration_state(_get_calibration_str(data, "State", "CalibState")),
        icon="mdi:progress-wrench",
        sensor_key="CalibrationState",
        node_type="BOX",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)
