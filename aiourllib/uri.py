import collections

from . import (
    exc,
    models,
    protocol)


def from_string(uri_reference):
    uri = {
        'scheme': None,
        'authority': None,
        'path': None,
        'query': None,
        'fragment': None,
        'components': None,
    }
    components = {
        'userinfo': None,
        'port': None,
        'host': None,
        'ipv6_address': None,
        'ipv4_address': None,
        'reg_name': None,
        'path_abempty': None,
        'path_absolute': None,
        'path_rootless': None,
        'path_empty': None,
        'relative_ref': None,
    }

    uri['scheme'], hier_part = protocol.URIProtocol.strip_scheme(uri_reference)
    uri['fragment'], hier_part = protocol.URIProtocol.strip_fragment(hier_part)
    uri['query'], hier_part = protocol.URIProtocol.strip_query(hier_part)
    if uri['scheme']:
        # hier_part
        if hier_part.startswith('//'):
            # authority
            authority, hier_part = protocol.URIProtocol.strip_authority(
                hier_part)
            uri['authority'] = authority
            components['userinfo'], authority = \
                protocol.URIProtocol.strip_userinfo(authority)
            components['port'], authority = \
                protocol.URIProtocol.strip_port(authority)
            host = components['host'] = authority
            if protocol.URIProtocol.verify_ipv6_address(host):
                components['ipv6_address'] = host
            elif protocol.URIProtocol.verify_ipv4_address(host):
                components['ipv4_address'] = host
            elif protocol.URIProtocol.verify_reg_name(host):
                components['reg_name'] = host
            else:
                raise exc.AuthorityException(host)

            if protocol.URIProtocol.verify_path_abempty(hier_part):
                uri['path'] = components['path_abempty'] = hier_part
            else:
                raise exc.PathException(hier_part)

        elif protocol.URIProtocol.verify_path_absolute(hier_part):
            uri['path'] = components['path_absolute'] = hier_part
        elif protocol.URIProtocol.verify_path_rootless(hier_part):
            uri['path'] = components['path_rootless'] = hier_part
        elif protocol.URIProtocol.verify_path_empty(hier_part):
            uri['path'] = components['path_empty'] = hier_part
        else:
            raise exc.PathException(hier_part)

    else:
        # relative_ref
        relative_ref = components['relative_ref'] = hier_part
        if relative_ref.startswith('//'):
            # authority
            authority, relative_ref = protocol.URIProtocol.strip_authority(
                relative_ref)
            uri['authority'] = authority
            components['userinfo'], authority = \
                protocol.URIProtocol.strip_userinfo(authority)
            components['port'], authority = \
                protocol.URIProtocol.strip_port(authority)
            host = components['host'] = authority
            if protocol.URIProtocol.verify_ipv6_address(host):
                components['ipv6_address'] = host
            elif protocol.URIProtocol.verify_ipv4_address(host):
                components['ipv4_address'] = host
            elif protocol.URIProtocol.verify_reg_name(host):
                components['reg_name'] = host
            else:
                raise exc.AuthorityException(host)

            if protocol.URIProtocol.verify_path_abempty(relative_ref):
                uri['path'] = components['path_abempty'] = relative_ref
            else:
                raise exc.PathException(relative_ref)

        elif protocol.URIProtocol.verify_path_absolute(relative_ref):
            uri['path'] = components['path_absolute'] = relative_ref
        elif protocol.URIProtocol.verify_path_noscheme(relative_ref):
            uri['path'] = components['path_noscheme'] = relative_ref
        elif protocol.URIProtocol.verify_path_empty(relative_ref):
            uri['path'] = components['path_empty'] = relative_ref
        else:
            raise exc.PathException(relative_ref)
    components = models.URIComponents(**components)
    uri['components'] = components
    return models.URI(**uri)


def to_string(uri):
    # scheme authority path query fragment
    uri_reference = ''
    if uri.scheme:
        uri_reference = '{}:'.format(uri.scheme)
    if uri.authority:
        uri_reference = '{}//{}'.format(uri_reference, uri.authority)
    uri_reference = '{}{}'.format(uri_reference, uri.path or '')
    if uri.query:
        uri_reference = '{}?{}'.format(uri_reference, uri.query)
    if uri.fragment:
        uri_reference = '{}#{}'.format(uri_reference, uri.fragment)
    return uri_reference
