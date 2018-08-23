import os

pkg_base_path = os.path.dirname(__file__)

with open(os.path.join(pkg_base_path, 'VERSION.txt')) as fh:
    version = fh.read().strip()

__version__ = version

from inspectomop.inspector import Inspector
from inspectomop import queries
from inspectomop import test
