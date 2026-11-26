"""Генерация тестовых данных."""
from uuid import uuid4

from faker import Faker

fake = Faker("ru_RU")


def generate_user() -> dict:
    """Данные нового пользователя с гарантированно уникальным email.

    fake.unique.email() не подходит: уникальность держится только внутри
    одного процесса, а регистрация — на стороне сервера.
    """
    return {
        "email": f"qa_{uuid4().hex[:12]}@example.com",
        "password": f"Aa1!{uuid4().hex[:8]}",
        "name": fake.first_name(),
    }
