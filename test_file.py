from queue import PriorityQueue

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
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0]]
# board = [
#         [0, 0, 1, -1, 0],
#         [0, 0, -1, 0, 0],
#         [0, -1, 1, 0, 0],
#         [1, 0, 0, 1, 0],
#         [0, 0, -1, 0, 0]]
size = 5

def list_neighbours(coord, tokens, n):
    neighbours_list = []

    if coord == OUTSIDE_LEFT_HEX_POSITION:
        neighbours_list = [(i, 0) for i in range(size)]
    elif coord == OUTSIDE_RIGHT_HEX_POSITION:
        neighbours_list = [(size - i - 1, size - 1) for i in range(size)]
    elif coord == OUTSIDE_TOP_HEX_POSITION:
        neighbours_list = [(size - 1, size - i - 1) for i in range(size)]
    elif coord == OUTSIDE_BOTTOM_HEX_POSITION:
        neighbours_list = [(0, i) for i in range(size)]
    else: 
        # horizontal neighbours
        if coord[1] != 0:
            neighbours_list.append([coord[0], coord[1] - 1])
        if coord[1] < n - 1:
            neighbours_list.append([coord[0], coord[1] + 1])

        # vertical neighbours
        if coord[0] != 0:
            neighbours_list.append([coord[0] - 1, coord[1]])
            if coord[1] != n - 1:
                neighbours_list.append([coord[0] - 1, coord[1] + 1])

        if coord[0] < n - 1:
            neighbours_list.append([coord[0] + 1, coord[1]])
            if coord[1] != 0:
                neighbours_list.append([coord[0] + 1, coord[1] - 1])
    
    neighbours_list2 = [tuple(elem) for elem in neighbours_list if tuple(elem) not in tokens]

    # # add imaginary outside hexes
    # if type(coord) == tuple:
    #     if coord[0] == 0:
    #         neighbours_list2.append(OUTSIDE_LEFT_HEX_POSITION)
    #     if coord[0] == size - 1:
    #         neighbours_list2.append(OUTSIDE_RIGHT_HEX_POSITION)
    #     if coord[1] == size - 1:
    #         neighbours_list2.append(OUTSIDE_TOP_HEX_POSITION)
    #     if coord[1] == 0:
    #         neighbours_list2.append(OUTSIDE_BOTTOM_HEX_POSITION)

    return neighbours_list2

def aStarHeuristic(goal, current):

    bias = 0
    # if current == OUTSIDE_LEFT_HEX_POSITION:
    #     bias += 1
    #     current = (0, goal[0])
    # if current == OUTSIDE_RIGHT_HEX_POSITION:
    #     bias += 1
    #     current = (size - 1, goal[0])
    # if current == OUTSIDE_BOTTOM_HEX_POSITION:
    #     bias += 1
    #     current = (goal[1], 0)
    # if current == OUTSIDE_TOP_HEX_POSITION:
    #     bias += 1
    #     current = (goal[1], size - 1)

    # Manhattan distance on a hex grid
    if (goal[1] == current[1]) & (goal[0] == current[0]):
        return bias + 0
    if goal[0] == current[0]: # same row
        return bias + abs(goal[1] - current[1])
    if goal[1] == current[1]: # same column
        return bias + abs(goal[0] - current[0])
    else: # column mismatch
        if goal[1] > current[1]: # if column 2 > column 1
            if goal[0] > current[0]: # if row 2 > row 1
                return bias + abs(goal[0] - current[0]) + abs(goal[1] - current[1])
            else: # if row 1 > row 2
                return bias + max(abs(goal[0] - current[0]), abs(goal[1] - current[1]))
        else: # if column 1 > column 2
            if goal[0] > current[0]: # if row 2 > row 1
                return bias + max(abs(goal[0] - current[0]), abs(goal[1] - current[1]))
            else: # if row 1 > row 2
                return bias + abs(goal[0] - current[0]) + abs(goal[1] - current[1])

# print(aStarHeuristic((2, 2), OUTSIDE_RIGHT_HEX_POSITION))

def aStarSearch(start, goal):
    start_coordinates = start
    goal_coordinates = goal

    token_coordinates = []

    # Find blockages
    for i in range(size):
        for j in range(size):
            if board[i][j] != 0:
                token_coordinates.append((i, j))

    frontier = PriorityQueue()
    frontier.put(tuple(start_coordinates), 0)
    came_from = dict()
    cost_so_far = dict()
    came_from[tuple(start_coordinates)] = None
    cost_so_far[tuple(start_coordinates)] = 0

    while not frontier.empty():
        current = frontier.get()

        if current == goal_coordinates:
            break
        
        # if str(current[0]).isalpha():
        #     current = current[0]
        # else:
        #     current = tuple(map(int, current))

        for next in list_neighbours(current, token_coordinates, size):
            
            new_cost = cost_so_far[current] + 1

            if next not in cost_so_far or new_cost < cost_so_far[next]:
                
                cost_so_far[next] = new_cost
                priority = new_cost + aStarHeuristic(goal_coordinates, next)
                # next = tuple(map(str, next))

                frontier.put(next, priority)
                came_from[next] = current
    
    print(goal_coordinates)
    print(cost_so_far)

    if tuple(goal_coordinates) not in cost_so_far:
        return 0
    else:
        return cost_so_far[tuple(goal_coordinates)] + 1

def check_pos(d_pos, d_size):
	# check validity of pos
	try:
		pi = d_pos[0]
		pj = d_pos[1]
		if pi<0 or pi>=d_size or pj<0 or pj>=d_size:
			return False
		else:
			return True
	except Exception:
		# could be type error or something
		return False

print(aStarSearch((0, 0), (2, 4)))