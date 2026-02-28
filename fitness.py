# fitness.py
# Scores a melody on a 0.0–1.0 scale using five musical criteria.
# This is the core "musical intelligence" of the app — the genetic
# algorithm evolves melodies toward higher scores from this function.


def fitness(
    melody: list[tuple[int, float]],
    scale: list[int],
    chord_pool: list[int],
) -> float:
    """Score a melody between 0.0 (poor) and 1.0 (excellent).

    Five sub-scores are computed independently, normalised to [0, 1],
    then combined with fixed weights that sum to 1.0.

    Sub-scores
    ----------
    1. Consonance (0.35)
       Fraction of notes that belong to the active scale.
       A melody entirely in-scale scores 1.0.

    2. Chord tone preference (0.20)
       Fraction of notes that land on tonic chord tones.
       Rewards melodies that emphasise stable harmonic targets.

    3. Rhythmic variety (0.20)
       Unique duration count normalised against 4 distinct values.
       Penalises monotonous rhythms where every note has the same length.

    4. Contour (0.15)
       Unique pitch count normalised against half the melody length.
       Penalises flat, repetitive lines with no melodic movement.

    5. Range (0.10)
       Ideal melodic range is 7–15 semitones (a fifth to a tenth).
       Scores drop off smoothly outside that window.

    Args:
        melody:     List of (midi_note, duration) tuples.
        scale:      Full scale as a list of MIDI note numbers.
        chord_pool: MIDI notes of the target chord (e.g. tonic triad).

    Returns:
        Float in [0.0, 1.0] rounded to 4 decimal places.
    """
    notes = [n for n, _ in melody]
    durs  = [d for _, d in melody]

    scale_set = set(scale)
    chord_set = set(chord_pool)

    # 1. Consonance — fraction of notes inside the scale
    consonance = sum(1 for n in notes if n in scale_set) / len(notes)

    # 2. Chord tone preference — fraction landing on chord tones
    chord_score = sum(1 for n in notes if n in chord_set) / len(notes)

    # 3. Rhythmic variety — reward using multiple distinct durations
    rhythm_variety = min(len(set(durs)) / 4.0, 1.0)

    # 4. Contour — reward melodic movement over static repetition
    unique_pitches = len(set(notes))
    contour = min(unique_pitches / (len(notes) * 0.5), 1.0)

    # 5. Range — ideal window is 7–15 semitones
    pitch_range = max(notes) - min(notes)
    if 7 <= pitch_range <= 15:
        range_score = 1.0
    else:
        range_score = max(0.0, 1.0 - abs(pitch_range - 11) / 11)

    # Weighted combination (weights sum to 1.0)
    score = (
        0.35 * consonance +
        0.20 * chord_score +
        0.20 * rhythm_variety +
        0.15 * contour +
        0.10 * range_score
    )
    return round(score, 4)


# ---------------------------------------------------------------------------
# Spot-check (run: python3 fitness.py)
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    from music_theory import build_scale, chord_notes, RHYTHM_PATTERNS

    scale      = build_scale('C', 'major', octaves=(4, 5))
    chord_pool = chord_notes(scale, 'I')   # C–E–G
    rhythm     = RHYTHM_PATTERNS[1]        # has variety: [0.5, 0.5, 1, 1, 1]

    # --- perfect melody: all in-scale, hits chord tones, good range, varied rhythm
    perfect = [(note, dur) for note, dur in zip(
        [60, 64, 67, 69, 71, 67, 65, 64],   # C E G A B G F E  — all C-major, good arc
        [0.5, 0.5, 1.0, 1.0, 2.0, 1.0, 0.5, 0.5],
    )]
    score_perfect = fitness(perfect, scale, chord_pool)
    print(f"Perfect melody score : {score_perfect}  (expect high, > 0.70)")
    assert score_perfect > 0.70, f"Expected > 0.70, got {score_perfect}"

    # --- poor melody: single repeated note, no rhythmic variety, zero pitch range.
    # C4 (60) is both in-scale and a chord tone, so consonance/chord scores stay
    # high — but rhythm_variety, contour, and range all floor out, capping the
    # total well below a musically interesting melody.
    poor = [(60, 1.0)] * 16
    score_poor = fitness(poor, scale, chord_pool)
    print(f"Poor melody score    : {score_poor}  (expect < 0.65)")
    assert score_poor < 0.65, f"Expected < 0.65, got {score_poor}"

    # --- score is always in [0, 1]
    assert 0.0 <= score_perfect <= 1.0
    assert 0.0 <= score_poor    <= 1.0
    print("Score range [0, 1]   : OK")

    # --- better melody must outscore poor one
    assert score_perfect > score_poor, "Perfect melody must outscore poor one"
    print("Ranking order        : OK")

    print("\nAll checks passed.")
