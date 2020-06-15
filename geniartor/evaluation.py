"""
Evaluate a musical composition represented as a `Piece` instance.

Author: Nikolay Lysenko
"""


from itertools import combinations
from math import floor
from typing import Any, Callable, Dict, List

from .music_theory import ScaleElement
from .piece import Piece


N_SEMITONES_PER_OCTAVE = 12


def compute_stability_of_sonority(
        sonority: List[ScaleElement],
        n_semitones_to_stability: Dict[int, float]
) -> float:
    """
    Compute stability of sonority as average stability of intervals forming it.

    :param sonority:
        simultaneously sounding pitches
    :param n_semitones_to_stability:
        mapping from interval size in semitones to its stability
    :return:
        stability of sonority (a number from 0 to 1)
    """
    stability = 0
    for first_element, second_element in combinations(sonority, 2):
        interval_in_semitones = abs(
            first_element.position_in_semitones
            - second_element.position_in_semitones
        )
        interval_in_semitones %= N_SEMITONES_PER_OCTAVE
        stability += n_semitones_to_stability[interval_in_semitones]
    n_pairs = len(sonority) * (len(sonority) - 1) / 2
    stability /= n_pairs
    return stability


def evaluate_dissipation_of_tension(
        piece: Piece, beat_weights: Dict[float, float],
        n_semitones_to_stability: Dict[int, float]
) -> float:
    """
    Evaluate dissipation of harmonic tension on strong beats.

    :param piece:
        `Piece` instance
    :param beat_weights:
        mapping from time interval (in fractions of whole measure)
        between start of current measure and start of current sonority
        to a weight of the current measure
    :param n_semitones_to_stability:
        mapping from interval size in semitones to its stability
    :return:
        score which is between -1 and 1
    """
    score = 0
    sum_of_weights = 0
    current_time = 0
    stability_of_previous_sonority = 0
    zipped = zip(piece.sonorities, piece.sonorities_durations)
    for sonority, duration in zipped:
        stability_of_current_sonority = compute_stability_of_sonority(
            sonority, n_semitones_to_stability
        )
        time_since_last_downbeat = current_time - floor(current_time)
        if time_since_last_downbeat in beat_weights:
            weight = beat_weights[time_since_last_downbeat]
            dissipation_of_tension = (
                stability_of_current_sonority
                - stability_of_previous_sonority
            )
            score += weight * dissipation_of_tension
            sum_of_weights += weight
        current_time += duration
        stability_of_previous_sonority = stability_of_current_sonority
    score /= sum_of_weights
    return score


def get_scoring_functions_registry() -> Dict[str, Callable]:
    """
    Get mapping from names of scoring functions to scoring functions.

    :return:
        registry of scoring functions
    """
    registry = {
        'dissipation_of_tension': evaluate_dissipation_of_tension
    }
    return registry


def evaluate(
        piece: Piece,
        scoring_coefs: Dict[str, float],
        scoring_fn_params: Dict[str, Dict[str, Any]],
        verbose: bool = False
) -> float:
    """
    Evaluate piece.

    :param piece:
        `Piece` instance
    :param scoring_coefs:
        mapping from scoring function names to their weights in final score
    :param scoring_fn_params:
        mapping from scoring function names to their parameters
    :param verbose:
        if it is set to `True`, scores are printed with detailing by functions
    :return:
        weighted sum of scores returned by various scoring functions
    """
    score = 0
    registry = get_scoring_functions_registry()
    for fn_name, weight in scoring_coefs.items():
        fn = registry[fn_name]
        fn_params = scoring_fn_params.get(fn_name, {})
        curr_score = weight * fn(piece, **fn_params)
        if verbose:
            print(f'{fn_name:>30}: {curr_score}')  # pragma: no cover
        score += curr_score
    return score
