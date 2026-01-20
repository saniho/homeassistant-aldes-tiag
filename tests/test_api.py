"""Tests for Aldes API client."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest
from aiohttp import ClientError, ClientSession

from custom_components.aldes.api import (
    AldesApi,
    AuthenticationError,
    CommandUid,
)
from custom_components.aldes.entity import DataApiEntity


@pytest.fixture
def mock_session():
    """Mock aiohttp session."""
    session = MagicMock(spec=ClientSession)
    session.post = AsyncMock()
    session.get = AsyncMock()
    session.patch = AsyncMock()
    return session


@pytest.fixture
def api(mock_session):
    """Return AldesApi instance."""
    return AldesApi("test_user", "test_password", mock_session)


async def test_authenticate_success(api, mock_session):
    """Test successful authentication."""
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json.return_value = {"access_token": "fake_token"}
    mock_session.post.return_value.__aenter__.return_value = mock_response

    await api.authenticate()

    assert api.token == "fake_token"
    
    # Verify headers
    call_kwargs = mock_session.post.call_args[1]
    headers = call_kwargs["headers"]
    assert headers["User-Agent"] == "AldesConnect/4.21"
    assert headers["apikey"] == "XQibgk1ozo1wjVQcvcoFQqMl3pjEwcRv"
    assert headers["sdkVersion"] == "a:17.0.0"


async def test_authenticate_failure(api, mock_session):
    """Test authentication failure."""
    mock_response = AsyncMock()
    mock_response.status = 401
    mock_response.text.return_value = "Unauthorized"
    mock_session.post.return_value.__aenter__.return_value = mock_response

    with pytest.raises(AuthenticationError):
        await api.authenticate()


async def test_fetch_data_success(api, mock_session):
    """Test fetching data successfully."""
    api.token = "valid_token"
    
    mock_data = [{
        "indicator": {
            "current_air_mode": "A",
            "current_water_mode": "L",
            "thermostats": []
        },
        "modem": "MODEM123",
        "isConnected": True
    }]
    
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json.return_value = mock_data
    mock_session.get.return_value.__aenter__.return_value = mock_response

    result = await api.fetch_data()

    assert isinstance(result, DataApiEntity)
    assert result.modem == "MODEM123"
    assert result.is_connected is True


async def test_change_mode(api, mock_session):
    """Test changing mode."""
    api.token = "valid_token"
    
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json.return_value = {"success": True}
    mock_session.post.return_value.__aenter__.return_value = mock_response

    await api.change_mode("MODEM123", "B", CommandUid.AIR_MODE)

    # Verify API call
    mock_session.post.assert_called()
    call_args = mock_session.post.call_args
    url = call_args[0][0]
    assert "commands" in url
    
    json_payload = call_args[1]["json"]
    assert json_payload["method"] == "changeMode"
    assert json_payload["params"] == ["B"]


async def test_temperature_worker(api, mock_session):
    """Test temperature worker queue processing."""
    api.token = "valid_token"
    
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_session.patch.return_value.__aenter__.return_value = mock_response

    # Mock sleep to speed up test
    with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
        # Add request to queue
        await api.set_target_temperature("MODEM123", 1, "Thermostat 1", 21)
        
        # Wait a bit for worker to process
        # We need to yield control to the event loop
        await asyncio.sleep(0.1)
        
        # Verify API was called
        mock_session.patch.assert_called()
        call_args = mock_session.patch.call_args
        url = call_args[0][0]
        assert "updateThermostats" in url
        
        json_payload = call_args[1]["json"]
        assert json_payload[0]["TemperatureSet"] == 21
        
        # Verify sleep was called (delay between requests)
        mock_sleep.assert_called()


async def test_auth_interceptor_reauth(api, mock_session):
    """Test automatic re-authentication on 401."""
    api.token = "expired_token"
    
    # First call returns 401, second call returns 200
    response_401 = AsyncMock()
    response_401.status = 401
    
    response_200 = AsyncMock()
    response_200.status = 200
    response_200.json.return_value = {"data": "ok"}
    
    # Mock authenticate to update token
    auth_response = AsyncMock()
    auth_response.status = 200
    auth_response.json.return_value = {"access_token": "new_token"}
    
    # Setup side effects
    # 1. GET request (fails 401)
    # 2. POST auth (succeeds)
    # 3. GET request retry (succeeds 200)
    
    # We need to mock the context managers properly
    # This is tricky with aiohttp mocks, so we'll mock the _request_with_auth_interceptor logic
    # or better, mock the session calls sequence
    
    # Let's mock authenticate method directly to simplify
    with patch.object(api, 'authenticate', new_callable=AsyncMock) as mock_auth:
        mock_auth.side_effect = lambda: setattr(api, '_token', 'new_token')
        
        # Configure session to return 401 then 200
        mock_session.get.side_effect = [
            AsyncMock(__aenter__=AsyncMock(return_value=response_401)),
            AsyncMock(__aenter__=AsyncMock(return_value=response_200))
        ]
        
        await api._api_request("get", "http://test.url")
        
        # Verify authenticate was called
        mock_auth.assert_called_once()
        
        # Verify request was retried
        assert mock_session.get.call_count == 2
        
        # Verify second call used new token
        call_kwargs = mock_session.get.call_args_list[1][1]
        assert call_kwargs["headers"]["Authorization"] == "Bearer new_token"
