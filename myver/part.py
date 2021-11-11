from __future__ import annotations

import abc
from typing import Optional, Union


class Part:
    """A version's part.

    Example - given a standard semantic version of `3.9.1`, the
    components of the version would be `major.minor.patch`. Where the
    parts are `major = 3`, `minor = 9`, and `patch = 1`.

    Internally, a part will treat its value as a string, this makes it
    much easier to deal with the value when operating on it. If the
    value is numeric, the conversion of the value into an integer can
    be delegated to the locations where it is needed as an integer.

    :param key: The unique key of the part. This is used to set dict
        keys for collections of parts.
    :param order: The order of the part in the version. This defines
        where the part should be located when the version is parsed.
    :param value: The actual value of the part.
    :param prefix: The prefix of the part.
    :param requires: Another part that this part requires. This means
        that the required part will need to be set if this part is set.
    :param numeric: Defines if the part is numeric or alphanumeric.
    :param start_value: The starting value of the part. This is used
        when the part goes out of a null state, or is reset to its
        original state.
    :param identifiers: List of valid identifiers that can be used
        as string values for this part.
    :param child: The child of the part.
    """

    def __init__(self,
                 key: str,
                 order: int,
                 value: Optional[Union[str, int]],
                 prefix: str = None,
                 requires: Optional[Part] = None,
                 numeric: bool = None,
                 start_value: Union[str, int] = None,
                 identifiers: list[str] = None,
                 child: Optional[Part] = None):
        self.key: str = key
        self.order: int = order
        self.value: Optional[Union[str, int]] = value
        self.prefix: str = prefix or ''
        self.requires: Optional[Part] = requires or None
        self.numeric: bool = numeric or True
        self.start_value: Optional[str] = start_value or str(0)
        self.identifiers: list[str] = identifiers or []
        self.child: Optional[Part] = child

        if identifiers and start_value is None:
            self.numeric = False
            self.start_value = start_value or self.identifiers[0]

    @abc.abstractmethod
    def next_value(self) -> Optional[str]:
        """Get the next part value."""
        if self.numeric:
            return self._next_number()
        else:
            return self._next_identifier()

    def bump(self, child_parts: list[str] = None) -> Part:
        """Bump part value.

        This will do a recursive call resetting each child part, and
        each child's child part etc...
        """
        self.value = self.next_value()
        self._reset_child(child_parts)
        return self

    @property
    def child_key(self) -> Optional[str]:
        """Get the key of this part's child if it has a child.

        :return: The key of this part's child.
        """
        if self.child is None:
            return None

        child_key = None
        for key in self.config.children:
            if self.config.children[key].order == self.child.config.order:
                child_key = key

        return child_key

    def reset(self, child_parts: list[str] = None):
        """Reset part value to the start value.

        Resetting the part to the start value will also make a recursive
        call to its child, reset them values too.
        """
        self.value = self.start_value
        self._reset_child(child_parts)

    def set_child(self, parts: dict[str, Part]) -> bool:
        """Sets the child for this part from a dict of parts.

        When getting a part from a value, you will not have its child
        straight away (if it should have one). If you have a dict of
        `Part` objects, you can find the child for part based on their
        configs.

        It is important to know that the child will be set to the
        reference value of the part in the dict if a child is found.

        :param parts: The dict of parts to look for a child.
        :return: True if a child is set.
        """
        if self.child is None:
            for key in parts:
                if key in self.config.children:
                    self.child = parts[key]
                    return True

        if self.child_key in parts:
            self.child = parts[self.child_key]
            return True

        return False

    def _next_number(self) -> Optional[str]:
        if self.value is not None:
            next_value = int(self.value)
            next_value += 1
            return str(next_value)
        else:
            return self.start_value

    def _next_identifier(self) -> Optional[str]:
        if self.value is not None:
            current_index = self.identifiers.index(self.value)
            next_index = current_index + 1

            if next_index < len(self.identifiers):
                return self.identifiers[next_index]
            return None
        else:
            return self.start_value

    def _reset_child(self, bump_keys: list[str] = None):
        if self.child is not None:
            if self.child.key == self.requires:
                # We have a required child so reset it without checking
                # `bump_keys` since the child will be reset anyway.
                self.child.reset(bump_keys)
            elif bump_keys is not None and self.child.key in bump_keys:
                # We are bumping a non-required child in this part's
                # group so we will reset it.
                self.child.reset(bump_keys)
            else:
                # Child is not required and it is not in the `bump_keys`
                # so we do not want it in the version.
                self.child.value = None

    def __str__(self):
        return f"{self.value}"

    def __eq__(self, other: Part) -> bool:
        """Checks if this part is equal to another part.

        The part equality is compared on the following attributes:
        * Part's order
        * Part's value
        * If the child is equal too

        :param other: The other part to compare for equality.
        :return: True if the parts are equal.
        """
        return (self.order == other.order) and (
                self.value == other.value) and (self.child == other.child)

    def __lt__(self, other: Part) -> bool:
        """This is used as a component of sorting parts.

        Compares part's order to see if one is less than another.

        :param other: The other part to compare.
        :return: True if this part is less than the other part.
        """
        return self.order < other.order
