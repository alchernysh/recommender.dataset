# -*- coding: utf-8 -*-
import argparse
from src.link_parser import parse_links
from src.article_parser import parse_articles
from src.similarity_calculator import calculate_similarity


commands = {
    'parse_links': parse_links,
    'parse_articles': parse_articles,
    'calculate_similarity': calculate_similarity,
}


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('command', type=str)

    args = parser.parse_args()
    commands[args.command]()
