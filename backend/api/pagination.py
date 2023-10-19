from rest_framework import pagination

from django.conf import settings


class CustomPagination(pagination.PageNumberPagination):
    page_size = settings.LIMIT_PAG_SIZE
    page_query_param = 'page'
    page_size_query_param = 'limit'
    max_page_size = settings.LIMIT_PAG


class CartPagination(pagination.LimitOffsetPagination):
    default_limit = settings.LIMIT_PAG
    page_query_param = 'page'
    page_size_query_param = 'limit'
    max_limit = settings.LIMIT_PAG
