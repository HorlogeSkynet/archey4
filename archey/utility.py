"""Archey Utility module"""

from typing import Tuple

from archey.singleton import Singleton


class Utility(metaclass=Singleton):
    """Miscellaneous logic used in Archey internals"""

    @classmethod
    def update_recursive(cls, old_dict: dict, new_dict: dict) -> None:
        """
        A method for recursively merging dictionaries as `dict.update()` is not able to do this.
        Original snippet taken from here : <https://gist.github.com/angstwad/bf22d1822c38a92ec0a9>
        """
        for key, value in new_dict.items():
            if key in old_dict and isinstance(old_dict[key], dict) and isinstance(value, dict):
                cls.update_recursive(old_dict[key], value)
            else:
                old_dict[key] = value

    @staticmethod
    def version_to_semver_segments(version: str) -> Tuple[int, ...]:
        """Transforms string `version` to a tuple containing SemVer segments"""
        return tuple(map(int, version.partition("-")[0].split(".")))
