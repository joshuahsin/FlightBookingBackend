from django.urls import path, include
from rest_framework.routers import DefaultRouter

from cart_item.views import CartItemViewSet

router = DefaultRouter()
router.register(r'cart-item', CartItemViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
