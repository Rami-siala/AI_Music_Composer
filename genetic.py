# genetic.py
# Genetic algorithm that evolves a population of melodies toward higher
# fitness scores. Pipeline: initialise → score → select → crossover → mutate
# → repeat for N generations → return the best melody found.

import random

from markov import generate_melody
from fitness import fitness


# ---------------------------------------------------------------------------
# 4.1  Initialise population
# ---------------------------------------------------------------------------

def init_population(
    size: int,
    scale: list[int],
    matrix,                     # np.ndarray from build_transition_matrix
    num_notes: int,
    rhythm_pattern: list[float],
) -> list:
    """Create an initial population of melodies using the Markov chain.

    Args:
        size:           Number of melodies in the population.
        scale:          Sorted list of MIDI note numbers.
        matrix:         Markov transition matrix.
        num_notes:      Length of each melody in notes.
        rhythm_pattern: Duration pattern to cycle through.

    Returns:
        List of `size` melodies, each a list of (midi_note, duration) tuples.
    """
    return [
        generate_melody(scale, matrix, num_notes, rhythm_pattern)
        for _ in range(size)
    ]


# ---------------------------------------------------------------------------
# 4.2  Selection — elitist top-half
# ---------------------------------------------------------------------------

def select(population: list, scores: list[float]) -> list:
    """Keep the top-scoring half of the population.

    Args:
        population: List of melodies.
        scores:     Fitness score for each melody (same order).

    Returns:
        Top 50% of melodies ranked by fitness, best first.
    """
    ranked = sorted(zip(scores, population), key=lambda x: x[0], reverse=True)
    return [melody for _, melody in ranked[: len(ranked) // 2]]


# ---------------------------------------------------------------------------
# 4.3  Crossover — single-point splice
# ---------------------------------------------------------------------------

def crossover(
    parent_a: list[tuple[int, float]],
    parent_b: list[tuple[int, float]],
) -> list[tuple[int, float]]:
    """Produce one child by splicing two parent melodies at a random cut point.

    The child inherits the opening from parent_a and the tail from parent_b.

    Args:
        parent_a: First parent melody.
        parent_b: Second parent melody (must be the same length).

    Returns:
        Child melody of the same length as the parents.
    """
    cut = random.randint(1, len(parent_a) - 1)
    return parent_a[:cut] + parent_b[cut:]


# ---------------------------------------------------------------------------
# 4.4  Mutation — per-note random swap
# ---------------------------------------------------------------------------

def mutate(
    melody: list[tuple[int, float]],
    scale: list[int],
    rhythm_pattern: list[float],
    rate: float,
) -> list[tuple[int, float]]:
    """Randomly alter individual notes and/or durations in a melody.

    Each note and each duration is independently replaced with probability
    `rate`, keeping exploration alive without destroying good structure.

    Args:
        melody:         Melody to mutate.
        scale:          Pool of legal MIDI note numbers.
        rhythm_pattern: Pool of legal durations.
        rate:           Probability of mutating any single note or duration.

    Returns:
        New melody (same length) with mutations applied.
    """
    result: list[tuple[int, float]] = []
    for note, dur in melody:
        if random.random() < rate:
            note = random.choice(scale)
        if random.random() < rate:
            dur = random.choice(rhythm_pattern)
        result.append((note, dur))
    return result


# ---------------------------------------------------------------------------
# 4.5  Main evolution loop
# ---------------------------------------------------------------------------

def evolve(
    population: list,
    scale: list[int],
    chord_pool: list[int],
    rhythm_pattern: list[float],
    generations: int,
    mutation_rate: float,
) -> tuple[list[tuple[int, float]], float]:
    """Evolve the population for a fixed number of generations.

    Each generation:
      1. Score every melody with the fitness function.
      2. Select the top half as survivors (elitism).
      3. Fill the remaining slots with crossover + mutated offspring.
      4. Print a progress line on generation 1, every 10th, and the last.

    Args:
        population:    Initial list of melodies.
        scale:         Scale MIDI notes used for mutation and fitness.
        chord_pool:    Chord tone MIDI notes used by the fitness function.
        rhythm_pattern: Duration pool for mutation.
        generations:   Number of evolutionary cycles to run.
        mutation_rate: Per-note probability of random replacement.

    Returns:
        Tuple of (best_melody, best_fitness_score) from the final generation.
    """
    for gen in range(1, generations + 1):
        scores = [fitness(m, scale, chord_pool) for m in population]
        best_score = max(scores)

        if gen == 1 or gen % 10 == 0 or gen == generations:
            print(f"Generation {gen:4d} | best fitness: {best_score:.4f}")

        survivors = select(population, scores)

        offspring: list = []
        while len(survivors) + len(offspring) < len(population):
            a, b = random.sample(survivors, 2)
            child = crossover(a, b)
            child = mutate(child, scale, rhythm_pattern, mutation_rate)
            offspring.append(child)

        population = survivors + offspring

    # pick the single best melody from the final generation
    final_scores = [fitness(m, scale, chord_pool) for m in population]
    best_idx = final_scores.index(max(final_scores))
    return population[best_idx], max(final_scores)


# ---------------------------------------------------------------------------
# Spot-check (run: python3 genetic.py)
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    from music_theory import build_scale, chord_notes, RHYTHM_PATTERNS
    from markov import build_transition_matrix

    scale       = build_scale('C', 'major', octaves=(4, 5))
    chord_pool  = chord_notes(scale, 'I')
    rhythm      = RHYTHM_PATTERNS[1]
    matrix      = build_transition_matrix(scale)

    POP_SIZE   = 20
    NUM_NOTES  = 16
    GENS       = 30

    # --- population initialisation
    pop = init_population(POP_SIZE, scale, matrix, NUM_NOTES, rhythm)
    assert len(pop) == POP_SIZE,    f"Expected {POP_SIZE} melodies, got {len(pop)}"
    assert len(pop[0]) == NUM_NOTES, f"Expected {NUM_NOTES} notes per melody"
    print(f"Population: {POP_SIZE} melodies × {NUM_NOTES} notes  OK")

    # --- selection keeps exactly half
    scores = [fitness(m, scale, chord_pool) for m in pop]
    survivors = select(pop, scores)
    assert len(survivors) == POP_SIZE // 2, "Selection must keep exactly half"
    print(f"Selection:  {len(survivors)} survivors from {POP_SIZE}  OK")

    # --- crossover produces correct length
    child = crossover(pop[0], pop[1])
    assert len(child) == NUM_NOTES, "Child must have same length as parents"
    print(f"Crossover:  child length = {len(child)}  OK")

    # --- mutation respects scale and rhythm pool
    mutated = mutate(pop[0], scale, rhythm, rate=1.0)   # rate=1.0 → mutate everything
    assert len(mutated) == NUM_NOTES
    assert all(n in scale for n, _ in mutated), "All mutated notes must be in scale"
    assert all(d in rhythm for _, d in mutated), "All mutated durations must be in rhythm pool"
    print(f"Mutation:   all notes in scale, all durations in pool  OK")

    # --- fitness must improve (or hold) over generations
    initial_best = max(fitness(m, scale, chord_pool) for m in pop)
    print(f"\nEvolving for {GENS} generations...")
    best_melody, final_best = evolve(
        pop, scale, chord_pool, rhythm,
        generations=GENS,
        mutation_rate=0.05,
    )
    assert final_best >= initial_best, "Fitness must not decrease after evolution"
    assert len(best_melody) == NUM_NOTES, "Best melody must have correct length"
    print(f"\nInitial best: {initial_best:.4f}  →  Final best: {final_best:.4f}")
    print("Fitness improved (or held)  OK")
    print("\nAll checks passed.")
