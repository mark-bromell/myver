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
                 children: list[PartConfig] = None):
        self.order: int = order
        self.required: bool = required
        self.prefix: str = prefix or ''
        self.suffix: str = suffix or ''
        self.children: list[PartConfig] = children or []

    @abc.abstractmethod
    def next_value(self, current_value: str) -> Optional[str]:
        """Get the next part value after the given value.

        :param current_value: The current value to iterate on.
        :return: The next part value. It will return `None` if the part
            config type is `StringPartConfig` and the `current_value` is
            at the end of its possible range of string values.
        """
        pass


class NumericPartConfig(PartConfig):
    """Represents the config for a version part that is a number.

    :param start_value: The starting value of the number version part.
        By default this is set to `0`. The start value will be invoked
        in cases where a parent version part is bumped, all child
        numeric parts must be reset.
    """

    def __init__(self,
                 order: int,
                 prefix: str = None,
                 suffix: str = None,
                 required: bool = False,
                 children: list[PartConfig] = None,
                 start_value: int = 0):
        super().__init__(order, prefix, suffix, required, children)
        self.start_value: str = str(start_value)

    def next_value(self, current_value: str) -> str:
        next_value = int(current_value)
        next_value += 1
        return str(next_value)


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
                 children: list[PartConfig] = None,
                 value_list: list[str] = None):
        super().__init__(order, prefix, suffix, required, children)
        self.value_list: list[str] = value_list or []

    def next_value(self, current_value: str) -> Optional[str]:
        current_index = self.value_list.index(current_value)
        next_index = current_index + 1

        if next_index < len(self.value_list):
            return self.value_list[next_index]

        return None


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

    def bump(self):
        pass

    def set_child(self,
                  part_list: list[Part]) -> bool:
        """Sets the child for this part from a list of parts.

        When getting a part from a value, you will not have its child
        straight away (if it should have one). If you have a list of
        `Part` objects, you can find the child for this part based on
        their configs.

        It is important to know that the child will be set to the
        reference value of the part in the list if a child is found.

        :param part_list: The list of parts to look for a child.
        :return: True if a child is found.
        """
        for child_config in self.config.children:
            for part in part_list:
                if part.config.order == child_config.order:
                    self.child = part
                    self.child.config = child_config
                    return True

        return False
