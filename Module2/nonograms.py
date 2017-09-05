
import sys


first_line = sys.stdin.readline().split(" ")
number_of_columns = int(first_line[0].strip())
number_of_rows = int(first_line[1].strip())

row_constraints = []
column_constraints = []

row_counter = 0
for line in sys.stdin:
    str_array = line.split(" ")
    int_array = map(int, str_array)
    if row_counter < number_of_rows:
        row_counter += 1
        row_constraints.append(int_array)
    else:
        column_constraints.append(int_array)

print "row constraints:",row_constraints
print "column constraints:",column_constraints
