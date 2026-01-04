"""Pytest fixtures for testing."""

from unittest.mock import MagicMock

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
            "base_url": "https://192.168.1.100",
        },
        options={
            "debug_verbosity": 0,
        },
        unique_id="08:d1:f9:c4:63:20",
    )


@pytest.fixture
def mock_ducopy():
    """Return a mock DucoPy client."""
    mock_client = MagicMock()
    mock_client.client._board_type = "Connectivity Board"
    mock_client.client._generation = 2
    mock_client.get_nodes.return_value = MagicMock(
        Nodes=[
            MagicMock(
                Node=1,
                General=MagicMock(Type="BOX"),
            )
        ]
    )
    return mock_client


@pytest.fixture
async def hass_instance(hass: HomeAssistant):
    """Return a Home Assistant instance."""
    return hass
