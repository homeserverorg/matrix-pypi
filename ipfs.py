import asyncio
from aioipfs import AsyncIPFS


async def add():
    c = AsyncIPFS(maddr='/ip4/127.0.0.1/tcp/5001')
    cids = [ entry['Hash'] async for entry in c.add('packages/') ]
    print(cids)
    await c.close()

async def main():
    task = asyncio.create_task(add())
    await task

if __name__ == '__main__':
    asyncio.run(main())
