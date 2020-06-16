"""
Find optimal piece with a variant of Variable Neighborhood Search.

Author: Nikolay Lysenko
"""


import itertools
from copy import deepcopy
from typing import Any, Dict

from .evaluation import evaluate
from .piece import Piece


def change_one_sonority(
        piece: Piece, sonority_position: int, evaluation_params: Dict[str, Any]
) -> Piece:
    """"""
    initial_score = evaluate(piece, **evaluation_params)
    best_result = {'piece': deepcopy(piece), 'score': initial_score}
    alternatives = itertools.combinations(piece.pitches, piece.n_voices)
    for alternative_sonority in alternatives:
        piece.sonorities[sonority_position] = alternative_sonority
        score = evaluate(piece, **evaluation_params)
        if score > best_result['score']:
            best_result = {'piece': deepcopy(piece), 'score': score}
    return best_result['piece']


def find_optimum_piece(
        piece: Piece, evaluation_params: Dict[str, Any], n_passes: int
) -> Piece:
    """"""
    for pass_number in range(n_passes):
        for position in range(len(piece.sonorities)):
            piece = change_one_sonority(piece, position, evaluation_params)
        print(f"Results after pass #{pass_number}:")
        evaluate(piece, **evaluation_params, verbose=True)
    return piece
