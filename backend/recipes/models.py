from colorfield.fields import ColorField
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint

User = get_user_model()


class Tag(models.Model):
    """Модель для тегов."""

    name = models.CharField(
        verbose_name='Название',
        max_length=settings.MAX_NAME_SLUG_MEASUREMENT_UNIT_LENGHT,
        unique=True,
    )
    color = ColorField(
        verbose_name='Цвет в HEX',
        max_length=settings.MAX_TAG_COLOR_LENGHT,
        unique=True
    )
    slug = models.SlugField(
        verbose_name='Ссылка',
        max_length=settings.MAX_NAME_SLUG_MEASUREMENT_UNIT_LENGHT,
        unique=True,
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class Ingredient(models.Model):
    """Модель для ингредиента."""
    name = models.CharField(
        db_index=True,
        verbose_name='Название ингредиента',
        max_length=settings.MAX_NAME_SLUG_MEASUREMENT_UNIT_LENGHT,
    )
    measurement_unit = models.CharField(
        verbose_name='Единицы измерения',
        max_length=settings.MAX_NAME_SLUG_MEASUREMENT_UNIT_LENGHT,
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = (
            models.UniqueConstraint(
                fields=[
                    'name',
                    'measurement_unit',
                ],
                name='unique_name_measurement_unit',
            ),
        )


class Recipe(models.Model):
    """Модель рецепта."""

    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        related_name='recipe_author',
        on_delete=models.CASCADE,
    )
    name = models.CharField(
        verbose_name='Название блюда',
        max_length=settings.MAX_NAME_SLUG_MEASUREMENT_UNIT_LENGHT,
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='recipes/images/',
    )
    text = models.TextField(
        verbose_name='Описание',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredientAmount',
        related_name='ingredients_in_recipe',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тег',
        related_name='recipe_tags',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время готовки',
        validators=(
            MinValueValidator(
                settings.MIN_COOKING_TIME
            ),
            MaxValueValidator(
                settings.MAX_COOKING_TIME
            )
        )
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        ordering = ('-pub_date', 'name',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class RecipeIngredientAmount(models.Model):
    """Модель ингредиентов в рецепте"""
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        on_delete=models.CASCADE,
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=(
            MinValueValidator(
                settings.MIN_AMOUNT
            ),
            MaxValueValidator(
                settings.MAX_AMOUNT
            )
        )
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=[
                    'recipe',
                    'ingredient',
                ],
                name='unique_recipe_ingredient',
            ),
        )
        ordering = ('recipe', 'ingredient',)
        verbose_name = 'Количество ингредиента в рецепте'


class AbstractUsersRecipe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )

    class Meta:
        abstract = True
        constraints = [
            UniqueConstraint(
                fields=('user', 'recipe'),
                name='%(app_label)s_%(class)s_unique'
            )
        ]


class FavoriteRecipe(AbstractUsersRecipe):
    """Модель  избранных рецептов"""
    add_to_favorite_date = models.DateTimeField(
        verbose_name='Дата добавления в избранное',
        auto_now=True,
    )

    class Meta(AbstractUsersRecipe.Meta):
        default_related_name = 'favorites'
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        ordering = ('add_to_favorite_date',)


class Cart(AbstractUsersRecipe):
    """Модель списка покупок"""
    add_to_shopping_cart_date = models.DateTimeField(
        verbose_name='Дата добавления в корзину',
        auto_now=True,
    )

    class Meta(AbstractUsersRecipe.Meta):
        default_related_name = 'shopping_cart'
        verbose_name = 'Рецепт в корзине'
        verbose_name_plural = 'Рецепты в корзине'
        ordering = ('-id',)
