from etl_logger import logger

from functools import wraps
from time import sleep
from traceback import format_exc


def backoff(errors=(Exception,), steps=2):
    def decorator(func):
        @wraps(func)
        def inner(*args, **kwargs):
            for t in range(1, inner.timing + 1):
                try:
                    result = func(*args, **kwargs)
                    return result
                except errors:
                    logger.error(format_exc())
                    if t == inner.timing:
                        break
                    sleep(t)

        inner.timing = steps
        return inner

    return decorator
