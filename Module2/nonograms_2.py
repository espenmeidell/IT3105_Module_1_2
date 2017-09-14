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

def generate_minimum_placement(spec):
    insert_positions = [0]
    result = []
    for item in spec:
        result.extend([1] * item)
        result.append(0)
        insert_positions.append(len(result) -1)
    result.pop()
    return (result, insert_positions)

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
                                  , "domain": generate_domain( *generate_minimum_placement(spec)
                                                             , target_length = target_length
                                                             )
                                  }
              , enumerate(specifications))

print create_variables(row_specs, True, number_of_rows)[0]
