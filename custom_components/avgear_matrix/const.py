"""Constants for the AVGear Matrix integration."""

from datetime import timedelta

DOMAIN = "avgear_matrix"

SCAN_INTERVAL = timedelta(seconds=30)

DEFAULT_PORT = 4001

SUPPORTED_MODELS = {
    "TMX44PRO AVK": {
        "inputs":4,
        "outputs": 4
    }
}