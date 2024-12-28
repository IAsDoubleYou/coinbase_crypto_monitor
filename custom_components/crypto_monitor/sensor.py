from datetime import datetime, timedelta  # noqa: D100
import logging  # noqa: D100
import requests
from homeassistant.components.sensor import SensorEntity
from .const import DOMAIN
from .utils import fetch_wallet_cryptos, get_crypto_price
from typing import Any
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback

_LOGGER = logging.getLogger(__name__)


class CryptoMonitorSensor(SensorEntity):
    """Representation of a cryptocurrency sensor."""

    def __init__(self, connection, crypto_name, exchange_currency, crypto_free_balance, crypto_price, crypto_value) -> None:
        """Initialize the sensor."""
        self._exchange_currency = exchange_currency
        self._pair = f"{crypto_name}/{self._exchange_currency}"
        self._crypto_name = crypto_name.lower()
        self._connection = connection
        self._crypto_free_balance = crypto_free_balance
        self._crypto_price = crypto_price
        self._crypto_value = crypto_value
        self._state = f"{self._crypto_value:.2f}"
        self._attributes = {}
        self._last_update = datetime.utcnow()  # Last update timestamp
        self._update_interval = timedelta(minutes=5)  # Update interval
        self._unique_id = f"coinbase_crypto_monitor_{crypto_name}_{exchange_currency}"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return f"Crypto Monitor {self._crypto_name.upper()}_{self._exchange_currency.upper()}"

    @property
    def unique_id(self) -> str:
        return self._unique_id

    @property
    def state(self) -> str:
        """Return the state of the sensor."""
        return self._state

    @property
    def extra_state_attributes(self) -> dict:
        """Return additional attributes of the sensor."""
        return self._attributes

    @property
    def unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return self._exchange_currency

    @property
    def price(self) -> str:
        """Return the price of the crypto."""
        return self._crypto_price

    @property
    def free_balance(self) -> str:
        """Return the free balance of the crypto."""
        return self._crypto_free_balance

    @property
    def value(self) -> str:
        """Return the value of the crypto balance."""
        return self._crypto_value

    async def async_update(self) -> None:  # noqa: D102
        now = datetime.utcnow()  # noqa: DTZ003

        # Check if the data is still up-to-date
        if self._last_update and now - self._last_update < self._update_interval:
            # Use cached data
            _LOGGER.debug("Using cached data for %s", self._crypto_name)
        else:
            # Retrieve the coins' price in the requested exchange currency
            try:
                self._crypto_price = await self.hass.async_add_executor_job(get_crypto_price, self._connection, self._pair)
                self._crypto_value = self._crypto_free_balance * self._crypto_price
            except Exception as e:
                _LOGGER.error("Error fetching crypto price for pair %s: %s", self._pair, e)

            self._last_update = now
            _LOGGER.debug("Updating data for %s", self._crypto_name)

            connection = self._connection

            # Fetch wallet cryptos
            data = await self.hass.async_add_executor_job(fetch_wallet_cryptos, connection)
            if not data:
                _LOGGER.error("No data received from API for %s", self._crypto_name)
                return
            _LOGGER.debug("Updated data for %s", self._crypto_name)

        # Update the crypto_free_balance
        self._attributes = {
            "price": self._crypto_price,
            "free_balance": self._crypto_free_balance,
            "value": self._crypto_value,
        }

        self._state = round(self._crypto_value, 2)

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up Crypto Monitor sensors from a config entry."""

    # Lazy-loaded since to avoid circular import
    from .coordinator import EntityManagementCoordinator

    entities = []
    connection = hass.data[DOMAIN]["connection"]
    exchange_currency = hass.data[DOMAIN]["exchange_currency"]

    try:
        wallet_cryptos = await hass.async_add_executor_job(fetch_wallet_cryptos, connection)
    except Exception as e:
        _LOGGER.error("Error fetching wallet cryptos: %s", e)
        return

    if not wallet_cryptos:
        _LOGGER.error("No data received from API")
        return

    for crypto_name, crypto_data in wallet_cryptos.items():
        if 'free' in crypto_data and crypto_data['free'] > 0.0:
            crypto_free_balance = crypto_data['free']

            # Retrieve the price in exchange_currency
            pair = f"{crypto_name}/{exchange_currency}"
            try:
                crypto_price = await hass.async_add_executor_job(get_crypto_price, connection, pair)

                if crypto_price == 0.0:
                    _LOGGER.info(f"sensor.py: No price found for pair {pair}, skipping this crypto")
                    continue

                _LOGGER.debug(f"sensor.py: Successfully got the price for pair {pair}")

                crypto_value = crypto_free_balance * crypto_price

                entities.append(
                    CryptoMonitorSensor(
                        connection,
                        crypto_name,
                        exchange_currency,
                        crypto_free_balance,
                        crypto_price,
                        crypto_value,
                    )
                )

            except Exception as e:
                _LOGGER.info(f"Error fetching price for pair {pair}, skipping. Error: {e}")
                continue

        else:
            # Skip this crypto if no crypto_free_balance is found or if it's value is 0.0
            _LOGGER.info(f"sensor.py: No (free) crypto_free_balance found for {crypto_name}, skipping this crypto")
            continue

    if entities:
        async_add_entities(entities, update_before_add=False)
        _LOGGER.info("Added %d Crypto Monitor sensors", len(entities))
    else:
        _LOGGER.warning("No entities to add")

    coordinator = EntityManagementCoordinator(hass)

    hass.data[DOMAIN] = {
        'platform': {'async_add_entities': async_add_entities},
        'connection': connection,
        "exchange_currency": exchange_currency,
    }

    await coordinator.async_start_updates()
    hass.data[DOMAIN]['coordinator'] = coordinator
