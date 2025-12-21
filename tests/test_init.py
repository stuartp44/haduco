"""Test the DUCO Ventilation & Sun Control integration setup."""
from unittest.mock import patch

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntryState
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.duco_ventilation_sun_control.const import DOMAIN


@pytest.mark.asyncio
async def test_setup_entry(hass: HomeAssistant, mock_config_entry: MockConfigEntry):
    """Test setting up the integration."""
    mock_config_entry.add_to_hass(hass)

    with patch(
        "custom_components.duco_ventilation_sun_control.DucoboxDataUpdateCoordinator.async_config_entry_first_refresh"
    ):
        assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    # Verify the entry is loaded
    assert mock_config_entry.state == ConfigEntryState.LOADED
    assert DOMAIN in hass.data


@pytest.mark.asyncio
async def test_unload_entry(hass: HomeAssistant, mock_config_entry: MockConfigEntry):
    """Test unloading the integration."""
    mock_config_entry.add_to_hass(hass)

    with patch(
        "custom_components.duco_ventilation_sun_control.DucoboxDataUpdateCoordinator.async_config_entry_first_refresh"
    ):
        assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    assert await hass.config_entries.async_unload(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    # Verify the entry is unloaded
    assert mock_config_entry.state == ConfigEntryState.NOT_LOADED
