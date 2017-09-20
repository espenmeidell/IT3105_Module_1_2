from PIL import Image, ImageDraw, ImageFont
from copy import copy, deepcopy
import cProfile
import os, shutil

import sys
sys.path.append('../')
from astar import astar
from dfs import dfs



# --------------------------------
# ------------- GUI --------------
# --------------------------------

#Use pillow to paint a board with some text and a number
def paintboard(board, iteration, final):
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
    if final:
        text = "Move #"+ str(iteration)
    else:
        text = "Expansion #"+ str(iteration)
    draw.text((10, 310), text,(0,0,0))
    if final:
        im.save("output/" + str(iteration) + ".png")
    else:
        im.save("expansion/" + str(iteration) + ".png")

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
    folder = 'expansion'
    for img in os.listdir(folder):
        img_path = os.path.join(folder, img)
        try:
            if os.path.isfile(img_path):
                os.unlink(img_path)
        except Exception as e:
            print(e)



# --------------------------------
# ------- HELPER FUNCTIONS -------
# --------------------------------

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
def is_stuck(car, board):
    return calculate_options(car, board) == 0

#Returnes the car that is blocking the coordinate
def get_blocking_car(x,y, board):
    for car in board:
        if (x,y) in get_car_coords(car):
            return car

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



# --------------------------------
# ---------- HEURISTICS ----------
# --------------------------------

# Returns 0 if the coordinate is not blocked
# 1 if it is blocked or
# 2 if it is blocked and the blocking car is stuck
def advanced_block_score(x, y, board):
    if not is_blocked(x,y,board):
        return 0
    blockingCar = get_blocking_car(x,y, board)
    if is_stuck(blockingCar, board):
        return 2
    return 1

# Returns the sum of the advanced_block_score for the cars in the way
def advanced_blocking(board):
    n = 0
    for i in range(board[0][1]+2, 6):
        n += advanced_block_score(i, 2, board)
    return n

# Returns the sum of the advanced_blocking and manhattan
def advanced_blocking_and_manhattan(board):
    return advanced_blocking(board) + manhattan(board)

# Returns the sum of the simple_blocking and manhattan
def simple_blocking_and_manhattan(board):
    return  simple_blocking(board) + manhattan(board)

# Returns the number of blocked cells in the way of the car
def simple_blocking(board):
    n = 0
    for i in range(board[0][1]+2, 6):   #how many of those are blocked?
        if is_blocked(i, 2, board):
            n = n + 1
    return n

# Returns the number of spaces to goal
def manhattan(board):
    return  4 - board[0][1]

# Returns 0...
def zero_heuristic(board):
    return 0






board = []
for line in sys.stdin:
    data = line.split(",")
    board.append([int(data[0]), int(data[1]), int(data[2]), int(data[3])])

delete_previous_output()

#dfs(board, get_neighbours, is_won, hash_board)

astar(
    board,
    get_best_board,
    get_neighbours,
    zero_heuristic,
    is_won,
    hash_board)
astar(
    board,
    get_best_board,
    get_neighbours,
    simple_blocking,
    is_won,
    hash_board)
astar(
    board,
    get_best_board,
    get_neighbours,
    manhattan,
    is_won,
    hash_board)
astar(
    board,
    get_best_board,
    get_neighbours,
    simple_blocking_and_manhattan,
    is_won,
    hash_board,
    display = paintboard)
# astar(
#     board,
#     get_best_board,
#     get_neighbours,
#     advanced_blocking,
#     is_won,
#     hash_board,)
# astar(
#     board,
#     get_best_board,
#     get_neighbours,
#     advanced_blocking_and_manhattan,
#     is_won,
#     hash_board)

#cProfile.run('astar(board, False, zero_heuristic)')    #run the astar() function with profiling tools
#cProfile.run('astar(board, False, simple_blocking_and_manhattan)')
