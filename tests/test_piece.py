"""
Test `geniartor.piece` module.

Author: Nikolay Lysenko
"""


from typing import Dict, List, Optional, Tuple

import pytest

from geniartor.piece import (
    PieceElement,
    ScaleElement,
    Sonority,
    create_diatonic_scale,
    find_sonorities,
    generate_line_durations,
    generate_random_piece,
    get_elements_by_indices,
    select_appropriate_durations,
    slice_scale,
    update_current_measure_durations,
    validate_line_durations,
    validate_rhythm_arguments,
)


@pytest.mark.parametrize(
    "tonic, scale_type, n_elements_to_take, expected",
    [
        (
            'C',
            'major',
            7,
            [(0, 6), (2, 7), (3, 1), (5, 2), (7, 3), (8, 4), (10, 5)]
        ),
        (
            'C',
            'natural_minor',
            7,
            [(1, 7), (3, 1), (5, 2), (6, 3), (8, 4), (10, 5), (11, 6)]
        ),
    ]
)
def test_create_diatonic_scale(
        tonic: str, scale_type: str, n_elements_to_take: int,
        expected: List[Tuple[int, int]]
) -> None:
    """Test that `elements` attribute is properly filled."""
    scale = create_diatonic_scale(tonic, scale_type)
    result = [
        (x.position_in_semitones, x.degree)
        for x in scale[:n_elements_to_take]
    ]
    assert result == expected


@pytest.mark.parametrize(
    "melodic_lines, custom_position_types, expected",
    [
        (
            # `melodic_lines`
            [
                [
                    PieceElement('C4', 39, 23, 1, 0.0, 0.25),
                    PieceElement('C4', 39, 23, 1, 0.25, 0.125),
                    PieceElement('C4', 39, 23, 1, 0.375, 0.125),
                    PieceElement('C4', 39, 23, 1, 0.5, 0.25),
                    PieceElement('C4', 39, 23, 1, 0.75, 0.25),
                ],
                [
                    PieceElement('C4', 39, 23, 1, 0.0, 0.5),
                    PieceElement('C4', 39, 23, 1, 0.5, 0.25),
                    PieceElement('C4', 39, 23, 1, 0.75, 0.125),
                    PieceElement('C4', 39, 23, 1, 0.875, 0.125),
                ]
            ],
            # `custom_position_types`
            {0.75: 'custom'},
            # `expected`
            [
                Sonority(
                    [
                        PieceElement('C4', 39, 23, 1, 0.0, 0.25),
                        PieceElement('C4', 39, 23, 1, 0.0, 0.5),
                    ],
                    [0, 0],
                    'beginning'
                ),
                Sonority(
                    [
                        PieceElement('C4', 39, 23, 1, 0.25, 0.125),
                        PieceElement('C4', 39, 23, 1, 0.0, 0.5),
                    ],
                    [1, 0],
                    'other'
                ),
                Sonority(
                    [
                        PieceElement('C4', 39, 23, 1, 0.375, 0.125),
                        PieceElement('C4', 39, 23, 1, 0.0, 0.5),
                    ],
                    [2, 0],
                    'other'
                ),
                Sonority(
                    [
                        PieceElement('C4', 39, 23, 1, 0.5, 0.25),
                        PieceElement('C4', 39, 23, 1, 0.5, 0.25),
                    ],
                    [3, 1],
                    'middle'
                ),
                Sonority(
                    [
                        PieceElement('C4', 39, 23, 1, 0.75, 0.25),
                        PieceElement('C4', 39, 23, 1, 0.75, 0.125),
                    ],
                    [4, 2],
                    'custom'
                ),
                Sonority(
                    [
                        PieceElement('C4', 39, 23, 1, 0.75, 0.25),
                        PieceElement('C4', 39, 23, 1, 0.875, 0.125),
                    ],
                    [-1, -1],
                    'ending'
                ),
            ]
        ),
        (
            # `melodic_lines`
            [
                [
                    PieceElement('C4', 39, 23, 1, 0.0, 0.5),
                    PieceElement('C4', 39, 23, 1, 0.5, 1.0),
                    PieceElement('C4', 39, 23, 1, 1.5, 0.5),
                    PieceElement('C4', 39, 23, 1, 2.0, 0.5),
                    PieceElement('C4', 39, 23, 1, 2.5, 0.25),
                    PieceElement('C4', 39, 23, 1, 2.75, 0.25),
                ],
                [
                    PieceElement('C4', 39, 23, 1, 0.0, 0.5),
                    PieceElement('C4', 39, 23, 1, 0.5, 0.25),
                    PieceElement('C4', 39, 23, 1, 0.75, 0.25),
                    PieceElement('C4', 39, 23, 1, 1.0, 0.25),
                    PieceElement('C4', 39, 23, 1, 1.25, 0.25),
                    PieceElement('C4', 39, 23, 1, 1.5, 0.25),
                    PieceElement('C4', 39, 23, 1, 1.75, 0.25),
                    PieceElement('C4', 39, 23, 1, 2.0, 0.5),
                    PieceElement('C4', 39, 23, 1, 2.5, 0.5),
                ]
            ],
            # `custom_position_types`
            None,
            # `expected`
            [
                Sonority(
                    [
                        PieceElement('C4', 39, 23, 1, 0.0, 0.5),
                        PieceElement('C4', 39, 23, 1, 0.0, 0.5),
                    ],
                    [0, 0],
                    'beginning'
                ),
                Sonority(
                    [
                        PieceElement('C4', 39, 23, 1, 0.5, 1.0),
                        PieceElement('C4', 39, 23, 1, 0.5, 0.25),
                    ],
                    [1, 1],
                    'middle'
                ),
                Sonority(
                    [
                        PieceElement('C4', 39, 23, 1, 0.5, 1.0),
                        PieceElement('C4', 39, 23, 1, 0.75, 0.25),
                    ],
                    [1, 2],
                    'other'
                ),
                Sonority(
                    [
                        PieceElement('C4', 39, 23, 1, 0.5, 1.0),
                        PieceElement('C4', 39, 23, 1, 1.0, 0.25),
                    ],
                    [1, 3],
                    'downbeat'
                ),
                Sonority(
                    [
                        PieceElement('C4', 39, 23, 1, 0.5, 1.0),
                        PieceElement('C4', 39, 23, 1, 1.25, 0.25),
                    ],
                    [1, 4],
                    'other'
                ),
                Sonority(
                    [
                        PieceElement('C4', 39, 23, 1, 1.5, 0.5),
                        PieceElement('C4', 39, 23, 1, 1.5, 0.25),
                    ],
                    [2, 5],
                    'middle'
                ),
                Sonority(
                    [
                        PieceElement('C4', 39, 23, 1, 1.5, 0.5),
                        PieceElement('C4', 39, 23, 1, 1.75, 0.25),
                    ],
                    [2, 6],
                    'other'
                ),
                Sonority(
                    [
                        PieceElement('C4', 39, 23, 1, 2.0, 0.5),
                        PieceElement('C4', 39, 23, 1, 2.0, 0.5),
                    ],
                    [3, 7],
                    'downbeat'
                ),
                Sonority(
                    [
                        PieceElement('C4', 39, 23, 1, 2.5, 0.25),
                        PieceElement('C4', 39, 23, 1, 2.5, 0.5),
                    ],
                    [4, 8],
                    'middle'
                ),
                Sonority(
                    [
                        PieceElement('C4', 39, 23, 1, 2.75, 0.25),
                        PieceElement('C4', 39, 23, 1, 2.5, 0.5),
                    ],
                    [-1, -1],
                    'ending'
                ),
            ]
        ),
    ]
)
def test_find_sonorities(
        melodic_lines: List[List[PieceElement]],
        custom_position_types: Optional[Dict[float, str]],
        expected: List[Sonority]
) -> None:
    """Test `find_sonorities` function."""
    result = find_sonorities(melodic_lines, custom_position_types)
    assert result == expected


@pytest.mark.parametrize(
    "n_measures, duration_weights, valid_rhythmic_patterns, "
    "end_with_whole_note",
    [
        (
            5,
            {0.125: 0, 0.25: 0.5, 0.5: 0.5, 1.0: 0},
            [[1.0], [0.5, 0.25, 0.25], [0.5, 0.25, 0.125, 0.125]],
            True
        ),
        (
            5,
            {0.125: 0, 0.25: 0.5, 0.5: 0.5, 1.0: 0},
            [[1.0], [0.5, 0.25, 0.25], [0.5, 0.25, 0.125, 0.125]],
            False
        ),
    ]
)
def test_generate_line_durations(
        n_measures: int,
        duration_weights: Dict[float, float],
        valid_rhythmic_patterns: List[List[float]],
        end_with_whole_note: bool
) -> None:
    """Test `generate_line_durations` function."""
    line_durations = generate_line_durations(
        n_measures, duration_weights, valid_rhythmic_patterns,
        end_with_whole_note
    )
    assert sum(line_durations) == n_measures
    for duration in line_durations[:-1]:
        assert duration_weights[duration] > 0
    if end_with_whole_note:
        assert line_durations[-1] == 1.0


@pytest.mark.parametrize(
    "tonic, scale_type, lowest_note, highest_note, n_measures, "
    "valid_rhythmic_patterns, lines_durations, duration_weights, "
    "custom_position_types",
    [
        (
            'C',
            'harmonic_minor',
            'C4',
            'C6',
            3,
            [[0.5, 0.5], [0.5, 0.25, 0.25]],
            [None, [0.5, 0.5, 0.5, 0.5, 0.5, 0.5]],
            {0.125: 0.1, 0.25: 0.4, 0.5: 0.4, 1.0: 0.1},
            None
        ),
    ]
)
def test_generate_random_piece(
        tonic: str,
        scale_type: str,
        lowest_note: str,
        highest_note: str,
        n_measures: int,
        valid_rhythmic_patterns: List[List[float]],
        lines_durations: List[Optional[List[float]]],
        duration_weights: Optional[Dict[float, float]],
        custom_position_types: Optional[Dict[float, str]]
) -> None:
    """Test `generate_random_piece` function."""
    piece = generate_random_piece(
        tonic, scale_type, lowest_note, highest_note, n_measures,
        valid_rhythmic_patterns, lines_durations, duration_weights,
        custom_position_types
    )
    assert piece.n_measures == n_measures


@pytest.mark.parametrize(
    "indices, melodic_lines, expected",
    [
        (
            # `indices`
            [1, 1],
            # `melodic_lines`
            [
                [
                    PieceElement('C4', 39, 23, 1, 0.0, 0.5),
                    PieceElement('C5', 51, 30, 1, 0.5, 0.5)
                ],
                [
                    PieceElement('G4', 46, 27, 5, 0.0, 0.5),
                    PieceElement('F4', 44, 26, 4, 0.5, 0.25),
                    PieceElement('G4', 46, 27, 5, 0.75, 0.25),
                ]
            ],
            # `expected`
            [
                 PieceElement('C5', 51, 30, 1, 0.5, 0.5),
                 PieceElement('F4', 44, 26, 4, 0.5, 0.25),
            ]
        ),
    ]
)
def test_convert_sonority_to_its_elements(
        indices: List[int],
        melodic_lines: List[List[PieceElement]],
        expected: List[PieceElement]
) -> None:
    """Test `convert_sonority_to_its_elements` function."""
    result = get_elements_by_indices(indices, melodic_lines)
    assert result == expected


@pytest.mark.parametrize(
    "current_time, total_time, current_measure_durations, "
    "valid_rhythmic_patterns, expected",
    [
        (
            3.0,
            4.0,
            [],
            [[1.0], [0.5, 0.5], [0.25, 0.25, 0.25, 0.25]],
            [0.25, 0.5, 1.0]
        ),
        (
            3.5,
            4.0,
            [0.5],
            [[0.5, 1.0], [0.5, 0.5], [0.25, 0.25, 0.25, 0.25]],
            [0.5]
        ),
    ]
)
def test_select_appropriate_durations(
        current_time: float,
        total_time: float,
        current_measure_durations: List[float],
        valid_rhythmic_patterns: List[List[float]],
        expected: List[float]
) -> None:
    """Test `select_appropriate_durations` function."""
    result = select_appropriate_durations(
        current_time, total_time, current_measure_durations,
        valid_rhythmic_patterns
    )
    assert result == expected


@pytest.mark.parametrize(
    "scale, lowest_note, highest_note, expected",
    [
        (
            [
                ScaleElement('A0', 0, 0, 6),
                ScaleElement('B0', 2, 1, 7),
                ScaleElement('C1', 3, 2, 1),
            ],
            'A0', 'B0',
            [
                ScaleElement('A0', 0, 0, 6),
                ScaleElement('B0', 2, 1, 7),
            ]
        ),
        (
            [
                ScaleElement('A0', 0, 0, 6),
                ScaleElement('B0', 2, 1, 7),
                ScaleElement('C1', 3, 2, 1),
            ],
            'B0', 'C2',
            [
                ScaleElement('B0', 2, 1, 7),
                ScaleElement('C1', 3, 2, 1),
            ]
        ),
    ]
)
def test_slice_scale(
        scale: List[ScaleElement], lowest_note: str, highest_note: str,
        expected: List[ScaleElement]
) -> None:
    """Test `slice_scale` function."""
    result = slice_scale(scale, lowest_note, highest_note)
    assert result == expected


@pytest.mark.parametrize(
    "current_measure_durations, next_duration, expected",
    [
        ([0.5, 0.25], 0.25, []),
        ([0.5, 0.25], 0.125, [0.5, 0.25, 0.125]),
        ([0.5], 1.0, [0.5]),
    ]
)
def test_update_current_measure_durations(
        current_measure_durations: List[float], next_duration: float,
        expected: List[float]
) -> None:
    """Test `update_current_measure_durations` function."""
    result = update_current_measure_durations(
        current_measure_durations, next_duration
    )
    assert result == expected


@pytest.mark.parametrize(
    "line_durations, valid_rhythmic_patterns, n_measures, match",
    [
        (
            [1.0, 0.25, 0.5, 0.25],
            [[1.0], [0.25, 0.25, 0.25, 0.25]],
            2,
            'Disallowed rhythmic pattern found'
        ),
        (
            [0.1, 0.9, 1.0],
            [[1.0], [0.25, 0.25, 0.25, 0.25]],
            2,
            'Disallowed rhythmic pattern found'
        ),
        (
            [1.0, 1.0, 1.0, 0.25, 0.25, 0.25, 0.25, 1.0],
            [[1.0], [0.25, 0.25, 0.25, 0.25]],
            4,
            'Line lasts'
        ),
    ]
)
def test_validate_line_durations_with_invalid_arguments(
        line_durations: Optional[List[float]],
        valid_rhythmic_patterns: List[List[float]],
        n_measures: int,
        match: str
) -> None:
    """Test `validate_line_durations` function with invalid arguments."""
    with pytest.raises(ValueError, match=match):
        validate_line_durations(
            line_durations, valid_rhythmic_patterns, n_measures
        )


@pytest.mark.parametrize(
    "line_durations, valid_rhythmic_patterns, n_measures",
    [
        (
            None,
            [[1.0], [0.25, 0.25, 0.25, 0.25]],
            2,
        ),
        (
            [1.0, 1.0, 1.0, 0.25, 0.25, 0.25, 0.25, 1.0],
            [[1.0], [0.25, 0.25, 0.25, 0.25]],
            5
        ),
    ]
)
def test_validate_line_durations_with_valid_arguments(
        line_durations: Optional[List[float]],
        valid_rhythmic_patterns: List[List[float]],
        n_measures: int
) -> None:
    """Test `validate_line_durations` function with valid arguments."""
    validate_line_durations(
        line_durations, valid_rhythmic_patterns, n_measures
    )


@pytest.mark.parametrize(
    "lines_durations, valid_rhythmic_patterns, n_measures, duration_weights, "
    "match",
    [
        (
            [None, [1.0, 1.0, 1.0, 0.25, 0.25, 0.25, 0.25, 1.0]],
            [[1.0], [0.25, 0.25, 0.25, 0.25]],
            5,
            None,
            "If `duration_weights` are not passed"
        ),
        (
            [[1.0, 1.0, 1.0, 0.25, 0.25, 0.25, 0.25, 1.0], [0.5, 0.5, 0.5]],
            [[1.0], [0.25, 0.25, 0.25, 0.25]],
            5,
            None,
            "Disallowed rhythmic pattern found"
        ),
    ]
)
def test_validate_rhythm_arguments_with_invalid_arguments(
        lines_durations: List[Optional[List[float]]],
        valid_rhythmic_patterns: List[List[float]],
        n_measures: int,
        duration_weights: Optional[Dict[float, float]],
        match: str
) -> None:
    """Test `validate_rhythm_arguments` function with invalid arguments."""
    with pytest.raises(ValueError, match=match):
        validate_rhythm_arguments(
            lines_durations, valid_rhythmic_patterns, n_measures,
            duration_weights
        )
