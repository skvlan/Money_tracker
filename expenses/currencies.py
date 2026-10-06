from django.utils.translation import gettext_lazy as _

CURRENCY_FORMATS = {
    "EUR": ("€", ""),
    "USD": ("$", ""),
    "GBP": ("£", ""),
    "PLN": ("", " zł"),
    "CHF": ("CHF ", ""),
    "CAD": ("CA$", ""),
    "AUD": ("A$", ""),
    "JPY": ("¥", ""),
    "INR": ("₹", ""),
    "SEK": ("", " kr"),
}

CURRENCY_CHOICES = (
    ("EUR", _("Euro (EUR)")),
    ("USD", _("US dollar (USD)")),
    ("GBP", _("British pound (GBP)")),
    ("PLN", _("Polish złoty (PLN)")),
    ("CHF", _("Swiss franc (CHF)")),
    ("CAD", _("Canadian dollar (CAD)")),
    ("AUD", _("Australian dollar (AUD)")),
    ("JPY", _("Japanese yen (JPY)")),
    ("INR", _("Indian rupee (INR)")),
    ("SEK", _("Swedish krona (SEK)")),
)
