import collections

Connection = collections.namedtuple('Connection', [
    'url',
    'reader',
    'writer',
    'connection_timeout',
    'read_timeout',
])
