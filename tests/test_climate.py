"""Tests for Aldes Climate entity."""

import asyncio
from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.components.climate import HVACAction, HVACMode
from homeassistant.const import ATTR_TEMPERATURE
from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util

from custom_components.aldes.climate import AldesClimateEntity
from custom_components.aldes.const import AirMode
from custom_components.aldes.entity import ThermostatApiEntity


@pytest.fixture
def mock_coordinator():
    """Mock the data update coordinator."""
    coordinator = MagicMock()
    coordinator.data = MagicMock()
    coordinator.api = MagicMock()
    coordinator.api.set_target_temperature = AsyncMock()
    coordinator.api.change_mode = AsyncMock()
    coordinator.async_request_refresh = AsyncMock()
    return coordinator


@pytest.fixture
def mock_thermostat_data():
    """Mock thermostat data."""
    return ThermostatApiEntity({
        "ThermostatId": 1,
        "Name": "Salon",
        "Number": 1,
        "TemperatureSet": 19,
        "CurrentTemperature": 20.5
    })


@pytest.fixture
def climate_entity(mock_coordinator, mock_thermostat_data):
    """Create a climate entity instance."""
    # Setup coordinator data structure
    mock_coordinator.data.indicator.thermostats = [mock_thermostat_data]
    mock_coordinator.data.indicator.current_air_mode = AirMode.HEAT_COMFORT
    mock_coordinator.data.is_connected = True
    mock_coordinator.data.week_planning = []
    
    entity = AldesClimateEntity(
        mock_coordinator,
        MagicMock(), # config_entry
        mock_thermostat_data
    )
    entity.hass = MagicMock(spec=HomeAssistant)
    entity.async_write_ha_state = MagicMock()
    
    # Initial update
    entity._async_update_attrs()
    
    return entity


async def test_optimistic_state_temperature(climate_entity):
    """Test optimistic state update for temperature."""
    # Initial state
    assert climate_entity.target_temperature == 19
    
    # Set new temperature
    await climate_entity.async_set_temperature(temperature=22)
    
    # Verify API called
    climate_entity.coordinator.api.set_target_temperature.assert_called_with(
        climate_entity.modem, 1, "Salon", 22
    )
    
    # Verify optimistic state is set immediately
    assert climate_entity.target_temperature == 22
    assert climate_entity._optimistic_end_time is not None
    
    # Simulate update from coordinator with OLD data (API lag)
    climate_entity.coordinator.data.indicator.thermostats[0].temperature_set = 19
    climate_entity._async_update_attrs()
    
    # Should still show 22 (optimistic)
    assert climate_entity.target_temperature == 22
    
    # Fast forward time past optimistic duration (60s)
    with patch("custom_components.aldes.climate.dt_util.now") as mock_now:
        mock_now.return_value = dt_util.now() + timedelta(seconds=61)
        
        # Update again
        climate_entity._async_update_attrs()
        
        # Should revert to coordinator data (19) if API failed to update
        assert climate_entity.target_temperature == 19


async def test_retry_logic_temperature(climate_entity):
    """Test retry logic when API update is silent."""
    # Mock asyncio.sleep to avoid waiting
    with patch("asyncio.sleep", new_callable=AsyncMock):
        # Set temperature
        await climate_entity.async_set_temperature(temperature=22)
        
        # Reset API mock to track retries
        climate_entity.coordinator.api.set_target_temperature.reset_mock()
        
        # Simulate verification task running
        # We need to manually trigger the verification logic
        # In real life this runs in background task
        
        # 1. First verification (T+60s)
        # Coordinator still has old data (19)
        climate_entity.coordinator.data.indicator.thermostats[0].temperature_set = 19
        
        await climate_entity._verify_temperature_change_after_delay(attempt=1)
        
        # Should have retried API call
        climate_entity.coordinator.api.set_target_temperature.assert_called_with(
            climate_entity.modem, 1, "Salon", 22
        )
        
        # Should have extended optimistic time
        assert climate_entity._optimistic_end_time > dt_util.now() + timedelta(seconds=30)


async def test_hvac_action_heating(climate_entity):
    """Test HVAC action logic."""
    # Current: 20.5, Target: 19 -> IDLE
    assert climate_entity.hvac_action == HVACAction.IDLE
    
    # Set target: 22 -> HEATING
    await climate_entity.async_set_temperature(temperature=22)
    assert climate_entity.hvac_action == HVACAction.HEATING


async def test_eco_mode_offset(climate_entity):
    """Test temperature offset in ECO mode."""
    # Switch to ECO mode
    climate_entity.coordinator.data.indicator.current_air_mode = AirMode.HEAT_ECO
    # API sends 19°C (PAC target), but user should see 17°C (19 - 2)
    climate_entity.coordinator.data.indicator.thermostats[0].temperature_set = 19
    
    climate_entity._async_update_attrs()
    
    assert climate_entity.target_temperature == 17
    
    # User sets 18°C -> API should receive 20°C (18 + 2)
    await climate_entity.async_set_temperature(temperature=18)
    
    climate_entity.coordinator.api.set_target_temperature.assert_called_with(
        climate_entity.modem, 1, "Salon", 20
    )
