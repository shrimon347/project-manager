from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response


class StandardResultsSetPagination(LimitOffsetPagination):
    default_limit = 10
    limit_query_param = "limit"
    offset_query_param = "offset"
    max_limit = 100

    def get_paginated_response(self, data):
        limit = self.limit if self.limit is not None else self.default_limit
        offset = self.offset
        total_items = self.count

        return Response(
            {
                "success": True,
                "message": "Data fetched successfully.",
                "data": {
                    "items": data,
                    "pagination": {
                        "limit": limit,
                        "offset": offset,
                        "total_items": total_items,
                        "has_next": self.get_next_link() is not None,
                        "has_previous": self.get_previous_link() is not None,
                        "next": self.get_next_link(),
                        "previous": self.get_previous_link(),
                    },
                },
            }
        )
