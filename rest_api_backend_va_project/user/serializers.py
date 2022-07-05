from rest_framework import serializers
from .models import User, Subscription


class CreateUserSerializers(serializers.ModelSerializer):
    """Post request"""
    confirm_email = serializers.BooleanField(read_only=True)
    confirm_account = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'username', 'first_name', 'last_name', 'email', 'city',
            'birth_day', 'sex', 'photo', 'confirm_email', 'confirm_account'
        )


class UserSerializers(serializers.ModelSerializer):
    """Get request ===> that get_city_display works"""
    confirm_email = serializers.BooleanField(read_only=True)
    confirm_account = serializers.BooleanField(read_only=True)
    city = serializers.CharField(source="get_city_display")
    sex = serializers.CharField(source="get_sex_display")

    class Meta:
        model = User
        fields = (
            'id', 'username', 'first_name', 'last_name', 'email', 'city',
            'birth_day', 'sex', 'photo', 'confirm_email', 'confirm_account'
        )


class ChangePasswordSerializer(serializers.Serializer):
    """Change password"""
    model = User
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_new_password = serializers.CharField(required=True)


class GetMeSerializer(serializers.ModelSerializer):
    """Get data about me"""
    class Meta:
        model = User
        fields = (
            'id', 'username', 'first_name', 'sex',
            'birth_day', 'city', 'email', 'photo',
            'confirm_email', 'confirm_account'
        )


class UpdateUserSerializers(serializers.ModelSerializer):
    """Change data user"""
    class Meta:
        model = User
        fields = ('first_name', 'city', 'birth_day', 'sex', 'photo')


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = (
            'author', 'date_start', 'date_end'
        )


class UserRoomChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'photo')


class UserAdOnMapSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'photo')
