# -*- coding: utf-8 -*-
import asyncio
import redis
from tqdm import tqdm
from src.utils.parser import Parser


def parse_num_pages_link(href):
    href = href[0]
    num_pages = href[href.find('page')+4:len(href)-1]
    return int(num_pages)


async def run():
    links_xpath = '/html/body/div[1]/div[3]/div/div/div[1]/div[3]/ul[2]/li/div[1]/div/div/a/@href'
    num_pages_link_xpath = '/html/body/div[1]/div[3]/div/div[1]/div[1]/div[3]/div/ul[2]/li[9]/a/@href'
    article_links_xpath = '/html/body/div[1]/div[3]/div/div[1]/div[1]/div[3]/ul/li/article/h2/a/@href'
    site = 'habr'
    r = redis.StrictRedis(host='localhost', port=6379)
    parser = Parser()
    links = (await parser.parse_page('https://habr.com/ru/hubs/', [links_xpath]))[0]
    for link in links:
        article_links = list()
        num_pages_link = (await parser.parse_page(link, [num_pages_link_xpath]))[0]
        num_pages = parse_num_pages_link(num_pages_link)
        coroutines = [parser.parse_page(f'{link}page{i}', [article_links_xpath]) for i in range(1, num_pages+1)]
        async with asyncio.Semaphore(100):
            for f in tqdm(asyncio.as_completed(coroutines), total=len(coroutines)):
                article_links.append((await f)[0])
        article_links = {item for sublist in article_links for item in sublist}
        r.sadd(f'links.{site}', *article_links)

def parse_links():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
    loop.close()
