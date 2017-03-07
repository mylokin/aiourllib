import collections

Connection = collections.namedtuple('Connection', [
    'url',
    'socket_pair',
    'connection_timeout',
    'read_timeout',
])


SocketPair = collections.namedtuple('SocketPair', [
    'reader',
    'writer',
])
