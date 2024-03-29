from rest_framework import serializers
from .models import User  # Импортируйте вашу модель пользователя

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'role', 'name']  # Укажите поля, которые вы хотите включить в сериализацию
