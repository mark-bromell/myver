from __future__ import annotations

import abc
from typing import Optional, Union

from myver.error import ConfigError


class Part(abc.ABC):
    """The base class for a version part.

    :param key: The unique key of the part. This is used to set dict
        keys for collections of parts.
    :param value: The actual value of the part.
    :param requires: Another part that this part requires. This means
        that the required part will need to be set if this part is set.
    """

    def __init__(self,
                 key: str,
                 value: Optional[Union[str, int]],
                 requires: Optional[str] = None,
                 prefix: Optional[str] = None,
                 child: Optional[Part] = None,
                 parent: Optional[Part] = None):
        self._prefix: Optional[str] = prefix
        self._child: Optional[Part] = None
        self._parent: Optional[Part] = None
        self.key: str = key
        self.value: Optional[Union[str, int]] = value
        self.requires: Optional[str] = requires
        self.child = child
        self.parent = parent

    @abc.abstractmethod
    def next_value(self) -> Optional[Union[str, int]]:
        """Get the next part value."""

    @property
    @abc.abstractmethod
    def start(self) -> Union[str, int]:
        """Get the start value in a usable form (i.e. not None)"""

    @start.setter
    @abc.abstractmethod
    def start(self, new_start: Union[str, int]):
        """Set the start value"""

    @property
    def prefix(self) -> str:
        return self._prefix or ''

    @prefix.setter
    def prefix(self, new_prefix: Optional[str]):
        self._prefix = new_prefix

    @property
    def child(self) -> Optional[Part]:
        return self._child

    @child.setter
    def child(self, part: Optional[Part]):
        self._child = part
        if self._child and not self._child.parent:
            self._child.parent = self

    @property
    def parent(self) -> Optional[Part]:
        return self._parent

    @parent.setter
    def parent(self, part: Optional[Part]):
        self._parent = part
        if self._parent and not self._parent.child:
            self._parent.child = self

    def is_set(self) -> bool:
        """Checks if the part's value is not None."""
        return self.value is not None

    def bump(self, bump_keys: list[str] = None):
        """Bump this part's value.

        :param bump_keys: The keys that are being bumped.
        """
        bump_keys = bump_keys or []
        self.value = self.next_value()
        if self.child:
            self.child.reset(bump_keys)

    def reset(self, bump_keys: list[str] = None):
        """Reset part value to the start value.

        Resetting the part to the start value will also make a recursive
        call to its child, resetting their values too.

        :param bump_keys: The keys that are being bumped.
        """
        bump_keys = bump_keys or []

        # If this part is required and it's in the bump keys, we want to
        # skip this step so that we do not get a double bump.
        if self.is_required() and self.key not in bump_keys:
            self.value = self.start
        else:
            self.value = None

        if self.child:
            self.child.reset()

    def is_required(self) -> bool:
        """Checks if this part is required by any parents."""
        return self._parent_requires(self.key)

    def _parent_requires(self, key: str) -> bool:
        """Check if a part is required based on its key.

        This does a recursive call up to all of the parents until it
        reaches the final parent to check if any of them require the
        part specified.

        :param key: The key of the part that you want to check.
        """
        if self.parent is not None:
            if self.parent.requires == key and self.parent.is_set():
                return True
            else:
                return self.parent._parent_requires(key)
        return False

    def __str__(self):
        return f'{self.prefix}{self.value}'

    def __eq__(self, other: Part) -> bool:
        return (self.key == other.key) and (self.value == other.value)


class IdentifierPart(Part):
    """An identifier part.

    :param strings: List of valid strings that can be used as an
        identifier for this part.
    :param start: The starting value of the part. This is used when the
        part goes out of a null state, or is reset to its original
        state. If this is specified it must be a string that is in the
        `self.strings` list.
    """

    def __init__(self,
                 key: str,
                 value: Optional[str],
                 strings: list[str],
                 requires: Optional[str] = None,
                 prefix: Optional[str] = None,
                 child: Optional[Part] = None,
                 parent: Optional[Part] = None,
                 start: str = None):
        super().__init__(key, value, requires, prefix, child, parent)
        self._strings: list[str] = strings
        self._start: Optional[str] = start
        self.strings = strings
        self.start = start

    @property
    def strings(self):
        return self._strings

    @strings.setter
    def strings(self, new_strings: list[str]):
        self._validate_strings(new_strings)
        self._strings: list[str] = new_strings

    @property
    def start(self) -> str:
        return self._start or self.strings[0]

    @start.setter
    def start(self, new_start: str):
        self._validate_start(new_start)
        self._start = new_start

    def _validate_start(self, start: Optional[str]):
        if start is not None and start not in self.strings:
            raise ConfigError(
                f'Part `{self.key}` has an `identifier.start` value that is '
                f'not in the `identifier.strings` list')

    def _validate_strings(self, strings: list[str]):
        if not len(strings) > 0:
            raise ConfigError(
                f'Part `{self.key}` has an `identifier.strings` has an empty '
                f'list, the list must have at least one string')

    def next_value(self) -> Optional[str]:
        if self.is_set():
            current_index = self.strings.index(self.value)
            next_index = current_index + 1

            if next_index < len(self.strings):
                return self.strings[next_index]
            return None
        else:
            return self.start


class NumberPart(Part):
    """A number part.

    :param label_suffix: String to use for separating the label and the
        number.
    :param start: Starting value of the part. This is used when the part
        goes out of a null state, or is reset to its original state.
    :param show_start: If true, the start value will be shown in the
        version. If false, then the start value wont be shown although
        the next value (after a bump) will be shown.
    """

    def __init__(self,
                 key: str,
                 value: Optional[int],
                 requires: Optional[str] = None,
                 prefix: Optional[str] = None,
                 child: Optional[Part] = None,
                 parent: Optional[Part] = None,
                 label: Optional[str] = None,
                 label_suffix: Optional[str] = None,
                 start: int = None,
                 show_start: bool = True):
        super().__init__(key, value, requires, prefix, child, parent)
        self._label: Optional[str] = label
        self._label_suffix: Optional[str] = label_suffix
        self._start: Optional[int] = start
        self.show_start: bool = show_start
        self.start = start

    @property
    def label(self) -> Optional[str]:
        return self._label or ''

    @label.setter
    def label(self, new_label: str):
        self._label = new_label

    @property
    def label_suffix(self) -> Optional[str]:
        return self._label_suffix or ''

    @label_suffix.setter
    def label_suffix(self, new_label_suffix: str):
        self._label_suffix = new_label_suffix

    @property
    def start(self) -> int:
        return self._start or 0

    @start.setter
    def start(self, new_start: int):
        self._validate_start(new_start)
        self._start = new_start

    def next_value(self) -> Optional[int]:
        if self.is_set():
            return self.value + 1
        else:
            return self.start

    def _validate_start(self, start: Optional[int]):
        if start is not None:
            try:
                int(start)
            except ValueError:
                raise ConfigError(
                    f'Part `{self.key}` has an invalid value for its '
                    f'`number.start` attribute, it must be an integer')

        if start is not None and start < 0:
            raise ConfigError(
                f'Part `{self.key}` has an negative value for its '
                f'`number.start` attribute, it must be positive')

    def __str__(self):
        if self.value == self.start and not self.show_start:
            return f'{self.prefix}{self.label}'
        return f'{self.prefix}{self.label}{self.label_suffix}{self.value}'
