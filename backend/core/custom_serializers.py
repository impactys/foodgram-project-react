from django.db.models import F


def get_recipes_count(self, obj):
    return obj.recipe_author.count()


def get_recipes(self, obj):
    from api.serializers import IndexSerializer
    request = self.context['request']
    recipes_limit = request.GET.get('recipes_limit')
    recipes = obj.recipe_author.all()
    if recipes_limit:
        recipes = recipes[:int(recipes_limit)]
    return IndexSerializer(
        recipes, many=True, read_only=True
    ).data


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
