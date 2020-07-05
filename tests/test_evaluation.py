"""
Test `geniartor.evaluation` module.

Author: Nikolay Lysenko
"""


from typing import Dict, List, Tuple

import pytest

from geniartor.evaluation import (
    compute_rolling_extrema,
    evaluate_absence_of_large_intervals,
    evaluate_absence_of_narrow_ranges,
    evaluate_absence_of_parallel_intervals,
    evaluate_absence_of_voice_crossing,
    evaluate_conjunct_motion,
    evaluate_dominance_of_tertian_harmony,
    evaluate_harmonic_stability,
    evaluate_tonal_stability,
)
from geniartor.piece import Piece, PieceElement, ScaleElement, Sonority


@pytest.mark.parametrize(
    "values, window_size, expected",
    [
        (
            [0, 5, 2, 1, -3, 6, 4, 7],
            3,
            [(0, 5), (1, 5), (-3, 2), (-3, 6), (-3, 6), (4, 7)]
        ),
    ]
)
def test_compute_rolling_extrema(
        values: List[float], window_size: int,
        expected: List[Tuple[float, float]]
) -> None:
    """Test `compute_rolling_extrema` function."""
    result = compute_rolling_extrema(values, window_size)
    assert result == expected


@pytest.mark.parametrize(
    "piece, max_n_semitones, expected",
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
            # `max_n_semitones`
            5,
            # `expected`
            -0.75
        ),
    ]
)
def test_evaluate_absence_of_large_intervals(
        piece: Piece, max_n_semitones: int, expected: float
) -> None:
    """Test `evaluate_absence_of_large_intervals` function."""
    result = evaluate_absence_of_large_intervals(piece, max_n_semitones)
    assert result == expected


@pytest.mark.parametrize(
    "piece, penalties, min_size, expected",
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
            # `penalties`
            {1: 1, 2: 0.5},
            # `min_size`
            3,
            # `expected`
            -0.5
        ),
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
                        PieceElement('C4', 39, 23, 1, 0.0, 0.5),
                        PieceElement('D4', 41, 24, 2, 0.5, 0.5),
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
                            PieceElement('C4', 39, 23, 1, 0.0, 0.5),
                            PieceElement('C5', 51, 30, 1, 1.0, 1.0),
                        ],
                        [2, 1],
                        'downbeat'
                    ),
                    Sonority(
                        [
                            PieceElement('D4', 41, 24, 2, 0.5, 0.5),
                            PieceElement('C5', 51, 30, 1, 1.0, 1.0),
                        ],
                        [-1, -1],
                        'ending'
                    ),
                ]
            ),
            # `penalties`
            {1: 1, 2: 0.5},
            # `min_size`
            3,
            # `expected`
            -1.0
        ),
    ]
)
def test_evaluate_absence_of_narrow_ranges(
        piece: Piece, penalties: Dict[int, float], min_size: int,
        expected: float
) -> None:
    """Test `evaluate_absence_of_narrow_ranges` function."""
    result = evaluate_absence_of_narrow_ranges(piece, penalties, min_size)
    assert result == expected


@pytest.mark.parametrize(
    "piece, n_degrees_to_penalty, expected",
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
                        PieceElement('C4', 39, 23, 1, 0.5, 0.5),
                        PieceElement('E4', 43, 25, 3, 1.0, 0.5),
                        PieceElement('F4', 44, 26, 4, 1.5, 0.5),
                    ],
                    [
                        PieceElement('G4', 46, 27, 5, 0.0, 1.0),
                        PieceElement('B4', 50, 29, 7, 1.0, 1.0),
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
                            PieceElement('C4', 39, 23, 1, 0.5, 0.5),
                            PieceElement('G4', 46, 27, 5, 0.0, 1.0),
                        ],
                        [1, 0],
                        'middle'
                    ),
                    Sonority(
                        [
                            PieceElement('E4', 43, 25, 3, 1.0, 0.5),
                            PieceElement('B4', 50, 29, 7, 1.0, 1.0),
                        ],
                        [2, 1],
                        'downbeat'
                    ),
                    Sonority(
                        [
                            PieceElement('F4', 44, 26, 4, 1.5, 0.5),
                            PieceElement('B4', 50, 29, 7, 1.0, 1.0),
                        ],
                        [-1, -1],
                        'ending'
                    ),
                ]
            ),
            # `n_degrees_to_penalty`
            {4: 0.5, 7: 1.0},
            # `expected`
            -0.5 / 3
        ),
    ]
)
def test_evaluate_absence_of_parallel_intervals(
        piece: Piece, n_degrees_to_penalty: Dict[int, float], expected: float
) -> None:
    """Test `evaluate_absence_of_parallel_intervals` function."""
    result = evaluate_absence_of_parallel_intervals(
        piece, n_degrees_to_penalty
    )
    assert result == expected


@pytest.mark.parametrize(
    "piece, expected",
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
                        PieceElement('C4', 39, 23, 1, 1.0, 0.5),
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
                            PieceElement('C4', 39, 23, 1, 1.0, 1.0),
                        ],
                        [2, 1],
                        'downbeat'
                    ),
                    Sonority(
                        [
                            PieceElement('F4', 44, 26, 4, 1.5, 0.5),
                            PieceElement('C4', 39, 23, 1, 1.0, 1.0),
                        ],
                        [-1, -1],
                        'ending'
                    ),
                ]
            ),
            # `expected`
            -0.5
        ),
    ]
)
def test_evaluate_absence_of_voice_crossing(
        piece: Piece, expected: float
) -> None:
    """Test `evaluate_absence_of_voice_crossing` function."""
    result = evaluate_absence_of_voice_crossing(piece)
    assert result == expected


@pytest.mark.parametrize(
    "piece, penalty_deduction_per_line, n_semitones_to_penalty, expected",
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
            # `penalty_deduction_per_line`
            0.2,
            # `n_semitones_to_penalty`
            {
                0: 0.0, 1: 0.0, 2: 0.0, 3: 0.1, 4: 0.2, 5: 0.3, 6: 0.4,
                7: 0.5, 8: 0.6, 9: 0.7, 10: 0.8, 11: 0.9, 12: 1.0
            },
            # `expected`
            -0.05
        ),
    ]
)
def test_evaluate_conjunct_motion(
        piece: Piece, penalty_deduction_per_line: float,
        n_semitones_to_penalty: Dict[int, float], expected: float
) -> None:
    """Test `evaluate_conjunct_motion` function."""
    result = evaluate_conjunct_motion(
        piece, penalty_deduction_per_line, n_semitones_to_penalty
    )
    assert round(result, 8) == expected


@pytest.mark.parametrize(
    "piece, expected",
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
                        PieceElement('E4', 43, 25, 3, 1.0, 1.0),
                        PieceElement('G4', 46, 27, 5, 0.0, 1.0),
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
                            PieceElement('E4', 43, 25, 3, 1.0, 1.0),
                            PieceElement('G4', 46, 27, 5, 0.0, 1.0),
                        ],
                        [0, 0, 0],
                        'beginning'
                    ),
                    Sonority(
                        [
                            PieceElement('D4', 41, 24, 2, 0.5, 0.5),
                            PieceElement('E4', 43, 25, 3, 1.0, 1.0),
                            PieceElement('G4', 46, 27, 5, 0.0, 1.0),
                        ],
                        [1, 0, 0],
                        'middle'
                    ),
                    Sonority(
                        [
                            PieceElement('E4', 43, 25, 3, 1.0, 0.5),
                            PieceElement('G4', 46, 27, 5, 0.0, 1.0),
                            PieceElement('C5', 51, 30, 1, 1.0, 1.0),
                        ],
                        [2, 1, 1],
                        'downbeat'
                    ),
                    Sonority(
                        [
                            PieceElement('F4', 44, 26, 4, 1.5, 0.5),
                            PieceElement('G4', 46, 27, 5, 0.0, 1.0),
                            PieceElement('C5', 51, 30, 1, 1.0, 1.0),
                        ],
                        [-1, -1, -1],
                        'ending'
                    ),
                ]
            ),
            # `expected`
            -0.5
        ),
    ]
)
def test_evaluate_dominance_of_tertian_harmony(
        piece: Piece, expected: float
) -> None:
    """Test `evaluate_dominance_of_tertian_harmony` function."""
    result = evaluate_dominance_of_tertian_harmony(piece)
    assert result == expected


@pytest.mark.parametrize(
    "piece, min_stabilities, max_stabilities, n_semitones_to_stability, "
    "expected",
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
            # `min_stabilities`
            {
                'beginning': 0.5,
                'downbeat': 0.7,
                'middle': 0.5,
                'other': 0.3,
                'ending': 0.8,
            },
            # `max_stabilities`
            {
                'beginning': 0.8,
                'downbeat': 1.0,
                'middle': 0.9,
                'other': 0.7,
                'ending': 1.0,
            },
            # `n_semitones_to_stability`
            {
                0: 1.0, 1: 0.2, 2: 0.2, 3: 0.7, 4: 0.8, 5: 0.5,
                6: 0.0, 7: 0.9, 8: 0.6, 9: 0.6, 10: 0.2, 11: 0.2,
            },
            # `expected`
            -0.05
        ),
    ]
)
def test_evaluate_harmonic_stability(
        piece: Piece,
        min_stabilities: Dict[str, float],
        max_stabilities: Dict[str, float],
        n_semitones_to_stability: Dict[int, float],
        expected: float
) -> None:
    """Test `evaluate_harmonic_stability` function."""
    result = evaluate_harmonic_stability(
        piece, min_stabilities, max_stabilities, n_semitones_to_stability
    )
    assert round(result, 8) == expected


@pytest.mark.parametrize(
    "piece, min_stabilities, max_stabilities, degree_to_stability, expected",
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
            # `min_stabilities`
            {
                'beginning': 0.5,
                'downbeat': 0.7,
                'middle': 0.5,
                'other': 0.3,
                'ending': 0.8,
            },
            # `max_stabilities`
            {
                'beginning': 0.8,
                'downbeat': 1.0,
                'middle': 0.9,
                'other': 0.7,
                'ending': 1.0,
            },
            # `degree_to_stability`
            {1: 1.0, 2: 0.4, 3: 0.7, 4: 0.4, 5: 0.8, 6: 0.4, 7: 0.0},
            # `expected`
            -0.05
        ),
    ]
)
def test_evaluate_tonal_stability(
        piece: Piece,
        min_stabilities: Dict[str, float],
        max_stabilities: Dict[str, float],
        degree_to_stability: Dict[int, float],
        expected: float
) -> None:
    """Test `evaluate_tonal_stability` function."""
    result = evaluate_tonal_stability(
        piece, min_stabilities, max_stabilities, degree_to_stability
    )
    assert round(result, 8) == expected
