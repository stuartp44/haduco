from homeassistant.const import (
    EntityCategory,
)

from .common import _process_network_status
from .ducobox_classes import DucoboxNodeSensorEntityDescription, DucoboxSensorEntityDescription

DUCONETWORK_SENSORS: tuple[DucoboxSensorEntityDescription, ...] = {
    DucoboxNodeSensorEntityDescription(
        key='NetworkDuco',
        name='Network Status',
        value_fn=lambda data: _process_network_status(
            data.get('general_data').get("General", {}).get("NetworkDuco", {}).get("State", {}).get("Val"),
        ),
        icon="mdi:wifi-arrow-left-right",
        sensor_key='NetworkDuco',
        node_type='BOX',
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
}
