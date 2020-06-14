"""
Define data structures representing a musical piece.

Author: Nikolay Lysenko
"""


from typing import List

import numpy as np

from .music_theory import (
    ScaleElement,
    create_diatonic_scale,
    find_strong_beat_events,
    slice_scale,
)


class Piece:
    """A musical piece stored in multiple formats."""

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
        self.roll_shape = (len(self.pitches), len(self.sonorities_durations))
        self.strong_beats = find_strong_beat_events(self.sonorities_durations)

        self.raw_roll = None
        self.sonorities = None
        self.melodic_parts = None

    @property
    def __sonorities(self) -> List[List[ScaleElement]]:
        """
        Represent a piece as a list of sonorities.

        :return:
            list of sonorities
        """
        top_indices = np.argsort(self.raw_roll, axis=0)[-self.n_voices:, :]
        top_indices = np.sort(top_indices, axis=0)
        list_of_pitch_indices = top_indices.T.tolist()
        sonorities = [
            [self.pitches[pitch_index] for pitch_index in pitch_indices]
            for pitch_indices in list_of_pitch_indices
        ]
        return sonorities

    @property
    def __melodic_parts(self) -> List[List[ScaleElement]]:
        """
        Represent a piece as a list of melodic parts (voices).

        :return:
            list of voices
        """
        melodic_parts = []
        for i in range(self.n_voices):
            melodic_part = [sonority[i] for sonority in self.sonorities]
            melodic_parts.append(melodic_part)
        return melodic_parts

    def set_piece_content(self, raw_roll: np.ndarray) -> None:
        """
        Set piece content based on new value of `self.raw_roll`.

        :param raw_roll:
            new value for `self.raw_roll`
        :return:
            None
        """
        if raw_roll.shape != self.roll_shape:
            raise ValueError(
                f"Wrong shape: {raw_roll.shape}, expected: {self.roll_shape}."
            )
        self.raw_roll = raw_roll
        self.sonorities = self.__sonorities
        self.melodic_parts = self.__melodic_parts
