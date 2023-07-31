from rest_framework import serializers
from rest_framework.exceptions import ValidationError, PermissionDenied, NotFound

from core.serializers import ProfileSerializers
from goals.models import GoalCategory, Goal, GoalComment


class GoalCategorySerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = GoalCategory
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'user', 'is_deleted')


class GoalCategoryWithUserSerializer(GoalCategorySerializer):
    user = ProfileSerializers(read_only=True)


class GoalSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Goal
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'user')


    def validated_categry(self, value: GoalCategory) -> GoalCategory:
        if value.is_deleted:
            raise NotFound('Category not found')

        if self.context['request'].user_id != value.user_id:
            raise PermissionDenied
        return value


class GoalWithUserSerializer(GoalSerializer):
    user = ProfileSerializers(read_only=True)


class GoalCommentSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = GoalComment
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'user')

    def validate_goal(self, value: Goal) -> Goal:
        if value.status == Goal.Status.archived:
            raise NotFound('Goal not found')
        if self.context['request'].user_id != value.user_id:
            raise PermissionDenied
        return value


class GoalCommentWithUserSerializer(GoalCommentSerializer):
    user = ProfileSerializers(read_only=True)
    goal = serializers.PrimaryKeyRelatedField(read_only=True)


