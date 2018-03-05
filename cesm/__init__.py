#!/usr/bin/env python
# -*- coding: utf-8 -*-


# get version
from .version import version
__version__ = version

from ._case.case import case, print_casenames
from ._case.comp import _lnd, _atm, _ice, _ocn
from ._case.combcase import combcase

from ._load import load


