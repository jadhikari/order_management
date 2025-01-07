from rest_framework import serializers
from .models import CustomUser, Restaurant, RestaurantProfile


class CustomUserSerializer(serializers.ModelSerializer):
    restaurant_id = serializers.PrimaryKeyRelatedField(
        queryset=Restaurant.objects.all(), write_only=True, source='restaurant', required=False
    )

    class Meta:
        model = CustomUser
        fields = [
            'id', 'email', 'role', 'restaurant', 'restaurant_id',
            'is_active', 'is_staff', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'restaurant']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, data):
        user = self.context['request'].user
        if user.role == 'admin' and data.get('role') not in ['cook', 'waiter', 'accountant']:
            raise serializers.ValidationError("Admins can only create cook, waiter, or accountant roles.")
        return data

    def create(self, validated_data):
        request_user = self.context['request'].user
        if request_user.role == 'admin':
            validated_data['restaurant'] = request_user.restaurant
        user = CustomUser.objects.create(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


class RestaurantProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestaurantProfile
        fields = ['id', 'restaurant', 'phone_number', 'address', 'website']
        read_only_fields = ['restaurant']


class RestaurantSerializer(serializers.ModelSerializer):
    profile = RestaurantProfileSerializer(read_only=True)

    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'unique_code', 'subscription_active', 'subscription_date', 'profile', 'created_at', 'updated_at']
        read_only_fields = ['unique_code', 'created_at', 'updated_at']
