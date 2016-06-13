import collections

Connection = collections.namedtuple('Connection', [
    'url',
    'reader',
    'writer',
])
