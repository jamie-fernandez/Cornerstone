import functools
import logging

from app.exceptions import BridgeError

logger = logging.getLogger(__name__)


def bridge_method(func):
    """Wrap an API method with the standard bridge response envelope.

    Returns ``{"status": "success", "data": ...}`` on success and
    ``{"status": "error", "message": ...}`` on failure. Unexpected exceptions
    are logged in full server-side; only ``BridgeError`` messages cross the
    bridge, so internals (paths, SQL, stack traces) never leak to JS.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            data = func(*args, **kwargs)
            return {"status": "success", "data": data}
        except BridgeError as e:
            return {"status": "error", "message": str(e)}
        except Exception:
            logger.exception("API call '%s' failed", func.__name__)
            return {"status": "error", "message": "An internal error occurred"}

    return wrapper
