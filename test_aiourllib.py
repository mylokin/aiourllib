import asyncio
import contextlib

import aiourllib


async def fetch(url):
    with contextlib.closing(await aiourllib.get(url)) as response:
        content = await response.read_text()
        print(content)


def main():
    loop = asyncio.get_event_loop()
    tasks = [
        fetch('https://httpbin.org'),
        fetch('https://httpbin.org/stream/20'),
    ]
    loop.run_until_complete(asyncio.gather(*tasks))

if __name__ == '__main__':
    main()
