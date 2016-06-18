__version__ = '0.1.0'
__all__ = ['get', 'URI', 'URIException']

from .api import get
from .uri import (
    URI,
    URIException)
