import numpy as np
import sys
from termcolor import colored
from collections import deque
from copy import copy, deepcopy
sys.path.append('../')
from astar import astar
import itertools
import cProfile



'''
        Read specifications from input
'''

first_line = sys.stdin.readline().split(" ")
number_of_cols = int(first_line[0].strip())
number_of_rows = int(first_line[1].strip())

row_specs = []
col_specs = []

row_counter = 0
for line in sys.stdin:
    str_array = line.split(" ")
    int_array = map(int, str_array)
    if row_counter < number_of_rows:
        row_counter += 1
        row_specs.append(int_array)
    else:
        col_specs.append(int_array)

row_specs.reverse()

'''
        Functions to create variables, domains and
        constraints for the specifications
'''

# for example: [1,2] results in the following list: [1,0,1,1]. This list is
# returned together with a list of positions we can insert zeros
def generate_minimum_placement(spec):
    insert_positions = [0]
    result = []
    for item in spec:
        result.extend([1] * item)
        result.append(0)
        insert_positions.append(len(result) -1)
    result.pop()
    return (result, insert_positions)

# Creates the domain of possible values of a certain length, given a specification
def create_domain(length, specifications):

    min_placement, insert_indices = generate_minimum_placement(specifications)
    domain = []
    number_to_insert = length - len(min_placement)

    # We need to insert number_to_insert zeros to achieve the correct length.
    # to do this we generate all length - len(min_placement) combination with replacements of the insert_indices,
    # that are of that length. This list will tell us where to insert each zero.
    combinations = itertools.combinations_with_replacement(insert_indices, number_to_insert)

    for c in combinations:
        result = min_placement[:]
        insert_positions = list(c)
        insert_positions.sort()
        # Once we insert a zero we have to increase all the following indices
        # to prevent destroying the pattern. To do this we use the offset variable
        offset = 0
        for index in insert_positions:
            result.insert(index + offset, 0)
            offset += 1
        domain.append(result)
    return domain


def create_variables(specifications, is_row, target_length):
    variables = []
    for (i, spec) in enumerate(specifications):
        variable_name = "R" + str(i) if is_row else "C" + str(i)
        domains[variable_name] = create_domain(target_length, spec)
        variables.append(variable_name)
    return variables

'''
        Define the variables, domains and constraint pairs
'''

domains = {}

variables = create_variables(row_specs, True, number_of_cols)
variables.extend(create_variables(col_specs, False, number_of_rows))


constraint_pairs = list(itertools.product( filter(lambda v: v[0] == 'R', variables)
                                         , filter(lambda v: v[0] == 'C', variables)))
constraint_pairs.extend(itertools.product( filter(lambda v: v[0] == 'C', variables)
                                         , filter(lambda v: v[0] == 'R', variables)))

# the constraint used in the puzzle
def evaluate_intersection(X, Y, value_X, value_Y):
    return value_X[get_index_from_variable(Y)] == value_Y[get_index_from_variable(X)]


'''
        Utility functions
'''

# checks if a variable is a row
def is_row(variable):
    return variable[0] == "R"

# Takes a varaible (string) and returns its index in the puzzle
def get_index_from_variable(variable):
    return int(variable[1:])

# Prints the nonogram in a pretty way
def print_result(variables, domain):
    rows = filter(lambda v: is_row(v), variables)
    print
    print colored(' ', 'white', attrs=['reverse', 'blink']) * (number_of_cols * 2 + 3)
    for row in rows:
        print colored(' ', 'white', attrs=['reverse', 'blink']),
        if len(domain[row]) == 1:
            for c in domain[row][0]:
                if c:
                    print colored(' ', 'red', attrs=['reverse', 'blink']),
                else:
                    print ' ',
        else:
            print ' ' * ((number_of_cols * 2)-1),
        print colored(' ', 'white', attrs=['reverse', 'blink'])

    print colored(' ', 'white', attrs=['reverse', 'blink']) * (number_of_cols * 2 + 3)


'''
        A* Functions
'''
# finds the best successor, currently only using the heuristic score
def find_successor(open_set, cost, heuristic):
    bestcost = float("inf")
    bestboard = None
    for board in open_set:
        if heuristic(board) < bestcost:
            bestboard = board
            bestcost = heuristic(board)
    return bestboard

# Create successor state by creating new triples where the domain is cloned and
# reduced using the domain_filtering_loop function.
def generate_successors(current):
    successors = []
    # sorted_variables = current[0][:]                              # sort by length of domain
    # sorted_variables.sort(key=lambda v: len(current[1][v]))       # sort by length of domain
    for var in current[0]:
        for p in current[1][var]:
            child_domain = deepcopy(current[1])
            child_domain[var] = [p]
            # Reduce domain of successors
            queue = deque([])
            for c in current[2]:
                if var == c[1]:
                    queue.append(c)
            domain_filtering_loop(queue, child_domain, current[2], evaluate_intersection)
            # Only retain successor if it is a legal state
            if (all(len(child_domain[v]) > 0 for v in current[0])):
                successors.append((current[0], child_domain, current[2]))
    return successors

# The sum of the length of the domains in the current state, a useful constraint
# when selecting the next state to investigate
def heuristic(state):
    return sum(map(lambda d: len(d), state[1].values()))

# Check if the domain length for each variable is 1
def is_terminal(state):
    return len(state[0]) == len(filter(lambda v: len(v) == 1, state[1].values()))

# Create a hash of the domain
def hash_function(s):
    return str(s[1])

'''
        CSP Functions
'''

# Uses the evaluate_variables function to remove illegal values in the domains of
# the two variables, X and Y
def revise(X, Y, domains, evaluate_variables):
    new_domain = []
    for dX in domains[X]:
        for dY in domains[Y]:
            if evaluate_variables(X, Y, dX, dY):
                if dX not in new_domain:
                    new_domain.append(dX)
                break

    reduced = len(domains[X]) > len(new_domain)
    domains[X] = new_domain
    return reduced

# Will filter the domains for variables in the constraint pairs
def domain_filtering_loop(queue, domains, constraints, evaluate_variables):
    done_domain_count = len(filter(lambda d: len(d) == 1, domains.values()))                # DISPLAY CODE
    while queue:
        X, Y = queue.popleft()
        reduced = revise(X, Y, domains, evaluate_variables)
        if reduced:
            new_done_domain_count = len(filter(lambda d: len(d) == 1, domains.values()))    # DISPLAY CODE
            if new_done_domain_count > done_domain_count:                                   # DISPLAY CODE
                done_domain_count = new_done_domain_count                                   # DISPLAY CODE
                print_result(variables, domains)                                            # DISPLAY CODE
            for Ck in constraints:
                if X == Ck[1]:
                    queue.append(Ck)

# Takes a list of variables, dictionary of domains, constrains between
# the variables and a function that evaluates possible values for two
# variables.
def solve(variables, domains, constraints, evaluate_variables):
    queue = deque([])
    for c in constraints:
        queue.append(c)

    domain_filtering_loop(queue, domains, constraints, evaluate_variables)

    if any(map(lambda v: len(domains[v]) > 1, variables)):
        result = astar((variables, domains, constraints)
                      , find_successor
                      , generate_successors
                      , heuristic
                      , is_terminal
                      , hash_function)
        print_result(result[1][0], result[1][1])

    elif any(map(lambda v: len(domains[v]) == 0, variables)):
        print "No solution found, got this far: "
        print_result(variables, domains)
    else:
        print_result(variables, domains)


'''
        Launching
'''

# cProfile.run('solve(variables, domains, constraint_pairs, evaluate_intersection)')
solve(variables, domains, constraint_pairs, evaluate_intersection)
