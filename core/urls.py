from django.urls import path

from core.apps import CoreConfig
from core.views import SignupView, LoginView, ProfileView, UpdatePasswordView

app_name = 'core'

urlpatterns = [
    path('signup', SignupView.as_view()),
    path('login', LoginView.as_view()),
    path('profile', ProfileView.as_view()),
    path('update_password', UpdatePasswordView.as_view()),
]
