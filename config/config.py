"""Константы окружения.

Всё, что может отличаться между прогонами (стенд, таймауты), берётся из
переменных окружения — код не правится при переезде на другой стенд.
"""
import os

BASE_URL = os.getenv("SB_BASE_URL", "https://stellarburgers.education-services.ru")
FEED_URL = f"{BASE_URL}/feed"
LOGIN_URL = f"{BASE_URL}/login"
ORDERS_HISTORY_URL = f"{BASE_URL}/account/order-history"

DEFAULT_TIMEOUT = float(os.getenv("SB_TIMEOUT", "15"))
POLL_FREQUENCY = float(os.getenv("SB_POLL", "0.25"))
API_TIMEOUT = float(os.getenv("SB_API_TIMEOUT", "10"))
