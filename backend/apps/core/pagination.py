from rest_framework.pagination import PageNumberPagination

class StandardResultsSetPagination(PageNumberPagination):
    """
    Standard pagination with support for page_size query param
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 1000
