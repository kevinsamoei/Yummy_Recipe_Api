# coding=utf-8
from flask import url_for
from flask import current_app


class Pagination:
    """
    This is a helper method to create pagination
    """
    def __init__(self, request, query, resource_for_url, key_name, schema, results_per_page, page):
        self.request = request
        self.query = query
        self.resource_for_url = resource_for_url
        self.key_name = key_name
        self.schema = schema
        self.page = page
        self.results_per_page = results_per_page
        self.page_argument_name = current_app.config['PAGINATION_PAGE_ARGUMENT_NAME']

    def paginate_query(self):
        """
        create paginated queries of the resources
        """
        page_number = self.request.args.get(self.page_argument_name, 1, type=int)
        paginated_objects = self.query.paginate(
            page_number,
            per_page=self.results_per_page,
            error_out=False
        )
        objects = paginated_objects.items
        if paginated_objects.has_prev:
            previous_page_url = url_for(
                self.resource_for_url,
                page=page_number-1,
                _external=True
            )
        else:
            previous_page_url = None
        if paginated_objects.has_next:
            next_page_url = url_for(
                self.resource_for_url,
                page=page_number+1,
                _external=True
            )
        else:
            next_page_url = None
        dumped_objects = self.schema.dump(objects, many=True).data
        return ({
            self.key_name: dumped_objects,
            'previous': previous_page_url,
            'pages': paginated_objects.pages,
            'next': next_page_url,
            'count': paginated_objects.total
        })
