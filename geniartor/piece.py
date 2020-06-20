"""
Define data structure representing a musical piece.

Author: Nikolay Lysenko
"""


import random
from itertools import accumulate
from math import floor
from typing import Dict, List, NamedTuple, Tuple

from sinethesizer.io.utils import get_note_to_position_mapping


NOTE_TO_POSITION = get_note_to_position_mapping()


class ScaleElement(NamedTuple):
    """A pitch from a scale."""
    note: str
    position_in_semitones: int
    position_in_degrees: int
    degree: int


class PieceElement(NamedTuple):
    """An element of a musical piece."""
    note: str
    position_in_semitones: int
    position_in_degrees: int
    degree: int
    start_time: float
    duration: float


class Sonority(NamedTuple):
    """Simultaneously sounding pitches."""
    start_time: float
    position_type: str
    indices: List[int]


class Piece(NamedTuple):
    """A musical piece based on diatonic scale."""
    n_voices: int
    pitches: List[ScaleElement]
    melodic_lines: List[List[PieceElement]]
    sonorities: List[Sonority]


def create_diatonic_scale(tonic: str, scale_type: str) -> List[ScaleElement]:
    """
    Create scale elements list sorted by their pitch.

    :param tonic:
        tonic pitch class represented by letter (like C or A#)
    :param scale_type:
        type of scale (currently, 'major', 'natural_minor', and
        'harmonic_minor' are supported)
    :return:
        diatonic scale
    """
    patterns = {
        'major': [1, None, 2, None, 3, 4, None, 5, None, 6, None, 7],
        'natural_minor': [1, None, 2, 3, None, 4, None, 5, 6, None, 7, None],
        'harmonic_minor': [1, None, 2, 3, None, 4, None, 5, 6, None, None, 7],
    }
    pattern = patterns[scale_type]
    tonic_position = NOTE_TO_POSITION[tonic + '1']
    elements = []
    position_in_degrees = 0
    for note, position_in_semitones in NOTE_TO_POSITION.items():
        remainder = (position_in_semitones - tonic_position) % len(pattern)
        degree = pattern[remainder]
        if degree is not None:
            element = ScaleElement(
                note=note,
                position_in_semitones=position_in_semitones,
                position_in_degrees=position_in_degrees,
                degree=degree
            )
            elements.append(element)
            position_in_degrees += 1
    return elements


def slice_scale(
        scale: List[ScaleElement], lowest_note: str, highest_note: str
) -> List[ScaleElement]:
    """
    Slice scale.

    :param scale:
        scale
    :param lowest_note:
        lowest note to keep (inclusively)
    :param highest_note:
        highest note to keep (inclusively)
    """
    min_pos = NOTE_TO_POSITION[lowest_note]
    max_pos = NOTE_TO_POSITION[highest_note]
    res = [x for x in scale if min_pos <= x.position_in_semitones <= max_pos]
    return res


def select_appropriate_durations(
        current_time: float, total_time: float,
        current_rhythm: List[float], valid_rhythmic_patterns: List[List[float]]
) -> List[float]:
    """"""
    all_durations = [0.125, 0.25, 0.5, 1.0]
    appropriate_durations = []
    for duration in all_durations:
        if current_time + duration > total_time:
            continue
        extended_rhythm = current_rhythm + [duration]
        for valid_pattern in valid_rhythmic_patterns:
            if valid_pattern[:len(extended_rhythm)] == extended_rhythm:
                appropriate_durations.append(duration)
                break
    return appropriate_durations


def generate_line_durations(
        n_measures: int,
        duration_weights: Dict[float, float],
        valid_rhythmic_patterns: List[List[float]],
        end_with_whole_note: bool = True
) -> List[float]:
    """"""
    current_time = 0
    rhythm = []
    current_rhythm = []
    total_time = n_measures - int(end_with_whole_note)

    while current_time < total_time:
        appropriate_durations = select_appropriate_durations(
            current_time, total_time, current_rhythm, valid_rhythmic_patterns
        )
        duration = random.choices(
            appropriate_durations,
            [duration_weights[x] for x in appropriate_durations]
        )

        current_time += duration

        extended_rhythm = sum(current_rhythm) + duration
        if extended_rhythm < 1:
            current_rhythm.append(duration)
        elif extended_rhythm == 1:
            current_rhythm = []
        else:
            syncopated_duration = extended_rhythm - 1
            current_rhythm = [syncopated_duration]

        rhythm.append(duration)

    if end_with_whole_note:
        rhythm.append(1.0)
    return rhythm


def generate_random_line(
        n_measures: int,
        duration_weights: Dict[float, float],
        valid_rhythmic_patterns: List[List[float]],
        pitches: List[ScaleElement]
) -> Tuple[List[float], List[PieceElement]]:
    """"""
    line_durations = generate_line_durations(
        n_measures, duration_weights, valid_rhythmic_patterns
    )

    melodic_line = []
    current_time = 0
    for duration in line_durations:
        scale_element = random.choice(pitches)
        piece_element = PieceElement(
            start_time=current_time,
            duration=duration,
            **scale_element
        )
        melodic_line.append(piece_element)
        current_time += duration

    return line_durations, melodic_line


def find_sonorities(
        lines_durations: List[List[float]],
        melodic_lines: List[List[PieceElement]]
) -> List[Sonority]:
    """"""
    start_times_with_duplicates = sum(accumulate(x) for x in lines_durations)
    start_times = sorted(list(set(start_times_with_duplicates)))
    indices_in_lines = [0 for _ in melodic_lines]
    initial_sonority = Sonority(
        start_time=0,
        position_type='beginning',
        indices=indices_in_lines
    )
    sonorities = [initial_sonority]
    types = {0.0: 'downbeat', 0.5: 'middle'}
    for start_time in start_times[1:-1]:
        position_type = types.get(start_time - floor(start_time), 'other')
        indices_in_lines = [
            index + 1
            if melodic_line[index + 1].start_time >= start_time
            else index
            for index, melodic_line in zip(indices_in_lines, melodic_lines)
        ]
        sonority = Sonority(start_time, position_type, indices_in_lines)
        sonorities.append(sonority)
    last_sonority = Sonority(
        start_time=start_times[-1],
        position_type='ending',
        indices=[-1 for _ in melodic_lines]
    )
    sonorities.append(last_sonority)
    return sonorities


def convert_sonority_to_its_elements(
        sonority: Sonority,
        melodic_lines: List[List[PieceElement]]
) -> List[PieceElement]:
    """"""
    sonority_as_elements = [
        melodic_line[index]
        for melodic_line, index in zip(melodic_lines, sonority.indices)
    ]
    return sonority_as_elements


def generate_random_piece(
        tonic: str,
        scale_type: str,
        lowest_note: str,
        highest_note: str,
        n_voices: int,
        n_measures: int,
        duration_weights: Dict[float, float],
        valid_rhythmic_patterns: List[List[float]]
) -> Piece:
    """
    Generate random piece.

    :param tonic:
        tonic pitch class represented by letter (like C or A#)
    :param scale_type:
        type of scale (currently, 'major', 'natural_minor', and
        'harmonic_minor' are supported)
    :param lowest_note:
        lowest available note (like C4)
    :param highest_note:
        highest available note (like C6)
    :param n_voices:
        number of voices (parts, melodic lines)
    :param n_measures:
        duration of piece in measures
    :param duration_weights:
        mapping of line element duration to weight of its random selection
    :param valid_rhythmic_patterns:
        all valid ways to split measure span into spans of its notes;
        durations of tied over bar notes are included without clipping
    """
    scale = create_diatonic_scale(tonic, scale_type)
    pitches = slice_scale(scale, lowest_note, highest_note)
    lines_durations = []
    melodic_lines = []
    for _ in range(n_voices):
        line_durations, melodic_line = generate_random_line(
            n_measures, duration_weights, valid_rhythmic_patterns, pitches
        )
        lines_durations.append(line_durations)
        melodic_lines.append(melodic_line)
    sonorities = find_sonorities(lines_durations, melodic_lines)
    piece = Piece(n_voices, pitches, melodic_lines, sonorities)
    return piece
