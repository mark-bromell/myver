import re
from dataclasses import dataclass
from glob import glob
from logging import getLogger

from jinja2 import Template

log = getLogger(__name__)


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
        log.debug(f'Doing update for glob <{self.path}>')
        for path in glob(self.path):
            try:
                log.info(f'Updating <{path}>')
                with open(path, 'r') as file:
                    data = file.read()
                with open(path, 'w') as file:
                    updated = self._update_data(data, old_version, new_version)
                    file.write(updated)
            except FileNotFoundError:
                log.error(f'Path does not exist <{path}>')
            except OSError as e:
                log.error(f'Error {e.errno} updating <{path}>, {e.strerror}')

    def _update_data(self, data: str, old_version: str,
                     new_version: str) -> str:
        rendered_patterns = self._rendered_patterns(old_version)
        update_pairs: list[UpdatePair] = []
        updated_data = data

        for pattern in rendered_patterns:
            log.debug(f'Searching for pattern <{pattern}>')
            for match in re.findall(pattern, data):
                original = match
                updated = match.replace(old_version, new_version)
                log.debug(f'Changing <{original}> to <{updated}>')
                update_pairs.append(UpdatePair(original, updated))

        for pair in update_pairs:
            updated_data = updated_data.replace(pair.original, pair.updated)

        return updated_data

    def _rendered_patterns(self, version: str) -> list[str]:
        rendered_patterns = []

        for pattern in self.patterns:
            log.debug(f'Rendering pattern <{pattern}>')
            template = Template(pattern)
            regex_valid_version = f'{re.escape(version)}'
            rendered = template.render(version=regex_valid_version)
            log.debug(f'Rendered as <{rendered}>')
            rendered_patterns.append(rendered)

        return rendered_patterns

    def __eq__(self, other):
        return (self.path == other.path) and (self.patterns == self.patterns)


@dataclass
class UpdatePair:
    original: str
    updated: str
