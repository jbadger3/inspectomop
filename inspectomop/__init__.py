
with open('inspectomop/VERSION.txt') as fh:
    version = fh.read().strip()

__version__ = version

from inspectomop.inspector import Inspector
from inspectomop import queries

