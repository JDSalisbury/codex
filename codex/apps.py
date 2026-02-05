from django.apps import AppConfig


class CodexConfig(AppConfig):
    name = "codex"

    def ready(self):
        """Import signals when app is ready"""
        import codex.signals  # noqa: F401
