from __future__ import annotations

import abc
from typing import Optional, Union


class Part(abc.ABC):
    """The base class for a version part.

    For example, given a standard semantic version of `3.9.1`, the
    components of the version would be `major.minor.patch`. Where the
    parts are `major = 3`, `minor = 9`, and `patch = 1`.

    Internally, a part will treat its value as a string, this makes it
    much easier to deal with the value when operating on it. If the
    value is numeric, the conversion of the value into an integer can
    be delegated to the locations where it is needed as an integer.

    :param key: The unique key of the part. This is used to set dict
        keys for collections of parts.
    :param value: The actual value of the part.
    :param prefix: The prefix of the part.
    :param requires: Another part that this part requires. This means
        that the required part will need to be set if this part is set.
    :param child: The child of the part.
    """

    def __init__(self,
                 key: str,
                 value: Optional[Union[str, int]],
                 prefix: str = None,
                 requires: Optional[str] = None,
                 child: Optional[Part] = None,
                 parent: Optional[Part] = None):
        self.key: str = key
        self.value: Optional[Union[str, int]] = value
        self.prefix: str = prefix or ''
        self.requires: Optional[str] = requires or None
        self.parent: Optional[Part] = None
        self.child: Optional[Part] = child
        self.parent: Optional[Part] = parent

    @property
    @abc.abstractmethod
    def start(self) -> str:
        """The default start value of a part."""

    @abc.abstractmethod
    def next_value(self) -> Optional[str]:
        """Get the next part value."""

    def is_set(self) -> bool:
        """Checks if the part's value is not None."""
        return self.value is not None

    def bump(self):
        """Bump this part's value."""
        self.value = self.next_value()
        self.child.reset()

    def reset(self):
        """Reset part value to the start value.

        Resetting the part to the start value will also make a recursive
        call to its child, resetting their values too.
        """
        if self.is_required(self.key):
            self.value = self.start
        else:
            self.value = None

        if self.child is not None:
            self.child.reset()

    def is_required(self, key: str) -> bool:
        """Check if a part is required based on its key.

        This does a recursive call up to all of the parents until it
        reaches the final parent to check if any of them require the
        part specified.

        :param key: The key of the part that you want to check.
        """
        return self._is_required(key)

    def _is_required(self, key: str) -> bool:
        if self.parent is not None:
            if self.parent.requires == key and self.parent.is_set():
                return True
            else:
                return self.parent.is_required(key)
        return False

    def __str__(self):
        return f'{self.prefix}{self.value}'

    def __eq__(self, other: Part) -> bool:
        """Checks if this part is equal to another part.

        The part equality is compared on the following attributes:
        * Part's order
        * Part's value
        * If the child is equal too

        :param other: The other part to compare for equality.
        :return: True if the parts are equal.
        """
        return (self.value == other.value) and (self.child == other.child)


class IdentifierPart(Part):
    """An identifier part.

    :param strings: List of valid strings that can be used as an
        identifier for this part.
    :param start: The starting value of the part. This is used when the
        part goes out of a null state, or is reset to its original
        state. If this is specified it must be a string that is in the
        `strings` list.
    """

    def __init__(self,
                 key: str,
                 value: Optional[Union[str, int]],
                 strings: list[str],
                 prefix: str = None,
                 requires: Optional[str] = None,
                 child: Optional[Part] = None,
                 parent: Optional[Part] = None,
                 start: str = None):
        super().__init__(key, value, prefix, requires, child, parent)
        self.strings: list[str] = strings
        self._start: str = start or self.strings[0]

    @property
    def start(self) -> str:
        return self._start

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

    :param label: The label for the number part.
    :param label_suffix: The suffix to use for separating the label and
        the number.
    :param start: The starting value of the part. This is used when the
        part goes out of a null state, or is reset to its original
        state.
    :param show_start: If true, the start value will be shown in the
        version. If false, then the start value wont be shown although
        the next value (after a bump) will be shown.
    """

    def __init__(self,
                 key: str,
                 value: Optional[Union[str, int]],
                 prefix: str = None,
                 requires: Optional[str] = None,
                 child: Optional[Part] = None,
                 parent: Optional[Part] = None,
                 label: str = None,
                 label_suffix: str = None,
                 start: int = None,
                 show_start: bool = True):
        super().__init__(key, value, prefix, requires, child, parent)
        self.label: str = label or ''
        self.label_suffix: str = label_suffix or ''
        self._start: str = start or str(0)
        self.show_start: bool = show_start

    @property
    def start(self) -> str:
        return self._start

    def next_value(self) -> Optional[str]:
        if self.is_set():
            next_value = int(self.value)
            next_value += 1
            return str(next_value)
        else:
            return self.start

    def __str__(self):
        if self.value == self.start and not self.show_start:
            return f'{self.prefix}{self.label}'
        return f'{self.prefix}{self.label}{self.label_suffix}{self.value}'
