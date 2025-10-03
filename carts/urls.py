from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CartViewSet, CartAccessoryViewSet

router = DefaultRouter()
router.register(r'carts', CartViewSet)
router.register(r'cart-items', CartAccessoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
