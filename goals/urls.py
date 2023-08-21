from goals.apps import GoalsConfig
from django.urls import path

from goals.views.boards import BoardCreateView, BoardListView, BoardDetailView
from goals.views.category import CategoryListView, CategoryCreateView, CategoryDetailView
from goals.views.goals import GoalListView, GoalCreateView, GoaDetailView
from goals.views.comments import GoalCommentListView, GoalCommentCreateView, GoalCommentDetailView

app_name = 'goals'

urlpatterns = [
    path('board/create', BoardCreateView.as_view(), name='create_board'),
    path('board/list', BoardListView.as_view(), name='board_list'),
    path('board/<int:pk>', BoardDetailView.as_view(), name='board_detail'),

    path('goal_category/create', CategoryCreateView.as_view(), name='create_category'),
    path('goal_category/list', CategoryListView.as_view(), name='category_list'),
    path('goal_category/<int:pk>', CategoryDetailView.as_view(), name='category_detail'),

    path('goal/create', GoalCreateView.as_view(), name='create_goal'),
    path('goal/list', GoalListView.as_view(), name='goal_list'),
    path('goal/<int:pk>', GoaDetailView.as_view(), name='goal_detail'),

    path('goal_comment/create', GoalCommentCreateView.as_view(), name='create_comment'),
    path('goal_comment/list', GoalCommentListView.as_view(), name='comment_list'),
    path('goal_comment/<int:pk>', GoalCommentDetailView.as_view(), name='comment_detail'),
]
