import numpy as np
import sys
from collections import deque
import itertools



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

def create_variables(specifications, is_row, target_length):
    return map( lambda (i, spec): { "index": i
                                  , "is_row": is_row
                                  , "value": None
                                  , "domain": generate_domain( *generate_minimum_placement(spec)
                                                             , target_length = target_length
                                                             )
                                  }
              , enumerate(specifications))

row_variables = create_variables(row_specs, True, number_of_cols)
col_variables = create_variables(col_specs, False, number_of_rows)

variables = row_variables[:]
variables.extend(col_variables[:])

intersection_constraint = makefunc(["row", "col"], "row['value'][col['index']] == col['value'][row['index']]")



constraints = map( lambda pair: { "variables": pair
                                , "function": intersection_constraint}
                 , itertools.product(row_variables, col_variables))

def revise(X, C):
    new_domain = []
    Y = C["variables"][1]
    for dX in X["domain"]:
        X["value"] = dX
        for dY in Y["domain"]:
            Y["value"] = dY
            if apply(C["function"], (X, Y)):
                if dX not in new_domain:
                    new_domain.append(dX)
                continue
    X["domain"] = new_domain

def solve(variables, constraints):
    # Initialize
    queue = deque([])
    for c in constraints:
        queue.append((c["variables"][0], c))

    # Domain Filtering Loop
    while queue:
        Xstar, Ci = queue.popleft()
        original_domain_length = len(Xstar["domain"])
        revise(Xstar, Ci)
        if original_domain_length < len(Xstar["domain"]):
            # print "YAY"
            for Ck in constraints:
                if Ck != Ci:
                    if Ck["variables"][1] == Xstar:
                        queue.append((Ck["variables"][0], Ck))





solve(variables, constraints)

for variable in row_variables:
    print len(variable["domain"])
