from PIL import Image, ImageDraw, ImageFont
from copy import copy, deepcopy
import cProfile
import sys
import os, shutil

#Use pillow to paint a board with some text and a number
def paintboard(board, iteration):
    im = Image.new("RGB", (6*50, 7*50), "white")
    draw = ImageDraw.Draw(im)
    y = 0
    for row in range(6):
        x = 0
        for col in range(6):
            draw.ellipse([(x+20, y+20), (x+30, y+30)], (0,0,0))
            x = x + 50
        y = y + 50
    colors = {1: "#F44336",2: "#E91E63",3: "#9C27B0",4: "#673AB7",5: "#3F51B5",6: "#2196F3",7: "#03A9F4",8: "#00BCD4",9: "#009688",10: "#4CAF50",11: "#8BC34A",12: "#CDDC39",13: "#FFEB3B"}
    for car in board:
        color = colors[board.index(car)+1]
        x = 50*car[1]
        y = 50*car[2]
        deltax = 0
        deltay = 0
        if not car[0]:    #horizontal
            deltax = 50
        else:           #vertical
            deltay = 50
        for i in range(car[3]):
            draw.rectangle([x, y, x+50, y+50], color)
            x = x + deltax
            y = y + deltay
    text = "Iteration #"+ str(iteration)
    draw.text((10, 310), text,(0,0,0))
    im.save("output/" + str(iteration) + ".png")

#Deletes the output of previous run
def delete_previous_output():
    folder = 'output'
    for img in os.listdir(folder):
        img_path = os.path.join(folder, img)
        try:
            if os.path.isfile(img_path):
                os.unlink(img_path)
        except Exception as e:
            print(e)

#Calculate the coordinates occupied by a given car
def get_car_coords(car):
    coords = []
    x = car[1]
    y = car[2]
    deltax = 0
    deltay = 0
    if car[0]:    #vertical
        deltay = 1
    else:           #horizontal
        deltax = 1
    for i in range(car[3]):
        coords.append((x,y))
        x = x + deltax
        y = y + deltay
    return coords


#Returnes wether the car is stuck or not
def isStuck(car, board):
    return calculate_options(car, board) == 0

#Returnes the car that is blocking the coordinate
def getBlockingCar(x,y, board):
    for car in board:
        if (x,y) in get_car_coords(car):
            return car

#Returnes 0 if the coordinate is not blocked
#1 if it is blocked or
#2 if it is blocked and the blocking car is stuck
def blockScore(x, y, board):
    if not is_blocked(x,y,board):
        return 0
    blockingCar = getBlockingCar(x,y, board)
    if isStuck(blockingCar, board):
        return 2
    return 1


#Checks if a certain coordinate is occupied by a car
def is_blocked(x, y, board):
    if x < 0 or x > 5 or y < 0 or y > 5:
        return True
    for car in board:
        if (x,y) in get_car_coords(car):
            return True
    return False

#Takes a car and a board and calculates the possible moves of that car in the board
def calculate_options(car, board):
    new_boards = []
    coords = get_car_coords(car)
    index = board.index(car)
    if car[0]:  #vertical
        if not is_blocked(coords[0][0],coords[0][1]-1, board): #move up
            nb = deepcopy(board)
            nb[index][2] = nb[index][2]-1
            new_boards.append(nb)
        if not is_blocked(coords[len(coords)-1][0],coords[len(coords)-1][1]+1, board): #move down
            nb = deepcopy(board)
            nb[index][2] = nb[index][2]+1
            new_boards.append(nb)
    else:       #horizontal
        if not is_blocked(coords[0][0]-1,coords[0][1], board): #move right
            nb = deepcopy(board)
            nb[index][1] = nb[index][1]-1
            new_boards.append(nb)
        if not is_blocked(coords[len(coords)-1][0]+1,coords[len(coords)-1][1], board): #move left
            nb = deepcopy(board)
            nb[index][1] = nb[index][1]+1
            new_boards.append(nb)
    return new_boards

#For each car in the board, calculate the moves it can do and return them as a list
def get_neighbours(board):
    neighbours = []
    for car in board:
        neighbours.extend(calculate_options(car, board))
    return neighbours

#Check if red car is in winning position
def is_won(board):
    return board[0][1] + board[0][3] -1 == 5

#Our best attempt at a heuristic function. Turns out, its not good...
def simple_blocking_and_manhattan(board):
    return  simple_blocking(board) + manhattan(board)

def simple_blocking(board):
    n = 0
    for i in range(board[0][1]+2, 6):   #how many of those are blocked?
        if is_blocked(i, 2, board):
            n = n + 1
    return  n

def manhattan(board):
    return  4 - board[0][1]


def zero_heuristic(board):
    return 0


#Iterates through the open set and returns the best board in it
def get_best_board(open_set, cost, heuristic):
    bestcost = float("inf")
    bestboard = None
    for board in open_set:
        if cost[hash_board(board)] + heuristic(board) < bestcost:
            bestboard = board
            bestcost = cost[hash_board(board)] + heuristic(board)
    return bestboard

#Python cannot hash lists, so to be able to use them as keys in dictionaries
#we created a custom hash function
def hash_board(board):
    return ', '.join(str(x) for x in sum(board, []))

#Create a history of boards to reach the current board. Used to visualize the process
#Can calculate how many moves to reach goal, as well display all steps
def backtrack(node, parent, display):
    history = []
    while hash_board(node) in parent.keys():
        history.append(node)
        node = parent[hash_board(node)]
    history.reverse()
    print "Solution Found:", len(history), "moves"
    if display:
        counter = 1
        for board in history:
            paintboard(board, counter)
            counter = counter + 1

#Generic A* code
def astar(board, display, heuristic):
    closed_set = set() # visited boards
    open_set = [board] # unvisited
    # parent and costs maps with the hashed boards
    parent = {}
    cost = {hash_board(board): 0}
    counter = 0
    while open_set:
        counter = counter +1
        current = get_best_board(open_set, cost, heuristic)
        if is_won(current):
            print "-"*80
            print "Heuristic: " + heuristic.__name__
            print "Open set: " + str(len(open_set))
            print "Closed set: " + str(len(closed_set))
            print "Total number of nodes: " + str(len(open_set) + len(closed_set))
            print "Used", counter, "iterations to compute result"
            backtrack(current, parent, display)
            print "-"*80
            return True
        open_set.remove(current)
        closed_set.add(hash_board(current))
        for neighbour in get_neighbours(current):
            if hash_board(neighbour) in closed_set:
                continue

            if neighbour not in open_set:
                open_set.append(neighbour)
            tentative_score = cost[hash_board(current)] + 1
            if tentative_score >= cost.get(hash_board(neighbour), float("inf")):
                continue
            parent[hash_board(neighbour)] = current
            cost[hash_board(neighbour)] = tentative_score

    return False

def dfs(board, display):
    closed_set = []
    open_set = [board]
    parent = {}
    counter = 0
    while open_set:
        counter = counter + 1
        current = open_set.pop()
        closed_set.append(current)
        if is_won(current):
            print "Open set: " + str(len(open_set))
            print "Closed set: " + str(len(closed_set))
            print "Total number of nodes: " + str(len(open_set) + len(closed_set))
            print "Used", counter, "iterations to compute result"
            backtrack(current, parent, display)
            return True
        for neighbour in get_neighbours(current):
            if neighbour in closed_set or neighbour in open_set:
                continue
            open_set.append(neighbour)
            parent[hash_board(neighbour)] = current

    return False



board = []
for line in sys.stdin:
    data = line.split(",")
    board.append([int(data[0]), int(data[1]), int(data[2]), int(data[3])])

delete_previous_output()
astar(board, True, simple_blocking_and_manhattan)
#dfs(board, True)
#cProfile.run('astar(BOARD_1, True)')    #run the astar() function with profiling tools
