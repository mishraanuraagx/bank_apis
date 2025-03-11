import json
import os


class Localization:
    def __init__(self, locale="en"):
        self.strings = None
        self.locale = locale
        self.load_locale()

    def load_locale(self):
        # locale_file_path = os.path.join("locales", f"{self.locale}.json")
        locale_file_path = os.path.join(os.path.dirname(__file__), 'locales', 'en.json')
        with open(locale_file_path, "r", encoding="utf-8") as file:
            self.strings = json.load(file)

    def get(self, key: str, **kwargs) -> str:
        message = self.strings.get(key, key)
        return message.format(**kwargs)
