from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 15


class CustomPagination(PageNumberPagination):
    # page = DEFAULT_PAGE  # <-- This variable name should not be used !
    page_size = DEFAULT_PAGE_SIZE  # <-- how many results on a single page.

    # how to name the variable that points at page number.
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):

        # Testing:
        # print('LOG: CustomPagination: page=', self.page)
        # print('LOG: CustomPagination: data= ', data)
        # test = self.request.GET.get('page_size')
        # print('LOG: CustomPagination: test=', test)

        return Response({
            'data': data,  # query results, just as many as can fit the page.
            'meta': {  # page details.

                # how many pages will be.
                # use the built-in .page function to get the. num_page
                'last_page': self.page.paginator.num_pages,

                # use the ?= of the get method = query the url for variables
                # example: http://localhost:8000/api/users?page=1 --> ?page=1 --> query result: 1.
                'page': int(self.request.GET.get('page', DEFAULT_PAGE)),

                'page_size': str(self.page_size) + ' results'
            }
        })
