from goals.apps import GoalsConfig
from django.urls import path

from goals.views.boards import BoardCreateView, BoardListView, BoardDetailView
from goals.views.category import CategoryListView, CategoryCreateView, CategoryDetailView
from goals.views.goals import GoalListView, GoalCreateView, GoaDetailView
from goals.views.comments import GoalCommentListView, GoalCommentCreateView, GoalCommentDetailView

app_name = 'goals'

urlpatterns = [
    path('board/create', BoardCreateView.as_view()),
    path('board/list', BoardListView.as_view()),
    path('board/<int:pk>', BoardDetailView.as_view()),

    path('goal_category/create', CategoryCreateView.as_view()),
    path('goal_category/list', CategoryListView.as_view()),
    path('goal_category/<int:pk>', CategoryDetailView.as_view()),

    path('goal/create', GoalCreateView.as_view()),
    path('goal/list', GoalListView.as_view()),
    path('goal/<int:pk>', GoaDetailView.as_view()),

    path('goal_comment/create', GoalCommentCreateView.as_view()),
    path('goal_comment/list', GoalCommentListView.as_view()),
    path('goal_comment/<int:pk>', GoalCommentDetailView.as_view()),
]
