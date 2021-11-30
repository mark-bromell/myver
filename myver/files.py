import re
from dataclasses import dataclass
from glob import glob

from jinja2 import Template


class FileUpdater:
    """Updates files with new versions.

    :param path: The path glob for the files to update.
    :param patterns: The patterns to base off of when updating.
    """

    def __init__(self,
                 path: str,
                 patterns: list[str] = None):
        self.path: str = path
        self.patterns: list[str] = patterns or ['{{ version }}']

    def update(self, old_version: str, new_version: str):
        for path in glob(self.path):
            with open(path, 'r') as file:
                data = file.read()

            with open(path, 'w') as file:
                file.write(self._update_data(data, old_version, new_version))

    def _update_data(self, data: str, old_version: str,
                     new_version: str) -> str:
        rendered_patterns = self._rendered_patterns(old_version)
        update_pairs: list[UpdatePair] = []
        updated_data = data

        for pattern in rendered_patterns:
            for match in re.findall(pattern, data):
                original = match
                updated = match.replace(old_version, new_version)
                update_pairs.append(UpdatePair(original, updated))

        for pair in update_pairs:
            updated_data = updated_data.replace(pair.original, pair.updated)

        return updated_data

    def _rendered_patterns(self, version: str) -> list[str]:
        rendered_patterns = []

        for pattern in self.patterns:
            template = Template(pattern)
            regex_valid_version = f'{re.escape(version)}'
            rendered = template.render(version=regex_valid_version)
            rendered_patterns.append(rendered)

        return rendered_patterns

    def __eq__(self, other):
        return (self.path == other.path) and (self.patterns == self.patterns)


@dataclass
class UpdatePair:
    original: str
    updated: str
