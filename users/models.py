from django.db import models
from django.contrib.auth.models import AbstractBaseUser

class Role(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
class User(AbstractBaseUser):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    name = models.CharField(max_length=255, null=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, related_name="users")
    last_login = models.DateTimeField(blank=True, null=True)
    def __str__(self):
        return self.email