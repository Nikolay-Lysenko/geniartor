"""
Render piece to some formats such as WAV and MIDI.

Author: Nikolay Lysenko
"""


import datetime
import os
from pkg_resources import resource_filename
from typing import Any, Dict

import pretty_midi
from sinethesizer.io import (
    convert_tsv_to_timeline,
    create_timbres_registry,
    write_timeline_to_wav
)
from sinethesizer.io.utils import get_list_of_notes

from .piece import Piece


def create_midi_from_piece(
        piece: Piece,
        midi_path: str,
        measure_in_seconds: float,
        instrument: int,
        velocity: int,
        opening_silence_in_seconds: int = 1,
        trailing_silence_in_seconds: int = 1
) -> None:
    """
    Create MIDI file from a piece created by this package.

    :param piece:
        `Piece` instance
    :param midi_path:
        path where resulting MIDI file is going to be saved
    :param measure_in_seconds:
        duration of one measure in seconds
    :param instrument:
        for an instrument that plays the piece, its ID (number)
        according to General MIDI specification
    :param velocity:
        one common velocity for all notes
    :param opening_silence_in_seconds:
        number of seconds with silence to add at the start of the composition
    :param trailing_silence_in_seconds:
        number of seconds with silence to add at the end of the composition
    :return:
        None
    """
    numeration_shift = pretty_midi.note_name_to_number('A0')
    pretty_midi_instrument = pretty_midi.Instrument(program=instrument)
    for melodic_line in piece.melodic_lines:
        for element in melodic_line:
            start_time = element.start_time * measure_in_seconds
            start_time += opening_silence_in_seconds
            end_time = start_time + element.duration * measure_in_seconds
            pitch = element.position_in_semitones + numeration_shift
            note = pretty_midi.Note(
                velocity=velocity,
                pitch=pitch,
                start=start_time,
                end=end_time
            )
            pretty_midi_instrument.notes.append(note)
    pretty_midi_instrument.notes.sort(key=lambda x: x.start)

    note = pretty_midi.Note(
        velocity=0,
        pitch=1,  # Arbitrary value that affects nothing.
        start=piece.n_measures * measure_in_seconds,
        end=piece.n_measures * measure_in_seconds + trailing_silence_in_seconds
    )
    pretty_midi_instrument.notes.append(note)

    composition = pretty_midi.PrettyMIDI()
    composition.instruments.append(pretty_midi_instrument)
    composition.write(midi_path)


def create_events_from_piece(
        piece: Piece,
        events_path: str,
        measure_in_seconds: float,
        timbre: str,
        volume: float,
        location: int = 0,
        effects: str = '',
        opening_silence_in_seconds: int = 1
) -> None:
    """
    Create TSV file with `sinethesizer` events from a piece.

    :param piece:
        `Piece` instance
    :param events_path:
        path to a file where result is going to be saved
    :param measure_in_seconds:
        duration of one measure in seconds
    :param timbre:
        timbre to be used to play all notes
    :param volume:
        relative volume of sound to be played
    :param location:
        position of imaginary sound source
    :param effects:
        sound effects to be applied to the resulting event
    :param opening_silence_in_seconds:
        number of seconds with silence to add at the start of the composition
    :return:
        None
    """
    all_notes = get_list_of_notes()
    events = []
    for melodic_line in piece.melodic_lines:
        for element in melodic_line:
            start_time = element.start_time * measure_in_seconds
            start_time += opening_silence_in_seconds
            duration_in_seconds = element.duration * measure_in_seconds
            pitch_id = element.position_in_semitones
            note = all_notes[pitch_id]
            event = (timbre, start_time, duration_in_seconds, note, pitch_id)
            events.append(event)
    events = sorted(events, key=lambda x: (x[1], x[4], x[2]))
    events = [
        f"{x[0]}\t{x[1]}\t{x[2]}\t{x[3]}\t{volume}\t{location}\t{effects}"
        for x in events
    ]

    columns = [
        'timbre', 'start_time', 'duration', 'frequency',
        'volume', 'location', 'effects'
    ]
    header = '\t'.join(columns)
    results = [header] + events
    with open(events_path, 'w') as out_file:
        for line in results:
            out_file.write(line + '\n')


def create_wav_from_events(events_path: str, output_path: str) -> None:
    """
    Create WAV file based on `sinethesizer` TSV file.

    :param events_path:
        path to TSV file with track represented as `sinethesizer` events
    :param output_path:
        path where resulting WAV file is going to be saved
    :return:
        None
    """
    presets_path = resource_filename(
        'geniartor',
        'configs/sinethesizer_presets.yml'
    )
    settings = {
        'frame_rate': 44100,
        'trailing_silence': 1,
        'max_channel_delay': 0.02,
        'timbres_registry': create_timbres_registry(presets_path)
    }
    timeline = convert_tsv_to_timeline(events_path, settings)
    write_timeline_to_wav(output_path, timeline, settings['frame_rate'])


def render(piece: Piece, rendering_params: Dict[str, Any]) -> None:
    """
    Save piece to MIDI, TSV, and WAV files.

    :param piece:
        `Piece` instance
    :param rendering_params:
        settings of piece saving
    :return:
        None
    """
    top_level_dir = rendering_params['dir']
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S,%f")
    nested_dir = os.path.join(top_level_dir, f"result_{now}")
    os.mkdir(nested_dir)

    midi_path = os.path.join(nested_dir, 'music.mid')
    midi_params = rendering_params['midi']
    measure = rendering_params['measure_in_seconds']
    create_midi_from_piece(piece, midi_path, measure, **midi_params)

    events_path = os.path.join(nested_dir, 'sinethesizer_events.tsv')
    events_params = rendering_params['sinethesizer']
    create_events_from_piece(piece, events_path, measure, **events_params)

    wav_path = os.path.join(nested_dir, 'music.wav')
    create_wav_from_events(events_path, wav_path)
