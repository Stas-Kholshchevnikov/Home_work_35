import logging
from typing import Any

import requests
from pydantic import ValidationError

from bot.tg.schemas import GetUpdatesResponse, SendMessageResponse
from django.conf import settings

logger = logging.getLogger(__name__)


class TgClientError(Exception):
    ...


class TgClient:
    def __init__(self, token: str | None = None) -> None:
        self.__token = token if token else settings.BOT_TOKEN
        self.__base_url = f'https://api.telegram.org/bot{self.__token}/'

    def __get_url(self, method: str) -> str:
        return f'{self.__base_url}{method}'

    def _get(self, method: str, **params: Any) -> dict:
        url = self.__get_url(method)
        params.setdefault('timeout', 10)
        response = requests.get(url, params=params)
        if not response.ok:
            logger.warning("Invalid status code %d from %s", response.status_code, method)
            raise TgClientError

        return response.json()

    def get_updates(self, offset: int = 0, timeout: int = 60, **kwargs) -> GetUpdatesResponse:
        data = self._get('getUpdates', offset=offset, timeout=timeout, **kwargs)
        return self.__serialize_tg_response(GetUpdatesResponse, data)

    def send_message(self, chat_id: int, text: str, **kwargs) -> SendMessageResponse:
        data = self._get('sendMessage', chat_id=chat_id, text=text, **kwargs)
        return self.__serialize_tg_response(SendMessageResponse, data)

    @staticmethod
    def __serialize_tg_response(serializer_class, data: dict):
        try:
            return serializer_class(**data)
        except ValidationError:
            logger.error("Failed to serialize response", data)
            raise TgClientError
