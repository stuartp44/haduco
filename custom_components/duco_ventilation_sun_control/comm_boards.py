from .ducobox_classes import DucoboxSensorEntityDescription
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.const import (
    UnitOfTime,
    EntityCategory,
)
from common import (
    _process_rssi,
    _process_uptime
)

COMMBOARD_SENSORS: tuple[DucoboxSensorEntityDescription, ...] = (
    # Wi-Fi signal strength
    DucoboxSensorEntityDescription(
        key="RssiWifi",
        name="Wi-Fi Signal Strength",
        native_unit_of_measurement="dBm",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: _process_rssi(
            data.get('General', {}).get('Lan', {}).get('RssiWifi', {}).get('Val')
        ),
    ),
    # Device uptime
    DucoboxSensorEntityDescription(
        key="UpTime",
        name="Device Uptime",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        state_class=SensorStateClass.TOTAL_INCREASING,
        device_class=SensorDeviceClass.DURATION,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: _process_uptime(
            data.get('General', {}).get('Board', {}).get('UpTime', {}).get('Val')
        ),
    ),
)
