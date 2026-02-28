# composer.py
# CLI entry point — wires every module together and runs the full pipeline:
#   music theory → Markov chain → genetic algorithm → MIDI export → piano roll

import argparse
import os

from music_theory import build_scale, chord_notes, PROGRESSIONS, RHYTHM_PATTERNS, SCALE_INTERVALS
from markov import build_transition_matrix
from genetic import init_population, evolve
from midi_export import export_midi
from visualizer import draw_piano_roll


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description='AI Music Composer — generate original melodies using '
                    'Markov chains and a genetic algorithm.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument(
        '--key', default='C',
        help='Root note: C, C#, D, D#, E, F, F#, G, G#, A, A#, B',
    )
    p.add_argument(
        '--scale', default='major',
        choices=list(SCALE_INTERVALS.keys()),
        help='Scale type',
    )
    p.add_argument('--tempo',       type=int,   default=120,  help='Beats per minute')
    p.add_argument('--notes',       type=int,   default=32,   help='Number of notes in the melody')
    p.add_argument('--population',  type=int,   default=50,   help='Population size for the genetic algorithm')
    p.add_argument('--generations', type=int,   default=100,  help='Number of evolutionary generations')
    p.add_argument('--mutation',    type=float, default=0.05, help='Per-note mutation probability (0.0–1.0)')
    p.add_argument('--rhythm',      type=int,   default=0,    choices=range(len(RHYTHM_PATTERNS)),
                   help='Rhythm pattern index (0–3)')
    p.add_argument(
        '--output', default='output/composition',
        help='Output path prefix — .mid and _piano_roll.png will be appended',
    )
    return p.parse_args()


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def main() -> None:
    args = parse_args()

    # ensure the output directory exists
    out_dir = os.path.dirname(args.output)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    # 1. music theory
    scale      = build_scale(args.key, args.scale)
    rhythm     = RHYTHM_PATTERNS[args.rhythm]
    chord_pool = chord_notes(scale, PROGRESSIONS['I-IV-V-I'][0])   # tonic chord

    # 2. Markov chain transition matrix
    matrix = build_transition_matrix(scale)

    # 3. seed the initial population
    population = init_population(args.population, scale, matrix, args.notes, rhythm)

    # 4. evolve
    print(f"\nComposing in {args.key} {args.scale} | {args.tempo} BPM | "
          f"{args.notes} notes | population {args.population} | "
          f"{args.generations} generations\n")

    best_melody, best_score = evolve(
        population, scale, chord_pool, rhythm,
        generations=args.generations,
        mutation_rate=args.mutation,
    )
    print(f"\nFinal fitness: {best_score:.4f}\n")

    # 5. export MIDI and piano roll
    midi_path = f"{args.output}.mid"
    png_path  = f"{args.output}_piano_roll.png"
    export_midi(best_melody, args.tempo, midi_path)
    draw_piano_roll(best_melody, png_path)


if __name__ == '__main__':
    main()
