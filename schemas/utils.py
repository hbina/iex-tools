enable = True


def conditional(decorator):
    def wrapper(fn):
        if enable:
            return decorator(fn)
        else:
            return fn

    return wrapper
