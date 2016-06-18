import asyncio
import contextlib
import unittest

import aiourllib


class HttpbinTestCase(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.get_event_loop()

    def tearDown(self):
        self.loop.close()

    async def read(self, url):
        with contextlib.closing(await aiourllib.get(url)) as response:
            return await response.read_content()

    def fetch(self, url):
        return self.loop.run_until_complete(asyncio.async(self.read(url)))

    def test_httpbin(self):
        self.assertIsNotNone(self.fetch('https://httpbin.org'))
