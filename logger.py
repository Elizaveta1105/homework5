import asyncio
from datetime import datetime

from aiopath import AsyncPath
from aiofile import async_open


file = AsyncPath('log.txt')


async def add_logging():
    async with async_open(file, 'a+') as afp:
        await afp.write(f'The exchange message was used at {datetime.now()}\n')