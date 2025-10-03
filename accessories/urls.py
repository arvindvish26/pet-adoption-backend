from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, AccessoryViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'accessories', AccessoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
