# -*- coding: utf-8 -*-
import json
import random
import asyncio
import requests
from pathlib import Path

from lxml import etree
from aiohttp import ClientSession, ClientResponseError, TCPConnector
from aiohttp_socks import ProxyConnector


def parse_html(html, xpath):
    tree = etree.HTML(html)
    res = tree.xpath(xpath)
    return res


class Parser:
    def __init__(self):
        self._headers = self._get_headers()
        self._proxies = self._get_proxies()

    def _get_headers(self):
        with Path('./resources/headers.json').open(mode='r') as f:
            headers = json.load(f)
        return headers

    def _get_proxies(self):
        url = 'https://scrapingant.com/free-proxies/'
        xpath = '/html/body/main/div/div[1]/div/div/section[4]/div/div/div/div/div/div[1]/div/div/table/tr'
        session = requests.Session()
        response = session.get(url)
        html = response.text
        proxies = parse_html(html, xpath)
        proxies_dicts = list()
        for proxy in proxies[1:]:
            proxy_dict = dict()
            for i, p in enumerate(proxy.xpath('./td')):
                if i == 0:
                    proxy_dict.update({'ip': p.text})
                elif i == 1:
                    proxy_dict.update({'port': p.text})
                elif i == 2:
                    proxy_dict.update({'protocol': p.text})
            proxies_dicts.append(proxy_dict)
        return proxies_dicts

    def _get_user_agent(self):
        return {'User-Agent': self._headers[random.randrange(0, len(self._headers))]}

    def _get_connector(self):
        proxy = self._proxies[random.randrange(0, len(self._proxies))]
        return ProxyConnector.from_url(f"{proxy['protocol']}://{proxy['ip']}:{proxy['port']}")

    async def parse_page(self, url, xpaths, use_proxy=True):
        html = None
        while not html:
            try:
                connector = self._get_connector() if use_proxy else None
                async with ClientSession(connector=connector) as session:
                    async with session.get(url, headers=self._get_user_agent()) as response:
                        response.raise_for_status()
                        html = await response.text()
            except (UnicodeDecodeError, ClientResponseError):
                return None
            except BaseException:
                await asyncio.sleep(4)
        results = list()
        for xpath in xpaths:
            results.append(parse_html(html, xpath))
        return results
