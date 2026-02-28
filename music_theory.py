# music_theory.py
# Foundation module: MIDI note mapping, scales, chords, rhythm patterns.
# Everything else in the app depends on this module.

# ---------------------------------------------------------------------------
# 1.1  MIDI note numbers
# ---------------------------------------------------------------------------

# Semitone offset for each note name within an octave
_SEMITONES: dict[str, int] = {
    'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5,
    'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11,
}


def note_to_midi(note: str, octave: int) -> int:
    """Convert a note name + octave to a MIDI pitch number.

    Middle C (C4) = 60.  Valid range is 0–127.

    Args:
        note:   Note name, e.g. 'C', 'F#', 'A#'.
        octave: Octave number (4 = middle octave).

    Returns:
        MIDI integer in range 0–127.

    Raises:
        KeyError: if `note` is not a recognised note name.
    """
    return 12 * (octave + 1) + _SEMITONES[note]


# ---------------------------------------------------------------------------
# 1.2  Scale definitions
# ---------------------------------------------------------------------------

# Semitone intervals from the root for each supported scale type
SCALE_INTERVALS: dict[str, list[int]] = {
    'major':      [0, 2, 4, 5, 7, 9, 11],
    'minor':      [0, 2, 3, 5, 7, 8, 10],
    'pentatonic': [0, 2, 4, 7, 9],
    'blues':      [0, 3, 5, 6, 7, 10],
}


def build_scale(
    root: str,
    scale_type: str,
    octaves: tuple[int, int] = (4, 5),
) -> list[int]:
    """Return a sorted list of MIDI note numbers for the given key and range.

    Args:
        root:       Root note name, e.g. 'C', 'D', 'F#'.
        scale_type: One of the keys in SCALE_INTERVALS.
        octaves:    Inclusive (low, high) octave range to cover.

    Returns:
        Sorted list of unique MIDI note numbers within 0–127.

    Raises:
        KeyError: if `scale_type` is not recognised.
    """
    intervals = SCALE_INTERVALS[scale_type]
    notes: list[int] = []
    for octave in range(octaves[0], octaves[1] + 1):
        base = note_to_midi(root, octave)
        notes += [base + interval for interval in intervals]
    return sorted(set(n for n in notes if 0 <= n <= 127))


# ---------------------------------------------------------------------------
# 1.3  Chord progressions
# ---------------------------------------------------------------------------

# Scale-degree indices (0-based) for the three notes of each chord
CHORD_DEGREES: dict[str, list[int]] = {
    'I':  [0, 2, 4],
    'IV': [3, 5, 0],   # wraps around the scale
    'V':  [4, 6, 1],
    'vi': [5, 0, 2],
}

# Named common progressions expressed as ordered lists of chord symbols
PROGRESSIONS: dict[str, list[str]] = {
    'I-IV-V-I':  ['I', 'IV', 'V', 'I'],
    'I-V-vi-IV': ['I', 'V', 'vi', 'IV'],
}


def chord_notes(scale: list[int], degree: str) -> list[int]:
    """Return the MIDI notes that form a chord within a given scale.

    Args:
        scale:  Built scale (output of build_scale).
        degree: Chord symbol, e.g. 'I', 'IV', 'V', 'vi'.

    Returns:
        List of three MIDI note numbers.

    Raises:
        KeyError: if `degree` is not in CHORD_DEGREES.
    """
    indices = CHORD_DEGREES[degree]
    return [scale[i % len(scale)] for i in indices]


# ---------------------------------------------------------------------------
# 1.4  Rhythm patterns
# ---------------------------------------------------------------------------

# Each pattern is a list of note durations in beats (1.0 = quarter note).
# The melody generator cycles through the pattern to fill num_notes.
RHYTHM_PATTERNS: list[list[float]] = [
    [1.0, 1.0, 1.0, 1.0],           # four quarter notes
    [0.5, 0.5, 1.0, 1.0, 1.0],      # two eighths + three quarters
    [2.0, 1.0, 1.0],                 # half note + two quarters
    [1.5, 0.5, 1.0, 1.0],           # dotted quarter + eighth + two quarters
]


# ---------------------------------------------------------------------------
# Spot-check (run: python music_theory.py)
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    # MIDI numbers
    assert note_to_midi('C', 4) == 60, "Middle C should be 60"
    assert note_to_midi('A', 4) == 69, "A4 should be 69"

    # C major across octaves 4–5
    c_major = build_scale('C', 'major', octaves=(4, 5))
    assert 60 in c_major, "C4 must be in C major"
    assert 62 in c_major, "D4 must be in C major"
    assert 61 not in c_major, "C#4 must NOT be in C major"
    print(f"C major (oct 4-5): {c_major}")

    # D minor across octaves 4–5
    d_minor = build_scale('D', 'minor', octaves=(4, 5))
    print(f"D minor (oct 4-5): {d_minor}")

    # Chord notes
    tonic = chord_notes(c_major, 'I')
    print(f"C major tonic chord (I): {tonic}")

    # Rhythm pattern round-trip
    assert len(RHYTHM_PATTERNS) == 4
    print(f"Rhythm patterns: {RHYTHM_PATTERNS}")

    print("\nAll checks passed.")
