from rest_framework import serializers
from .models import CustomUser, Restaurant, Profile
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        data['role'] = user.role
        if user.role != 'super_admin':
            data['restaurant'] = user.restaurant.unique_code if user.restaurant else None
        return data


class ChangePasswordSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    new_password = serializers.CharField(write_only=True, min_length=8, required=True)

    def validate_user_id(self, value):
        """
        Validate that the user exists.
        """
        try:
            user = CustomUser.objects.get(id=value)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("User not found.")
        return value

    def update_password(self, user, new_password):
        """
        Update the user's password.
        """
        user.set_password(new_password)
        user.save()
        return user


# Restaurant Serializer
class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = [
            'id', 'name', 'unique_code', 'subscription_active',
            'subscription_date', 'expiration_date'
        ]


# Profile Serializer
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id', 'phone_number', 'address', 'user']
        extra_kwargs = {'user': {'read_only': True}}


# Custom User Serializer
class CustomUserSerializer(serializers.ModelSerializer):
    restaurant = RestaurantSerializer(read_only=True)
    profile = ProfileSerializer(read_only=True)
    restaurant_id = serializers.PrimaryKeyRelatedField(
        queryset=Restaurant.objects.all(), write_only=True, source='restaurant', required=False
    )
    profile_data = ProfileSerializer(write_only=True, required=False)
    restaurant_code = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            'id', 'email', 'username', 'role', 'restaurant_code',
            'restaurant', 'restaurant_id', 'profile', 'profile_data'
        ]
        extra_kwargs = {
            'username': {'required': False},  # Set username as optional since email is the primary identifier
        }

    def get_restaurant_code(self, obj):
        """
        Dynamically retrieve the restaurant's unique code.
        """
        return obj.restaurant.unique_code if obj.restaurant else None

    def create(self, validated_data):
        profile_data = validated_data.pop('profile_data', None)
        user = super().create(validated_data)

        # Create Profile if profile_data is provided
        if profile_data:
            Profile.objects.create(user=user, **profile_data)

        return user

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile_data', None)

        # Update user data
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update or create profile if profile_data is provided
        if profile_data:
            Profile.objects.update_or_create(user=instance, defaults=profile_data)

        return instance
