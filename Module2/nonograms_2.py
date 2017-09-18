import numpy as np
import sys
from termcolor import colored
from collections import deque
from copy import copy, deepcopy
sys.path.append('../')
from astar import astar
import itertools
import cProfile


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

# for example: [1,2] results in the following list: [1,0,1,1]
def generate_minimum_placement(spec):
    insert_positions = [0]
    result = []
    for item in spec:
        result.extend([1] * item)
        result.append(0)
        insert_positions.append(len(result) -1)
    result.pop()
    return (result, insert_positions)


def create_domain(length, specifications):
    # generate minimum placement
    domain = []
    min_placement = []
    for s in specifications:
        for i in range(s):
            min_placement.append(1)
        min_placement.append(0)
    min_placement.pop(len(min_placement) - 1)

    insert_indices = [i + 1 for i, x in enumerate(min_placement) if x == 0]
    insert_indices.extend([0, len(min_placement)])
    combinations = itertools.combinations_with_replacement(insert_indices, length - len(min_placement))
    for c in combinations:
        result = min_placement[:]
        insert_positions = list(c)
        insert_positions.sort()
        offset = 0
        for index in insert_positions:
            result.insert(index + offset, 0)
            offset += 1
        domain.append(result)
    return domain


domains = {}

def create_variables_2(specifications, is_row, target_length):
    variables = []
    for (i, spec) in enumerate(specifications):
        variable_name = "R" + str(i) if is_row else "C" + str(i)
        domains[variable_name] = create_domain(target_length, spec)
        variables.append(variable_name)
    return variables

variables2 = create_variables_2(row_specs, True, number_of_cols)
variables2.extend(create_variables_2(col_specs, False, number_of_rows))

constraint_pairs = list(itertools.product( filter(lambda v: v[0] == 'R', variables2)
                                         , filter(lambda v: v[0] == 'C', variables2)))
constraint_pairs.extend(itertools.product( filter(lambda v: v[0] == 'C', variables2)
                                         , filter(lambda v: v[0] == 'R', variables2)))





def print_result(variables, domain):
    rows = filter(lambda v: is_row(v), variables)
    print colored(' ', 'white', attrs=['reverse', 'blink']) * (number_of_cols * 2 + 3)
    for row in rows:
        print colored(' ', 'white', attrs=['reverse', 'blink']),
        for c in domain[row][0]:
            if c:
                print colored(' ', 'red', attrs=['reverse', 'blink']),
            else:
                print ' ',
        print colored(' ', 'white', attrs=['reverse', 'blink'])
    print colored(' ', 'white', attrs=['reverse', 'blink']) * (number_of_cols * 2 + 3)


def is_row(variable):
    return variable[0] == "R"

def get_index_from_variable(variable):
    return int(variable[1:])

def check_constraint(row, row_index, col, col_index):
    return row[col_index] == col[row_index]

def revise_2(X, Y, domains):
    new_domain = []
    for dX in domains[X]:
        for dY in domains[Y]:
            if is_row(X):
                if check_constraint(dX, get_index_from_variable(X), dY, get_index_from_variable(Y)):
                    if dX not in new_domain:
                        new_domain.append(dX)
                    continue
            else:
                if check_constraint(dY, get_index_from_variable(Y), dX, get_index_from_variable(X)):
                    if dX not in new_domain:
                        new_domain.append(dX)
                    continue
    reduced = len(domains[X]) > len(new_domain)
    domains[X] = new_domain
    return reduced

def find_successor(open_set, cost, heuristic):
    return open_set[0]

def generate_successors(current):
    variables = current.keys()
    successors = []
    for var in variables:
        for p in current[var]:
            child = deepcopy(current)
            child[var] = [p]
            successors.append(child)
    return successors

def heuristic(board):
    return 0

def is_terminal(board):
    return len(board.keys()) == len(filter(lambda v: len(v) == 1, board.values()))

def hash_function(a):
    return str(a)

def solve_2(variables, constraints, domains):
    queue = deque([])
    for c in constraints:
        queue.append(c)

    while queue:
        X, Y = queue.popleft()
        reduced = revise_2(X, Y, domains)
        if reduced:
            for Ck in constraints:
                if X == Ck[1]:
                    queue.append(Ck)

    if len(filter(lambda v: len(domains[v]) > 1, variables)) != 0:    # are all domains reduced to 1
        print astar(domains, find_successor, generate_successors, heuristic, is_terminal, hash_function)
    else:
        print_result(variables, domains)



# cProfile.run('solve(variables, constraints)')
solve_2(variables2, constraint_pairs, domains)
# for variable in row_variables:
#     print len(variable["domain"])
