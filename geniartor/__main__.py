"""
Run tasks related to music generation.

Author: Nikolay Lysenko
"""


import argparse
import os
from pkg_resources import resource_filename

import yaml

from .optimization import find_optimum_piece
from .piece import Piece
from .rendering import render


def parse_cli_args() -> argparse.Namespace:
    """
    Parse arguments passed via Command Line Interface (CLI).

    :return:
        namespace with arguments
    """
    parser = argparse.ArgumentParser(description='Music composition with RL')
    parser.add_argument(
        '-c', '--config_path', type=str, default=None,
        help='path to configuration file'
    )
    parser.add_argument(
        '-p', '--populations', type=int, default=100,
        help='number of populations for search of best piece'
    )
    cli_args = parser.parse_args()
    return cli_args


def main() -> None:
    """Parse CLI arguments and run requested tasks."""
    cli_args = parse_cli_args()

    default_config_path = 'configs/default_config.yml'
    default_config_path = resource_filename(__name__, default_config_path)
    config_path = cli_args.config_path or default_config_path
    with open(config_path) as config_file:
        settings = yaml.load(config_file, Loader=yaml.FullLoader)

    piece = Piece(**settings['piece'])
    piece = find_optimum_piece(
        piece, settings['evaluation'], **settings['optimization']
    )

    results_dir = settings['rendering']['dir']
    if not os.path.isdir(results_dir):
        os.mkdir(results_dir)
    render(piece, settings['rendering'])


if __name__ == '__main__':
    main()
