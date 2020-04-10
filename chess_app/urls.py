

from django.urls import path
from . import views

urlpatterns = [
    path('validate_move', views.move_validate),
    path('ai_move', views.ai_handler)
]
