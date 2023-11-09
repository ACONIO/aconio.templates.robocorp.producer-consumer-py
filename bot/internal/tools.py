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
            # ensure that all exceptions are prepared for Robocorp Control Room before they are
            # being sent (e.g. exception can't have more than 1000 chars)

            # Note: we're currently throwing an Exception instaed of an ApplicationError here,
            # because an ApplicationError would be caught by robocorp and no new run would be
            # started. We could implement a "re-init all apps" func but if there were any
            # leftover windows due to some error they could impact further runs. We need to
            # discuss what the best practice would be here. On the other hand, a "re-init"
            # would save significant amounts of runtime, since Control Room would not start a
            # new run upon error.
            log.warn(f'unexpected err during automation: {e}')
            raise Exception('unexpected automation error')

    return wrapper
