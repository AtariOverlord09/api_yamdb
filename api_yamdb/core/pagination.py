from rest_framework.pagination import PageNumberPagination


class PageNumPagination(PageNumberPagination):
    page_size = 5
