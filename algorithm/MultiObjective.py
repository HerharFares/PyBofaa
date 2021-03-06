from typing import List, Tuple, Set
from random import sample, randint, random

from models.Solution import Solution


class MultiObjective:
    @staticmethod
    def init_population(fragments_number: int, population_size: int) -> Tuple[List[Solution], Set[int]]:
        """This function create the initial population for the NSGA-II algorithm.

        ...

        Parameters
        ----------
        fragments_number: int
            The number of the fragments, since our solution must be a combination
            of all the fragments, therefore the solution will be only a combination
            of indexes for these fragments, stored in another variable.
        population_size: int
            The size of the wanted initial population.

        Returns
        -------
        list
            A list of Solution.
        """

        l = [i for i in range(fragments_number)]  # Our fragments, indexes

        # The hash values of each solution to avoid redundancy.
        hash_values = set()
        solutions = list()  # The list of solutions.

        count = 0  # To check if we've reached the number of the wanted population
        while count != population_size:
            sol = sample(l, fragments_number)
            # We can't calculate the hash value of mutable objects.
            hash_val = hash(tuple(sol))

            # Check if the solution already exists.
            if hash_val not in hash_values:
                hash_values.add(hash_val)
                solutions.append(Solution(sol, generation=0))
                count += 1

        return solutions, hash_values

    @staticmethod
    def domination(sol_1: Solution, sol_2: Solution) -> int:
        """This function test the dominance, between two solutions
        based on the two objective function listed above.
        It is for The Non-Domination Sorting Algorithm.

        ...

        Parameters
        ----------
        sol_1: Solution
            The first solution.
        sol_2: Solution
            The second solution.

        Returns
        -------
        int
            An int value,
            if -1 sol_1 dominates sol_2.
            if 1 sol_2 dominates sol_1.
            if 0 neither dominates the other.
        """
        if (sol_1.oaf >= sol_2.oaf) and (sol_1.odf < sol_2.odf):
            return -1
        elif (sol_2.oaf >= sol_1.oaf) and (sol_2.odf < sol_1.odf):
            return 1
        else:
            return 0

    @staticmethod
    def non_dominate_sorting(population: List[Solution]) -> List[List[int]]:
        """This fonction is for the non dominate sorting for the NSGA-II Algorithm,
        The how the function works wont be explained here, look at the full Algorithm
        online, or take a look at the research paper.
        It returns the fonts, where each font is a list of integers, that represents
        the indexes of the solutions, in the population list.

        ...

        Parameters
        ----------
        population: list
            A list of solutions.


        Returns
        -------
        list
            A list of lists of integers.
        """
        # It contains all our fonts, in which each solutoin belongs to only one.
        fonts = [[]]
        # Each solution my dominate other solutions, in that case they are stores here.
        dominated = [[] for i in range(len(population))]
        # In case a solution gets dominated by another solution, we store how many times.
        dominate_number = [0 for i in range(len(population))]

        # STEP-1: Calculation the first Font.
        for p in range(len(population)):
            for q in range(len(population)):
                # Go to the domination function.
                d = MultiObjective.domination(population[p], population[q])
                if d == -1:
                    dominated[p].append(q)
                if d == 1:
                    dominate_number[p] += 1
            if dominate_number[p] == 0:
                fonts[0].append(p)
                # set the rank to one, since it belongs to the first font.
                population[p].rank = 1

        # STEP-2: Calculating the rest of the Fonts.
        fonts_counter = 1

        while fonts_counter <= len(fonts):
            for p in fonts[fonts_counter - 1]:
                for q in dominated[p]:
                    dominate_number[q] -= 1

                    # if the solution is no longer dominated, add it to the next Front.
                    if dominate_number[q] == 0:
                        # set the rank to one, since it belongs to the next font.
                        population[q].rank = fonts_counter + 1
                        if len(fonts) == fonts_counter:
                            fonts.append([q])
                        else:
                            fonts[-1].append(q)
            fonts_counter += 1

        return fonts

    @staticmethod
    def crowding_distance(population: List[Solution], fonts: List[List[int]]) -> List[float]:
        """This function is for calculation the crowding distance of each solution.
        at first we sort the solution, for each front based on oaf values,
        and odf values separately, while odf ascendant dort, and oaf is descendant sort.
        After that, we calculate the crownding distance for each solution,
        with oaf and odf sorts, and exluding the limits of each sorted font(first and last element),
        we set them to -1. Than, we chack if the values match the excluded and sum them.
        It returns a list of floats, that represents the crowding distances for each solution.

        ...

        Parameters
        ----------
        population: list
            A list of solutions.
        fonts: list
            A list of Fonts(list of int).


        Returns
        -------
        list
            A list of integers, that represents the crowding distance of each solution.
        """
        # Each fonts, will be sorted first by oaf, then odf
        # while maximize oaf, and minimize odf
        oaf_sorted_fonts = []
        odf_sorted_fonts = []

        # The crowding will be calculated, by oaf, odf separately, than summed
        oaf_cwrowding = [0 for i in range(len(population))]
        odf_cwrowding = [0 for i in range(len(population))]
        crowding = [0.0 for i in range(len(population))]

        # STEP-0 sorting
        for p in fonts:
            if len(p) == 1:
                oaf_sorted_fonts.append(p)
                odf_sorted_fonts.append(p)
            if len(p) > 1:
                temp = [population[q] for q in p]

                # Sort by oaf, reversed for acendant
                temp.sort(key=lambda sol: sol.oaf, reverse=True)
                oaf_sorted_fonts.append([population.index(q) for q in temp])
                # Sort by odf, not reversed for desandant
                temp.sort(key=lambda sol: sol.odf)
                odf_sorted_fonts.append([population.index(q) for q in temp])

        # STEP-1 calculate crowding distances
        # STEP-1.1 for oaf
        for p in oaf_sorted_fonts:
            oaf_cwrowding[p[0]] = -1
            # The fraction of max - min
            kill = population[p[0]].oaf - \
                population[p[-1]].oaf
            if len(p) > 1:
                temp_oaf = 0
                oaf_cwrowding[p[-1]] = -1
                # calculating the oaf crowding for each element of the font, excluding limits
                for q in range(1, len(p) - 1):
                    # In case a division by zero, which means infinity(Maths limits)
                    # so it goes by -1, as an indecation, as the boundries(limits)
                    try:
                        temp_oaf += (population[p[q - 1]].oaf -
                                     population[p[q + 1]].oaf) / kill
                        oaf_cwrowding[p[q]] = temp_oaf
                    except ZeroDivisionError:
                        oaf_cwrowding[p[q]] = -1

        # STEP-1.2 for odf
        for p in odf_sorted_fonts:
            odf_cwrowding[p[0]] = -1
            # The fraction of (max - min)
            kill = population[p[-1]].odf - \
                population[p[0]].odf
            if len(p) > 1:
                temp_odf = 0
                odf_cwrowding[p[-1]] = -1
                # calculating the oaf crowding for each element of the font, excluding limits
                for q in range(1, len(p) - 1):
                    # In case a division by zero, which means infinity(Maths limits)
                    # so it goes by -1, as an indecation, as the boundries(limits)
                    try:
                        temp_odf += (population[p[q + 1]].odf -
                                     population[p[q - 1]].odf) / kill
                        odf_cwrowding[p[q]] = temp_odf
                    except ZeroDivisionError:
                        odf_cwrowding[p[q]] = -1

        # STEP-2 assembling crowding distances
        # since we sort twice, for odf and oaf, so some solution get exluded
        # in one sort, and not in another, there for we will check
        for index in range(len(population)):
            if oaf_cwrowding[index] == -1 or odf_cwrowding[index] == -1:
                crowding[index] = float(-1)
                population[index].crowding_distance = float(-1)
            else:
                crowding[index] = float(
                    oaf_cwrowding[index] + odf_cwrowding[index])
                population[index].crowding_distance = float(oaf_cwrowding[index] +
                                                            odf_cwrowding[index])

        return crowding
