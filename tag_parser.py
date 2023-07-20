from urllib.parse import urlparse, urlunparse
from html.parser import HTMLParser
from html import escape

import logging
logger = logging.getLogger("uvicorn")

def replace_netloc(old_url: str, netloc: str):
    parts = urlparse(old_url)
    return urlunparse(parts._replace(netloc=netloc, scheme='http'))

class RewriteParser(HTMLParser):
    def __init__(self, request, *args, **kwargs):
        self.request = request
        self.buffer = ''
        self.output = ''
        super().__init__(*args, **kwargs)

    def feed(self, data):
        self.buffer += data.strip()
        self.output = ''
        while '>' in self.buffer:
            tag, self.buffer = self.buffer.split('>', 1)
            tag += '>'
            super().feed(tag)
        return self.output

    def handle_starttag(self, tag, attrs):
        #logger.info(f'handle_starttag::{tag}::{attrs}')
        if tag == "a":
            attrs = [(name, replace_netloc(value, self.request.base_url.netloc)) if name == "href" else (name, escape(value)) for name, value in attrs]
        elif tag == "br":
            self.output += f'<{tag} />'
            return
        attr_str = ' '.join(f'{name}="{value}"' for name, value in attrs)
        self.output += f'<{tag} {attr_str}>'

    def handle_endtag(self, tag):
        #logger.info(f'handle_endtag::{tag}')
        # bug? https://bugs.python.org/issue25258
        if tag == "br":
            return
        self.output += f"</{tag}>"

    def handle_data(self, data):
        self.output += data

    # def handle_startendtag(self, tag, attrs):
    #     if tag != "br":
    #         attr_str = ' '.join(f'{name}="{value}"' for name, value in attrs)
    #         self.output += f'<{tag} {attr_str}/>'

    def flush(self):
        if self.buffer:
            self.output = ''
            super().feed(self.buffer)
            self.buffer = ''
        logger.info(f'flush::{self.output}')
        return self.output
