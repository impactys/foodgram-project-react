from rest_framework import pagination

from core.constants import limit_pag, limit_pag_size


class CustomPagination(pagination.PageNumberPagination):
    page_size = limit_pag_size
    page_query_param = 'page'
    page_size_query_param = 'limit'
    max_page_size = limit_pag


class CartPagination(pagination.LimitOffsetPagination):
    default_limit = limit_pag
    page_query_param = 'page'
    page_size_query_param = 'limit'
    max_limit = limit_pag
