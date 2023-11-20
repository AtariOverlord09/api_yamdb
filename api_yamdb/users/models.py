"""Модель User и менеджер модели User."""
from django.contrib.auth.models import (AbstractUser)
from django.db import models
from django.contrib.auth.validators import UnicodeUsernameValidator


class UserRole(models.TextChoices):
    """Модель выбора роли пользователя."""
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER = 'user'


class User(AbstractUser):
    """Модель User."""
    username = models.CharField(
        max_length=150,
        unique=True,
        verbose_name='юзернейм',
        validators=(UnicodeUsernameValidator(),)
    )
    email = models.EmailField(
        max_length=254,
        unique=True,
        verbose_name='адрес электронной почты',
    )
    confirmation_code = models.CharField(
        max_length=7,
        verbose_name='код подтверждения',
    )
    bio = models.TextField(
        max_length=256,
        verbose_name='биография',
        blank=True,
        null=True,
    )
    role = models.CharField(
        max_length=30,
        choices=UserRole.choices,
        default=UserRole.USER,
        blank=False,
        null=False,
        verbose_name='роль',
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    @property
    def user_is_staff(self):
        return self.is_staff

    @property
    def is_admin(self):
        return self.role == UserRole.ADMIN

    @property
    def is_moderator(self):
        return self.role == UserRole.MODERATOR

    @property
    def is_user(self):
        return self.role == UserRole.USER

    def __str__(self):
        return self.username
