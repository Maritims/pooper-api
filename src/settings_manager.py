import os


class Setting:
    key: str
    value: str

    def __init__(self, key: str, value: str):
        self.key = key
        self.value = value


class SettingsManager:
    __settings: dict = {}

    def __init__(self):
        keys = [
            'API_BASE_URL',
            'CLIENT_BASE_URL',
            'API_SECRET_AUTH_KEY',
            'SENDER_EMAIL_ADDRESS',
            'SENDGRID_API_KEY',
            'MARIADB_USER',
            'MARIADB_PASSWORD',
            'MARIADB_DATABASE',
            'MARIADB_SERVER',
            #'VAPID_PUBLIC_KEY',
            #'VAPID_PRIVATE_KEY'
        ]

        for key in keys:
            value = os.environ.get(key)

            if value is None:
                raise Exception(f"The environment variable '{key}' is not set.")

            self.__settings[key] = value

    def get_setting(self, key: str):
        value: str = self.__settings[key]

        if value is None:
            raise Exception(f"Unable to find any setting with the key {key}. Did you make a typo somewhere?")

        return value


settingsManager = SettingsManager()
