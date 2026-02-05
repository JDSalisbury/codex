# battle/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import MailViewSet, ArenaViewSet

router = DefaultRouter()

# Register ViewSets
router.register(r'mail', MailViewSet, basename='mail')
router.register(r'arena', ArenaViewSet, basename='arena')

# Future ViewSets:
# router.register(r'battles', BattleViewSet, basename='battle')
# router.register(r'missions', MissionViewSet, basename='mission')

urlpatterns = [
    path('', include(router.urls)),
]
