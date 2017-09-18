import numpy as np
import sys
from termcolor import colored
from collections import deque
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

def makefunc(var_names, expression, envir=globals()):
    args = ",".join(var_names)
    return eval("(lambda " + args + ": " + expression + ")", envir)

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

# recursively extend a minimum placement list until it is the correct length
def generate_domain(wip_result, insert_positions, target_length):
    if len(wip_result) == target_length:
        return [wip_result]
    result = []
    for i in range(len(insert_positions)):
        new_wip = wip_result[:]
        new_wip.insert(insert_positions[i], 0)
        new_pos = insert_positions[:]
        for j in range(i, len(insert_positions)):
            new_pos[j] = new_pos[j] + 1
        result.extend(generate_domain(new_wip, new_pos, target_length))
    return list(map(list, set(map(tuple, result))))

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

# Espen sin variant

# def create_variables(specifications, is_row, target_length):
#     return map( lambda (i, spec): { "index": i
#                                   , "is_row": is_row
#                                   , "value": None
#                                   , "domain": generate_domain( *generate_minimum_placement(spec)
#                                                              , target_length = target_length
#                                                              )
#                                   }
#               , enumerate(specifications))

# Markus sin variant

def create_variables(specifications, is_row, target_length):
  return map( lambda (i, spec): { "index": i
                                , "is_row": is_row
                                , "name": "R" + str(i) if is_row else "C" + str(i)
                                , "value": None
                                , "domain": create_domain(target_length, spec)
                                }
            , enumerate(specifications))

row_variables = create_variables(row_specs, True, number_of_cols)
col_variables = create_variables(col_specs, False, number_of_rows)

variables = row_variables[:]
variables.extend(col_variables[:])

intersection_constraint = makefunc(["row", "col"], "row['value'][col['index']] == col['value'][row['index']]")


# row-col
constraints = map( lambda pair: { "variables": pair
                                , "function": intersection_constraint}
                 , itertools.product(row_variables, col_variables))

# col-row
constraints.extend(map( lambda pair: { "variables": pair
                                     , "function": intersection_constraint}
                      , itertools.product(col_variables, row_variables)))



def print_result(variables):
    rows = filter(lambda v: v["is_row"], variables)
    print colored(' ', 'white', attrs=['reverse', 'blink']) * (number_of_cols * 2 + 3)
    for row in rows:
        print colored(' ', 'white', attrs=['reverse', 'blink']),
        for c in row["domain"][0]:
            if c:
                print colored(' ', 'red', attrs=['reverse', 'blink']),
            else:
                print ' ',
        print colored(' ', 'white', attrs=['reverse', 'blink'])
    print colored(' ', 'white', attrs=['reverse', 'blink']) * (number_of_cols * 2 + 3)


def revise(C):
    new_domain = []
    X, Y = C["variables"]
    for dX in X["domain"]:
        X["value"] = dX
        for dY in Y["domain"]:
            Y["value"] = dY
            if X["is_row"]:     # row-col constraint
                if apply(C["function"], (X, Y)):
                    if dX not in new_domain:
                        new_domain.append(dX)
                    continue
            else:               #col-row constraint
                if apply(C["function"], (Y, X)):
                    if dX not in new_domain:
                        new_domain.append(dX)
                    continue
    reduced = len(X["domain"]) > len(new_domain)
    X["domain"] = new_domain
    return reduced


def solve(variables, constraints):
    # Initialize
    queue = deque([])
    for c in constraints:
        queue.append(c)

    # Domain Filtering Loop
    while queue:
        Ci = queue.popleft()
        reduced = revise(Ci)
        if reduced:
            for Ck in constraints:
                if Ci["variables"][0] == Ck["variables"][1]:
                    queue.append(Ck)
                # if Ck != Ci:
                #     if Ci["variables"][0] == Ck["variables"][1] and Ci["variables"][0] != Ck["variables"][0]:
                #         queue.append(Ck)

    print_result(variables)

cProfile.run('solve(variables, constraints)')

# for variable in row_variables:
#     print len(variable["domain"])
