from django_filters.rest_framework import FilterSet, filters

from recipes.models import Ingredient, Recipe, Tag


def get_queryset_filter(queryset, user, value, relation):
    if user.is_anonymous:
        return queryset
    if bool(value):
        return queryset.filter(**{relation: user})
    return queryset.exclude(**{relation: user})


class IngredientFilter(FilterSet):

    name = filters.CharFilter(
        field_name='name',
        lookup_expr='istartswith',
    )

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(FilterSet):

    is_favorited = filters.BooleanFilter(method='is_favorited_filter')
    is_in_shopping_list = filters.BooleanFilter(
        method='is_in_shopping_cart_filter'
    )
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )

    class Meta:
        model = Recipe
        fields = (
            'tags',
            'author',
            'is_favorited',
            'is_in_shopping_cart',
        )

    def is_favorited_filter(self, queryset, name, value):
        if value:
            return queryset.filter(favorites__user=self.request.user)
        return queryset.exclude(
            favorites__user=self.request.user
        )

    def is_in_shopping_cart_filter(self, queryset, name, value):
        if value:
            return Recipe.objects.filter(
                shopping_cart__user=self.request.user
            )
        else:
            return False
