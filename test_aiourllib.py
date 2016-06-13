import asyncio
import contextlib

import aiourllib


async def fetch():
    response = await aiourllib.get('https://ya.ru')
    content = await response.read_text()
    response.close()
    print(len(content))


async def fetch_contextmanager():
    with contextlib.closing(await aiourllib.get('https://ya.ru/')) as response:
        content = await response.read_text()
        print(len(content))


def main():
    loop = asyncio.get_event_loop()
    tasks = [
        fetch(),
        fetch_contextmanager(),
    ]
    loop.run_until_complete(asyncio.gather(*tasks))

if __name__ == '__main__':
    main()
