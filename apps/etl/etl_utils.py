from etl_logger import logger

import functools
from time import sleep


def backoff(errors=(Exception,), steps=2):
    def decorator(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            for t in range(1, inner.timing + 1):
                try:
                    result = func(*args, **kwargs)
                    return result
                except errors as e:
                    logger.error(e)
                    if t == inner.timing:
                        break
                    sleep(t)

        inner.timing = steps
        return inner

    return decorator
