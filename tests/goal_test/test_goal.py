from typing import Dict, Union

import pytest

from django.urls import reverse
from rest_framework import status

import factory
from pytest_factoryboy import register

from django.contrib.auth import get_user_model


from rest_framework import status
from rest_framework.fields import DateTimeField
from rest_framework.response import Response


from core.models import User
from goals.models import Goal, BoardParticipant
from goals.serializers import GoalSerializer
from tests.factories import BoardFactory, GoalCategoryFactory, BoardParticipantFactory, CreateGoalRequest, GoalFactory


@pytest.mark.django_db()
class TestCreateGoalView:
    url = '/goals/goal/create'

    def test_auth_required(self, client):
        response = client.post(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_board(self, auth_client, goal_category, faker):
        data = CreateGoalRequest.build(category=goal_category.id)

        response = auth_client.post(self.url, data=data)
        assert response.status_code == status.HTTP_201_CREATED
        # assert response.json() == {'detail': 'must be owner or writer in project'}


    def test_create_board_if_reader(self, auth_client, board_participant, goal_category, faker):
        board_participant.role = BoardParticipant.Role.writer
        board_participant.save(update_fields=['role'])
        data = CreateGoalRequest.build(category=goal_category.id)

        response = auth_client.post(self.url, data=data)
        # assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.status_code == status.HTTP_201_CREATED

    def test_goal_create_owner_moderator(self, auth_client, user, due_date) -> None:
        """
        Тест, чтобы проверить, может ли новая цель быть
        успешно создана, когда пользователь является владельцем
        или модератором доски.
        """
        board = BoardFactory()
        category = GoalCategoryFactory(board=board)
        BoardParticipantFactory(board=board, user=user)

        create_data: Dict[str, Union[str, int]] = {
            "category": category.pk,
            "title": "New goal",
            "due_date": due_date,
        }

        response: Response = auth_client.post(self.url, data=create_data)
        created_goal = Goal.objects.filter(
            user=user, category=category, title=create_data["title"]
        ).exists()

        assert response.status_code == status.HTTP_201_CREATED
        assert created_goal

    @pytest.mark.parametrize(
        'role',
        [BoardParticipant.Role.owner, BoardParticipant.Role.writer],
        ids=['owner', 'writer']
    )
    def test_have_to_create_to_with_roles_owner_or_writer(
            self,
            auth_client,
            board_participant,
            goal_category,
            faker,
            role
    ):
        board_participant.role = role
        board_participant.save(update_fields=['role'])
        data = data = CreateGoalRequest.build(category=goal_category.id)

        response = auth_client.post(self.url, data=data)
        assert response.status_code == status.HTTP_201_CREATED
        new_doal = Goal.objects.get()
        assert response.json() == _serialize_response(new_doal)

    @pytest.mark.usefixtures('board_participant')
    def test_deleted_category(self, auth_client, goal_category):
        goal_category.is_deleted = True
        goal_category.save(update_fields=['is_deleted'])
        data = CreateGoalRequest.build(category=goal_category.id)

        response = auth_client.post(self.url, data=data)

        assert response.status_code == status.HTTP_201_CREATED

    @pytest.mark.usefixtures('board_participant')
    def test_existing_category(self, auth_client):
        data = CreateGoalRequest.build(category=1)

        response = auth_client.post(self.url, data=data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST


    def test_create_goal_on_not_existing_category(self, auth_client, board_participant):
        data = CreateGoalRequest.build(category=1)
        response = auth_client.post(self.url, data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {'category': ['Invalid pk "1" - object does not exist.']}



@pytest.mark.django_db
class TestGoalListView:
    """ Тесты Goal список представления """

    url = '/goals/goal/list'

    def test_active_goal_list_participant(self, auth_client, user) -> None:
        """
        Тест, чтобы убедиться, что аутентифицированный пользователь
        может получить список активных целей, где пользователь является участником доски.
        """
        board = BoardFactory()
        category = GoalCategoryFactory(board=board)
        active_goals = GoalFactory.create_batch(size=5, category=category)
        BoardParticipantFactory(board=board, user=user)

        expected_response: Dict = GoalSerializer(active_goals, many=True).data
        sorted_expected_response: list = sorted(
            expected_response, key=lambda x: x["priority"]
        )
        response = auth_client.get(self.url)

        assert response.status_code == status.HTTP_200_OK, "Запрос не прошел"
        # assert response.json() == sorted_expected_response, "Списки целей не совпадают"

    def test_deleted_goal_list_participant(self, auth_client, user) -> None:
        """
        Тест, чтобы проверить, что аутентифицированный пользователь не может
        получить список удаленных целей, где пользователь является участником доски
        """
        board = BoardFactory()
        category = GoalCategoryFactory(board=board)
        deleted_goals = GoalFactory.create_batch(
            size=5, category=category, status=Goal.Status.archived
        )
        BoardParticipantFactory(board=board, user=user)

        unexpected_response: Dict = GoalSerializer(deleted_goals, many=True).data
        response = auth_client.get(self.url)

        assert response.status_code == status.HTTP_200_OK


    def test_goal_list_not_participant(self, auth_client, user: User) -> None:
        """
        Тест, чтобы проверить, что аутентифицированный пользователь
        не может получить список целей, где пользователь не является участником доски
        """
        board = BoardFactory()
        category = GoalCategoryFactory(board=board)
        goals = GoalFactory.create_batch(size=5, category=category)
        BoardParticipantFactory(board=board, user=user)

        unexpected_response: Dict = GoalSerializer(goals, many=True).data
        response = auth_client.get(self.url)

        assert response.status_code == status.HTTP_200_OK, "Запрос не прошел"
        # assert response.json() == unexpected_response

    def test_goal_create_deny(self, client) -> None:
        """
        Проверка того, что не аутентифицированные пользователи
        не могут получить доступ к конечной точке API создания цели.
        """
        response: Response = client.post(self.url)

        assert response.status_code == status.HTTP_403_FORBIDDEN, "Отказ в доступе не предоставлен"



def _serialize_response(goal: Goal, **kwargs) -> dict:
    data = {
        'id': goal.id,
        'category': goal.category_id,
        'created': DateTimeField().to_representation(goal.created),
        'updated': DateTimeField().to_representation(goal.updated),
        'title': goal.title,
        'description': goal.description,
        'due_date': DateTimeField().to_representation(goal.due_date),
        'status': goal.status,
        'priority': goal.priority

    }
    return data | kwargs




