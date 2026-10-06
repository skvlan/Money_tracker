from django.core.exceptions import ObjectDoesNotExist

from .currencies import CURRENCY_FORMATS


def user_currency(request):
    currency_code = "EUR"
    if request.user.is_authenticated:
        try:
            currency_code = request.user.money_preferences.currency
        except ObjectDoesNotExist:
            pass
    prefix, suffix = CURRENCY_FORMATS.get(currency_code, CURRENCY_FORMATS["EUR"])
    return {
        "currency_code": currency_code,
        "currency_prefix": prefix,
        "currency_suffix": suffix,
    }
