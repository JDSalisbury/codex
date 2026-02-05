
from rest_framework import routers
from codex.views import OperatorView, GarageView, CoreView, ScrapyardView, MoveView

router = routers.DefaultRouter()

router.register(r'operators', OperatorView, basename='operator')
router.register(r'garages', GarageView, basename='garage')
router.register(r'cores', CoreView, basename='core')
router.register(r'scrapyard', ScrapyardView, basename='scrapyard')
router.register(r'moves', MoveView, basename='move')

urlpatterns = [] + router.urls
