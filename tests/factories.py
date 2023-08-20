import factory.django
import factory
from django.utils import timezone

from bot.models import TgUser
from core.models import User
from pytest_factoryboy import register

from goals.models import Board, BoardParticipant, GoalCategory, Goal, GoalComment


@register
class UserFactory(factory.django.DjangoModelFactory):
    username = factory.Faker('user_name')
    password = factory.Faker('password')

    class Meta:
        model = User

    @classmethod
    def _create(cls, model_class, *args, **kwargs) ->User:
        return User.objects.create_user(*args, **kwargs)

class DatesFactoryMixin(factory.django.DjangoModelFactory):
    created = factory.LazyFunction(timezone.now)
    updated = factory.LazyFunction(timezone.now)


@register
class BoardFactory(DatesFactoryMixin):
    title = factory.Faker('sentence')

    class Meta:
        model = Board

    @factory.post_generation
    def board_with_owner(self, create, owner, **kwargs):
        if owner:
            BoardParticipant.objects.create(board=self, user=owner, role=BoardParticipant.Role.owner)


@register
class BoardParticipantFactory(DatesFactoryMixin):
    board = factory.SubFactory(BoardFactory)
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = BoardParticipant


@register
class GoalCategoryFactory(DatesFactoryMixin):
    title = factory.Faker('catch_phrase')
    user = factory.SubFactory(UserFactory)
    board = factory.SubFactory(BoardFactory)

    class Meta:
        model = GoalCategory





@register
class GoalFactory(DatesFactoryMixin):
    user = factory.SubFactory(UserFactory)
    category = factory.SubFactory(GoalCategoryFactory)
    title = factory.Faker('catch_phrase')

    class Meta:
        model = Goal


@register
class GoalCommentFactory(DatesFactoryMixin):
    user = factory.SubFactory(UserFactory)
    goal = factory.SubFactory(GoalFactory)
    text = factory.Faker('sentence')

    class Meta:
        model = GoalComment

class SignUpRequest(factory.DictFactory):
    username = factory.Faker('user_name')
    password = factory.Faker('password')
    password_repeat = factory.LazyAttribute(lambda o: o.password)


class CreateGoalCategoryRequest(factory.DictFactory):
    title =factory.Faker('catch_phrase')


class CreateGoalRequest(factory.DictFactory):
    title =factory.Faker('catch_phrase')

class CreateGoalCommentRequest(factory.DictFactory):
    text =factory.Faker('sentence')

@register
class TuserFactory(factory.django.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    chat_id = factory.Faker('pyint')
    user_ud = chat_id
    username = user,
    verification_code = 'correct'

    class Meta:
        model = TgUser