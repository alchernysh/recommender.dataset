# -*- coding: utf-8 -*-
import json
from pathlib import Path
from collections import OrderedDict

import asyncio
import aioredis
from tqdm import tqdm

from src.utils.parser import Parser


xpaths_dict = OrderedDict(
    {
        'title': '//article/div[1]/h1/span',
        'topics': '//article/div[1]/ul[1]/li/a',
        'content': '//*[@id="post-content-body"]',
        'tags': '//article/div[1]/dl[1]/dd/ul/li/a',
    }
)


def get_article_id(link):
    end = len(link) - 1
    start = link[:end].rfind('/') + 1
    return link[start:end]


def prepare_texts_path():
    texts_path = Path('data').joinpath('texts')
    texts_path.mkdir(parents=True, exist_ok=True)
    return texts_path


def get_article_content(content):
    for i in content[0].iter():
        if i.tag == 'pre':
            i.getparent().remove(i)
    text = ''.join(content[0].itertext()).replace('\n', ' ').replace('\r', ' ')
    return text


async def parse_article(parser, redis, link, texts_path, semaphore):
    async with semaphore:
        id_ = get_article_id(link)
        parser_results = await parser.parse_page(link, xpaths_dict.values())
        if parser_results is not None:
            title, topics, content, tags = parser_results

            content = get_article_content(content)
            with texts_path.joinpath(f'{id_}.txt').open(mode='w') as f:
                f.write(content)

            article_dict = {
                'link': link,
                'title': title[0].text,
                'topics': [t.text for t in topics],
                'tags': [t.text for t in tags],
                'length': len(content),
            }
            await redis.set(f'habr:articles.{id_}', json.dumps(article_dict))


async def get_coroutines(redis, article_prefix, parser):
    texts_path = prepare_texts_path()
    coroutines = list()

    semaphore = asyncio.Semaphore(100)
    for article_link in (await redis.smembers('links.habr')):
        id_ = get_article_id(article_link.decode("utf-8"))
        t = await redis.get(f'{article_prefix}{id_}')
        if t is None:
            coroutines.append(
                parse_article(
                    parser,
                    redis,
                    article_link.decode("utf-8"),
                    texts_path,
                    semaphore
                )
            )
    return coroutines


async def dump_desc(redis, article_prefix):
    results = list()
    for i in tqdm(await redis.keys(f'{article_prefix}*', encoding='utf-8')):
        article_desc = json.loads(await redis.get(i, encoding='utf-8'))
        article_desc.update({'id': i.replace(article_prefix, '')})
        results.append(article_desc)

    with Path('data').joinpath('desc.json').open(mode='w') as f:
        json.dump(results, f, indent=4, ensure_ascii=False)


async def main():
    parser = Parser()

    redis = await aioredis.create_redis_pool('redis://localhost:6379')
    article_prefix = 'habr:articles.'

    coroutines = await get_coroutines(redis, article_prefix, parser)

    for func in tqdm(asyncio.as_completed(coroutines), total=len(coroutines)):
        await func

    await dump_desc(redis, article_prefix)

    redis.close()
    await redis.wait_closed()

def parse_articles():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
