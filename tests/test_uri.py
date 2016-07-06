import unittest

from aiourllib import uri


class TestURI(unittest.TestCase):
    def assertMatch(self, uri_reference):
        self.assertEqual(
            uri.to_string(uri.from_string(uri_reference)), uri_reference)

    def test_ftp(self):
        self.assertMatch('ftp://ftp.is.co.za/rfc/rfc1808.txt')

    def test_http(self):
        self.assertMatch('http://www.ietf.org/rfc/rfc2396.txt')

    def test_http_query_fragment(self):
        self.assertMatch('http://www.ietf.org/rfc/rfc2396.txt?a#b')

    def test_mailto(self):
        self.assertMatch('mailto:John.Doe@example.com')

    def test_news(self):
        self.assertMatch('news:comp.infosystems.www.servers.unix')

    def test_tel(self):
        self.assertMatch('tel:+1-816-555-1212')

    def test_telnet(self):
        self.assertMatch('telnet://192.0.2.16:80/')

    def test_urn(self):
        self.assertMatch('urn:oasis:names:specification:docbook:dtd:xml:4.1.2')
