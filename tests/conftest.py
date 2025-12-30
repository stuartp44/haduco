"""Pytest fixtures for testing."""

import pytest
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.duco_ventilation_sun_control.const import DOMAIN


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations."""
    yield


@pytest.fixture
def mock_config_entry() -> MockConfigEntry:
    """Return a mock config entry."""
    return MockConfigEntry(
        domain=DOMAIN,
        data={
            "host": "192.168.1.100",
            "port": 80,
        },
        unique_id="test_unique_id",
    )


@pytest.fixture
async def hass_instance(hass: HomeAssistant):
    """Return a Home Assistant instance."""
    return hass
