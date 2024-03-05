import functools

from robocorp import log, workitems

from bot.core import errors, items


def run_function(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except errors.AutomationError as e:
            raise e
        except Exception as e:
            # ensure that all uncaught exceptions are prepared for Robocorp Control Room before
            # they are being sent (e.g. exception can't have more than 1000 chars)
            log.warn(f'unexpected err during automation: {e}')
            raise Exception('unexpected automation error')

    return wrapper


def attach_reporter(run_function):
    """
    Intercepts a `BusinessError` and creates an output work item for the reporter.

    If the BusinessError does not offer a `code`, it will be re-raised, since the exception
    is not considered "catchable" by the reporter without a code.
    """
    @functools.wraps(run_function)
    def wrapper(*args, **kwargs):
        try:
            return run_function(*args, **kwargs)
        except errors.BusinessError as e:
            if e.code:
                item = workitems.inputs.current

                workitems.outputs.create(
                    items.ReporterItem(
                        failed_wi_id=item.id,
                        failed_wi_code=e.code,
                        failed_wi_payload=item.payload
                    ).to_dict()
                )

            else:
                raise e

    return wrapper
