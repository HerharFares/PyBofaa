from time import time

from tools import read_fragments
from config import *
from scoring import *
from nsga2 import *


if __name__ == "__main__":
    # Counting the number of generations
    generation_counter = 1

    start = time()
    # STEP 0, reading fragments from file
    print("STEP-0 :: READING FRAGMENTS FROM FILE --> {}".format(BECHMARK_FILE))
    fragments = read_fragments(BECHMARK_FILE)

    # STEP 1, compute pair wise overlap
    print("STEP-1 :: CALCULATING THE OVERLAP SCORES.")
    scores = overlap_scores(fragments, MATCH_SCORE, MISMATCH_SCORE, GAP_COST)

    # STEP 2, generate initial population, and retreving the set of the solutions
    print("STEP-2 :: GENERATING SOLUTIONS (INITIAL POPULATION).")
    population = init_population(len(fragments), POPULATION_SIZE)
    population, hash_values = population[0], population[-1]

    while generation_counter <= GENERATIONS_NUMBER:
        print("GENERATION :: {}".format(generation_counter))

        print("\tG-{} --> STEP-3 :: CALCULATING OBJECTIVE FUNCTIONS.".format(generation_counter))
        # STEP 3, compute ODF and OAF fitness
        for sol in population:
            sol.oaf_objective(scores)
            sol.odf_objective(scores)

        print("\tG-{} --> STEP-4 :: CALCULATING AND ATTRIBUTING FONTS.".format(generation_counter))
        # STEP 4, calculate the fonts
        fonts = non_dominate_sorting(population)

        print("\tG-{} --> STEP-5 :: CALCULATING CROWDING DISTANCES.".format(generation_counter))
        # STEP 5, calculate the crowding distances
        crownding = crowding_distance(population, fonts)

        print("\tG-{} --> STEP-6 :: SELECTING SOLUTIONS POOL.".format(generation_counter))
        # STEP 6, select solutions for pool
        selection = select_cross_solutions(population, CROSS_OVER_PROBABILITY)

        # STEP 7, crossover and mutation
        print("\tG-{} --> STEP-7.1 :: OPERATING CROSSOVER.".format(generation_counter))
        # STEP 7.1, crossover
        childs = crossover(population, selection,
                           hash_values, generation_counter)

        print("\tG-{} --> STEP-7.2 :: OPERATING MUTATION.".format(generation_counter))
        # STEP 7.2, mutation
        childs.extend(mutation(population, selection,
                               hash_values, MUTATION_PROBABILITY, generation_counter))

        # STEP 8, offsoring
        print("\tG-{} --> STEP-8.1 :: CALCULATING OBJECTIVE FUNCTIONS FOR CHILDS.".format(generation_counter))
        # STEP 8.1, calculate oaf, odf to the childs
        for child in childs:
            child.oaf_objective(scores)
            child.odf_objective(scores)

        # STEP 8.2, merge child with current population
        print(
            "\tG-{} --> STEP-8.2 :: CREATING OFFSPRING POPULATION.".format(generation_counter))
        # to create offspring population
        population.extend(childs)

        print("\tG-{} --> STEP-8.3 :: CALCULATING AND ATTRIBUTING FONTS FOR THE OFFSPRING POPULATION.".format(generation_counter))
        # STEP 8.3, recalculate the fonts for the offspring population
        fonts = non_dominate_sorting(population)

        print("\tG-{} --> STEP-8.4 :: CALCULATING CROWDING DISTANCES FOR THE OFFSPRING POPULATION.".format(generation_counter))
        # STEP 8.4, recalculate the crowding distances for the offspring population
        crownding = crowding_distance(population, fonts)

        print("\tG-{} --> STEP-9 :: PASSING THE FIRST {} OFFSSPRING SOLUTION THE NEXT GENERATION POPULATION.".format(
            generation_counter, GENERATIONS_NUMBER))
        # STEP 9, passing the next first POPULATION_SIZE solutions
        temp = [index for indexes in fonts for index in indexes]
        population = [population[p] for p in temp[:POPULATION_SIZE]]

        generation_counter += 1

    for p in sorted(population, key=lambda x: x.rank):
        if p.rank == 1:
            p.contigs_number(scores)
            print(p)
            print("---------------")

    print("DONE.\n")
    print("EXECTION TIME:: {} Seconds.".format(round(time() - start)))
