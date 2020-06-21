"""
Find optimal piece with a variant of Variable Neighborhood Search.

Author: Nikolay Lysenko
"""


import itertools
import random
from copy import deepcopy
from typing import Any, Dict, List

from .evaluation import evaluate
from .piece import Piece, PieceElement, ScaleElement


def set_new_values_for_sonority(
        melodic_lines: List[List[PieceElement]],
        indices: List[int],
        new_values: List[ScaleElement]
) -> None:
    """"""
    zipped = zip(melodic_lines, indices, new_values)
    for melodic_line, index, new_scale_element in zipped:
        old_piece_element = melodic_line[index]
        melodic_line[index] = PieceElement(
            note=new_scale_element.note,
            position_in_semitones=new_scale_element.position_in_semitones,
            position_in_degrees=new_scale_element.position_in_degrees,
            degree=new_scale_element.degree,
            start_time=old_piece_element.start_time,
            duration=old_piece_element.duration
        )


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
    indices = piece.sonorities[sonority_position].indices
    n_lines = len(piece.melodic_lines)
    alternatives = itertools.combinations(piece.pitches, n_lines)
    for alternative in alternatives:
        set_new_values_for_sonority(piece.melodic_lines, indices, alternative)
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
    for sonority in piece.sonorities:
        to_keep = random.choices([False, True], weights)[0]
        if to_keep:
            continue
        new_scale_elements = sorted(
            random.sample(piece.pitches, len(piece.melodic_lines)),
            key=lambda x: x.position_in_semitones
        )
        set_new_values_for_sonority(
            piece.melodic_lines, sonority.indices, new_scale_elements
        )
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
