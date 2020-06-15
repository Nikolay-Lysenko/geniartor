"""
Run tasks related to music generation.

Author: Nikolay Lysenko
"""


import argparse
import os
from pkg_resources import resource_filename
from typing import Any, Dict

import yaml
import numpy as np
from optimiser.population import optimize_with_crossentropy_method

from .evaluation import evaluate
from .piece import Piece
from .rendering import render


def evaluate_piece_defined_by_raw_roll(
        raw_roll: np.ndarray,
        piece_params: Dict[str, Any],
        evaluation_params: Dict[str, Any]
) -> float:
    """
    Evaluate piece defined by its raw roll.

    :param raw_roll:
        an array that resembles piano roll, but keeps no information about
        columns duration and contains float values that must be converted to
        0 or 1 by setting to 1 only cells with highest values for each column
    :param piece_params:
        settings of `Piece` instance
    :param evaluation_params:
        settings of evaluation
    :return:
        reward earned by the agent with the given weights
    """
    piece = Piece(**piece_params)
    piece.set_piece_content(raw_roll)
    score = evaluate(piece, **evaluation_params)
    return score


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
        settings = yaml.safe_load(config_file)

    piece = Piece(**settings['piece'])
    initial_mean = np.zeros(piece.roll_shape)
    target_fn_kwargs = {
        'piece_params': settings['piece'],
        'evaluation_params': settings['evaluation'],
    }
    best_raw_roll = optimize_with_crossentropy_method(
        evaluate_piece_defined_by_raw_roll,
        target_fn_kwargs=target_fn_kwargs,
        n_populations=cli_args.populations,
        initial_mean=initial_mean,
        **settings['optimization']
    )
    piece.set_piece_content(best_raw_roll)
    evaluate(piece, **settings['evaluation'], verbose=True)

    results_dir = settings['rendering']['dir']
    if not os.path.isdir(results_dir):
        os.mkdir(results_dir)
    render(piece, settings['rendering'])


if __name__ == '__main__':
    main()
