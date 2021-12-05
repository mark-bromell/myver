from __future__ import annotations

from logging import getLogger
from typing import List

from myver.error import ConfigError, BumpError
from myver.part import Part

log = getLogger(__name__)


class Version:
    """Represents the version itself.

    This is the top level class for a version. It contains the groups
    of parts and this is where the version operations are performed.

    :param parts: The List of parts in the version.
    """

    def __init__(self, parts: List[Part] = None):
        self._parts: List[Part] = parts or []
        self.parts = parts or []

    @property
    def parts(self) -> List[Part]:
        return self._parts

    @parts.setter
    def parts(self, new_parts: List[Part]):
        """Sets the parts List.

        :param new_parts: The parts to set.
        :raise KeyConflictError: A part key appears 2 or more times in
            the List.
        """
        validate_keys(new_parts)
        validate_requires(new_parts)
        self._parts = new_parts
        set_relationships(self._parts)

    def bump(self, args: List[str]):
        """Bump the version based on bumping args.

        :param args: The List of part keys to bump. An arg may have a
            key value pair with the syntax of `<key>=<value>`.
        :raise BumpError: When the bumping fails.
        """
        log.debug('Starting version bump')
        for arg in args:
            if arg.count('=') > 1:
                raise BumpError(
                    f'The bump arg `{arg}` contains more than 1 `=` symbol, '
                    f'there can only be 0 or 1 `=` symbol in the bump arg')
            elif arg.count('=') == 1:
                key = arg.split('=')[0]
                value_override = arg.split('=')[1]
                self.part(key).bump(args, value_override)
            else:
                self.part(arg).bump(args)

    def reset(self, keys: List[str]):
        """Reset parts based on their keys.

        :param keys: The keys of the parts to reset.
        :raise KeyError: If a key in the `keys` List does not reference
            a valid part in the version.
        """
        log.debug('Starting version reset')
        for key in keys:
            self.part(key).reset()

    def part(self, key: str) -> Part:
        """Gets a part based on its key.

        :param key: The key of the part you are getting.
        :raise KeyError: If no part has the key provided.
        """
        for part in self._parts:
            if part.key == key:
                return part
        raise KeyError(key)

    def parse(self, keys: List[str]):
        """Parses specific parts in the version.

        Lets say you parse the keys `['a', 'z']`, if `z` is not a null
        value, then all parts in between `a` and `z` will also be
        parsed, such as `b`, `c`, `d` etc... If `z` is null then only
        `a` will be parsed, and not their intermediary parts.

        :param keys: The keys of the parts to parse. They must be in
            chronological order from how they are configured.
        :raise KeyError: If an invalid part key is provided.
        """
        end_key = ''
        for key in keys:
            if self.part(key).is_set():
                end_key = key

        parsed = ''
        for part in self._parts:
            if part.is_set():
                parsed += str(part)
            if part.key == end_key:
                break

        return parsed

    def __eq__(self, other: Version):
        for this_part, other_part in zip(self.parts, other.parts):
            if not this_part == other_part:
                return False
        return True

    def __str__(self):
        version_str = ''

        for part in self._parts:
            if part.is_set():
                version_str += str(part)

        return version_str


def validate_requires(parts: List[Part]):
    """Validates that parts require other valid parts.

    :raise ConfigError: If a part requires itself or a part that does
        not exist.
    """
    keys = [p.key for p in parts] or []
    for part in parts:
        if not part.requires:
            continue

        if part.requires == part.key:
            raise ConfigError(
                f'Part `{part.key}` has a `requires` key that is'
                f'referencing itself, it must reference another part')
        if part.requires not in keys:
            raise ConfigError(
                f'Part `{part.key}` has a `requires` key '
                f'"{part.requires}" that does not exist, it must be a '
                f'valid key of another part')


def validate_keys(parts: List[Part]):
    """Validates that they keys are unique.

    :raise ConfigError: If two or more parts with the same key.
    """
    keys = [p.key for p in parts] or []
    for key in keys:
        if keys.count(key) > 1:
            raise ConfigError(
                f'Key "{key}" is configured on more than one part, all '
                f'parts must have a unique key')


def set_relationships(parts: List[Part]):
    """Sets the parent-child relationships between a List of parts.

    :param parts: The parts to set the relationships for.
    """
    for i in range(len(parts)):
        if i < len(parts) - 1:
            parts[i].child = parts[i + 1]
