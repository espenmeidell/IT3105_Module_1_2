
import sys


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

row_default_domain = [x for x in range(number_of_cols)]
col_default_domain = [x for x in range(number_of_rows)]

def create_variables_from_spec(spec, default_domain, is_row, number):
    return map( lambda s: {"start" : -1
                          ,"domain": filter( lambda d: d + s <= len(default_domain)
                                           , default_domain[:])
                          ,"length": s
                          ,"number": number}
              , spec)


# Helper function to make a function from the params
def makefunc(var_names, expression, envir=globals()):
    args = ",".join(var_names)
    return eval("(lambda " + args + ": " + expression + ")", envir)


# Checks if the index is occupied given a set of variables
# Used to check intersections
def occupied_cell(index, variables):
    for var in variables:
        start_pos = var["start"]
        if start_pos == -1:
            continue
        if start_pos <= index and start_pos + var["length"] >= index:
            return True
    return False

pair_constraint = makefunc(["a", "b"], "b['start'] > a['start'] + a['length']")
intersection_constraint = makefunc(["a", "b"], "occupied_cell(b[0]['number'], a) == occupied_cell(a[0]['number'], b)")

row_variables = map(lambda (i,s): create_variables_from_spec(s, row_default_domain, True, i),
                    enumerate(row_specs))
col_variables = map(lambda (i,s): create_variables_from_spec(s, col_default_domain, False, i),
                    enumerate(col_specs))


constraints = []
# row pair_constraints
for i in range(len(row_variables)):
    for j in range(len(row_variables[i])-1):
        constraints.append(
            {
                "variables":(row_variables[i][j], row_variables[i][j+1]),
                "function": pair_constraint
            })

# col pair_constraints
for i in range(len(col_variables)):
    for j in range(len(col_variables[i])-1):
        constraints.append(
            {
                "variables":(col_variables[i][j], col_variables[i][j+1]),
                "function": pair_constraint
            })

# all intersection_constraints
for row in row_variables:
    for col in col_variables:
        constraints.append(
            {
                "variables":(row,col),
                "function": intersection_constraint
            })

# flatten and join lists of variables
variables = [ item for sublist in row_variables for item in sublist] \
            + [ item for sublist in col_variables for item in sublist]

def select_unassigned_variable(variables):
    return next((v for v in variables if v["start"] == -1), None)

print select_unassigned_variable(variables)

# print "row specs:",row_specs
# print "col specs:",col_specs

# print row_default_domain
# print col_default_domain
