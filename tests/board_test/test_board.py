from datetime import datetime
from typing import Dict

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response

from goals.models import Board
from goals.serializers import BoardParticipantSerializer, BoardSerializer
from tests.factories import BoardParticipantFactory, BoardFactory


@pytest.mark.django_db
class TestBoardView:
    url: str = reverse('goals:board_list')

    def test_board_create(self, client, auth_client):
        """ Тест создание доски """
        url = '/goals/board/create'

        expected_response = {
            'created': datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
            'updated': datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
            'title': 'test board',
            'is_deleted': False
        }
        response = client.post(path=url, data=expected_response)

        assert response.status_code == status.HTTP_201_CREATED
        board = Board.objects.get()
        assert board.title == expected_response['title']
        assert response.data['is_deleted'] == expected_response['is_deleted']

    def test_board_list_deny(self, client) -> None:
        """ Проверка того, отсутствия доступа не аутентифицированныех пользователей.   """
        response: Response = client.get(self.url)

        assert (
                response.status_code == status.HTTP_403_FORBIDDEN
        ), "Отказ в доступе не предоставлен"


    def test_deleted_board_retrieve_participant(self, auth_client, user) -> None:
        """Проверка, что пользователь не получит удаленную доску"""
        board = BoardFactory(is_deleted=True)
        BoardParticipantFactory(board=board, user=user)
        url = f'goals//board/{board.id}'
        response: Response = auth_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


    def test_board_retrieve_not_participant(self, auth_client) -> None:
        """
        Проверка, что пользователь, не являющийся участником не может получить доступ к доске.
        """
        board = BoardFactory(is_deleted=True)
        BoardParticipantFactory(board=board)
        url = f'goals//board/{board.id}'
        response: Response = auth_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


    def test_board_retrieve_deny(self, client) -> None:
        """
        Проверка, что пользователи, не прошедшие проверку
        подлинности, не могут получить доступ.
        """

        url = 'goals/board/1'
        response: Response = client.get(url)

        assert (
                response.status_code == status.HTTP_404_NOT_FOUND
        ), "Отказ. Доступ не предоставлен"
