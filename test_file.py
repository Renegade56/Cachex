from queue import PriorityQueue
import numpy
import random

RED_PLAYER = -1
BLUE_PLAYER = 1

OUTSIDE_LEFT_HEX_POSITION = "L"
OUTSIDE_RIGHT_HEX_POSITION = "R"
OUTSIDE_TOP_HEX_POSITION = "T"
OUTSIDE_BOTTOM_HEX_POSITION = "B"

board = [
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, -1, -1, -1, -1],
        [0, 1, 0, 0, 0],
        [0, 0, 0, 0, 0]]

size = 5

possible_moves = [(i, j) for i in range(size) for j in range(size) if board[i][j] == 0]
print(possible_moves)
print(random.choice(possible_moves))