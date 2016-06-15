import string
import re

REGEX_SPECIAL_CHARACTERS = {
    '.': '\.',
    '^': '\^',
    '$': '\$',
    '*': '\*',
    '+': '\+',
    '?': '\?',
    '[': '\[',
    ']': '\]',
    '(': '\(',
    ')': '\)',
    '{': '\{',
    '}': '\}',
    '-': '\-',
    '%': '\%',
}

class Protocol(object):
    LOWALPHA = string.ascii_lowercase
    UPALPHA = string.ascii_uppercase
    ALPHA = LOWALPHA + UPALPHA

    DIGIT = string.digits
    ALPHANUM = ALPHA + DIGIT

    MARK = '-' '_' '.' '!' '~' '*' '\'' '(' ')'

    UNRESERVED = ALPHANUM + MARK

    HEX = string.hexdigits
    ESCAPED = '%' + HEX

    RESERVED = ';' '/' '?' ':' '@' '&' '=' '+' '$' ',' '[' ']'

    URIC = RESERVED + UNRESERVED + ESCAPED
    URIC_NO_SLASH = UNRESERVED + ESCAPED + ';' '?' ':' '@' '&' '=' '+' '$' ','

    DELIMS = '<' '>' '#' '%' '"'
    UNWISE = '{' '}' '|' '\\' '^' '`'

    PCHAR = UNRESERVED + ESCAPED + ':' '@' '&' '=' '+' '$' ','


class URIException(Exception):
    pass


class SchemeException(URIException):
    pass


class UserInfoException(URIException):
    pass


class PortException(URIException):
    pass


class AuthorityException(URIException):
    pass


class FragmentException(URIException):
    pass


class QueryException(URIException):
    pass


class PathSegmentException(URIException):
    pass


class URI(object):
    SCHEME = Protocol.ALPHANUM + '+' '-' '.'
    USERINFO = Protocol.UNRESERVED + Protocol.ESCAPED + ';' ':' '&' '=' '+' '$' ','
    TOPLABEL = Protocol.ALPHANUM + '-'
    SEGMENT = Protocol.PCHAR + ';'

    PORTS = {
        'http': 80,
        'https': 443,
    }

    def __init__(self, uri):
        if ':' not in uri:
            # relative uri
            raise NotImplementedError(uri)

        scheme, scheme_specific_part = uri.split(':', 1)
        if scheme[0] not in Protocol.ALPHA:
            raise SchemeException(uri)

        if any(c not in self.SCHEME for c in scheme[1:]):
            raise SchemeException(scheme)

        self.scheme = scheme.lower()

        if scheme_specific_part.startswith('//'):
            scheme_specific_part = scheme_specific_part[2:]

            if '/' in scheme_specific_part:
                authority, scheme_specific_part = scheme_specific_part.split('/', 1)
            else:
                authority = scheme_specific_part
                scheme_specific_part = ''

            if '@' in authority:
                userinfo, authority = authority.split('@', 1)
                if any(c not in self.USERINFO for c in userinfo):
                    raise UserInfoException(userinfo)
                if not userinfo:
                    userinfo = None
            else:
                userinfo = None
            self.userinfo = userinfo

            if ':' in authority:
                host, port = authority.rsplit(':', 1)
                if port.isdigit():
                    port = int(port)
                else:
                    raise PortException(port)
            else:
                host = authority
                port = self.PORTS.get(self.scheme)
            self.port = port

            self.ipv6_address = self.ipv4_address = None
            self.toplabel = self.domainlabels = self.hostname = None

            if host.startswith('[') and host.endswith(']'):
                # ipv6
                raise NotImplementedError(host)
            elif host.replace('.', '').isdigit():
                host = host.split('.')
                if len(host) == 4 and all(n and n.isdigit() and int(n) <= 255 for n in host):
                    host = '.'.join(host)
                else:
                    raise AuthorityException('.'.join(host))
                self.ipv4_address = host
            elif host:
                host = host.split('.')

                toplabel = host[-1]
                if toplabel.endswith('.'):
                    toplabel = toplabel[:-1]
                if not toplabel:
                    raise AuthorityException('.'.join(host))
                if not (toplabel[0] in Protocol.ALPHA):
                    raise AuthorityException(toplabel)
                if not (toplabel[-1] in Protocol.ALPHANUM):
                    raise AuthorityException(toplabel)
                if any(c not in self.TOPLABEL for c in toplabel[1:-1]):
                    raise AuthorityException(toplabel)
                self.toplabel = toplabel

                domainlabels = host[:-1]
                for domainlabel in domainlabels:
                    if not domainlabel:
                        raise AuthorityException('.'.join(host))
                    if not (domainlabel[0] in Protocol.ALPHANUM):
                        raise AuthorityException(domainlabel)
                    if not (domainlabel[-1] in Protocol.ALPHANUM):
                        raise AuthorityException(domainlabel)
                    if any(c not in self.TOPLABEL for c in domainlabel[1:-1]):
                        raise AuthorityException(domainlabel)
                self.domainlabels = domainlabels

                host = '.'.join(host)
                self.hostname = host

            self.authority = host

            if scheme_specific_part:
                if '#' in scheme_specific_part:
                    scheme_specific_part, fragment = scheme_specific_part.rsplit('#', 1)
                    if any(c not in Protocol.URIC for c in fragment):
                        raise FragmentException(fragment)
                    self.fragment = fragment
                else:
                    self.fragment = None
                if '?' in scheme_specific_part:
                    scheme_specific_part, query = scheme_specific_part.rsplit('?', 1)
                    if any(c not in Protocol.URIC for c in query):
                        raise QueryException(query)
                    self.query = query
                else:
                    self.query = None

                path = scheme_specific_part or '/'
                if not path.startswith('/'):
                    path = '/{}'.format(path)

                segments = path.strip('/').split('/')
                for segment in segments:
                    if not segment:
                        continue
                    if segment[0] not in Protocol.PCHAR:
                        raise PathSegmentException(segment)
                    if any(c not in self.SEGMENT for c in segment):
                        raise PathSegmentException(segment)
                self.segments = segments

                self.path = path
            else:
                self.path = '/'
                self.segments = None
                self.fragment = self.query = None

        elif scheme_specific_part.startswith('/'):
            # hier_part(abs_path)
            raise NotImplementedError(uri)
        elif scheme_specific_part[0] in Protocol.URIC_NO_SLASH:
            # opaque_part
            raise NotImplementedError(uri)
        else:
            raise URIException(uri)

    def __str__(self):
        result = ''
        if self.scheme:
            result = '{}{}:'.format(result, self.scheme)
        if self.authority:
            result = '{}//{}'.format(result, self.authority)
        else:
            result = '{}//'.format(result)
        result = '{}{}'.format(result, self.path)
        if self.query:
            result = '{}?{}'.format(result, self.query)
        if self.fragment:
            result = '{}#{}'.format(result, self.fragment)
        return result

def main():
    uri = URI('http://ya.ru/fads/fasd/./fasd#fasdfasd')
    print(uri)
    print(URI('file:///tm{}p/test.py'))

if __name__ == '__main__':
    main()
