import logging
from datetime import timedelta
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from .const import DOMAIN
from .utils import fetch_wallet_cryptos, get_crypto_price

_LOGGER = logging.getLogger(__name__)

class EntityManagementCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant) -> None:
        super().__init__(
            hass,
            logger=_LOGGER,
            name="Crypto Monitor Entity Manager",
            update_interval=timedelta(minutes=2)  # Check regularly for wallet changes
        )

    async def _async_update_data(self):
        # Lazy-loaded since to avoid circular import
        from .sensor import CryptoMonitorSensor

        connection = self.hass.data[DOMAIN]["connection"]
        exchange_currency = self.hass.data[DOMAIN]["exchange_currency"]

        all_sensors = self.hass.states.async_entity_ids("sensor")
        current_crypto_sensors = [
            entity_id.replace("sensor.crypto_monitor_", "").split("_")[0].upper()
            for entity_id in all_sensors
            if entity_id.startswith("sensor.crypto_monitor")
        ]

        try:
            wallet_cryptos = await self.hass.async_add_executor_job(fetch_wallet_cryptos, connection)
        except Exception as e:
            _LOGGER.error("Coordinator.py: Error fetching wallet cryptos: %s", e)
            return

        if not wallet_cryptos:
            _LOGGER.error("Coordinator.py: No data received from API")
            return

        valid_fetched_cryptos = []
        for crypto_name, crypto_values in wallet_cryptos.items():
            if 'free' in crypto_values and crypto_values['free'] > 0.0:
                balance = crypto_values['free']

                if balance == 0:
                    _LOGGER.debug(f"coordinator.py: No balance available for pair {crypto_name}, skipping this crypto")
                    continue

                # Determine the crypto's price in exchange_currency. If the price is 0.0, skip this crypto
                pair = f"{crypto_name}/{exchange_currency}"
                try:
                    price_in_exchange_currency = await self.hass.async_add_executor_job(get_crypto_price, connection, pair)

                    if price_in_exchange_currency == 0.0:
                        _LOGGER.debug(f"coordinator.py: No price found for pair {pair}, skipping this crypto")
                        continue

                    _LOGGER.debug(f"coordinator.py: Successfully got the price for pair {pair}")
                    value_in_exchange_currency = balance * price_in_exchange_currency

                    valid_fetched_cryptos.append({"crypto_name": crypto_name,
                       "balance": balance
                     , "price_in_exchange_currency": price_in_exchange_currency
                     , "value_in_exchange_currency": value_in_exchange_currency})

                except Exception as e:
                    _LOGGER.debug(f"No price could be fetched for pair {pair}, skipping. Error: {e}")
                    continue

            else:
                # Skip cryptos with no balance
                _LOGGER.debug(f"coordinator.py: No (free) balance found for {crypto_name}, skipping this crypto")
                continue

        # Convert dictionary keys to sets for comparison
        wallet_crypto_name_set = set(item['crypto_name'] for item in valid_fetched_cryptos)
        current_crypto_sensors_set = set(current_crypto_sensors)

        # Determine which sensors need to be added or removed
        new_currencies = wallet_crypto_name_set - current_crypto_sensors_set
        removed_currencies = current_crypto_sensors_set - wallet_crypto_name_set

        if new_currencies or removed_currencies:
            platform = self.hass.data[DOMAIN]['platform']
            async_add_entities = platform.get('async_add_entities')
            if async_add_entities is None:
                _LOGGER.error(f"async_add_entities is not available in platform: {platform}")
                return

            # Add new sensors for cryptos that are in the wallet but not in the registry
            if new_currencies:
                entities = []
                for currency in new_currencies:
                    crypto_data = next((item for item in valid_fetched_cryptos if item['crypto_name'] == currency), None)

                    new_entity = CryptoMonitorSensor(
                        connection,
                        crypto_data['crypto_name'],
                        exchange_currency,
                        crypto_data['balance'],
                        crypto_data['price_in_exchange_currency'],
                        crypto_data['value_in_exchange_currency'],
                    )

                    entities.append(new_entity)
                    _LOGGER.info(f"Adding new entity: {crypto_data['crypto_name']}")

                async_add_entities(entities)

            # Remove sensors that doesn't exist in the wallet anymore
            if removed_currencies:
                registry = self.hass.data['entity_registry']
                for currency in removed_currencies:
                    entity_id = f"sensor.crypto_monitor_{currency.lower()}_{exchange_currency.lower()}"
                    if registry.async_get(entity_id):
                        _LOGGER.info(f"Removing entity_id: {entity_id}")
                        registry.async_remove(entity_id)
                    else:
                        _LOGGER.debug(f"Entity {entity_id} not found in registry, skipping removal")


        return wallet_cryptos

    async def async_start_updates(self):
        """Start the automatic updates explicitly."""
        self.async_add_listener(lambda: None)  # Add a dummy listener to start updates
        await self.async_refresh()  # Start the first update

