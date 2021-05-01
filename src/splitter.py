# -*- coding: utf-8 -*-
import numpy as np

import json
from random import shuffle
from pathlib import Path


def split_dataset():
    description_path = Path('data/desc_filtered.json')

    with description_path.open(mode='r') as f:
        dataset = json.load(f)

    shuffle(dataset)

    train_size = 0.7
    test_size = 0.2

    limits = [
        int(len(dataset)*train_size),
        int(len(dataset)*(train_size + test_size))
    ]

    train, test, val = np.split(dataset, limits)
    result = {
        'train': train,
        'test': test,
        'val': val,
    }
    return result
