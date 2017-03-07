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


URI = collections.namedtuple('URI', [
    'scheme',
    'authority',
    'path',
    'query',
    'fragment',
    'components',
])


URIComponents = collections.namedtuple('URIComponents', [
    'userinfo',
    'port',
    'host',
    'ipv6_address',
    'ipv4_address',
    'reg_name',
    'path_abempty',
    'path_absolute',
    'path_rootless',
    'path_empty',
    'relative_ref',
])
