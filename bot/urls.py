from django.urls import path

from . import views

app_name = 'bot'

urlpatterns = [
    path("verify", views.VerificationView.as_view(), name='verify'),
]
