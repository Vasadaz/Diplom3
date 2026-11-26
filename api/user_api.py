"""Создание и удаление тестового пользователя через API."""
import requests

from config.config import API_TIMEOUT, BASE_URL


class UserApi:
    """Работа с /api/auth/register и /api/auth/user."""

    def __init__(self) -> None:
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        self.access_token: str | None = None
        self.user: dict | None = None

    def register(self, email: str, password: str, name: str) -> dict:
        """Регистрирует пользователя и сохраняет accessToken.

        :raises AssertionError: если API вернуло ошибку
        """
        response = self.session.post(
            f"{self.base_url}/api/auth/register",
            json={"email": email, "password": password, "name": name},
            timeout=API_TIMEOUT,
        )
        assert response.status_code == 200, (
            f"Регистрация упала: {response.status_code} {response.text}"
        )
        data = response.json()
        assert data.get("success"), f"API вернуло ошибку: {data}"
        self.access_token = data.get("accessToken")
        return data

    def delete(self) -> None:
        """Удаляет ранее созданного пользователя по токену."""
        if not self.access_token:
            return
        self.session.delete(
            f"{self.base_url}/api/auth/user",
            headers={"Authorization": self.access_token},
            timeout=API_TIMEOUT,
        )
        self.access_token = None
