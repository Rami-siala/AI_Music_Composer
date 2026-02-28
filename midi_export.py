# midi_export.py
# Writes a melody to a standard MIDI file (.mid) using midiutil.
# The output can be opened and played in any music application or DAW.

from midiutil import MIDIFile


def export_midi(
    melody: list[tuple[int, float]],
    tempo: int,
    output_path: str,
) -> None:
    """Export a melody as a MIDI file.

    Creates a single-track, single-channel MIDI file at the given tempo.
    Notes are written sequentially with no overlap; each note starts
    immediately after the previous one ends.

    Args:
        melody:      List of (midi_note, duration) tuples.
                     duration is in beats (1.0 = quarter note).
        tempo:       Playback speed in beats per minute.
        output_path: File path to write, e.g. 'composition.mid'.
    """
    midi = MIDIFile(1)          # single track
    track, channel = 0, 0
    velocity = 100              # fixed note velocity (0–127)

    midi.addTempo(track, 0, tempo)

    time = 0.0
    for pitch, duration in melody:
        midi.addNote(track, channel, pitch, time, duration, velocity)
        time += duration

    with open(output_path, 'wb') as f:
        midi.writeFile(f)

    print(f"Saved: {output_path}")


# ---------------------------------------------------------------------------
# Spot-check (run: python3 midi_export.py)
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    import os
    from midiutil import MIDIFile as _MIDIFile   # confirm import works

    # short test melody: C major scale fragment
    test_melody = [
        (60, 1.0), (62, 1.0), (64, 1.0), (65, 1.0),
        (67, 0.5), (67, 0.5), (69, 2.0),
    ]
    out = '/tmp/test_composition.mid'
    export_midi(test_melody, tempo=120, output_path=out)

    # file must exist and be non-empty
    assert os.path.exists(out), "MIDI file was not created"
    size = os.path.getsize(out)
    assert size > 0, "MIDI file is empty"
    print(f"File size: {size} bytes  OK")

    # MIDI files begin with the header chunk identifier 'MThd'
    with open(out, 'rb') as f:
        header = f.read(4)
    assert header == b'MThd', f"Expected MThd header, got {header}"
    print(f"MIDI header: {header}  OK")

    print("\nAll checks passed.")
