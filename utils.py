import time


def timeit(func):
    def wrapper(*arg, **kw):
        t1 = time.time()
        res = func(*arg, **kw)
        t2 = time.time()
        print(f'{t2 - t1:0.6f} {func.__name__}')
        return res
    return wrapper


def timeout_handler(signum, frame):
    raise TimeoutError
