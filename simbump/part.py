from __future__ import annotations

import abc
from typing import Optional, Union


class PartConfig(abc.ABC):
    """Base config for version parts.

    :param order: The order of the part in the version. This defines
        where the part should be located when the version is parsed.
    :param required: If the part is required to be in the version. More
        specifically this is used for parts that are a child part. It
        is used for the parent part to know if the child of the parent
        is required to be in the version, if the parent is in the
        version.
    :param prefix: The prefix of the part. When the part is parsed, it
        will put the prefix string at the start of the string before
        the value. For example, with a version of `3.9.1`, the prefix
        of `3` is nothing (an empty string), for `9` it is `.`, and for
        `1` it is also `.`. When the version is parsed, and each part
        is parsed, these prefixes gives this readable semantic version.
    :param suffix: The suffix of the part. Similar to the prefix, except
        it is a string that will be put at the end of the string when
        the part is parsed. This is less common and has no typical use
        case, although it is here to allow for maximum control in how
        versions get parsed.
    :param children: The possible children that a part can have. Keep in
        mind that an actual `Part` can only have one child part, but it
        can select that child from a range of possible children.
    """

    def __init__(self,
                 order: int,
                 prefix: str = None,
                 suffix: str = None,
                 required: bool = False,
                 children: dict[str, PartConfig] = None):
        self.order: int = order
        self.required: bool = required
        self.prefix: str = prefix or ''
        self.suffix: str = suffix or ''
        self.children: dict[str, PartConfig] = children or dict()

    @abc.abstractmethod
    def next_value(self, current_value: str) -> Optional[str]:
        """Get the next part value after the given value.

        :param current_value: The current value to iterate on.
        :return: The next part value. It will return `None` if the part
            config type is `StringPartConfig` and the `current_value` is
            at the end of its possible range of string values.
        """

    @property
    @abc.abstractmethod
    def start_value(self) -> str:
        """Get the starting value of the part.

        :return: The starting vale of the part.
        """


class NumericPartConfig(PartConfig):
    """Represents the config for a version part that is a number."""

    def __init__(self,
                 order: int,
                 prefix: str = None,
                 suffix: str = None,
                 required: bool = True,
                 children: dict[str, PartConfig] = None,
                 start_value: int = 0):
        super().__init__(order, prefix, suffix, required, children)
        self._start_value: str = str(start_value)

    def next_value(self, current_value: str) -> str:
        next_value = int(current_value)
        next_value += 1
        return str(next_value)

    @property
    def start_value(self) -> str:
        return self._start_value


class StringPartConfig(PartConfig):
    """Represents the config for a version part that is a string.

    :param value_list: The list of strings available for the part.
        There should be no duplicates inside the value list. Having
        a duplicate string value could also lead to a duplicate
        overall version, which is not allowed.
    """

    def __init__(self,
                 order: int,
                 prefix: str = None,
                 suffix: str = None,
                 required: bool = False,
                 children: dict[str, PartConfig] = None,
                 value_list: list[str] = None):
        super().__init__(order, prefix, suffix, required, children)
        self.value_list: list[str] = value_list or []

    def next_value(self, current_value: str) -> Optional[str]:
        current_index = self.value_list.index(current_value)
        next_index = current_index + 1

        if next_index < len(self.value_list):
            return self.value_list[next_index]

        return None

    @property
    def start_value(self) -> str:
        return self.value_list[0]


class Part:
    """Represents a version part.

    Example - given a standard semantic version of `3.9.1`, the
    components of the version would be `major.minor.patch`. Where
    `major = 3`, `minor = 9`, and `patch = 1`.

    A version part can have a child part, and they can only have one
    child. This is because a part with multiple child parts would mean
    that there is multiple branches from one branch into its children.
    If we have a version of `3.9.1`, and it can have a child of `dev` or
    of `alpha`, it cannot be possible for `3.9.1` to be both at the same
    time. What would it look like? `3.9.1.dev.alpha` or
    `3.9.1.alpha.dev`? It is inherently ambiguous, that is the reason
    for enforcing a part to only have a single child.

    Internally, a part will treat its value as a string, this makes it
    much easier to deal with the value when operating on it. If the
    value is numeric, the conversion of the value into an integer can
    be delegated to the locations where it is needed as an integer.

    :param config: The config of the part. This is used for evaluating
        most of the details and operations of the version part.
    :param value: The value of the part. This can be a string or
        integer, but internally the part stores its value as a string.
        This is to make most internal operations easier to manage.
    :param child: The child of the part (optional).
    """

    def __init__(self,
                 config: PartConfig,
                 value: Union[str, int],
                 child: Optional[Part] = None):
        self.config: PartConfig = config
        self.value: str = str(value)
        self.child: Optional[Part] = child

    def __str__(self):
        return f"{self.config.prefix}{self.value}{self.config.suffix}"

    def __eq__(self, other: Part) -> bool:
        """Checks if this part is equal to another part.

        The part equality is compared on the following attributes:
        * Part's order
        * Part's value
        * If the child is equal too

        :param other: The other part to compare for equality.
        :return: True if the parts are equal.
        """
        return (self.config.order == other.config.order) and (
                self.value == other.value) and (self.child == other.child)

    def __lt__(self, other: Part) -> bool:
        """This is used as a component of sorting parts.

        Compares part's order to see if one is less than another.

        :param other: The other part to compare.
        :return: True if this part is less than the other part.
        """
        return self.config.order < other.config.order

    def bump(self, child_parts: list[str] = None) -> Part:
        """Bump part value.

        This will do a recursive call resetting each child part, and
        each child's child part etc...
        """
        self.value = self.config.next_value(self.value)
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

    def _reset_child(self, child_parts: list[str] = None):
        if self.child is not None:
            if self.child.config.required is True:
                self.child.reset(child_parts)
            elif child_parts is not None and self.child_key in child_parts:
                self.child.reset(child_parts)
            else:
                self.child = None

    def reset(self, child_parts: list[str] = None):
        """Reset part value to the start value.

        Resetting the part to the start value will also make a recursive
        call to its child, reset them values too.
        """
        self.value = self.config.start_value
        self._reset_child(child_parts)

    def set_child(self,
                  parts: dict[str, Part]) -> bool:
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
