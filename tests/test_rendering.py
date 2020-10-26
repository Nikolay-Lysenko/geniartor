"""
Test `geniartor.rendering` package.

Author: Nikolay Lysenko
"""


from typing import Dict, List

import pretty_midi
import pytest

from geniartor.piece import Piece, PieceElement, ScaleElement, Sonority
from geniartor.rendering import (
    create_events_from_piece,
    create_lilypond_file_from_piece,
    create_midi_from_piece,
    create_sinethesizer_instruments,
    create_wav_from_events,
)


@pytest.mark.parametrize(
    "piece, measure_in_seconds, velocity, expected",
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
            # `measure_in_seconds`
            2,
            # `velocity`
            0.2,
            # `expected`
            (
                "instrument\tstart_time\tduration\tfrequency\tvelocity\teffects\n"
                "default_instrument\t1.0\t1.0\tC4\t0.2\t\n"
                "default_instrument\t1.0\t2.0\tG4\t0.2\t\n"
                "default_instrument\t2.0\t1.0\tD4\t0.2\t\n"
                "default_instrument\t3.0\t1.0\tE4\t0.2\t\n"
                "default_instrument\t3.0\t2.0\tC5\t0.2\t\n"
                "default_instrument\t4.0\t1.0\tF4\t0.2\t\n"
            )
        ),
    ]
)
def test_create_events_from_piece(
        path_to_tmp_file: str, piece: Piece,
        measure_in_seconds: int, velocity: float, expected: str
) -> None:
    """Test `create_events_from_piece` function."""
    create_events_from_piece(
        piece,
        path_to_tmp_file,
        measure_in_seconds=measure_in_seconds,
        instruments=['default_instrument' for _ in piece.melodic_lines],
        velocity=velocity,
        opening_silence_in_seconds=1
    )
    with open(path_to_tmp_file) as in_file:
        result = in_file.read()
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
                        PieceElement('E4', 43, 25, 3, 0.0, 1.0),
                        PieceElement('G4', 46, 27, 5, 1.0, 1.0),
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
            # `expected`
            "\\version \"2.18.2\"\n"
            "\\layout {\n"
            "    indent = #0\n"
            "}\n"
            "\\new StaffGroup <<\n"
            "    \\new Staff <<\n"
            "        \\clef treble\n"
            "        \\time 4/4\n"
            "        {g'1 c''1}\n"
            "        \\\\\n"
            "        {e'1 g'1}\n"
            "    >>\n"
            "    \\new Staff <<\n"
            "        \\clef bass\n"
            "        \\time 4/4\n"
            "        {c'2 d'2 e'2 f'2}\n"
            "    >>\n"
            ">>"
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
                        PieceElement('D4', 41, 24, 2, 0.5, 1.0),
                        PieceElement('E4', 43, 25, 3, 1.5, 0.25),
                        PieceElement('F4', 44, 26, 4, 1.75, 0.25),
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
            # `expected`
            (
                "\\version \"2.18.2\"\n"
                "\\layout {\n"
                "    indent = #0\n"
                "}\n"
                "\\new StaffGroup <<\n"
                "    \\new Staff <<\n"
                "        \\clef treble\n"
                "        \\time 4/4\n"
                "        {g'1 c''1}\n"
                "    >>\n"
                "    \\new Staff <<\n"
                "        \\clef bass\n"
                "        \\time 4/4\n"
                "        {c'2 d'2~ d'2 e'4 f'4}\n"
                "    >>\n"
                ">>"
            )
        ),
        (
            # `piece`
            Piece(
                n_measures=1,
                pitches=[
                    ScaleElement('C2', 15, 9, 1),
                    ScaleElement('D2', 17, 10, 2),
                    ScaleElement('E2', 19, 11, 3),
                    ScaleElement('F2', 20, 12, 4),
                ],
                melodic_lines=[
                    [
                        PieceElement('C2', 15, 9, 1, 0.0, 0.5),
                        PieceElement('D2', 17, 10, 2, 0.5, 0.5),
                        PieceElement('E2', 19, 11, 3, 1.0, 0.5),
                        PieceElement('F2', 20, 12, 4, 1.5, 0.5),
                    ],
                ],
                sonorities=[
                    Sonority(
                        [
                            PieceElement('C2', 15, 9, 1, 0.0, 0.5),
                        ],
                        [0],
                        'beginning'
                    ),
                    Sonority(
                        [
                            PieceElement('D2', 17, 10, 2, 0.5, 0.5),
                        ],
                        [1],
                        'middle'
                    ),
                    Sonority(
                        [
                            PieceElement('E2', 19, 11, 3, 1.0, 0.5),
                        ],
                        [2],
                        'downbeat'
                    ),
                    Sonority(
                        [
                            PieceElement('F4', 20, 12, 4, 1.5, 0.5),
                        ],
                        [-1],
                        'ending'
                    ),
                ]
            ),
            # `expected`
            "\\version \"2.18.2\"\n"
            "\\layout {\n"
            "    indent = #0\n"
            "}\n"
            "\\new StaffGroup <<\n"
            "    \\new Staff <<\n"
            "        \\clef treble\n"
            "        \\time 4/4\n"
            "        {c,2 d,2 e,2 f,2}\n"
            "    >>\n"
            "    \\new Staff <<\n"
            "        \\clef bass\n"
            "        \\time 4/4\n"
            "    >>\n"
            ">>"
        ),
    ]
)
def test_create_lilypond_file_from_piece(
        path_to_tmp_file: str, piece: Piece, expected: str
) -> None:
    """Test `create_lilypond_file_from_piece` function."""
    create_lilypond_file_from_piece(piece, path_to_tmp_file)
    with open(path_to_tmp_file) as in_file:
        result = in_file.read()
        assert result == expected


@pytest.mark.parametrize(
    "piece, note_number, expected",
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
            # `note_number`
            2,
            # `expected`
            {'pitch': 64, 'start': 2.0, 'end': 2.5}
        ),
    ]
)
def test_create_midi_from_piece(
        path_to_tmp_file: str, piece: Piece, note_number: int,
        expected: Dict[str, float]
) -> None:
    """Test `create_midi_from_piece` function."""
    create_midi_from_piece(
        piece,
        path_to_tmp_file,
        measure_in_seconds=1,
        instruments=[0 for _ in piece.melodic_lines],
        velocity=100,
        opening_silence_in_seconds=1,
        trailing_silence_in_seconds=1
    )
    midi_data = pretty_midi.PrettyMIDI(path_to_tmp_file)
    instrument = midi_data.instruments[0]
    midi_note = instrument.notes[note_number]
    result = {
        'pitch': midi_note.pitch,
        'start': midi_note.start,
        'end': midi_note.end
    }
    assert result == expected


@pytest.mark.parametrize(
    "tsv_content, trailing_silence_in_seconds",
    [
        (
            [
                'instrument\tstart_time\tduration\tfrequency\tvelocity\teffects',
                'sawtooth_with_filter_envelope\t1\t1\tA0\t1\t',
                'sawtooth_with_filter_envelope\t2\t1\t1\t1\t[{"name": "tremolo", "frequency": 1}]'
            ],
            1.0
        )
    ]
)
def test_create_wav_from_events(
        path_to_tmp_file: str, path_to_another_tmp_file: str,
        tsv_content: List[str], trailing_silence_in_seconds: float
) -> None:
    """Test `create_wav_from_events` function."""
    with open(path_to_tmp_file, 'w') as tmp_tsv_file:
        for line in tsv_content:
            tmp_tsv_file.write(line + '\n')
    n_melodic_lines = 1
    instruments_registry = create_sinethesizer_instruments(n_melodic_lines)
    create_wav_from_events(
        path_to_tmp_file,
        path_to_another_tmp_file,
        instruments_registry,
        trailing_silence_in_seconds
    )
