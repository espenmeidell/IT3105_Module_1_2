
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
                          ,"is_row": is_row
                          ,"number": number}
              , spec)


def makefunc(var_names, expression, envir=globals()):
    args = ",".join(var_names)
    return eval("(lambda " + args + ": " + expression + ")", envir)

pair_constraint = makefunc(["a", "b"], "b['start'] > a['start'] + a['length']")

#intersection_constraint = makefunc(["a", "b"], "")

# print apply(pair_constraint, [{"start": 0, "length": 2}, {"start":3, "length": 1}])

row_variables = map(lambda (i,s): create_variables_from_spec(s, row_default_domain, True, i), enumerate(row_specs))
col_variables = map(lambda (i,s): create_variables_from_spec(s, col_default_domain, False, i), enumerate(col_specs))


constraints = []

for i in range(len(row_variables)):
    for j in range(len(row_variables[i])-1):
        constraints.append((row_variables[i][j], row_variables[i][j+1]))

for i in range(len(col_variables)):
    for j in range(len(col_variables[i])-1):
        constraints.append((col_variables[i][j], col_variables[i][j+1]))


for row in col_variables:
    print row

# print "row specs:",row_specs
# print "col specs:",col_specs

# print row_default_domain
# print col_default_domain
