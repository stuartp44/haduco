from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.device_registry import DeviceInfo


def get_device_info(
    hass: HomeAssistant,
    device_info: DeviceInfo,
    parent_identifier: tuple[str, str] | None,
    config_entry_id: str,
) -> DeviceInfo:
    """Return device info with the registered parent device ID."""
    if parent_identifier is None:
        return device_info

    return DeviceInfo(
        **device_info,
        via_device_id=dr.async_get_device_id_by_identifier(
            hass,
            parent_identifier,
            config_entry_id=config_entry_id,
        ),
    )
