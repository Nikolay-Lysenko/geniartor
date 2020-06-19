"""
Evaluate a musical composition represented as a `Piece` instance.

Author: Nikolay Lysenko
"""


from itertools import combinations
from typing import Any, Callable, Dict, List

from .music_theory import ScaleElement
from .piece import Piece


N_SEMITONES_PER_OCTAVE = 12


def compute_harmonic_stability_of_sonority(
        sonority: List[ScaleElement],
        n_semitones_to_stability: Dict[int, float]
) -> float:
    """
    Compute stability of sonority as average stability of intervals forming it.

    :param sonority:
        simultaneously sounding pitches
    :param n_semitones_to_stability:
        mapping from interval size in semitones to its harmonic stability
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


def evaluate_harmonic_stability(
        piece: Piece, min_stabilities: Dict[str, float],
        n_semitones_to_stability: Dict[int, float]
) -> float:
    """
    Evaluate deviation of actual harmonic stability from its desired level.

    :param piece:
        `Piece` instance
    :param min_stabilities:
        mapping from type of sonority's start position to minimum
        sufficient stability
    :param n_semitones_to_stability:
        mapping from interval size in semitones to its harmonic stability
    :return:
        average over all sonorities lack of stability, a score between -1 and 0
    """
    score = 0
    zipped = zip(piece.sonorities, piece.position_types)
    for sonority, position_type in zipped:
        stability_of_current_sonority = compute_harmonic_stability_of_sonority(
            sonority, n_semitones_to_stability
        )
        sufficient_stability = min_stabilities[position_type]
        score += min(stability_of_current_sonority - sufficient_stability, 0)
    score /= len(piece.sonorities)
    return score


def compute_tonal_stability_of_sonority(
        sonority: List[ScaleElement],
        degree_to_stability: Dict[int, float]
) -> float:
    """
    Compute stability of sonority as average stability of pitches forming it.

    :param sonority:
        simultaneously sounding pitches
    :param degree_to_stability:
        mapping from scale degree to its tonal stability
    :return:
        stability of sonority (a number from 0 to 1)
    """
    stability = sum(degree_to_stability[x.degree] for x in sonority)
    stability /= len(sonority)
    return stability


def evaluate_tonal_stability(
        piece: Piece, min_stabilities: Dict[str, float],
        degree_to_stability: Dict[int, float]
) -> float:
    """
    Evaluate deviation of actual tonal stability from its desired level.

    :param piece:
        `Piece` instance
    :param min_stabilities:
        mapping from type of sonority's start position to minimum
        sufficient stability
    :param degree_to_stability:
        mapping from scale degree to its tonal stability
    :return:
        average over all sonorities lack of stability, a score between -1 and 0
    """
    score = 0
    zipped = zip(piece.sonorities, piece.position_types)
    for sonority, position_type in zipped:
        stability_of_current_sonority = compute_tonal_stability_of_sonority(
            sonority, degree_to_stability
        )
        sufficient_stability = min_stabilities[position_type]
        score += min(stability_of_current_sonority - sufficient_stability, 0)
    score /= len(piece.sonorities)
    return score


def get_scoring_functions_registry() -> Dict[str, Callable]:
    """
    Get mapping from names of scoring functions to scoring functions.

    :return:
        registry of scoring functions
    """
    registry = {
        'harmonic_stability': evaluate_harmonic_stability,
        'tonal_stability': evaluate_tonal_stability,
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
