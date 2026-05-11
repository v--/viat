"""The command-line interface for viat."""

import importlib.util

from viat.exceptions import ViatIntegrityError


if not importlib.util.find_spec('click'):
    raise ViatIntegrityError('Could not import the click module')


from ._cli import viat


__all__ = ['viat']
