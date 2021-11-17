from __future__ import annotations

import abc
from typing import Optional, Union

from myver.config import PartConfig


class Part(abc.ABC):
    """The base class for a version part.

    :param config: Part's configuration.
    :param child: The child of the part.
    :param parent: The parent of the part.
    """

    def __init__(self,
                 config: PartConfig,
                 child: Optional[Part] = None,
                 parent: Optional[Part] = None):
        self.config: PartConfig = config
        self._child: Optional[Part] = None
        self._parent: Optional[Part] = None
        self.child = child
        self.parent = parent

    @abc.abstractmethod
    def next_value(self) -> Optional[Union[str, int]]:
        """Get the next part value."""

    @property
    @abc.abstractmethod
    def start(self) -> Union[str, int]:
        """Get the start value in a usable form (i.e. not None)"""

    @property
    def key(self):
        return self.config.key

    @property
    def value(self) -> Union[str, int]:
        return self.config.value

    @value.setter
    def value(self, new_value: Union[str, int]):
        self.config.value = new_value

    @property
    def requires(self) -> Optional[str]:
        return self.config.requires

    @property
    def prefix(self):
        return self.config.prefix or ''

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

    def bump(self):
        """Bump this part's value."""
        self.value = self.next_value()
        if self.child:
            self.child.reset()

    def reset(self):
        """Reset part value to the start value.

        Resetting the part to the start value will also make a recursive
        call to its child, resetting their values too.
        """
        if self.is_required():
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
    """An identifier part."""

    def __init__(self,
                 config: PartConfig,
                 child: Optional[Part] = None,
                 parent: Optional[Part] = None):
        super().__init__(config, child, parent)

    @property
    def strings(self) -> list[str]:
        return self.config.identifier.strings

    @property
    def start(self) -> str:
        return self.config.identifier.start

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
    """A number part."""

    def __init__(self,
                 config: PartConfig,
                 child: Optional[Part] = None,
                 parent: Optional[Part] = None):
        super().__init__(config, child, parent)

    @property
    def label(self) -> Optional[str]:
        return self.config.number.label or ''

    @property
    def label_suffix(self) -> Optional[str]:
        return self.config.number.label_suffix or ''

    @property
    def start(self) -> int:
        return self.config.number.start or 0

    @property
    def show_start(self) -> bool:
        return self.config.number.show_start

    def next_value(self) -> Optional[int]:
        if self.is_set():
            return self.value + 1
        else:
            return self.start

    def __str__(self):
        if self.value == self.start and not self.show_start:
            return f'{self.prefix}{self.label}'
        return f'{self.prefix}{self.label}{self.label_suffix}{self.value}'
