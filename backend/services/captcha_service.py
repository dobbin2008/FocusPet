import requests
from flask import current_app


class TurnstileUnavailableError(Exception):
    pass


class ValidarTurnstileService:
    SITEVERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"

    def execute(self, token, remote_ip=None):
        if current_app.testing and current_app.config.get("TURNSTILE_TEST_BYPASS"):
            return True
        if not isinstance(token, str) or not token or len(token) > 2048:
            return False
        secret = current_app.config.get("TURNSTILE_SECRET_KEY")
        if not current_app.config.get("TURNSTILE_SITE_KEY") or not secret:
            raise TurnstileUnavailableError("CAPTCHA não está configurado")
        try:
            response = requests.post(
                self.SITEVERIFY_URL,
                data={
                    "secret": secret,
                    "response": token,
                    "remoteip": remote_ip or "",
                },
                timeout=8,
            )
            response.raise_for_status()
            return response.json().get("success") is True
        except (requests.RequestException, ValueError) as erro:
            raise TurnstileUnavailableError("Não foi possível validar o CAPTCHA") from erro