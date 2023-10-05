from robocorp import log
from robocorp.tasks import task


@task
def generic_test():
    """This test case can be used to test various functionality throughout the development process."""
    log.info('Generic test successful!')
    pass
