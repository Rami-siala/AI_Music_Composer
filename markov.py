# markov.py
# First-order Markov chain melody generator.
# Builds a transition probability matrix biased toward musically natural
# note motion, then samples it to produce raw candidate melodies.

import numpy as np


# ---------------------------------------------------------------------------
# 2.1  Transition matrix
# ---------------------------------------------------------------------------

def build_transition_matrix(scale: list[int]) -> np.ndarray:
    """Build an N×N stochastic transition matrix over the scale notes.

    Entry [i][j] is the probability of moving from scale[i] to scale[j].
    Weights favour stepwise motion and penalise large leaps, reflecting
    common melodic practice.

    Args:
        scale: Sorted list of MIDI note numbers (output of build_scale).

    Returns:
        numpy array of shape (N, N) where every row sums to 1.0.
    """
    n = len(scale)
    matrix = np.zeros((n, n))

    for i, from_note in enumerate(scale):
        for j, to_note in enumerate(scale):
            interval = abs(to_note - from_note)

            if interval == 0:
                weight = 0.5    # repeat same note: allowed but not preferred
            elif interval <= 2:
                weight = 3.0    # semitone / whole-tone step: strongly preferred
            elif interval <= 4:
                weight = 2.0    # minor/major third: preferred
            elif interval <= 7:
                weight = 1.0    # up to a fifth: neutral
            else:
                weight = 0.2    # large leap: discouraged

            matrix[i][j] = weight

        # normalise so each row is a valid probability distribution
        row_sum = matrix[i].sum()
        if row_sum > 0:
            matrix[i] /= row_sum

    return matrix


# ---------------------------------------------------------------------------
# 2.2  Melody sampler
# ---------------------------------------------------------------------------

def generate_melody(
    scale: list[int],
    matrix: np.ndarray,
    num_notes: int,
    rhythm_pattern: list[float],
) -> list[tuple[int, float]]:
    """Sample a melody from the Markov chain.

    Always starts on the root note (index 0 of the scale) so the melody
    opens on a tonally stable pitch. Durations cycle through rhythm_pattern.

    Args:
        scale:          Sorted list of MIDI note numbers.
        matrix:         Transition matrix from build_transition_matrix.
        num_notes:      Total number of notes to generate.
        rhythm_pattern: List of beat durations to cycle through.

    Returns:
        List of (midi_note, duration) tuples, length == num_notes.
    """
    rng = np.random.default_rng()
    note_idx = 0        # anchor the first note on the root
    melody: list[tuple[int, float]] = []

    for i in range(num_notes):
        note = scale[note_idx]
        duration = rhythm_pattern[i % len(rhythm_pattern)]
        melody.append((note, duration))
        note_idx = int(rng.choice(len(scale), p=matrix[note_idx]))

    return melody


# ---------------------------------------------------------------------------
# Spot-check (run: python3 markov.py)
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    from music_theory import build_scale, RHYTHM_PATTERNS

    scale = build_scale('C', 'major', octaves=(4, 5))
    matrix = build_transition_matrix(scale)

    # matrix shape and row-stochastic property
    n = len(scale)
    assert matrix.shape == (n, n), "Matrix must be N×N"
    for i in range(n):
        total = matrix[i].sum()
        assert abs(total - 1.0) < 1e-9, f"Row {i} does not sum to 1 (got {total})"
    print(f"Transition matrix: {n}×{n}, all rows sum to 1.0  OK")

    # stepwise bias: from C4 (index 0), moving to D4 (index 1) should be
    # more likely than jumping to B4 (last note in the octave)
    root_row = matrix[0]
    step_prob = root_row[1]         # C4 → D4
    leap_prob = root_row[n - 1]     # C4 → highest note
    assert step_prob > leap_prob, "Stepwise motion must be more probable than large leap"
    print(f"C4→D4 prob: {step_prob:.4f}  |  C4→top prob: {leap_prob:.4f}  (step > leap)  OK")

    # melody length and structure
    rhythm = RHYTHM_PATTERNS[0]
    melody = generate_melody(scale, matrix, num_notes=16, rhythm_pattern=rhythm)
    assert len(melody) == 16, "Melody must have exactly 16 notes"
    assert melody[0][0] == scale[0], "Melody must start on the root note"
    assert all(note in scale for note, _ in melody), "All notes must belong to the scale"
    assert all(dur > 0 for _, dur in melody), "All durations must be positive"

    notes, durs = zip(*melody)
    print(f"Melody (16 notes): {list(notes)}")
    print(f"Durations:         {list(durs)}")
    print("\nAll checks passed.")
