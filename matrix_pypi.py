from urllib.parse import urlparse, urlunparse
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse

from starlette.types import Send
import aiohttp

from bs4 import BeautifulSoup

app = FastAPI()

PYPI_URL = "https://pypi.org/simple"


from aiohttp import ClientSession, ClientResponse
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse

import logging

from tag_parser import RewriteParser

logger = logging.getLogger("uvicorn")

app = FastAPI()

CHUNK_SIZE = 128 * 1024


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
        async for chunk in response.content.iter_any():
            chunk = chunk.decode()
            #logger.info(f'modify_html_stream::{chunk}')
            modified_chunk = parser.feed(chunk)
            yield modified_chunk.encode()
        await session.close()

    async def stream_response(response: ClientResponse):
        # Stream the response back to the client
        buffer = b''
        async for data in response.content.iter_any():
            buffer += data
            while len(data) >= CHUNK_SIZE:
                yield buffer[:128 * 1024]
                buffer = buffer[128 * 1024:]
        if buffer:
            yield buffer

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
        async for data in response.content.iter_any():
            buffer += data
            while len(buffer) >= CHUNK_SIZE:
                yield buffer[:CHUNK_SIZE]
                buffer = buffer[CHUNK_SIZE:]
        if buffer:
            yield buffer
        await session.close()

    headers = dict(response.headers)
    headers.pop('Content-Length', None)
    headers['Transfer-Encoding'] = 'chunked'
    return StreamingResponse(stream_and_close(), headers=headers)
