import os
from urllib.parse import urlparse, urlunparse
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse

from starlette.types import Send
import aiohttp
import aiofiles

from bs4 import BeautifulSoup
import logging
from loggingmx import getLogger

logger = getLogger(__name__)
logger.setLevel('DEBUG')

uv_logger = logging.getLogger("uvicorn")
uv_logger.addHandler(logger.handlers[0])
access_logger = logging.getLogger("uvicorn.access")
access_logger.addHandler(logger.handlers[0])

app = FastAPI()

PYPI_URL = "https://pypi.org/simple"


from aiohttp import ClientSession, ClientResponse
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse

import logging

from tag_parser import RewriteParser

#logger = logging.getLogger("uvicorn")

app = FastAPI()

CHUNK_SIZE = 128 * 1024

def get_package_name_hash(url):
    return url.path.split('/')[-1]

@app.get("/simple/{package_name}/")
async def get_package_page(package_name: str, request: Request):
    parser = RewriteParser(request)

    logger.info(f'get_package_page::{request.base_url}')
    # Create an aiohttp ClientSession
    session = ClientSession()

    # Fetch the package data
    response = await session.get(f"https://pypi.org/simple/{package_name}/")

    if response.status != 200:
        await session.close()
        raise HTTPException(status_code=404, detail="Package not found")

    async def modify_html_stream(response):
        async with aiofiles.open('test.tar.gz', mode='ab') as f:
            async for chunk in response.content.iter_any():
                await f.write(chunk)
                chunk = chunk.decode()
                #logger.info(f'modify_html_stream::{chunk}')
                modified_chunk = parser.feed(chunk)
                yield modified_chunk.encode()
        # Close the aiohttp ClientSession once we're done streaming
        await session.close()

    return StreamingResponse(modify_html_stream(response), media_type='text/html')

@app.get("/packages/{path:path}")
async def get_package_file(path: str, request: Request):
    session = aiohttp.ClientSession()
    response = await session.get(f"https://files.pythonhosted.org/packages/{path}")

    if response.status != 200:
        await session.close()
        raise HTTPException(status_code=404, detail="Package not found")

    async def stream_and_close():
        buffer = b''
        package_filename = get_package_name_hash(request.url)
        async with aiofiles.open(os.path.join(f'packages/{package_filename}'), mode='ab') as f:
            async for data in response.content.iter_any():
                buffer += data
                while len(buffer) >= CHUNK_SIZE:
                    await f.write(buffer[:CHUNK_SIZE])
                    yield buffer[:CHUNK_SIZE]
                    buffer = buffer[CHUNK_SIZE:]
            if buffer:
                await f.write(buffer)
                yield buffer
        await session.close()

    headers = dict(response.headers)
    headers.pop('Content-Length', None)
    headers['Transfer-Encoding'] = 'chunked'
    return StreamingResponse(stream_and_close(), headers=headers)
