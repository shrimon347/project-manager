import logging
import time
import uuid
from urllib.parse import urlencode


class RequestContextFilter(logging.Filter):
    def filter(self, record):
        if not hasattr(record, "request_id"):
            record.request_id = "-"
        return True


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger("app.request")

    def __call__(self, request):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        start_time = time.perf_counter()
        query_string = urlencode(sorted(request.GET.items()))
        full_path = f"{request.path}?{query_string}" if query_string else request.path
        user_id = getattr(getattr(request, "user", None), "id", None) or "anonymous"

        request.request_id = request_id
        self.logger.info(
            "Incoming request method=%s path=%s remote=%s user=%s",
            request.method,
            full_path,
            request.META.get("REMOTE_ADDR", "-"),
            user_id,
            extra={"request_id": request_id},
        )

        try:
            response = self.get_response(request)
        except Exception:
            duration_ms = int((time.perf_counter() - start_time) * 1000)
            self.logger.exception(
                "Unhandled exception method=%s path=%s duration_ms=%s user=%s",
                request.method,
                full_path,
                duration_ms,
                user_id,
                extra={"request_id": request_id},
            )
            raise

        duration_ms = int((time.perf_counter() - start_time) * 1000)
        response["X-Request-ID"] = request_id
        message = "Completed request method=%s path=%s status=%s duration_ms=%s user=%s"
        args = (request.method, full_path, response.status_code, duration_ms, user_id)
        if response.status_code >= 500:
            self.logger.error(message, *args, extra={"request_id": request_id})
        elif response.status_code >= 400:
            self.logger.warning(message, *args, extra={"request_id": request_id})
        else:
            self.logger.info(message, *args, extra={"request_id": request_id})
        return response
