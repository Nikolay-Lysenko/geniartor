"""
Define data structure representing a musical piece.

Author: Nikolay Lysenko
"""


import random
from math import floor
from typing import Dict, List, NamedTuple, Optional

from sinethesizer.io.utils import get_note_to_position_mapping


NOTE_TO_POSITION = get_note_to_position_mapping()


class ScaleElement(NamedTuple):
    """A pitch from a diatonic scale."""
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
    elements: List[PieceElement]
    indices: List[int]
    position_type: str


class Piece(NamedTuple):
    """A musical piece based on a diatonic scale."""
    n_measures: int
    pitches: List[ScaleElement]
    melodic_lines: List[List[PieceElement]]
    sonorities: List[Sonority]


def update_current_measure_durations(
        current_measure_durations: List[float], next_duration: float
) -> List[float]:
    """
    Update a list of notes durations from a measure in progress.

    :param current_measure_durations:
        durations of notes (in fractions of whole measure)
        from start of the measure to the last added duration
    :param next_duration:
        duration of the next note (in fractions of whole measure)
    :return:
        list of notes durations from the current measure if it is still
        unfinished or list of notes durations from the next measure
    """
    duration_of_one_measure = 1
    extended_duration = sum(current_measure_durations) + next_duration
    if extended_duration < duration_of_one_measure:
        current_measure_durations.append(next_duration)
    elif extended_duration == duration_of_one_measure:
        current_measure_durations = []
    else:
        syncopated_duration = extended_duration - duration_of_one_measure
        current_measure_durations = [syncopated_duration]
    return current_measure_durations


def validate_line_durations(
        line_durations: Optional[List[float]],
        valid_rhythmic_patterns: List[List[float]],
        n_measures: int
) -> None:
    """
    Check that line has proper total duration and has valid rhythmic patterns.

    :param line_durations:
        durations of all notes from the line from its start to its finish
        (in fractions of whole measure)
    :param valid_rhythmic_patterns:
        list of all valid ways to split a measure duration into durations of
        its notes; every note duration must be given in fractions of measure
    :param n_measures:
        required duration of the line (in measures)
    :return:
        None
    """
    if line_durations is None:
        return
    total_time = 0
    current_measure_durations = []
    for duration in line_durations:
        extended_durations = current_measure_durations + [duration]
        is_valid = any(
            valid_pattern[:len(extended_durations)] == extended_durations
            for valid_pattern in valid_rhythmic_patterns
        )
        if not is_valid:
            raise ValueError(
                f"Disallowed rhythmic pattern found: {extended_durations}."
            )
        total_time += duration
        current_measure_durations = update_current_measure_durations(
            current_measure_durations, duration
        )
    if total_time != n_measures:
        raise ValueError(
            f"Line lasts {total_time} measures, "
            f"but {n_measures} measures are needed."
        )


def validate_rhythm_arguments(
        lines_durations: List[Optional[List[float]]],
        valid_rhythmic_patterns: List[List[float]],
        n_measures: int,
        duration_weights: Optional[Dict[float, float]] = None
) -> None:
    """
    Check that arguments defining rhythm of a piece to be created, are valid.

    :param lines_durations:
        durations of notes (in fractions of whole measure) for each line;
        some of them may be `None`
    :param valid_rhythmic_patterns:
        list of all valid ways to split a measure duration into durations of
        its notes; every note duration must be given in fractions of measure
    :param n_measures:
        duration of a piece (in measures)
    :param duration_weights:
        mapping of line element duration to weight for its random selection
    :return:
        None
    """
    if duration_weights is None and any(x is None for x in lines_durations):
        raise ValueError(
            "If `duration_weights` are not passed, "
            "no elements of `lines_durations` can be `None`."
        )
    for line_durations in lines_durations:
        validate_line_durations(
            line_durations, valid_rhythmic_patterns, n_measures
        )


def select_appropriate_durations(
        current_time: float,
        total_time: float,
        current_measure_durations: List[float],
        valid_rhythmic_patterns: List[List[float]]
) -> List[float]:
    """
    Find all options to continue rhythm of unfinished measure one note ahead.

    :param current_time:
        total duration of all previous notes
    :param total_time:
        required total time of all notes to be generated
    :param current_measure_durations:
        durations of notes (in fractions of whole measure)
        from start of the measure to the last added duration
    :param valid_rhythmic_patterns:
        list of all valid ways to split a measure duration into durations of
        its notes; every note duration must be given in fractions of measure
    :return:
        all possible durations of the next note
    """
    all_durations = [0.125, 0.25, 0.5, 1.0]
    appropriate_durations = []
    for duration in all_durations:
        if current_time + duration > total_time:
            continue
        extended_durations = current_measure_durations + [duration]
        for valid_pattern in valid_rhythmic_patterns:
            if valid_pattern[:len(extended_durations)] == extended_durations:
                appropriate_durations.append(duration)
                break
    return appropriate_durations


def generate_line_durations(
        n_measures: int,
        duration_weights: Dict[float, float],
        valid_rhythmic_patterns: List[List[float]],
        end_with_whole_note: bool = True
) -> List[float]:
    """
    Generate duration of notes from a line at random.

    :param n_measures:
        total duration of a line (in measures)
    :param duration_weights:
        mapping of line element duration to weight for its random selection
    :param valid_rhythmic_patterns:
        list of all valid ways to split a measure duration into durations of
        its notes; every note duration must be given in fractions of measure
    :param end_with_whole_note:
        if it is set to `True`, it is guaranteed that line is ended with a
        whole note; if it is set to `False`, line can end with a whole note
        by chance
    :return:
        durations of all line notes (in fractions of whole measure)
    """
    current_time = 0
    line_durations = []
    current_measure_durations = []
    total_time = n_measures - int(end_with_whole_note)

    while current_time < total_time:
        appropriate_durations = select_appropriate_durations(
            current_time, total_time, current_measure_durations,
            valid_rhythmic_patterns
        )
        duration = random.choices(
            appropriate_durations,
            [duration_weights[x] for x in appropriate_durations]
        )[0]
        current_time += duration
        current_measure_durations = update_current_measure_durations(
            current_measure_durations, duration
        )
        line_durations.append(duration)

    if end_with_whole_note:
        line_durations.append(1.0)
    return line_durations


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
    :return:
        sliced scale
    """
    min_pos = NOTE_TO_POSITION[lowest_note]
    max_pos = NOTE_TO_POSITION[highest_note]
    res = [x for x in scale if min_pos <= x.position_in_semitones <= max_pos]
    return res


def generate_random_line(
        line_durations: List[float],
        pitches: List[ScaleElement]
) -> List[PieceElement]:
    """
    Generate line at random given its rhythm.

    :param line_durations:
        durations of all notes from the line from its start to its finish
        (in fractions of whole measure)
    :param pitches:
        all pitches available in a piece
    :return:
        melodic line
    """
    melodic_line = []
    current_time = 0
    for duration in line_durations:
        scale_element = random.choice(pitches)
        piece_element = PieceElement(
            note=scale_element.note,
            position_in_semitones=scale_element.position_in_semitones,
            position_in_degrees=scale_element.position_in_degrees,
            degree=scale_element.degree,
            start_time=current_time,
            duration=duration
        )
        melodic_line.append(piece_element)
        current_time += duration
    return melodic_line


def get_elements_by_indices(
        indices: List[int],
        melodic_lines: List[List[PieceElement]]
) -> List[PieceElement]:
    """
    Get elements of piece by their positions in melodic lines.

    :param indices:
        positions of piece elements
    :param melodic_lines:
        lists of successive piece elements
    :return:
        piece elements
    """
    elements = [
        melodic_line[index]
        for melodic_line, index in zip(melodic_lines, indices)
    ]
    return elements


def find_sonorities(
        melodic_lines: List[List[PieceElement]],
        custom_position_types: Optional[Dict[float, str]] = None
) -> List[Sonority]:
    """
    Find all simultaneously sounding pitches.

    :param melodic_lines:
        lists of successive piece elements
    :param custom_position_types:
        mapping from start time of sonority to its user-defined type
    :return:
        all simultaneously sounding pitches found in a piece
    """
    all_lines_start_times = [
        [x.start_time for x in melodic_line]
        for melodic_line in melodic_lines
    ]
    flat_start_times = [
        x
        for line_start_times in all_lines_start_times
        for x in line_start_times
    ]
    unique_start_times = sorted(list(set(flat_start_times)))
    indices_in_lines = [0 for _ in melodic_lines]
    initial_sonority = Sonority(
        elements=get_elements_by_indices(indices_in_lines, melodic_lines),
        indices=indices_in_lines,
        position_type='beginning',
    )
    sonorities = [initial_sonority]
    custom_position_types = custom_position_types or {}
    core_position_types = {0.0: 'downbeat', 0.5: 'middle'}
    for start_time in unique_start_times[1:-1]:
        position_type = custom_position_types.get(
            start_time,
            core_position_types.get(start_time - floor(start_time), 'other')
        )
        zipped = zip(indices_in_lines, all_lines_start_times)
        indices_in_lines = [
            index + 1
            if line_start_times[index + 1] <= start_time
            else index
            for index, line_start_times in zipped
        ]
        sonority = Sonority(
            get_elements_by_indices(indices_in_lines, melodic_lines),
            indices_in_lines,
            position_type
        )
        sonorities.append(sonority)
    last_indices = [-1 for _ in melodic_lines]
    last_sonority = Sonority(
        elements=get_elements_by_indices(last_indices, melodic_lines),
        indices=last_indices,
        position_type='ending',
    )
    sonorities.append(last_sonority)
    return sonorities


def generate_random_piece(
        tonic: str,
        scale_type: str,
        lowest_note: str,
        highest_note: str,
        n_measures: int,
        valid_rhythmic_patterns: List[List[float]],
        lines_durations: List[Optional[List[float]]],
        duration_weights: Optional[Dict[float, float]] = None,
        custom_position_types: Optional[Dict[float, str]] = None
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
    :param n_measures:
        duration of piece in measures
    :param valid_rhythmic_patterns:
        all valid ways to split measure span into spans of its notes;
        durations of tied over bar notes are included without clipping
    :param lines_durations:
        durations of notes (in fractions of whole measure) for each line;
        there can be `None` values for some line, if so, durations for them
        are generated at random
    :param duration_weights:
        mapping of line element duration to weight for its random selection
    :param custom_position_types:
        mapping from start time of sonority to its user-defined type
    """
    validate_rhythm_arguments(
        lines_durations, valid_rhythmic_patterns, n_measures, duration_weights
    )
    for index, line_duration in enumerate(lines_durations):
        if line_duration is None:
            lines_durations[index] = generate_line_durations(
                n_measures, duration_weights, valid_rhythmic_patterns
            )
    scale = create_diatonic_scale(tonic, scale_type)
    pitches = slice_scale(scale, lowest_note, highest_note)
    melodic_lines = []
    for line_durations in lines_durations:
        melodic_line = generate_random_line(line_durations, pitches)
        melodic_lines.append(melodic_line)
    sonorities = find_sonorities(melodic_lines, custom_position_types)
    piece = Piece(n_measures, pitches, melodic_lines, sonorities)
    return piece
