
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

def create_variables_from_spec(spec, default_domain):
    return map( lambda s: {"domain": filter( lambda d: d + s <= len(default_domain)
                                           , default_domain[:])
                          ,"length": s}
              , spec)



row_variables = map(lambda s: create_variables_from_spec(s, row_default_domain), row_specs)
col_variables = map(lambda s: create_variables_from_spec(s, col_default_domain), col_specs)


print row_variables[0]



# print "row specs:",row_specs
# print "col specs:",col_specs

# print row_default_domain
# print col_default_domain
