# visualizer.py
# Renders a melody as a piano roll and saves it as a PNG image.
# Each note is drawn as a rounded horizontal bar: x = time, y = MIDI pitch.

import matplotlib
matplotlib.use('Agg')   # non-interactive backend — safe for headless environments
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


def draw_piano_roll(
    melody: list[tuple[int, float]],
    output_path: str,
) -> None:
    """Render a melody as a piano roll image and save it to disk.

    Each note is drawn as a rounded rectangle:
      - x position  = cumulative beat time at note onset
      - x width     = note duration (slightly inset so adjacent notes don't touch)
      - y position  = MIDI pitch number

    Args:
        melody:      List of (midi_note, duration) tuples.
        output_path: File path for the saved image, e.g. 'piano_roll.png'.
    """
    fig, ax = plt.subplots(figsize=(14, 5))

    time = 0.0
    for pitch, duration in melody:
        rect = mpatches.FancyBboxPatch(
            (time, pitch - 0.4),        # (x, y) bottom-left corner
            duration - 0.05,            # width  (small gap between notes)
            0.8,                        # height (narrow bar per pitch row)
            boxstyle="round,pad=0.02",
            linewidth=0.5,
            edgecolor='black',
            facecolor='steelblue',
        )
        ax.add_patch(rect)
        time += duration

    pitches = [p for p, _ in melody]
    ax.set_xlim(0, time)
    ax.set_ylim(min(pitches) - 2, max(pitches) + 2)
    ax.set_xlabel('Time (beats)')
    ax.set_ylabel('MIDI pitch')
    ax.set_title('Piano Roll')
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"Saved: {output_path}")


# ---------------------------------------------------------------------------
# Spot-check (run: python3 visualizer.py)
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    import os
    from PIL import Image   # optional check; skip gracefully if not installed

    test_melody = [
        (60, 1.0), (62, 0.5), (64, 0.5), (65, 1.0),
        (67, 0.5), (69, 0.5), (71, 1.0), (72, 2.0),
    ]
    out = '/tmp/test_piano_roll.png'
    draw_piano_roll(test_melody, output_path=out)

    assert os.path.exists(out), "PNG file was not created"
    size = os.path.getsize(out)
    assert size > 0, "PNG file is empty"
    print(f"File size: {size} bytes  OK")

    # verify PNG magic bytes (first 8 bytes of every PNG file)
    PNG_MAGIC = b'\x89PNG\r\n\x1a\n'
    with open(out, 'rb') as f:
        header = f.read(8)
    assert header == PNG_MAGIC, f"Not a valid PNG: {header!r}"
    print(f"PNG header valid  OK")

    print("\nAll checks passed.")
