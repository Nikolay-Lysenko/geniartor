"""
Evaluate a musical composition represented as a `Piece` instance.

Author: Nikolay Lysenko
"""


from itertools import combinations
from typing import Any, Callable, Dict, List, Tuple

from .piece import Piece, PieceElement


N_SEMITONES_PER_OCTAVE = 12


def evaluate_absence_of_large_intervals(
        piece: Piece, max_n_semitones: int = 16
) -> float:
    """
    Evaluate absence of too large harmonic intervals between adjacent voices.

    :param piece:
        musical piece
    :param max_n_semitones:
        maximum allowed interval in semitones between two
        simultaneously sounding pitches from adjacent voices
    :return:
        fraction of sonorities with large intervals multiplied by -1
    """
    score = 0
    for sonority in piece.sonorities:
        for first, second in zip(sonority.elements, sonority.elements[1:]):
            first_pos = first.position_in_semitones
            second_pos = second.position_in_semitones
            if abs(second_pos - first_pos) > max_n_semitones:
                score -= 1
                break
    score /= len(piece.sonorities)
    return score


def compute_rolling_extrema(
        values: List[float], window_size: int
) -> List[Tuple[float, float]]:
    """
    Compute rolling minima and rolling maxima.

    :param values:
        list of values to be aggregated
    :param window_size:
        size of rolling window
    :return:
        list of pairs of rolling extrema
    """
    results = []
    for k in range(window_size, len(values) + 1):
        window = values[(k - window_size):k]
        results.append((min(window), max(window)))
    return results


def evaluate_absence_of_narrow_ranges(
        piece: Piece, penalties: Dict[int, float], range_size: int = 9
) -> float:
    """
    Evaluate melodic fluency based on absence of stalling within narrow ranges.

    :param piece:
        musical piece
    :param penalties:
        mapping from width of a range (in scale degrees) to penalty
        applicable to ranges of not greater width
    :param range_size:
        size of ranges (in line elements) to be tested on narrowness
    :return:
        multiplied by -1 count of narrow ranges weighted based on their width
    """
    score = 0
    for melodic_line in piece.melodic_lines:
        pitches = [x.position_in_degrees for x in melodic_line]
        borders = compute_rolling_extrema(pitches, range_size)
        for lower_border, upper_border in borders:
            width = upper_border - lower_border
            curr_penalties = [v for k, v in penalties.items() if k >= width]
            penalty = max(curr_penalties) if curr_penalties else 0
            score -= penalty
    score /= len(piece.melodic_lines)
    return score


def evaluate_absence_of_parallel_intervals(
        piece: Piece, n_degrees_to_penalty: Dict[int, float]
) -> float:
    """
    Evaluate absence of parallel intervals such as parallel fifths or octaves.

    :param piece:
        musical piece
    :param n_degrees_to_penalty:
        mapping from size of parallel interval in degrees to penalty for it
    :return:
        average penalty over all pairs of successive sonorities
    """
    intervals = []
    for sonority in piece.sonorities:
        current_intervals = []
        zipped = zip(
            sonority.indices, sonority.indices[1:],
            sonority.elements, sonority.elements[1:]
        )
        for lower_index, upper_index, lower_element, upper_element in zipped:
            n_degrees = (
                upper_element.position_in_degrees
                - lower_element.position_in_degrees
            )
            interval_info = {
                'lower_index': lower_index,
                'upper_index': upper_index,
                'n_degrees': n_degrees,
            }
            current_intervals.append(interval_info)
        intervals.append(current_intervals)

    score = 0
    for first, second in zip(intervals, intervals[1:]):
        for first_info, second_info in zip(first, second):
            same_interval = first_info['n_degrees'] == second_info['n_degrees']
            other_lower_element = (
                first_info['lower_index'] != second_info['lower_index']
            )
            other_upper_element = (
                first_info['upper_index'] != second_info['upper_index']
            )
            if same_interval and other_lower_element and other_upper_element:
                score -= n_degrees_to_penalty.get(first_info['n_degrees'], 0)
    score /= len(piece.sonorities) - 1
    return score


def evaluate_absence_of_voice_crossing(piece: Piece) -> float:
    """
    Evaluate absence of voice crossing.

    :param piece:
        musical piece
    :return:
        fraction of sonorities with voices in wrong order multiplied by -1
    """
    score = 0
    for sonority in piece.sonorities:
        for first, second in zip(sonority.elements, sonority.elements[1:]):
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
    Evaluate presence of coherent melodic lines that move almost without leaps.

    :param piece:
        `musical piece
    :param penalty_deduction_per_line:
        amount of leaps penalty that is deducted for each melodic line
    :param n_semitones_to_penalty:
        mapping from size of melodic interval in semitones to penalty for it
    :return:
        average over voices penalty, a score between -1 and 0
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
    score /= len(piece.melodic_lines)
    return score


def evaluate_dominance_of_tertian_harmony(piece: Piece) -> float:
    """
    Evaluate dominance of sonorities based on interval of a third.

    :param piece:
        musical piece
    :return:
        fraction of non-tertian sonorities multiplied by -1
    """
    score = 0
    circle_of_thirds = [1, 3, 5, 7, 2, 4, 6]
    for sonority in piece.sonorities:
        degrees = [x.degree for x in sonority.elements]
        active_circle = [int(x in degrees) for x in circle_of_thirds]
        shifted_active_circle = [active_circle[-1]] + active_circle[:-1]
        zipped = zip(active_circle, shifted_active_circle)
        n_changes = len([(x, y) for x, y in zipped if x != y])
        if n_changes > 2:
            score -= 1
    score /= len(piece.sonorities)
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
        piece: Piece,
        min_stabilities: Dict[str, float],
        max_stabilities: Dict[str, float],
        n_semitones_to_stability: Dict[int, float]
) -> float:
    """
    Evaluate deviation of actual harmonic stability from its desired level.

    :param piece:
        musical piece
    :param min_stabilities:
        mapping from type of sonority's start position to minimum
        sufficient stability
    :param max_stabilities:
        mapping from type of sonority's start position to maximum
        desired stability
    :param n_semitones_to_stability:
        mapping from interval size in semitones to its harmonic stability
    :return:
        average over all sonorities deviation of stability from its ranges,
        a score between -1 and 0
    """
    score = 0
    for sonority in piece.sonorities:
        stability_of_current_sonority = compute_harmonic_stability_of_sonority(
            sonority.elements, n_semitones_to_stability
        )
        min_stability = min_stabilities[sonority.position_type]
        score += min(stability_of_current_sonority - min_stability, 0)
        max_stability = max_stabilities[sonority.position_type]
        score += min(max_stability - stability_of_current_sonority, 0)
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
        piece: Piece,
        min_stabilities: Dict[str, float],
        max_stabilities: Dict[str, float],
        degree_to_stability: Dict[int, float]
) -> float:
    """
    Evaluate deviation of actual tonal stability from its desired level.

    :param piece:
        musical piece
    :param min_stabilities:
        mapping from type of sonority's start position to minimum
        sufficient stability
    :param max_stabilities:
        mapping from type of sonority's start position to maximum
        desired stability
    :param degree_to_stability:
        mapping from scale degree to its tonal stability
    :return:
        average over all sonorities deviation of stability from its ranges,
        a score between -1 and 0
    """
    score = 0
    for sonority in piece.sonorities:
        stability_of_current_sonority = compute_tonal_stability_of_sonority(
            sonority.elements, degree_to_stability
        )
        min_stability = min_stabilities[sonority.position_type]
        score += min(stability_of_current_sonority - min_stability, 0)
        max_stability = max_stabilities[sonority.position_type]
        score += min(max_stability - stability_of_current_sonority, 0)
    score /= len(piece.sonorities)
    return score


def get_scoring_functions_registry() -> Dict[str, Callable]:
    """
    Get mapping from names of scoring functions to scoring functions.

    :return:
        registry of scoring functions
    """
    registry = {
        'absence_of_large_intervals': evaluate_absence_of_large_intervals,
        'absence_of_narrow_ranges': evaluate_absence_of_narrow_ranges,
        'absence_of_parallel_intervals': evaluate_absence_of_parallel_intervals,
        'absence_of_voice_crossing': evaluate_absence_of_voice_crossing,
        'conjunct_motion': evaluate_conjunct_motion,
        'dominance_of_tertian_harmony': evaluate_dominance_of_tertian_harmony,
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
        musical piece
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
