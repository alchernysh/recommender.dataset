# -*- coding: utf-8 -*-
import concurrent
import json
from pathlib import Path

from tqdm import tqdm
from deep_translator import GoogleTranslator


def translate_words(words):
    result = list()
    for word in words:
        try:
            result.append(GoogleTranslator(source='auto', target='en').translate(word))
        except:
            result.append(word)
    return result


def translate_element(el):
    el.update(
        {
            'topics_en': translate_words(el['topics']),
            'tags_en': translate_words(el['tags']),
        }
    )
    return el

def translate_tags():
    desc_file = Path('data/desc.json')

    with desc_file.open(mode='r') as f:
        dataset = json.load(f)

    new_dataset = list()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        new_dataset = list(tqdm(executor.map(translate_element, dataset), total=len(dataset)))

    with desc_file.open(mode='w') as f:
        json.dump(new_dataset, f, indent=4)

