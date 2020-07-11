"""
Render piece to some formats such as WAV and MIDI.

Author: Nikolay Lysenko
"""


import datetime
import os
import subprocess
import traceback
from math import ceil, floor
from pkg_resources import resource_filename
from typing import Any, Dict, List

import pretty_midi
from sinethesizer.io import (
    convert_tsv_to_timeline,
    create_timbres_registry,
    write_timeline_to_wav
)
from sinethesizer.io.utils import get_list_of_notes

from .piece import Piece, PieceElement


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
        musical piece
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
                start=start_time,
                end=end_time,
                pitch=pitch,
                velocity=velocity
            )
            pretty_midi_instrument.notes.append(note)
    pretty_midi_instrument.notes.sort(key=lambda x: (x.start, x.pitch))

    trailing_silence_start = piece.n_measures * measure_in_seconds
    trailing_silence_start += opening_silence_in_seconds
    note = pretty_midi.Note(
        velocity=0,
        pitch=1,  # Arbitrary value that affects nothing.
        start=trailing_silence_start,
        end=trailing_silence_start + trailing_silence_in_seconds
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
        musical piece
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


def create_wav_from_events(
        events_path: str, output_path: str, trailing_silence_in_seconds: float
) -> None:
    """
    Create WAV file based on `sinethesizer` TSV file.

    :param events_path:
        path to TSV file with track represented as `sinethesizer` events
    :param output_path:
        path where resulting WAV file is going to be saved
    :param trailing_silence_in_seconds:
        number of seconds with silence to add at the end of the composition
    :return:
        None
    """
    presets_path = resource_filename(
        'geniartor',
        'configs/sinethesizer_presets.yml'
    )
    settings = {
        'frame_rate': 44100,
        'trailing_silence': trailing_silence_in_seconds,
        'max_channel_delay': 0.02,
        'timbres_registry': create_timbres_registry(presets_path)
    }
    timeline = convert_tsv_to_timeline(events_path, settings)
    write_timeline_to_wav(output_path, timeline, settings['frame_rate'])


def make_lilypond_template(n_voices: int) -> str:
    """
    Make template of Lilypond text file.

    :param n_voices:
        number of voices in a piece to be rendered
    :return:
        template
    """
    raw_template = (
        "\\version \"2.18.2\"\n"
        "\\layout {{{{\n"
        "    indent = #0\n"
        "}}}}\n"
        "\\new StaffGroup <<\n"
        "    \\new Staff <<\n"
        "        \\clef treble\n"
        "        \\time 4/4\n"
        "{}"
        "    >>\n"
        "    \\new Staff <<\n"
        "        \\clef bass\n"
        "        \\time 4/4\n"
        "{}"
        "    >>\n"
        ">>"
    )
    voices = ["        {{{}}}\n" for _ in range(n_voices)]
    treble_bass_threshold = ceil(n_voices / 2)
    template = raw_template.format(
        "        \\\\\n".join(voices[:treble_bass_threshold]),
        "        \\\\\n".join(voices[treble_bass_threshold:])
    )
    return template


def get_lilypond_order_of_voices(n_voices: int) -> List[int]:
    """
    Enumerate voices (from lowest to highest) in Lilypond order.

    See more about Lilypond order ('Voice order' section):
    http://lilypond.org/doc/v2.18/Documentation/notation/multiple-voices

    :param n_voices:
        number of voices in a piece to be rendered
    :return:
        indices of voices in Lilypond order
    """
    def enumerate_for_one_staff(n_voices_at_staff: int) -> List[int]:
        max_index = n_voices_at_staff - 1
        results = []
        for i in range(n_voices_at_staff):
            result = max_index - int(round(2 * abs(i - max_index / 2)))
            result += int(i < max_index / 2)
            results.append(result)
        return results

    n_voices_at_upper_staff = ceil(n_voices / 2)
    n_voices_at_lower_staff = floor(n_voices / 2)
    lower_voices_priorities = [
        x + n_voices_at_upper_staff
        for x in enumerate_for_one_staff(n_voices_at_lower_staff)
    ]
    upper_voices_priorities = enumerate_for_one_staff(n_voices_at_upper_staff)
    priorities = lower_voices_priorities + upper_voices_priorities
    ordering = sorted(
        list((index, priority) for index, priority in enumerate(priorities)),
        key=lambda x: x[1]
    )
    ordering = [x[0] for x in ordering]
    return ordering


def convert_to_lilypond_note(piece_element: PieceElement) -> str:
    """
    Convert `PieceElement` instance to note in Lilypond absolute notation.

    :param piece_element:
        element of a musical piece
    :return:
        note in Lilypond absolute notation
    """
    pitch_class = piece_element.note[:-1]
    pitch_class = pitch_class.replace('#', 'is').replace('b', 'es')
    pitch_class = pitch_class.lower()

    octave_id = int(piece_element.note[-1])
    lilypond_default_octave_id = 3
    octave_diff = octave_id - lilypond_default_octave_id
    octave_sign = "'" if octave_diff >= 0 else ','
    octave_info = "".join(octave_sign for _ in range(octave_diff))

    start_time = piece_element.start_time
    time_in_measure = start_time - floor(start_time)
    if piece_element.duration == 1.0 and time_in_measure > 0:
        remaining_duration = int(round(1 / (1 - time_in_measure)))
        remaining_note = f"{pitch_class}{octave_info}{remaining_duration}~"
        left_over_bar_duration = int(round(1 / time_in_measure))
        left_over_note = f"{pitch_class}{octave_info}{left_over_bar_duration}"
        return f"{remaining_note} {left_over_note}"
    else:
        duration = int(round((1 / piece_element.duration)))
        note = f"{pitch_class}{octave_info}{duration}"
        return note


def create_lilypond_file_from_piece(piece: Piece, output_path: str) -> None:
    """
    Create text file in format of Lilypond sheet music editor.

    :param piece:
        musical piece
    :param output_path:
        path where resulting file is going to be saved
    :return:
        None
    """
    template = make_lilypond_template(len(piece.melodic_lines))
    lilypond_voices = []
    indices = get_lilypond_order_of_voices(len(piece.melodic_lines))
    for index in indices:
        melodic_line = piece.melodic_lines[index]
        lilypond_voice = []
        for piece_element in melodic_line:
            note = convert_to_lilypond_note(piece_element)
            lilypond_voice.append(note)
        lilypond_voice = " ".join(lilypond_voice)
        lilypond_voices.append(lilypond_voice)
    result = template.format(*lilypond_voices)
    with open(output_path, 'w') as out_file:
        out_file.write(result)


def create_pdf_sheet_music_with_lilypond(
        lilypond_path: str
) -> None:  # pragma: no cover
    """
    Create PDF file with sheet music.

    :param lilypond_path:
        path to a text file in Lilypond format
    :return:
        None:
    """
    dir_path, filename = os.path.split(lilypond_path)
    bash_command = f"lilypond {filename}"
    try:
        process = subprocess.Popen(
            bash_command.split(),
            cwd=dir_path,
            stdout=subprocess.PIPE
        )
        process.communicate()
    except Exception:
        print("Rendering sheet music to PDF failed. Do you have Lilypond?")
        print(traceback.format_exc())


def render(
        piece: Piece, rendering_params: Dict[str, Any]
) -> None:  # pragma: no cover
    """
    Save piece to MIDI, WAV, TSV, PDF, and Lilypond files.

    :param piece:
        musical piece
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
    common_params = rendering_params['common']
    create_midi_from_piece(
        piece, midi_path, **midi_params, **common_params
    )

    events_path = os.path.join(nested_dir, 'sinethesizer_events.tsv')
    events_params = rendering_params['sinethesizer']
    trailing_silence_in_sec = common_params.pop('trailing_silence_in_seconds')
    create_events_from_piece(
        piece, events_path, **events_params, **common_params
    )

    wav_path = os.path.join(nested_dir, 'music.wav')
    create_wav_from_events(events_path, wav_path, trailing_silence_in_sec)

    lilypond_path = os.path.join(nested_dir, 'sheet_music.ly')
    create_lilypond_file_from_piece(piece, lilypond_path)
    create_pdf_sheet_music_with_lilypond(lilypond_path)
