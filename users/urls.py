from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomUserViewSet, RestaurantViewSet, RestaurantProfileViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

# Set up router for ViewSets
router = DefaultRouter()
router.register(r'users', CustomUserViewSet, basename='user')
router.register(r'restaurants', RestaurantViewSet, basename='restaurant')
router.register(r'profiles', RestaurantProfileViewSet, basename='profile')

# Define urlpatterns
urlpatterns = [
    path('', include(router.urls)),  # Include all router-based endpoints
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # JWT Token obtain
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # JWT Token refresh
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),  # JWT Token verification
]
