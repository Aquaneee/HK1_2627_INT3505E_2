from datetime import datetime, timezone
from email.utils import format_datetime
from functools import wraps
from flask import request, jsonify, make_response
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger("sunset")


def http_date(dt):
    return format_datetime(dt, usegmt=True)


def deprecate_at(sunset_date, replacement=None):
    def wrap(fn):
        @wraps(fn)
        def inner(*a, **kw):
            now = datetime.now(timezone.utc)
            log.warning("deprecated_call %s %s", request.path, request.remote_addr)

            if now >= sunset_date:
                r = make_response(
                    jsonify(
                        {
                            "error": "gone",
                            "sunset": http_date(sunset_date),
                            "use_instead": replacement,
                        }
                    ),
                    410,
                )
            else:
                result = fn(*a, **kw)
                body, status = result if isinstance(result, tuple) else (result, 200)
                r = make_response(jsonify(body), status)

            r.headers["Sunset"] = http_date(sunset_date)
            r.headers["Deprecation"] = "true"
            if replacement:
                r.headers["Link"] = f'<{replacement}>; rel="successor-version"'
            return r

        return inner

    return wrap