from rest_framework.response import Response


def success_response(*, message: str, data=None, status_code: int = 200) -> Response:
    payload = {
        "success": True,
        "message": message,
        "data": data if data is not None else {},
    }
    return Response(payload, status=status_code)
