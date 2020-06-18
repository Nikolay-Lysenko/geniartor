"""
Define data structure representing a musical piece.

Author: Nikolay Lysenko
"""


import random
from typing import List

from .music_theory import (
    create_diatonic_scale,
    slice_scale,
)


class Piece:
    """A musical piece with plain texture and without chromaticism."""

    def __init__(
            self,
            tonic: str,
            scale_type: str,
            n_voices: int,
            lowest_note: str,
            highest_note: str,
            sonorities_durations: List[float]
    ):
        """
        Initialize instance.

        :param tonic:
            tonic pitch class represented by letter (like C or A#)
        :param scale_type:
            type of scale (currently, 'major', 'natural_minor', and
            'harmonic_minor' are supported)
        :param n_voices:
            number of voices (parts, melodic lines)
        :param lowest_note:
            lowest available note (like C4)
        :param highest_note:
            highest available note (like C6)
        :param sonorities_durations:
            durations of sonorities (simultaneously starting and ending notes)
            in fractions of whole measure
        """
        self.tonic = tonic
        self.scale_type = scale_type
        self.n_voices = n_voices
        self.lowest_note = lowest_note
        self.highest_note = highest_note
        self.sonorities_durations = sonorities_durations

        scale = create_diatonic_scale(self.tonic, self.scale_type)
        self.pitches = slice_scale(scale, self.lowest_note, self.highest_note)
        self.sonorities = [
            sorted(
                random.sample(self.pitches, self.n_voices),
                key=lambda x: x.position_in_semitones
            )
            for _ in self.sonorities_durations
        ]
