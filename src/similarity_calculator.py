# -*- coding: utf-8 -*-
import json
from pathlib import Path
from random import randint
from uuid import uuid4

import numpy as np
from scipy import spatial
from tqdm import tqdm
import gensim.downloader
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

from src.splitter import split_dataset


def tokenize(word_list):
    result = list()
    for word in word_list:
        result.extend(word.replace('-', ' ').replace('-', ' ').split())
    return result


def word_processor(word_list):
    sentence = ' '.join(tokenize(word_list))
    word_tokens = word_tokenize(sentence)
    stop_words = set(stopwords.words('english'))
    filtered_sentence = [w for w in word_tokens if not w in stop_words]
    return filtered_sentence


def get_words_embedding(s, fasttext_vectors):
    s = word_processor(s)
    e = list()
    for i in s:
        try:
            e.append(fasttext_vectors.wv[i])
        except KeyError:
            continue
    return np.mean(e, axis=0)


def get_full_embedding(el, fasttext_vectors):
    words_list = el['topics_en'] + el['tags_en']
    embeddings = get_words_embedding(words_list, fasttext_vectors)
    return embeddings


def get_bow_similarity(el_x, el_y):
    words_list_1 = el_x['topics_en'] + el_x['tags_en']
    words_list_2 = el_y['topics_en'] + el_y['tags_en']
    corpus = list(set(words_list_1 + words_list_2))
    def get_embeddings(s):
        res = np.zeros(len(corpus))
        for w in s:
            x = np.zeros(len(corpus))
            idx = corpus.index(w)
            x[idx] = 1
            res += x
        return res
    
    embeddings_1 = get_embeddings(words_list_1)
    embeddings_2 = get_embeddings(words_list_2)
    similarity = 1 - spatial.distance.cosine(embeddings_1, embeddings_2)
    return 2*similarity - 1


def get_dataset_with_similarity(fasttext_vectors, dataset):
    processed_dataset = list()

    for el_x in tqdm(dataset, total=len(dataset)):
        for _ in range(3):
            el_y = dataset[randint(0, len(dataset)-1)]
            embeddings_x = get_full_embedding(el_x, fasttext_vectors)
            embeddings_y = get_full_embedding(el_y, fasttext_vectors)
            if not np.all(np.isnan(embeddings_y)) and not np.all(np.isnan(embeddings_x)):
                fasttext_similarity = 1 - spatial.distance.cosine(embeddings_x, embeddings_y)
                bow_similarity = get_bow_similarity(el_x, el_y)
                similarity = fasttext_similarity*0.7 + bow_similarity*0.3
                processed_dataset.append(
                    {
                        'id': str(uuid4()),
                        'sentence_ids': [el_x['id'], el_y['id']],
                        'similarity': round(similarity, 4),
                    }
                )
    return processed_dataset


def calculate_similarity():
    fasttext_vectors = gensim.downloader.load('fasttext-wiki-news-subwords-300')

    destination_path = Path('data')
    dataset_dict = split_dataset()
    for name, dataset in dataset_dict.items():
        print(f'calculating similarity for {name} dataset')
        processed_dataset = get_dataset_with_similarity(fasttext_vectors, dataset)
        with destination_path.joinpath(f'{name}.json').open('w') as f:
            json.dump(processed_dataset, f, indent=4)
