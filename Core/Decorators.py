__instances__ = {}


def singleton(class_):
    def get_instance(*args, **kwargs):
        global __instances__
        if class_ not in __instances__:
            __instances__[class_] = class_(*args, **kwargs)
        return __instances__[class_]

    return get_instance
