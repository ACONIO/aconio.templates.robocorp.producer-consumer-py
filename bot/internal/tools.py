from functools import wraps

from robocorp import log

from .errors import AutomationError


def run_function(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except AutomationError as e:
            raise e
        except Exception as e:
            # ensure that all uncaught exceptions are prepared for Robocorp Control Room before
            # they are being sent (e.g. exception can't have more than 1000 chars)
            log.warn(f'unexpected err during automation: {e}')
            raise Exception('unexpected automation error')

    return wrapper
