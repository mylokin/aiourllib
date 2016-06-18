from . import exc
from .api import get
from .uri import (
    URI,
    URIException)

__version__ = '0.1.2'
__all__ = ['get', 'exc', 'URI', 'URIException']
