from collections.abc import Callable
from dataclasses import dataclass
from homeassistant.components.sensor import (
    SensorEntityDescription,
)

@dataclass(frozen=True, kw_only=True)
class DucoboxSensorEntityDescription(SensorEntityDescription):
    """Describes a Ducobox sensor entity."""

    value_fn: Callable[[dict], float | None]


@dataclass(frozen=True, kw_only=True)
class DucoboxNodeSensorEntityDescription(SensorEntityDescription):
    """Describes a Ducobox node sensor entity."""

    value_fn: Callable[[dict], float | None]
    sensor_key: str
    node_type: str
    