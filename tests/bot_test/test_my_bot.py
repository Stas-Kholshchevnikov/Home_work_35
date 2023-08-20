from unittest.mock import patch
import pytest
from django.urls import reverse
from rest_framework import status
from bot.tg.client import TgClient
from core.models import User


@pytest.mark.django_db
class TestTgUser:
    url: str = reverse('bot:verify')

    def test_user_verified(self, auth_client, user: User, tuser_factory):
        """ Проверка верификации пользователя """
        tg_user = tuser_factory.create(verification_code='correct')
        payload = {'verification_code': 'correct'}  # A A A

        with patch.object(TgClient, "send_message") as mock:
            response = auth_client.patch(self.url, data=payload)

        tg_user.refresh_from_db()
        assert tg_user.user == user
        assert response.status_code == status.HTTP_200_OK
        mock.assert_called_once_with(tg_user.chat_id, '[verification has been completed]')

    def test_invalid_verifiaction_code(self, auth_client, tuser_factory):
        """ Валидация кода верификации """
        tg_user = tuser_factory.create(user=None, verification_code='correct')
        payload = {'verification_code': 'incorrect'}  # A A A

        with patch.object(TgClient, "send_message") as mock:
            response = auth_client.patch(self.url, data=payload)

        tg_user.refresh_from_db()
        assert tg_user.user is None
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        mock.assert_not_called()
