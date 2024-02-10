from rest_framework import serializers
from users.models import RSOUser, UserMedia


class UserAvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода аватарки из модели с Медиа юзера."""

    class Meta:
        model = UserMedia
        fields = ('photo',)


class ShortUserSerializer(serializers.ModelSerializer):
    """Для сериализации небольшой части данных пользователя."""

    avatar = UserAvatarSerializer(source='media', read_only=True)

    class Meta:
        model = RSOUser
        fields = (
            'id',
            'username',
            'avatar',
            'email',
            'first_name',
            'last_name',
            'patronymic_name',
            'date_of_birth',
            'membership_fee',
            'is_verified',
        )
