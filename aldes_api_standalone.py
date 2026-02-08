#!/usr/bin/env python3
"""Standalone Aldes API client - No Home Assistant dependencies."""

import asyncio
import base64
import contextlib
import json
import logging
from datetime import UTC, datetime
from enum import IntEnum
from typing import Any

import aiohttp
import backoff
from aiohttp import ClientError, ClientTimeout

_LOGGER = logging.getLogger(__name__)

HTTP_OK = 200
HTTP_UNAUTHORIZED = 401
REQUEST_DELAY = 5  # Delay between queued requests in seconds
CACHE_TTL = 300  # Cache TTL in seconds (5 minutes)


class CommandUid(IntEnum):
    """Command UIDs for API requests."""

    AIR_MODE = 1
    HOT_WATER = 2


class AuthenticationError(Exception):
    """Authentication error."""

    pass


class AldesApi:
    """Aldes API client - Standalone version without Home Assistant."""

    _API_URL_BASE = "https://aldesiotsuite-aldeswebapi.azurewebsites.net"
    _API_URL_TOKEN = f"{_API_URL_BASE}/oauth2/token"
    _API_URL_PRODUCTS = (
        f"{_API_URL_BASE}/aldesoc/v5/users/me/products"
    )

    _AUTHORIZATION_HEADER_KEY = "Authorization"
    _TOKEN_TYPE = "Bearer"

    # Constants from official app analysis
    _API_KEY = "XQibgk1ozo1wjVQcvcoFQqMl3pjEwcRv"
    _USER_AGENT = "AldesConnect/4.21"
    _SDK_VERSION = "a:17.0.0"

    def __init__(
        self,
        username: str,
        password: str,
        session: aiohttp.ClientSession,
        token: str = "",
    ) -> None:
        """Initialize Aldes API client."""
        self._username = username
        self._password = password
        self._session = session
        self._token = token
        self._timeout = ClientTimeout(total=30)
        self._cache: dict[str, Any] = {}
        self._cache_timestamp: dict[str, datetime] = {}
        self.queue_target_temperature: (
            asyncio.Queue[tuple[str, int, str, Any]] | None
        ) = None
        self._temperature_task: asyncio.Task[None] | None = None

    async def _ensure_temperature_worker_started(self) -> None:
        """Ensure the temperature worker task is started."""
        if self._temperature_task is None or self._temperature_task.done():
            _LOGGER.debug("Starting temperature worker task")
            if self.queue_target_temperature is None:
                self.queue_target_temperature = asyncio.Queue()
            self._temperature_task = asyncio.create_task(self._temperature_worker())
        else:
            _LOGGER.debug("Temperature worker task already running")

    def _log_request_details(
        self, method: str, url: str, headers: dict, data: Any = None
    ) -> None:
        """Log request details for debugging with sensitive data masking."""
        _LOGGER.debug("=== Request Details ===")
        _LOGGER.debug("Method: %s", method)
        _LOGGER.debug("URL: %s", url)
        # Log headers excluding sensitive auth info if needed
        safe_headers = {
            k: v for k, v in headers.items() if k.lower() != "authorization"
        }
        _LOGGER.debug("Headers: %s", safe_headers)

        if data:
            safe_data = data
            if isinstance(data, dict) and "password" in data:
                safe_data = data.copy()
                safe_data["password"] = "***"
            _LOGGER.debug("Data: %s", safe_data)

    @backoff.on_exception(
        backoff.expo,
        (ClientError, TimeoutError),
        max_tries=3,
        max_time=60,
    )
    async def authenticate(self) -> None:
        """Authenticate and retrieve access token from Aldes API."""
        _LOGGER.info("Authenticating with Aldes API...")

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "User-Agent": self._USER_AGENT,
            "apikey": self._API_KEY,
            "sdkVersion": self._SDK_VERSION,
        }

        data: dict[str, str] = {
            "grant_type": "password",
            "username": self._username,
            "password": self._password,
            "scope": "openid profile email offline_access",
        }

        self._log_request_details("POST", self._API_URL_TOKEN, headers, data)

        try:
            async with self._session.post(
                self._API_URL_TOKEN, data=data, headers=headers, timeout=self._timeout
            ) as response:
                if response.status == HTTP_OK:
                    json_resp = await response.json()
                    self._token = json_resp["access_token"]
                    _LOGGER.info("Successfully authenticated with Aldes API")
                else:
                    response_text = await response.text()
                    error_msg = (
                        f"Authentication failed with status {response.status}: "
                        f"{response_text}"
                    )
                    _LOGGER.error(error_msg)
                    raise AuthenticationError(error_msg)
        except (ClientError, TimeoutError) as err:
            error_msg = f"Authentication request failed: {err}"
            _LOGGER.exception(error_msg)
            raise AuthenticationError(error_msg) from err

    @backoff.on_exception(
        backoff.expo,
        (ClientError, TimeoutError),
        max_tries=3,
        max_time=60,
    )
    async def _api_request(
        self, method: str, url: str, **kwargs: Any
    ) -> list[Any] | dict[str, Any]:
        """Execute API request with retry, timeout and error handling."""
        # Verify token exists
        if not self._token:
            raise AuthenticationError("Token not available. Please authenticate first.")

        # Generate cache key from method and url
        cache_key = f"{method}:{url}"

        try:
            # Add timeout to kwargs if not already present
            if "timeout" not in kwargs:
                kwargs["timeout"] = self._timeout

            request_func = getattr(self._session, method.lower())

            # Prepare headers with auth
            headers = kwargs.get("headers", {})
            headers[self._AUTHORIZATION_HEADER_KEY] = f"{self._TOKEN_TYPE} {self._token}"
            kwargs["headers"] = headers

            # Execute request
            async with request_func(url, **kwargs) as response:
                if response.status == HTTP_OK:
                    data = await response.json()
                    # Store in cache for emergency fallback
                    self._cache[cache_key] = data
                    self._cache_timestamp[cache_key] = datetime.now(UTC)
                    _LOGGER.debug("Stored data in emergency cache for %s", cache_key)
                    return data
                else:
                    response_text = await response.text()
                    msg = (
                        f"API request failed with status {response.status}: {response_text}"
                    )
                    _LOGGER.error(msg)
                    _LOGGER.error("URL: %s", url)
                    _LOGGER.error(
                        "Auth headers sent: Authorization=%s",
                        "Bearer " + self._token[:20] + "..." if self._token else "None"
                    )
                    raise ClientError(msg)
        except Exception as err:
            # Log specific error type
            if isinstance(err, ClientError | TimeoutError):
                _LOGGER.exception("API request error")
            elif isinstance(err, KeyError | ValueError):
                _LOGGER.exception("Error parsing API response")
            else:
                _LOGGER.exception("Unexpected error during API request")

            # Use cached data as fallback for ANY error (regardless of age)
            if cache_key in self._cache:
                cache_age = datetime.now(UTC) - self._cache_timestamp.get(
                    cache_key, datetime.min.replace(tzinfo=UTC)
                )
                _LOGGER.warning(
                    "Using cached data as fallback due to error: %s (age: %s)",
                    type(err).__name__,
                    cache_age,
                )
                return self._cache[cache_key]

            # No cache available, propagate the error
            if isinstance(err, KeyError | ValueError):
                msg = f"Invalid API response: {err}"
                raise ClientError(msg) from err
            raise

    async def change_mode(self, modem: str, mode: str, uid: CommandUid) -> Any:
        """Change mode (air or hot water)."""
        mode_type = "air" if uid == CommandUid.AIR_MODE else "hot water"
        _LOGGER.info("Changing %s mode to: %s", mode_type, mode)
        return await self._send_command(modem, "changeMode", uid, mode)

    async def fetch_data(self) -> dict[str, Any] | None:
        """Fetch raw data from API and return dict."""
        _LOGGER.debug("Fetching data from Aldes API...")
        _LOGGER.debug("URL: %s", self._API_URL_PRODUCTS)
        _LOGGER.debug("Token present: %s", bool(self._token))

        try:
            data = await self._api_request("get", self._API_URL_PRODUCTS)
        except (ClientError, TimeoutError) as err:
            _LOGGER.error("Failed to fetch data: %s", err)
            return None

        _LOGGER.debug("Fetched data: %s", data)

        if isinstance(data, list) and len(data) > 0:
            first_item: Any = data[0]
            if isinstance(first_item, dict):
                _LOGGER.debug("Successfully retrieved Aldes device data")
                return first_item

        _LOGGER.warning("No valid data received from Aldes API")
        return None

    async def _temperature_worker(self) -> None:
        """Process temperature change requests from queue with delay between each."""
        _LOGGER.info("Temperature worker started")
        while True:
            try:
                # Ensure queue exists before getting from it
                if self.queue_target_temperature is None:
                    _LOGGER.debug("Queue is None, waiting...")
                    await asyncio.sleep(1)
                    continue

                _LOGGER.debug("Worker waiting for next item in queue...")
                (
                    modem,
                    thermostat_id,
                    thermostat_name,
                    temperature,
                ) = await self.queue_target_temperature.get()

                _LOGGER.debug(
                    "Worker processing item: %s, %s, %s, %s",
                    modem,
                    thermostat_id,
                    thermostat_name,
                    temperature,
                )

                if modem and thermostat_id and thermostat_name and temperature:
                    try:
                        await self.change_temperature(
                            modem, thermostat_id, thermostat_name, temperature
                        )
                    except Exception:
                        _LOGGER.exception(
                            "Error changing temperature for %s. Worker continuing.",
                            thermostat_name,
                        )

                    _LOGGER.debug("Worker sleeping for %s seconds", REQUEST_DELAY)
                    await asyncio.sleep(REQUEST_DELAY)
                
                # Mark task as done immediately after processing
                self.queue_target_temperature.task_done()
                
            except asyncio.CancelledError:
                _LOGGER.debug("Temperature worker cancelled")
                break
            except Exception:
                _LOGGER.exception("Unexpected error in temperature worker")
                # In case of error, we still need to mark task as done if we got an item
                if self.queue_target_temperature is not None:
                    with contextlib.suppress(ValueError):
                        self.queue_target_temperature.task_done()
                await asyncio.sleep(REQUEST_DELAY)

    async def stop_temperature_worker(self) -> None:
        """Stop the temperature worker and wait for queue to empty."""
        if self._temperature_task and not self._temperature_task.done():
            # Wait for queue to be processed
            if self.queue_target_temperature:
                try:
                    await asyncio.wait_for(
                        self.queue_target_temperature.join(), timeout=10
                    )
                except asyncio.TimeoutError:
                    _LOGGER.warning("Temperature queue did not empty in time")

            # Cancel the worker task
            self._temperature_task.cancel()
            try:
                await self._temperature_task
            except asyncio.CancelledError:
                pass

    async def set_target_temperature(
        self,
        modem: str,
        thermostat_id: int,
        thermostat_name: str,
        target_temperature: Any,
    ) -> None:
        """Set target temperature."""
        await self._ensure_temperature_worker_started()
        if self.queue_target_temperature:
            _LOGGER.debug(
                "Queueing temperature change for %s: %s",
                thermostat_name,
                target_temperature,
            )
            await self.queue_target_temperature.put(
                (modem, thermostat_id, thermostat_name, target_temperature)
            )
        else:
            _LOGGER.error("Failed to queue temperature change: Queue is None")

    async def change_temperature(
        self,
        modem: str,
        thermostat_id: int,
        thermostat_name: str,
        target_temperature: Any,
    ) -> Any:
        """Change temperature of thermostat."""
        _LOGGER.info(
            "Changing temperature for thermostat %s (%s) to %s°C",
            thermostat_id,
            thermostat_name,
            target_temperature,
        )
        try:
            result = await self._api_request(
                "post",
                f"{self._API_URL_PRODUCTS}/{modem}/thermostats/{thermostat_id}/setTargetTemperature",
                json={"temperature": target_temperature},
            )
            _LOGGER.debug("Change temperature result: %s", result)
            return result
        except Exception as err:
            _LOGGER.exception("Error changing temperature: %s", err)
            raise

    async def _send_command(
        self, modem: str, command: str, uid: CommandUid, value: str
    ) -> Any:
        """Send command to device."""
        url = f"{self._API_URL_PRODUCTS}/{modem}/commands"
        payload = {
            "commandUid": int(uid),
            "value": value,
        }
        _LOGGER.debug("Sending command: %s", payload)
        try:
            result = await self._api_request("post", url, json=payload)
            _LOGGER.debug("Send command result: %s", result)
            return result
        except Exception as err:
            _LOGGER.exception("Error sending command: %s", err)
            raise
