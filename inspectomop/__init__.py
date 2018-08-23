import os as _os

_pkg_base_path = _os.path.dirname(__file__)

with open(_os.path.join(_pkg_base_path, 'VERSION.txt')) as _fh:
    _version = _fh.read().strip()

__version__ = _version

from inspectomop.inspector import Inspector
from inspectomop import queries
from inspectomop import test
