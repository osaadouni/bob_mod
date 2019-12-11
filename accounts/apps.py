from django.apps import AppConfig


class AccountsConfig(AppConfig):
    name = 'accounts'

    def ready(self):
        print(f"{self.__class__.__name__}::ready()")
        import accounts.signals
