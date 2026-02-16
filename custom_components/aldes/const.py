"""Constants for aldes."""

from homeassistant.const import Platform

NAME = "Aldes"
DOMAIN = "aldes"
VERSION = "0.0.1"

CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_PERFORMANCE_LOGS = "performance_logs"

MANUFACTURER = "Aldes"
PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
    Platform.CLIMATE,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SENSOR,
]

FRIENDLY_NAMES = {"TONE_AIR": "T.One® AIR", "TONE_AQUA_AIR": "T.One® AquaAIR"}

# ECO mode temperature offset (displayed to user as -2°C, sent to API as +2°C)
ECO_MODE_TEMPERATURE_OFFSET = 2

# State change verification constants
VERIFY_STATE_CHANGE_DELAY = 60  # Delay before verifying state change (seconds)
VERIFY_STATE_CHANGE_REFRESH_DELAY = (
    2  # Delay after refresh during verification (seconds)
)
TEMPERATURE_VERIFY_THRESHOLD = 0.5  # Threshold for temperature verification (°C)

# Planning program characters
PROGRAM_OFF = "0"
PROGRAM_COMFORT = "B"
PROGRAM_ECO = "C"
PROGRAM_BOOST = "G"

# Planning slot constants
HOUR_TO_CHAR_THRESHOLD = 10
SLOT_MIN_LENGTH = 3

# Statistics update interval
STATISTICS_UPDATE_INTERVAL = 3600  # Update every hour (seconds)

# Water level thresholds
WATER_LEVEL_THRESHOLDS = {
    "low": 25,
    "medium": 50,
    "high": 75,
}
