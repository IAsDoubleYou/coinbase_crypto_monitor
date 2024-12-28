import logging
_LOGGER = logging.getLogger(__name__)

def fetch_wallet_cryptos(connection):  # noqa: D103
    try:
        balances = connection.fetch_balance()
        return balances

    except requests.RequestException as ex:
        _LOGGER.error("Error fetching data from API: %s", ex)
        return {}

def fetch_price_from_exchange(connection, pair):  # noqa: D103
    try:
        base_coin, flat_currency = pair.split("/")
        ticker = connection.fetch_ticker(pair)
        price = ticker["last"]
        _LOGGER.debug(f"Price for {pair}: {price} {flat_currency}")
        return price
    except Exception as e:
        price = 0.0
        _LOGGER.debug(f"Error fetching price for pair {pair}. Error: {e}")
        return price

def flauwe_functie():
    return "flauwe functie"

def get_crypto_price(connection, pair):
    # Step1: Try to get the price directly
    price = fetch_price_from_exchange(connection, pair)

    if price > 0.0:
        return price  # Directe prijs is beschikbaar

    # Step 2: Check if fallback makes sense (only for EUR pairs)
    if not pair.endswith("/EUR"):
        return 0.0

    # Step 3: fallback to USDC or USDT as intermediate currency
    base_coin, _ = pair.split("/")
    fallback_pairs = [
        (f"{base_coin}/USDC", "USDC/EUR"),
        (f"{base_coin}/USDT", "USDT/EUR")
    ]

    for intermediate_pair, conversion_pair in fallback_pairs:
        # Retrieve the price of the intermediate currency (e.g. BTC/USDC)
        intermediate_price = fetch_price_from_exchange(connection, intermediate_pair)
        if intermediate_price > 0:
            # Now also retrieve the price of the conversion currency (e.g. USDC/EUR)
            conversion_price = fetch_price_from_exchange(connection, conversion_pair)
            if conversion_price > 0:
                # Compute the derived price in EUR
                price_in_eur = intermediate_price * conversion_price
                _LOGGER.debug(f"Price for {pair} through intermediate pair {intermediate_pair}: {price_in_eur} EUR")
                return price_in_eur

    # If no price could be derived, return 0.0
    return 0.0

