"""
Find optimal piece with a variant of Variable Neighborhood Search.

Author: Nikolay Lysenko
"""


import itertools
import random
from copy import deepcopy
from typing import Any, Dict

from .evaluation import evaluate
from .piece import Piece


def update_one_sonority(
        result: Dict[str, Any], sonority_position: int,
        evaluation_params: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Replace particular sonority with locally the best one.

    :param result:
        `Piece` instance and its evaluation score
    :param sonority_position:
        index of sonority to be updated
    :param evaluation_params:
        settings of piece evaluation
    :return:
        piece with one modified sonority
    """
    piece = deepcopy(result['piece'])
    alternatives = itertools.combinations(piece.pitches, piece.n_voices)
    for alternative_sonority in alternatives:
        piece.sonorities[sonority_position] = alternative_sonority
        score = evaluate(piece, **evaluation_params)
        if score > result['score']:
            result = {'piece': deepcopy(piece), 'score': score}
    return result


def perturb(piece: Piece, perturbation_probability: float) -> Piece:
    """
    Replace some sonorities with random sonorities.

    :param piece:
        `Piece` instance
    :param perturbation_probability:
        probability to replace sonority with a random sonority during
        perturbation stage
    :return:
        altered piece
    """
    weights = [perturbation_probability, 1 - perturbation_probability]
    new_sonorities = []
    for sonority in piece.sonorities:
        to_keep = random.choices([False, True], weights)[0]
        if to_keep:
            new_sonorities.append(sonority)
        else:
            new_sonority = sorted(
                random.sample(piece.pitches, piece.n_voices),
                key=lambda x: x.position_in_semitones
            )
            new_sonorities.append(new_sonority)
    piece.sonorities = new_sonorities
    return piece


def run_variable_neighborhood_search(
        piece: Piece, evaluation_params: Dict[str, Any],
        n_passes: int, perturbation_probability: float
) -> Piece:
    """
    Run Variable Neighborhood Search in order to find optimal piece.

    :param piece:
        random initial piece
    :param evaluation_params:
        settings of piece evaluation
    :param n_passes:
        number of passes through all neighborhoods
    :param perturbation_probability:
        probability to replace sonority with a random sonority during
        perturbation stage
    :return:
        found piece
    """
    initial_score = evaluate(piece, **evaluation_params)
    best_result = {'piece': deepcopy(piece), 'score': initial_score}
    previous_result = {'piece': deepcopy(piece), 'score': initial_score}
    result = {'piece': deepcopy(piece), 'score': initial_score}
    for pass_number in range(n_passes):
        for position in range(len(piece.sonorities)):
            result = update_one_sonority(result, position, evaluation_params)
        print(f"Results after pass #{pass_number}:")
        evaluate(result['piece'], **evaluation_params, verbose=True)
        if result['score'] > best_result['score']:
            best_result = deepcopy(result)
        elif result['score'] <= previous_result['score']:
            print("Local optimum is reached, perturbation is needed.")
            new_piece = perturb(result['piece'], perturbation_probability)
            print("Results after perturbation:")
            score = evaluate(new_piece, **evaluation_params, verbose=True)
            result = {'piece': deepcopy(new_piece), 'score': score}
        previous_result = deepcopy(result)
    final_piece = best_result['piece']
    return final_piece
