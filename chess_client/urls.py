

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view),
    path('new_game', views.new_game, name="new_game"),
    path('custom_match', views.custom_match, name="custom_match"),
    path('ai_vs_ai', views.ai_vs_ai, name="ai_vs_ai"),
    path('game', views.game, name="game"),
    path('validate', views.player_validate, name="validate"),
    path('call_ai', views.call_ai, name='call_ai'),
    path('pawn_promote', views.pawn_promote, name='pawn_promote')
]
