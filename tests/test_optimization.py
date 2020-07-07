"""
Test `geniartor.optimization` package.

Author: Nikolay Lysenko
"""


from typing import Any, Dict, List

import pytest

from geniartor.optimization import (
    run_variable_neighborhood_search,
    set_new_values_for_sonority
)
from geniartor.piece import Piece, PieceElement, ScaleElement, Sonority


@pytest.mark.parametrize(
    "piece, evaluation_params, "
    "n_passes, fraction_to_try, perturbation_probability",
    [
        (
            # `piece`
            Piece(
                n_measures=2,
                pitches=[
                    ScaleElement('C4', 39, 23, 1),
                    ScaleElement('D4', 41, 24, 2),
                    ScaleElement('E4', 43, 25, 3),
                    ScaleElement('F4', 44, 26, 4),
                    ScaleElement('G4', 46, 27, 5),
                    ScaleElement('A4', 48, 28, 6),
                    ScaleElement('B4', 50, 29, 7),
                    ScaleElement('C5', 51, 30, 1),
                ],
                melodic_lines=[
                    [
                        PieceElement('C4', 39, 23, 1, 0.0, 0.5),
                        PieceElement('D4', 41, 24, 2, 0.5, 0.5),
                        PieceElement('E4', 43, 25, 3, 1.0, 0.5),
                        PieceElement('F4', 44, 26, 4, 1.5, 0.5),
                    ],
                    [
                        PieceElement('G4', 46, 27, 5, 0.0, 1.0),
                        PieceElement('C5', 51, 30, 1, 1.0, 1.0),
                    ],
                ],
                sonorities=[
                    Sonority(
                        [
                            PieceElement('C4', 39, 23, 1, 0.0, 0.5),
                            PieceElement('G4', 46, 27, 5, 0.0, 1.0),
                        ],
                        [0, 0],
                        'beginning'
                    ),
                    Sonority(
                        [
                            PieceElement('D4', 41, 24, 2, 0.5, 0.5),
                            PieceElement('G4', 46, 27, 5, 0.0, 1.0),
                        ],
                        [1, 0],
                        'middle'
                    ),
                    Sonority(
                        [
                            PieceElement('E4', 43, 25, 3, 1.0, 0.5),
                            PieceElement('C5', 51, 30, 1, 1.0, 1.0),
                        ],
                        [2, 1],
                        'downbeat'
                    ),
                    Sonority(
                        [
                            PieceElement('F4', 44, 26, 4, 1.5, 0.5),
                            PieceElement('C5', 51, 30, 1, 1.0, 1.0),
                        ],
                        [-1, -1],
                        'ending'
                    ),
                ]
            ),
            # `evaluation_params`
            {
                'scoring_coefs': {
                    'harmonic_stability': 1
                },
                'scoring_fn_params': {
                    'harmonic_stability': {
                        'min_stabilities': {
                            'beginning': 0.8,
                            'ending': 0.9,
                            'downbeat': 0.75,
                            'middle': 0.5,
                            'other': 0.25,
                        },
                        'max_stabilities': {
                            'beginning': 1.0,
                            'ending': 1.0,
                            'downbeat': 1.0,
                            'middle': 0.9,
                            'other': 0.8,
                        },
                        'n_semitones_to_stability': {
                            0: 1.0,
                            1: 0.2,
                            2: 0.2,
                            3: 0.7,
                            4: 0.8,
                            5: 0.5,
                            6: 0.0,
                            7: 0.9,
                            8: 0.6,
                            9: 0.6,
                            10: 0.2,
                            11: 0.2,
                        }
                    }
                }
            },
            # `n_passes`
            10,
            # `fraction_to_try`
            0.9,
            # `perturbation_probability`
            0.5
        ),
    ]
)
def test_run_variable_neighborhood_search(
        piece: Piece, evaluation_params: Dict[str, Any],
        n_passes: int, fraction_to_try: float, perturbation_probability: float
) -> None:
    """Test `run_variable_neighborhood_search` function."""
    run_variable_neighborhood_search(
        piece, evaluation_params,
        n_passes, fraction_to_try, perturbation_probability
    )


@pytest.mark.parametrize(
    "piece, sonority_position, new_values, expected",
    [
        (
            # `piece`
            Piece(
                n_measures=2,
                pitches=[
                    ScaleElement('C4', 39, 23, 1),
                    ScaleElement('D4', 41, 24, 2),
                    ScaleElement('E4', 43, 25, 3),
                    ScaleElement('F4', 44, 26, 4),
                    ScaleElement('G4', 46, 27, 5),
                    ScaleElement('A4', 48, 28, 6),
                    ScaleElement('B4', 50, 29, 7),
                    ScaleElement('C5', 51, 30, 1),
                ],
                melodic_lines=[
                    [
                        PieceElement('C4', 39, 23, 1, 0.0, 0.5),
                        PieceElement('D4', 41, 24, 2, 0.5, 0.5),
                        PieceElement('E4', 43, 25, 3, 1.0, 0.5),
                        PieceElement('F4', 44, 26, 4, 1.5, 0.5),
                    ],
                    [
                        PieceElement('G4', 46, 27, 5, 0.0, 1.0),
                        PieceElement('C5', 51, 30, 1, 1.0, 1.0),
                    ],
                ],
                sonorities=[
                    Sonority(
                        [
                            PieceElement('C4', 39, 23, 1, 0.0, 0.5),
                            PieceElement('G4', 46, 27, 5, 0.0, 1.0),
                        ],
                        [0, 0],
                        'beginning'
                    ),
                    Sonority(
                        [
                            PieceElement('D4', 41, 24, 2, 0.5, 0.5),
                            PieceElement('G4', 46, 27, 5, 0.0, 1.0),
                        ],
                        [1, 0],
                        'middle'
                    ),
                    Sonority(
                        [
                            PieceElement('E4', 43, 25, 3, 1.0, 0.5),
                            PieceElement('C5', 51, 30, 1, 1.0, 1.0),
                        ],
                        [2, 1],
                        'downbeat'
                    ),
                    Sonority(
                        [
                            PieceElement('F4', 44, 26, 4, 1.5, 0.5),
                            PieceElement('C5', 51, 30, 1, 1.0, 1.0),
                        ],
                        [-1, -1],
                        'ending'
                    ),
                ]
            ),
            # `sonority_position`
            1,
            # `new_values`
            [ScaleElement('B3', 38, 22, 7), ScaleElement('G5', 58, 34, 5)],
            # `expected`
            Piece(
                n_measures=2,
                pitches=[
                    ScaleElement('C4', 39, 23, 1),
                    ScaleElement('D4', 41, 24, 2),
                    ScaleElement('E4', 43, 25, 3),
                    ScaleElement('F4', 44, 26, 4),
                    ScaleElement('G4', 46, 27, 5),
                    ScaleElement('A4', 48, 28, 6),
                    ScaleElement('B4', 50, 29, 7),
                    ScaleElement('C5', 51, 30, 1),
                ],
                melodic_lines=[
                    [
                        PieceElement('C4', 39, 23, 1, 0.0, 0.5),
                        PieceElement('B3', 38, 22, 7, 0.5, 0.5),
                        PieceElement('E4', 43, 25, 3, 1.0, 0.5),
                        PieceElement('F4', 44, 26, 4, 1.5, 0.5),
                    ],
                    [
                        PieceElement('G5', 58, 34, 5, 0.0, 1.0),
                        PieceElement('C5', 51, 30, 1, 1.0, 1.0),
                    ],
                ],
                sonorities=[
                    Sonority(
                        [
                            PieceElement('C4', 39, 23, 1, 0.0, 0.5),
                            PieceElement('G5', 58, 34, 5, 0.0, 1.0),
                        ],
                        [0, 0],
                        'beginning'
                    ),
                    Sonority(
                        [
                            PieceElement('B3', 38, 22, 7, 0.5, 0.5),
                            PieceElement('G5', 58, 34, 5, 0.0, 1.0),
                        ],
                        [1, 0],
                        'middle'
                    ),
                    Sonority(
                        [
                            PieceElement('E4', 43, 25, 3, 1.0, 0.5),
                            PieceElement('C5', 51, 30, 1, 1.0, 1.0),
                        ],
                        [2, 1],
                        'downbeat'
                    ),
                    Sonority(
                        [
                            PieceElement('F4', 44, 26, 4, 1.5, 0.5),
                            PieceElement('C5', 51, 30, 1, 1.0, 1.0),
                        ],
                        [-1, -1],
                        'ending'
                    ),
                ]
            ),
        ),
    ]
)
def test_set_new_values_for_sonority(
        piece: Piece,
        sonority_position: int,
        new_values: List[ScaleElement],
        expected: Piece
) -> None:
    """Test `set_new_values_for_sonority` function."""
    set_new_values_for_sonority(piece, sonority_position, new_values)
    assert piece == expected
