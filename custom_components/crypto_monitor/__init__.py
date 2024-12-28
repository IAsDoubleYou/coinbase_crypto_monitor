import logging
import ccxt
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import discovery
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.discovery import load_platform

from .const import DOMAIN, CONF_API_KEY, CONF_API_SECRET, CONF_EXCHANGE_CURRENCY


PLATFORMS: list[Platform] = [Platform.SENSOR]

_LOGGER = logging.getLogger(__name__)

def connect_exchange(api_key):
    """Function to establish a connection to the exchange."""  # noqa: D401

    _LOGGER.info("Connecting to exchange with API key")
    return ccxt.coinbase(api_key)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Example API from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    try:
        # Initialize API connection
        value = entry.data[CONF_API_KEY]
        api_key = value[0] if isinstance(value, tuple) else value

        value = entry.data[CONF_API_SECRET]
        api_secret = value[0] if isinstance(value, tuple) else value
        api_secret = api_secret.replace("\\n", "\n")

        value = entry.data[CONF_EXCHANGE_CURRENCY]
        exchange_currency = value[0] if isinstance(value, tuple) else value

        api_token = {"apiKey": api_key, "secret": api_secret, "verbose": False,}
        connection = await hass.async_add_executor_job(connect_exchange, api_token)

        # hass.data[DOMAIN][entry.entry_id] = {
        # "connection": connection,
        # "exchange_currency": exchange_currency,
        # }

        hass.data[DOMAIN] = {
        "connection": connection,
        "exchange_currency": exchange_currency,
        }

        # Set up platforms
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

        # Add update listener for config entry changes
        entry.async_on_unload(entry.add_update_listener(update_listener))

        return True

    except EOFError as err:
        _LOGGER.error("Failed to connect to API: %s", err)
        return False

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Unload platforms
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        # Remove API client
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok

async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)