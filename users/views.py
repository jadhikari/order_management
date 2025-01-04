from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import CustomUser, Restaurant
from .serializers import (
    CustomUserSerializer,
    RestaurantSerializer,
    CustomTokenObtainPairSerializer,
    ChangePasswordSerializer
)
from .permissions import IsSuperAdminOrRestaurantUser


class CustomTokenView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user_id = serializer.validated_data['user_id']
            new_password = serializer.validated_data['new_password']
            try:
                user_to_update = CustomUser.objects.get(id=user_id)
            except CustomUser.DoesNotExist:
                return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

            # Check permissions
            if request.user.role == 'super_admin':
                serializer.update_password(user_to_update, new_password)
            elif request.user.role == 'admin' and user_to_update.restaurant == request.user.restaurant:
                serializer.update_password(user_to_update, new_password)
            else:
                return Response({"error": "You do not have permission to change this password."}, status=status.HTTP_403_FORBIDDEN)

            return Response({"success": "Password updated successfully."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomUserViewSet(viewsets.ModelViewSet):
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'super_admin':
            return CustomUser.objects.all()
        return CustomUser.objects.filter(restaurant=user.restaurant)


class RestaurantViewSet(viewsets.ModelViewSet):
    serializer_class = RestaurantSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'super_admin':
            return Restaurant.objects.all()
        return Restaurant.objects.filter(id=user.restaurant.id)
