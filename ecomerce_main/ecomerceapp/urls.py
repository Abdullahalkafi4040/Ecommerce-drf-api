from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet, ProductViewSet, 
    CartItemViewSet, OrderViewSet, 
    PaymentInitiateView, PaymentSuccessView
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'cart-items', CartItemViewSet, basename='cart-item')
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    path('', include(router.urls)),
    path('payments/initiate/<int:order_id>/', PaymentInitiateView.as_view(), name='payment-initiate'),
    path('payments/success/', PaymentSuccessView.as_view(), name='payment-success'),
]