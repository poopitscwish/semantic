from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
from .models import User

class EmailAuthBackend(BaseBackend):

    def authenticate(self, request, username=None, password=None):
        try:
            print(username, password)
            user = User.objects.get(email=username)  # Используем email вместо username
            pwd_valid = check_password(password, user.password)
            if pwd_valid:
                return user
            return None
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
