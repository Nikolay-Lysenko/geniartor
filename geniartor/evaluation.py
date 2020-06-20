"""
Evaluate a musical composition represented as a `Piece` instance.

Author: Nikolay Lysenko
"""


from itertools import combinations
from typing import Any, Callable, Dict, List

from .piece import Piece, PieceElement, convert_sonority_to_its_elements


N_SEMITONES_PER_OCTAVE = 12


def evaluate_absence_of_voice_crossing(piece: Piece) -> float:
    """
    Evaluate absence of voice crossing.

    :param piece:
        `Piece` instance
    :return:
        fraction of sonorities with voices in wrong order
    """
    score = 0
    for sonority in piece.sonorities:
        sonority_elements = convert_sonority_to_its_elements(
            sonority, piece.melodic_lines
        )
        for first, second in zip(sonority_elements, sonority_elements[1:]):
            if first.position_in_semitones >= second.position_in_semitones:
                score -= 1
                break
    score /= len(piece.sonorities)
    return score


def evaluate_conjunct_motion(
        piece: Piece, penalty_deduction_per_line: float,
        n_semitones_to_penalty: Dict[int, float]
) -> float:
    """
    Evaluate presence of coherent melodic lines that move without leaps.

    :param piece:
        `Piece` instance
    :param penalty_deduction_per_line:
        amount of leaps penalty that is deducted for each melodic line
    :param n_semitones_to_penalty:
        mapping from size of melodic interval in semitones to penalty for it
    :return:
        score between -1 and 0
    """
    score = 0
    for line in piece.melodic_lines:
        curr_score = 0
        for first, second in zip(line, line[1:]):
            melodic_interval = abs(
                first.position_in_semitones - second.position_in_semitones
            )
            curr_score -= n_semitones_to_penalty.get(melodic_interval, 1.0)
        curr_score = min(curr_score + penalty_deduction_per_line, 0)
        curr_score /= (len(line) - 1)
        score += curr_score
    score /= piece.n_voices
    return score


def compute_harmonic_stability_of_sonority(
        sonority_elements: List[PieceElement],
        n_semitones_to_stability: Dict[int, float]
) -> float:
    """
    Compute stability of sonority as average stability of intervals forming it.

    :param sonority_elements:
        simultaneously sounding pitches
    :param n_semitones_to_stability:
        mapping from interval size in semitones to its harmonic stability
    :return:
        stability of sonority (a number from 0 to 1)
    """
    stability = 0
    for first, second in combinations(sonority_elements, 2):
        interval_in_semitones = abs(
            first.position_in_semitones - second.position_in_semitones
        )
        interval_in_semitones %= N_SEMITONES_PER_OCTAVE
        stability += n_semitones_to_stability[interval_in_semitones]
    n_pairs = len(sonority_elements) * (len(sonority_elements) - 1) / 2
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
    for sonority in piece.sonorities:
        sonority_elements = convert_sonority_to_its_elements(
            sonority, piece.melodic_lines
        )
        stability_of_current_sonority = compute_harmonic_stability_of_sonority(
            sonority_elements, n_semitones_to_stability
        )
        sufficient_stability = min_stabilities[sonority.position_type]
        score += min(stability_of_current_sonority - sufficient_stability, 0)
    score /= len(piece.sonorities)
    return score


def compute_tonal_stability_of_sonority(
        sonority_elements: List[PieceElement],
        degree_to_stability: Dict[int, float]
) -> float:
    """
    Compute stability of sonority as average stability of pitches forming it.

    :param sonority_elements:
        simultaneously sounding pitches
    :param degree_to_stability:
        mapping from scale degree to its tonal stability
    :return:
        stability of sonority (a number from 0 to 1)
    """
    stability = sum(degree_to_stability[x.degree] for x in sonority_elements)
    stability /= len(sonority_elements)
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
    for sonority in piece.sonorities:
        sonority_elements = convert_sonority_to_its_elements(
            sonority, piece.melodic_lines
        )
        stability_of_current_sonority = compute_tonal_stability_of_sonority(
            sonority_elements, degree_to_stability
        )
        sufficient_stability = min_stabilities[sonority.position_type]
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
        'absence_of_voice_crossing': evaluate_absence_of_voice_crossing,
        'conjunct_motion': evaluate_conjunct_motion,
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
