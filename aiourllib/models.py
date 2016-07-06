import collections

Connection = collections.namedtuple('Connection', [
    'url',
    'socket',
    'connection_timeout',
    'read_timeout',
])


Socket = collections.namedtuple('Socket', [
    'reader',
    'writer',
])
