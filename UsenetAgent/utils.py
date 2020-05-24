import time

def retry(func, *args, maxretries=20, timeout=1, exception=RuntimeError('Maximum amount of retries exceeded')):
    '''
    :param func: Callable to be run, return (success, ret-val)
    :param maxtries: Amount of retries
    :param timeout: Time in seconds to sleep between retries
    :param exceptions: To be raised if amount of retries is exceeded
    :return: The return of func
    '''
    for _ in range(maxretries):
        success, ret = func(*args)
        if success:
            return ret
        else:
            time.sleep(timeout)
    raise exception
