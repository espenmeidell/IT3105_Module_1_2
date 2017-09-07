import time
# --------------------------------
# -------------- A* --------------
# --------------------------------

#Create a history of boards to reach the current board. Used to visualize the process
#Can calculate how many moves to reach goal, as well display all steps
def backtrack(node, parent, display_function, hash_function):
    history = []
    while hash_function(node) in parent.keys():
        history.append(node)
        node = parent[hash_function(node)]
    history.reverse()
    print "Solution Found:", len(history), "moves"
    if display_function is not None:
        counter = 1
        for board in history:
            display_function(board, counter)
            counter = counter + 1

#Generic A* code
def astar(
        board,
        find_successor,
        generate_successors,
        heuristic,
        is_terminal,
        hash_function = lambda x: x,
        display = None):
    started = time.time()*1000
    closed_set = set() # visited boards
    open_set = [board] # unvisited
    # parent and costs maps with the hashed boards
    parent = {}
    cost = {hash_function(board): 0}
    while open_set:
        current = find_successor(open_set, cost, heuristic)
        if is_terminal(current):
            print "-"*80
            print "Heuristic:      " + heuristic.__name__.replace("_"," ").title()
            print "Elapsed time:   " + str(round((time.time() * 1000) - started)) + " ms"
            print "--------------------"
            print "Open nodes:     " + str(len(open_set))
            print "Closed nodes:   " + str(len(closed_set))
            print "Total nodes:    " + str(len(open_set) + len(closed_set))
            print "--------------------"
            backtrack(current, parent, display, hash_function)
            print "-"*80
            return True
        open_set.remove(current)
        closed_set.add(hash_function(current))
        for neighbour in generate_successors(current):
            if hash_function(neighbour) in closed_set:
                continue

            if neighbour not in open_set:
                open_set.append(neighbour)
            tentative_score = cost[hash_function(current)] + 1
            if tentative_score >= cost.get(hash_function(neighbour), float("inf")):
                continue
            parent[hash_function(neighbour)] = current
            cost[hash_function(neighbour)] = tentative_score
    return False
