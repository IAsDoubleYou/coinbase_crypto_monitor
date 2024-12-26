from datetime import datetime, timedelta  # noqa: D100
import logging  # noqa: D100

import requests

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import ATTR_ATTRIBUTION

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class CryptoMonitorSensor(SensorEntity):
    """Representation of a cryptocurrency sensor."""

    def __init__(self, connection, crypto_name, balance, price_in_eur, value_in_eur):
        """Initialize the sensor."""
        # Wisselkoers ophalen van crypto naar EUR
        self._fiat_currency = "EUR"  # Moet via config

        self._pair = f"{crypto_name}/{self._fiat_currency}"
        self._crypto_name = crypto_name.lower()  # API-symbolen zijn meestal in kleine letters
        self._connection = connection
        self._balance = balance
        self._price_in_eur = price_in_eur
        self._value_in_eur = value_in_eur
        self._state = round(self._value_in_eur, 2)
        self._attributes = {}
        self._last_update = datetime.utcnow()  # Tijdstip van de laatste API-aanroep
        self._update_interval = timedelta(minutes=5)  # Cachetijd

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"Crypto Monitor {self._crypto_name.upper()}"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Return additional attributes of the sensor."""
        return self._attributes

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return "EUR"


    async def async_update(self):  # noqa: D102
        now = datetime.utcnow()  # noqa: DTZ003

        # Controleer of we binnen de cachetijd zitten
        if self._last_update and now - self._last_update < self._update_interval:
            # Gebruik de gecachede waarde
            _LOGGER.debug("Using cached data for %s", self._crypto_name)
            return

        # Hier eigenlijk ook balance opnieuw ophalen voor de zekerheid (evt. met eigen cache instelling)
        # Prijs in EUR ophalen

        try:
            self._price_in_eur = await self.hass.async_add_executor_job(fetch_price, self._connection, self._pair)

            self._value_in_eur = self._balance * self._price_in_eur

        except Exception as e:
            _LOGGER.error("Error fetching crypto price for pair %s: %s", self._pair, e)


        self._last_update = now  # Werk de laatste update-tijd bij
        """Fetch new data for the sensor."""
        _LOGGER.debug("Updating data for %s", self._crypto_name)

#        connection = self.hass.data[DOMAIN]["connection"]
        connection = self._connection

        # API-aanroep voor prijsgegevens
        data = await self.hass.async_add_executor_job(fetch_wallet_cryptos, connection)
        if not data:
            _LOGGER.error("No data received from API for %s", self._crypto_name)
            return

        # Verwerk gegevens
        self._attributes = {
            ATTR_ATTRIBUTION: "Data provided by CoinGecko",
            "current_price": self._price_in_eur,
            "balance": self._balance,
            "current_value_in_eur": self._value_in_eur,
        }

        self._state = round(self._value_in_eur, 2)


def fetch_wallet_cryptos(connection):  # noqa: D103
    try:
        balances = connection.fetch_balance()
        return balances

    except requests.RequestException as ex:
        _LOGGER.error("Error fetching data from API: %s", ex)
        return {}


def fetch_price(connection, pair):  # noqa: D103
    try:
        ticker = connection.fetch_ticker(pair)
        price_in_eur = ticker["last"]
        _LOGGER.info(f"Price for {pair}: {price_in_eur} EUR")
    except:
        price_in_eur = 0.0

    return price_in_eur

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up Crypto Monitor sensors from a config entry."""

    entities = []
    connection = hass.data[DOMAIN][config_entry.entry_id]["connection"]
    try:
        wallet_cryptos = await hass.async_add_executor_job(fetch_wallet_cryptos, connection)
    except Exception as e:
        _LOGGER.error("Error fetching wallet cryptos: %s", e)
        return

    if not wallet_cryptos:
        _LOGGER.error("No data received from API")
        return

    for crypto_name, crypto_values in wallet_cryptos.items():
        if 'free' in crypto_values and crypto_values['free'] > 0.0:
            balance = crypto_values['free']

            # Prijs in EUR ophalen
            pair = f"{crypto_name}/EUR"
            try:
                price_in_eur = await hass.async_add_executor_job(fetch_price, connection, pair)

                if price_in_eur == 0.0:
                    _LOGGER.info(f"No price found for pair {pair}, skipping this crypto")
                    continue

                value_in_eur = balance * price_in_eur

                entities.append(
                    CryptoMonitorSensor(
                        connection,
                        crypto_name,
                        balance,
                        price_in_eur,
                        value_in_eur,
                    )
                )

            except Exception as e:
                _LOGGER.error(f"Error fetching price for pair {pair}, skipping. Error: {e}")
                continue

        else:
            # Overslaan als de waarde van 'free' <= 0.0 of niet bestaat
            continue

    if entities:
        async_add_entities(entities, update_before_add=False)
        _LOGGER.info("Added %d Crypto Monitor sensors", len(entities))
    else:
        _LOGGER.warning("No entities to add")
