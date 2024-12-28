[![HACS Custom][hacs_shield]][hacs]  
[![GitHub Latest Release][releases_shield]][latest_release]  
[![GitHub All Releases][downloads_total_shield]][releases]  
[![Community Forum][community_forum_shield]][community_forum]  

[hacs_shield]: https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge  
[hacs]: https://github.com/hacs/integration  

[latest_release]: https://github.com/IAsDoubleYou/coinbase_crypto_monitor/releases/latest  
[releases_shield]: https://img.shields.io/github/release/IAsDoubleYou/coinbase_crypto_monitor.svg?style=for-the-badge  

[releases]: https://github.com/IAsDoubleYou/coinbase_crypto_monitor/releases/  
[downloads_total_shield]: https://img.shields.io/github/downloads/IAsDoubleYou/coinbase_crypto_monitor/total?style=for-the-badge  

[community_forum_shield]: https://img.shields.io/static/v1.svg?label=%20&message=Forum&style=for-the-badge&color=41bdf5&logo=HomeAssistant&logoColor=white  
[community_forum]: https://community.home-assistant.io/t/mysql-query/734346  

# Crypto Monitor  

A Home Assistant custom component that creates sensors for cryptocurrencies in a user's Coinbase wallet. Sensors are only created for cryptocurrencies with a positive free balance.  

## Installation  

### Via [HACS](https://hacs.xyz/)  

This component can be installed using HACS. Follow the instructions [here](https://hacs.xyz/docs/faq/custom_repositories/) and use [https://github.com/IAsDoubleYou/coinbase_crypto_monitor](https://github.com/IAsDoubleYou/coinbase_crypto_monitor) as the repository URL.  

### Manual  

1. Open the Home Assistant configuration directory (where `configuration.yaml` is located) with your tool of choice.  
2. If there is no `custom_components` directory, create one.  
3. Inside the `custom_components` directory, create a new folder named `crypto_monitor`.  
4. Download _all_ files from the `custom_components/crypto_monitor/` directory of this repository.  
5. Place the downloaded files into the newly created directory.  
6. Restart Home Assistant.  
7. Apply the <i>configuration</i> as described below.  
8. Restart Home Assistant again.  

## Configuration  

The Crypto Monitor can only be configured via the GUI.  

1. Navigate to the **Settings / Integrations** page in Home Assistant.  
2. Click the [+] icon to add a new integration.  
3. Search for the Crypto Monitor integration and select it.  

You will be prompted to provide:  
1. Your API Key.  
2. Your API Secret.  
3. The currency you want to use (e.g., EUR, USD).  

After entering this information, the integration will create sensors for every crypto/currency pair in your wallet with a positive balance and for which the price can be retrieved from Coinbase. If the price in the specified currency is not available, the integration will use alternative currency pairs to estimate the value.  

The integration also monitors wallet changes and dynamically adds or removes sensors as the wallet's contents change.  

## Usage  

The sensors can be used in automations to send notifications when the price drops below a certain point or rises above another. Instead of monitoring individual crypto prices, you may find it simpler to monitor the total value of your wallet. This can serve as an easy trigger for trading decisions without constantly watching exchange rates.  

## API Key  

The required API key can be generated on the Coinbase website. Ensure that the API key has **read-only** privileges to minimize risks. Future versions of the integration will verify this requirement and refuse to connect if the key does not meet the criteria.  

## Remarks  

Use this tool at your own risk as an auxiliary helper. I accept no responsibility for missed trading opportunities or other issues arising from technical failures, such as notification errors, monitoring downtime, or API issues.
