# -*- coding: utf-8 -*-
import argparse
from src.link_parser import parse_links


commands = {
    'parse_links': parse_links,
}


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('command', type=str)

    args = parser.parse_args()
    commands[args.command]()
