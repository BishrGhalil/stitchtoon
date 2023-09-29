import functools
import logging
import os
import sys
from datetime import datetime

if os.getenv("STITCHTOON_DEBUG") and os.getenv("STITCHTOON_DEBUG").lower() == "true":
    DEFAULT_LOG_LEVEL = logging.DEBUG
else:
    DEFAULT_LOG_LEVEL = logging.INFO


def get_logger(log_level=DEFAULT_LOG_LEVEL, filename=sys.stdout):
    logger = logging.getLogger("STITCHTOON")
    logger.setLevel(log_level)
    log_format = "%(name)s:%(levelname)s:%(asctime)s:%(message)s"
    logging.basicConfig(format=log_format)
    if isinstance(filename, str):
        current_date = datetime.now()
        filename = current_date.strftime(filename)
        handler = logging.FileHandler(filename, mode="w")
        handler.setFormatter(logging.Formatter(log_format))
        logger.addHandler(handler)

    logger.debug("Logger Initialized")
    # Removes the pil logging from polluting the Debug Level.
    pil_logger = logging.getLogger("PIL")
    pil_logger.setLevel(logging.INFO)
    return logger


Logger = get_logger()


def logged(func=None, inclass=False, logger=Logger):
    if func is None:
        return functools.partial(logged, inclass=inclass)

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        args_repr = [repr(a) for a in args]
        if inclass:
            args_repr = [repr(args[i]) for i in range(1, len(args))]
        kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
        signature = ", ".join(args_repr + kwargs_repr)
        logger.debug(f"{func.__name__}:args:{signature}")
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            logger.exception(
                f"Exception raised in {func.__name__}. exception: {str(e)}"
            )
            raise e

    return wrapper
