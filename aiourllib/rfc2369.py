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

    RESERVED = ';' '/' '?' ':' '@' '&' '=' '+' '$' ','

    URIC = RESERVED + UNRESERVED + ESCAPED
    URIC_NO_SLASH = UNRESERVED + ESCAPED + ';' '?' ':' '@' '&' '=' '+' '$' ','

    DELIMS = '<' '>' '#' '%' '"'
    UNWISE = '{' '}' '|' '\\' '^' '[' ']' '`'


    REGEX_URIC = ''.join(REGEX_SPECIAL_CHARACTERS.get(c, c) for c in URIC)
    REGEX_URIC_NO_SLASH = ''.join(REGEX_SPECIAL_CHARACTERS.get(c, c) for c in URIC_NO_SLASH)

    REGEX_COMPONENTS = re.compile('(?P<scheme>.*)\:(?P<scheme_specific_part>.*)')
    REGEX_OPAQUE_PART = re.compile('[{uric_no_slash}][{uric}]*'.format(
        uric_no_slash=REGEX_URIC_NO_SLASH,
        uric=REGEX_URIC))

    REGEX_SCHEME = re.compile('^[{alpha}][{alpha}{digit}\+\-\.]*$'.format(
        alpha=ALPHA,
        digit=DIGIT))

    REGEX_TOPLABLE = re.compile('^(?:[{alpha}]|[{alpha}][{alphanum}\-]**( alphanum | "-" ) alphanum^')


class URIException(Exception):
    pass


class SchemeException(URIException):
    pass


class AuthorityException(URIException):
    pass


class URI(object):
    DEFAULT_PORT = 80
    DEFAULT_ABS_PATH = '/'

    def __init__(self, uri):
        match = Protocol.REGEX_COMPONENTS.match(uri)
        if not match:
            raise URIException(uri)
        scheme, scheme_specific_part = match.groups()

        match = Protocol.REGEX_SCHEME.match(scheme)
        if not match:
            raise SchemeException(scheme)

        # match = Protocol.REGEX_OPAQUE_PART.match(scheme_specific_part).groups()
        # if not match:
        #     raise

        # import pdb;pdb.set_trace()
        # if ':' not in url:
        #     raise URIException(uri)

        # scheme, uri = uri.split(':', 1)
        # if not scheme:
        #     raise SchemeException(scheme)

        # self.scheme = scheme

        # if not uri.startswith('//'):
        #     raise AuthorityException(uri)

        # uri = uri[2:]
        # authority, uri = uri.split('/', 1)

def simple(uri):
    scheme, scheme_specific_part = uri.split(':', 1)

    if scheme_specific_part.startswith('//'):
        # hier_part(net_path)
        pass
    elif scheme_specific_part.startswith('/'):
        # hier_part(abs_path)
        pass
    else:
        # opaque_part
        pass


def main():
    uri = URI('httfsa%%p:ya.ru//')
    # print('[{URIC_NO_SLASH}][{URIC}]*'.format(
    #     URIC_NO_SLASH=Protocol.REGEX_URIC_NO_SLASH,
    #     URIC=Protocol.REGEX_URIC))

if __name__ == '__main__':
    main()
