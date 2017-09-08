from astar import backtrack
import time


def dfs(
        board,
        generate_successors,
        is_terminal,
        hash_function,
        display = None):
    started = time.time()*1000
    closed_set = []
    open_set = [board]
    parent = {}
    counter = 0
    while open_set:
        counter = counter + 1
        current = open_set.pop()
        closed_set.append(current)
        if is_terminal(current):
            print "-"*80
            print "Elapsed time:   " + str(round((time.time() * 1000) - started)) + " ms"
            print "--------------------"
            print "Open nodes:     " + str(len(open_set))
            print "Closed nodes:   " + str(len(closed_set))
            print "Total nodes:    " + str(len(open_set) + len(closed_set))
            print "--------------------"
            backtrack(current, parent, display, hash_function)
            print "-"*80
            return True
        for neighbour in generate_successors(current):
            if neighbour in closed_set or neighbour in open_set:
                continue
            open_set.append(neighbour)
            parent[hash_function(neighbour)] = current

    return False
