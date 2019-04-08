# cython: language_level=3

cdef class Singleton(type):
    """
    Define an Instance operation that lets clients access its unique
    instance.
    """
    cdef readonly object instance
    cdef object __weakref__ # enable weak referencing support

    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)
        cls.instance = None

    def __call__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__call__(*args, **kwargs)
        return cls.instance
