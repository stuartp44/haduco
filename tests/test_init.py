"""Test the DUCO Ventilation & Sun Control integration setup."""

from unittest.mock import MagicMock, patch

import pytest
from homeassistant.config_entries import ConfigEntryNotReady, ConfigEntryState
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.duco_ventilation_sun_control.const import DOMAIN


@pytest.mark.asyncio
async def test_setup_entry(hass: HomeAssistant, mock_config_entry: MockConfigEntry, mock_ducopy):
    """Test setting up the integration."""
    mock_config_entry.add_to_hass(hass)

    with patch("custom_components.duco_ventilation_sun_control.DucoPy", return_value=mock_ducopy):
        assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    # Verify the entry is loaded
    assert mock_config_entry.state == ConfigEntryState.LOADED
    assert DOMAIN in hass.data
    assert hass.data[DOMAIN] == mock_ducopy


@pytest.mark.asyncio
async def test_setup_entry_connection_error(hass: HomeAssistant, mock_config_entry: MockConfigEntry):
    """Test setup fails when connection to device fails."""
    mock_config_entry.add_to_hass(hass)

    with patch(
        "custom_components.duco_ventilation_sun_control.DucoPy",
        side_effect=Exception("Connection refused"),
    ):
        with pytest.raises(ConfigEntryNotReady):
            await hass.config_entries.async_setup(mock_config_entry.entry_id)

    # Verify the entry is not loaded
    assert mock_config_entry.state == ConfigEntryState.SETUP_ERROR


@pytest.mark.asyncio
async def test_unload_entry(hass: HomeAssistant, mock_config_entry: MockConfigEntry, mock_ducopy):
    """Test unloading the integration."""
    mock_config_entry.add_to_hass(hass)

    with patch("custom_components.duco_ventilation_sun_control.DucoPy", return_value=mock_ducopy):
        assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    assert await hass.config_entries.async_unload(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    # Verify the entry is unloaded
    assert mock_config_entry.state == ConfigEntryState.NOT_LOADED
    # Verify DucoPy client was closed
    mock_ducopy.close.assert_called_once()
    # Verify data was cleaned up
    assert DOMAIN not in hass.data


@pytest.mark.asyncio
async def test_log_level_mapping(hass: HomeAssistant, mock_ducopy):
    """Test that debug verbosity is correctly mapped to log levels."""
    test_cases = [
        (0, "ERROR"),
        (1, "WARNING"),
        (2, "INFO"),
        (3, "DEBUG"),
    ]

    for verbosity, expected_log_level in test_cases:
        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"base_url": "https://192.168.1.100"},
            options={"debug_verbosity": verbosity},
            unique_id=f"test_{verbosity}",
        )
        entry.add_to_hass(hass)

        with patch("custom_components.duco_ventilation_sun_control.DucoPy") as mock_ducopy_class:
            mock_ducopy_class.return_value = mock_ducopy
            await hass.config_entries.async_setup(entry.entry_id)
            await hass.async_block_till_done()

            # Verify DucoPy was initialized with correct log level
            mock_ducopy_class.assert_called_once()
            call_kwargs = mock_ducopy_class.call_args[1]
            assert call_kwargs["log_level"] == expected_log_level

            # Clean up
            await hass.config_entries.async_unload(entry.entry_id)
            await hass.async_block_till_done()
            mock_ducopy_class.reset_mock()
