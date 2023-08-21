from unittest.mock import patch

import pytest
from django.urls import reverse
from rest_framework import status

from bot.models import TgUser
from bot.tg.client import TgClient
from core.models import User
from tests import factories


@pytest.mark.django_db
class TestTgUser:
    url: str = reverse('bot:verify')

    def test_bot_verify(self, auth_client, user: User):
        """ Проверяем пользователя на аутентификацию через Телеграмм бота """
        tg_user = factories.TuserFactory.create(
            chat_id='847509830',
            username='Tester',
            user=user,
            verification_code='correct'
        )
        payload = {'verification_code': 'correct'}

        with patch.object(TgClient, "send_message") as mock:
            response = auth_client.patch(self.url, data=payload)

        tg_user.refresh_from_db()
        assert tg_user.user == user
        assert response.status_code == status.HTTP_200_OK
        mock.assert_called_once_with(tg_user.chat_id, '[verification has been completed]')

    def test_incorrect(self, auth_client):
        """ Проверка на валидности кода верификации """
        tg_user = factories.TuserFactory.create(
            chat_id='847509830',
            username='Tester',
            user=None,
            verification_code='correct'
        )
        payload = {'verification_code': 'incorrect'}

        with patch.object(TgClient, "send_message") as mock:
            response = auth_client.patch(self.url, data=payload)
            mock.assert_not_called()

        tg_user.refresh_from_db()
        assert tg_user.user is None
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        mock.assert_not_called()


