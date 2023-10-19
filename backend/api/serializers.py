from django.db.models import F
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import (IntegerField, ModelSerializer,
                                        PrimaryKeyRelatedField,
                                        SerializerMethodField)
from rest_framework.status import HTTP_400_BAD_REQUEST

from core.constants import (MAX_AMOUNT, MAX_COOKING_TIME, MIN_AMOUNT,
                            MIN_COOKING_TIME)
from recipes.models import (Cart, Ingredient, Recipe, RecipeIngredientAmount,
                            Tag)
from users.models import User


class CartSerializer(ModelSerializer):
    """Сериализатор для модели Cart."""

    class Meta:
        model = Cart
        fields = '__all__'
        ordering = '-add_to_shopping_cart_date'


class IndexSerializer(ModelSerializer):
    """Сокращенная модель Рецептов."""
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )
        read_only_fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class CustomUserCreateSerializer(UserCreateSerializer):
    """Кастомный сериализатор от джосер, для создания пользователя."""

    class Meta:
        model = User
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
        )


class CustomUserSerializer(UserSerializer):
    """Кастомный сериализатор от джосер"""

    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return (
            user.subscriber_user.filter(author=obj).exists()
        )


class SubscriptionSerializer(CustomUserSerializer):
    """Сериализатор подписки."""

    recipes = SerializerMethodField()
    recipes_count = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )
        read_only_fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'recipes',
        )

    def get_recipes_count(self, obj):
        return obj.recipe_author.count()

    def get_recipes(self, obj):
        request = self.context['request']
        recipes_limit = request.GET.get('recipes_limit')
        recipes = obj.recipe_author.all()
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        return IndexSerializer(
            recipes, many=True, read_only=True
        ).data

    def validate(self, data):
        author = self.instance
        user = self.context['request'].user
        if user.subscriber_user.filter(author=author).exists():
            raise ValidationError(
                detail='Нельзя подписаться дважды!',
                code=HTTP_400_BAD_REQUEST
            )
        if user == author:
            raise ValidationError(
                detail='Нельзя подписаться на себя!',
                code=HTTP_400_BAD_REQUEST
            )
        return data


class TagSerializer(ModelSerializer):
    """Сериализатор тегов."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)
        read_only_fields = ('__all__',)


class IngredientSerializer(ModelSerializer):
    """Сериализатор ингредиентов."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)
        read_only_fields = ('__all__',)


class RecipeIngredientAmountSerializer(ModelSerializer):
    """Сериализатор игредиента в рецепте."""

    id = IntegerField(write_only=True)
    amount = IntegerField(min_value=MIN_AMOUNT, max_value=MAX_AMOUNT)

    class Meta:
        model = RecipeIngredientAmount
        fields = (
            'id',
            'amount',
        )


class ReadRecipeSerializer(ModelSerializer):
    """Сериализатор просмотра рецепта."""

    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    is_favorited = SerializerMethodField
    is_in_shopping_cart = SerializerMethodField
    ingredients = SerializerMethodField

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user and not user.is_anonymous:
            related_manager = getattr(user, 'favorites')
            return related_manager.filter(recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if not user.is_anonymous:
            related_manager = getattr(user, 'shopping_cart')
            return related_manager.filter(recipe=obj).exists()
        return False

    def get_ingredients(self, obj):
        return (
            obj.ingredients.values(
                'id',
                'name',
                'measurement_unit',
                amount=F('recipeingredientamount__amount')
            )
        )


class WriteRecipeSerializer(ModelSerializer):
    """Сериализатор создания рецепта."""

    ingredients = RecipeIngredientAmountSerializer(many=True)
    tags = PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )
    image = Base64ImageField()
    author = CustomUserSerializer(read_only=True)
    cooking_time = IntegerField(
        min_value=MIN_COOKING_TIME,
        max_value=MAX_COOKING_TIME
    )

    def empty_field(self, field, value):
        if field := value:
            return field
        else:
            raise ValidationError({
                "{field}": "Выберите что-нибудь!"
            })

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'author',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    def validate_ingredients(self, value):
        ingredients = self.empty_field(
            field='ingredients', value=value
        )
        if not ingredients:
            raise ValidationError({
                "ingredients": "Нельзя добавлять без ингредиентов!"
            })
        ingredients_in_recipe = []
        for ingredient in ingredients:
            if ingredient in ingredients_in_recipe:
                raise ValidationError({
                    "ingredients": "Вы уже добавили этот ингредиент!"
                })
            ingredients_in_recipe.append(ingredient)
        return value

    def validate_tags(self, value):
        tags = self.empty_field(
            field='tags', value=value
        )
        if not tags:
            raise ValidationError({
                "tags": "Добавьте хотя бы один тег!"
            })
        tags_in_recipe = []
        for tag in tags:
            if tag in tags_in_recipe:
                raise ValidationError({
                    "tags": "Этот тег уже выбран!"
                })
            tags_in_recipe.append(tag)
        return value

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')

        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)

        RecipeIngredientAmount.objects.bulk_create(
            [RecipeIngredientAmount(
                recipe=recipe,
                ingredient_id=ingredient['id'],
                amount=ingredient['amount']
            ) for ingredient in ingredients]
        )

        return recipe

    def update(self, instance, validated_data):
        if 'tags' in validated_data:
            instance.tags.clear()
            instance.tags.set(validated_data.pop('tags'))
        if 'ingredients' in validated_data:
            RecipeIngredientAmount.objects.filter(recipe=instance).delete()
            ingredients = validated_data.pop('ingredients')
            RecipeIngredientAmount.objects.bulk_create(
                [RecipeIngredientAmount(
                    recipe=instance,
                    ingredient_id=ingredient['id'],
                    amount=ingredient['amount']
                ) for ingredient in ingredients]
            )
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        request = self.context['request']
        context = {'request': request}
        return ReadRecipeSerializer(
            instance=instance,
            context=context,
        ).data
