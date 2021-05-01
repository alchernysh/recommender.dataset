# -*- coding: utf-8 -*-
import json
from pathlib import Path


def filter_data():
    with Path('data/desc.json').open() as f:
        data = json.load(f)
    print(len(data))
    filtered_data = list(filter(lambda x: x['length'] >= 2000 and len(x['tags']>=8), data))
    print(len(filtered_data))
    with Path('data/desc_filtered.json').open('w') as f:
        json.dump(filtered_data, f)
