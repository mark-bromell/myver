from __future__ import annotations

from typing import Optional, Union


class PartConfig:
    def __init__(self,
                 order: int,
                 prefix: str = None,
                 suffix: str = None,
                 children: list[ChildConfig] = None):
        self.order: int = order
        self.prefix: str = prefix or ''
        self.suffix: str = suffix or ''
        self.children: list[ChildConfig] = children or []


class ChildConfig(PartConfig):
    def __init__(self,
                 order: int,
                 prefix: str = None,
                 suffix: str = None,
                 children: list[ChildConfig] = None,
                 required: bool = False):
        super().__init__(order, prefix, suffix, children)
        self.required: bool = required


class Part:
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
        return (self.config.order == other.config.order) and (
                self.value == other.value) and (
                self.child == other.child)

    def __lt__(self, other: Part) -> bool:
        """This is used as a component of sorting parts.

        Compares `Part.config.order` to see if one is less than another.
        :param other: The other part to compare.
        :return: True if this part is less than the other part.
        """
        return self.config.order < other.config.order

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
