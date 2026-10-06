from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.utils import translation


class UserLanguageMiddleware:
    """Activate the language stored in the signed-in user's preferences."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            try:
                language = request.user.money_preferences.language
            except ObjectDoesNotExist:
                language = "en"
            if language not in dict(settings.LANGUAGES):
                language = "en"
            translation.activate(language)
            request.LANGUAGE_CODE = language
        return self.get_response(request)
