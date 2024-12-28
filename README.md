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
Custom component that creates sensors for cryptos of a user's Coinbase wallet. Sensors will only be created for crypto's with a positive free balance.
## Installation

### Using [HACS](https://hacs.xyz/)
This component can be installed using HACS. Please follow directions [here](https://hacs.xyz/docs/faq/custom_repositories/) and use [https://github.com/IAsDoubleYou/coinbase_crypto_monitor](https://github.com/IAsDoubleYou/coinbase_crypto_monitor) as the repository URL.
### Manual

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
2. If you do not have a `custom_components` directory (folder) there, you need to create it.
3. In the `custom_components` directory (folder) create a new folder called `mysql_query`.
4. Download _all_ the files from the `custom_components/crypto_monitor/` directory (folder) of this repository.
5. Place the files you downloaded in the new directory (folder) you created.
6. Restart Home Assistant
7. Apply the <i>configuration</i> as described below
8. Restart Home Assistant once more

## Configuration
The coinbase crypto monitor can only be configured by the GUI.
Navigate to the Settings/Integration page of Home Assistant and press the [+] icon to add a new integration.
Search for the Crypto Monitor integration in the dropdown and select it.

You will be asked to add:
1. your API Key
2. your API secret
3. and the currency you want to use (e.g. EUR, USD).

After you have provided the information, the integration will create sensors for every crypto/currency pair in your wallet that have a positive free balance and for which it is able to retrieve the price on the coinbase exchange.
When using EUR as the currency, the integration will try to use other currency pairs as an intermediate to compute the value in EUR if it could not retrieve the EUR price for the crypto. 

The integration also monitors the wallet independently from the crypto prices so that it can add or remove sensors if the content of the wallet changes.

## Usage
The sensors can be used with automations to send notification when the price drops below a specific point or rises above another point. Instead of monitoring crypto prices it may be useful and simpler to just monitor the total value of the individual crypto's in the wallet. Since you probably know better how much you've spent on any of them then what their exact price was when you bought them, this could be an easy trigger to decide to trade some of them at a given point. Also it let you sit back and wait until you receive a notification instead of watching the exhange prices the whole day ;-)

## API key
The needed API key can be retrieved at the coinbase site. Be sure to provide an API key that has READ-ONLY privileges on the wallet to avoid risk. For example accidentally posting it on a forum when support is requested. A future version of the crypto monitor integration will check if the API key has READ-ONLY privileges and will not establish the connection if it does not met that criteria.

## Remarks
Please use this on your own risk as an additional helper tool. I don't take any responsibility if the notification, or monitoring, or the api or any other technical failure that might lead in missing the "greatest trading moment of your live". 
