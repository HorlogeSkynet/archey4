"""Simple singleton meta-class definition"""

class Singleton(type):
    """
    Taken from : <https://stackoverflow.com/q/6760685/10599709>
    This meta-class allows us to declare `Configuration` as a singleton.
    This way, we are able to import `Configuration` in multiple modules, ...
    ... whereas it is effectively loaded only once.
    """
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
