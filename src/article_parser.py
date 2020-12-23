# -*- coding: utf-8 -*-
import json
from pathlib import Path

import asyncio
import aioredis
from tqdm import tqdm

from src.utils.parser import Parser

def get_article_id(link):
    end = len(link) - 1
    start = link[:end].rfind('/') + 1
    return link[start:end]


async def parse_article(parser, redis, link, texts_path, sem):
    async with sem:
        title_xpath = '//article/div[1]/h1/span'
        topics_xpath = '//article/div[1]/ul[1]/li/a'
        content_xpath = '//*[@id="post-content-body"]'
        tags_xpath = '//article/div[1]/dl[1]/dd/ul/li/a'
        xpaths = [title_xpath, topics_xpath, content_xpath, tags_xpath]
        id = get_article_id(link)
        res = await parser.parse_page(link, xpaths)
        if res is not None:
            title, topics, content, tags = res
        else:
            await redis.srem('links.habr', link)
            return
        for i in content[0].iter():
            if i.tag == 'pre':
                i.getparent().remove(i)
        article_dict = {
            'link': link,
            'title': title[0].text,
            'topics': [t.text for t in topics],
            'tags': [t.text for t in tags],
        }
        await redis.set(f'test:articles.{id}', json.dumps(article_dict))
        content = ''.join(content[0].itertext()).replace('\n', ' ').replace('\r', ' ')
        with texts_path.joinpath(f'{id}.txt').open(mode='w') as f:
            f.write(content)

async def run():
    parser = Parser()
    texts_path = Path('data').joinpath('texts')
    texts_path.mkdir(parents=True, exist_ok=True)
    redis = await aioredis.create_redis_pool('redis://localhost:6379')
    coroutines = list()
    article_prefix = 'test:articles.'

    sem = asyncio.Semaphore(100)
    for article_link in (await redis.smembers('links.habr')):
        id = get_article_id(article_link.decode("utf-8"))
        t = await redis.get(f'{article_prefix}{id}')
        if t is None:
            coroutines.append(
                parse_article(parser, redis, article_link.decode("utf-8"), texts_path, sem)
            )
    for f in tqdm(asyncio.as_completed(coroutines), total=len(coroutines)):
        await f

    results = list()
    for i in tqdm(await redis.keys(f'{article_prefix}*', encoding='utf-8')):
        article_desc = json.loads(await redis.get(i, encoding='utf-8'))
        article_desc.update({'id': i.replace(article_prefix, '')})
        results.append(article_desc)

    with Path('data').joinpath('desc.json').open(mode='w') as f:
        json.dump(results, f, indent=4, ensure_ascii=False)

    redis.close()
    await redis.wait_closed()


def parse_articles():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
    loop.close()
