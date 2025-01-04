from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.routers import DefaultRouter
from .views import CustomUserViewSet, RestaurantViewSet, ChangePasswordView

router = DefaultRouter()
router.register('users', CustomUserViewSet, basename='user')
router.register('restaurants', RestaurantViewSet, basename='restaurant')

urlpatterns = [
    path('', include(router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # Token obtain
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # Token refresh
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
]