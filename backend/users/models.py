from django.contrib.auth.models import AbstractUser
from django.db import models

from core import validators
from django.conf import settings


class User(AbstractUser):
    """Кастомная модель пользователя."""

    email = models.EmailField(
        verbose_name='Электронная почта',
        max_length=settings.MAX_EMAEL_LENGHT,
        unique=True,
    )
    username = models.CharField(
        verbose_name='Ник',
        max_length=settings.MAX_USER_LENGHT,
        unique=True,
        validators=(
            validators.validate_username,)
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=settings.MAX_USER_LENGHT,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=settings.MAX_USER_LENGHT,
    )
    password = models.CharField(
        verbose_name='Пароль',
        max_length=settings.MAX_USER_LENGHT,

    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = (
        'username',
        'first_name',
        'last_name',
    )

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        constraints = (
            models.UniqueConstraint(
                fields=[
                    'username',
                    'email',
                ],
                name='unique_username_email',
            ),
        )


class Subscription(models.Model):
    """Модель подписки."""
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        related_name='subscriber_user',
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор в подписке',
        related_name='author_in_subscription',
        on_delete=models.CASCADE,
    )
    subscription_date = models.DateTimeField(
        verbose_name='Дата подписки',
        auto_now=True,
    )

    class Meta:
        ordering = ('subscription_date',)
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.UniqueConstraint(
                fields=['user', 'author', ],
                name='unique_subscription',
            ),
            models.CheckConstraint(
                check=~models.Q(user_id=models.F('author_id')),
                name='no_self_subscription'
            ),
        )
