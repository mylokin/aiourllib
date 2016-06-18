import asyncio
import contextlib
import unittest

import aiourllib


class HttpbinTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.loop = asyncio.get_event_loop()

    @classmethod
    def tearDownClass(cls):
        cls.loop.close()

    async def read(self, url):
        with contextlib.closing(await aiourllib.get(url)) as response:
            return await response.read_content()

    async def read_json(self, url):
        with contextlib.closing(await aiourllib.get(url)) as response:
            return await response.read_content()

    def fetch(self, url):
        return self.loop.run_until_complete(
            self.read(url))

    def fetch_json(self, url):
        return self.loop.run_until_complete(
            self.read_json(url))

    def test_ip(self):
        self.fetch_json('https://httpbin.org/ip')

    def test_user_agent(self):
        self.fetch_json('https://httpbin.org/user-agent')

    def test_headers(self):
        self.fetch_json('https://httpbin.org/headers')

    def test_get(self):
        self.fetch_json('https://httpbin.org/get')

    def test_encoding_utf8(self):
        self.fetch('https://httpbin.org/encoding/utf8')

    def test_gzip(self):
        self.fetch_json('https://httpbin.org/gzip')

    def test_deflate(self):
        self.fetch_json('https://httpbin.org/deflate')

    def test_stream(self):
        self.fetch('https://httpbin.org/stream/20')

    def test_delay(self):
        self.fetch_json('https://httpbin.org/delay/3')

    def test_xml(self):
        self.fetch('https://httpbin.org/xml')
