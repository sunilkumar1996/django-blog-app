from django.db import models
from django.contrib.auth.models import AbstractUser
from .manager import PersonManager

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True, editable=False)
    class Meta:
        abstract = True

class User(AbstractUser, BaseModel):
    username = None
    first_name = models.CharField(max_length=100, blank=False)
    last_name = models.CharField(max_length=100, blank=False)
    contact_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(max_length=50, unique=True, null=True, blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = PersonManager()

    def __str__(self):
        return self.email
    
    # class Meta:
    #     verbose_name = 'User'
    #     verbose_name_plural = 'Users'
