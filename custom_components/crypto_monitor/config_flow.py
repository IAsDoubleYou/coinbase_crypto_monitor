import voluptuous as vol  # noqa: D100

from homeassistant import config_entries

from .const import DOMAIN, CONF_API_KEY, CONF_API_SECRET, CONF_EXCHANGE_CURRENCY


class CryptoMonitorConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Crypto Monitor."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Validate user input
            if not user_input[CONF_API_KEY]:
                errors[CONF_API_KEY]  = f"{CONF_API_KEY}_missing"
            if not user_input[CONF_API_SECRET]:
                errors[CONF_API_SECRET]  = f"{CONF_API_SECRET}_missing"
            if not user_input[CONF_EXCHANGE_CURRENCY]:
                errors[CONF_EXCHANGE_CURRENCY]  = f"{CONF_EXCHANGE_CURRENCY}_missing"

            if not errors:
                # Store the configuration information
                return self.async_create_entry(
                    title="Crypto Monitor",
                    data={
                        CONF_API_KEY: user_input[CONF_API_KEY],
                        CONF_API_SECRET: user_input[CONF_API_SECRET],
                        CONF_EXCHANGE_CURRENCY: user_input[CONF_EXCHANGE_CURRENCY],
                    },
                )

        # Show the configuration form
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_API_KEY): str,
                    vol.Required(CONF_API_SECRET): str,
                    vol.Required(CONF_EXCHANGE_CURRENCY, default="EUR"): str,
                }
            ),
            errors=errors,
        )