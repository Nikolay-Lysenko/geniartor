"""
Help to work with notions from music theory.

Author: Nikolay Lysenko
"""


from typing import List, NamedTuple

from sinethesizer.io.utils import get_note_to_position_mapping


NOTE_TO_POSITION = get_note_to_position_mapping()


class ScaleElement(NamedTuple):
    """A pitch from a scale."""
    note: str
    position_in_semitones: int
    position_in_degrees: int
    degree: int


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
