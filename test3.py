from queue import PriorityQueue

RED_PLAYER = -1
BLUE_PLAYER = 1

board = [
        [0, 0, 0, 0, 0],
        [0, 1, 1, 0, 0],
        [-1, 0, 0, 1, 0],
        [-1, 0, 0, 0, 0],
        [-1, 0, 0, 0, 0]]

size = 5

OUTSIDE_LEFT_HEX_POSITION = (123, 123)
OUTSIDE_RIGHT_HEX_POSITION = (234, 234)
OUTSIDE_TOP_HEX_POSITION = (345, 345)
OUTSIDE_BOTTOM_HEX_POSITION = (456, 456)

# print out the immediate neighbours of a cell (if they are within the game boundaries)
def list_neighbours_red(coord, n):
    neighbours_list = []

    if coord == OUTSIDE_TOP_HEX_POSITION:
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
    
    neighbours_list2 = [tuple(elem) for elem in neighbours_list]

    # add imaginary outside hexes
    if type(coord) == tuple:
        
        if coord[0] == 0:
            neighbours_list2.append(OUTSIDE_BOTTOM_HEX_POSITION)
        if coord[0] == size - 1:
            neighbours_list2.append(OUTSIDE_TOP_HEX_POSITION)

    return neighbours_list2

def list_neighbours_blue(coord, n):
    neighbours_list = []

    if coord == OUTSIDE_LEFT_HEX_POSITION:
        neighbours_list = [(i, 0) for i in range(size)]
    elif coord == OUTSIDE_RIGHT_HEX_POSITION:
        neighbours_list = [(size - i - 1, size - 1) for i in range(size)]

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
    
    neighbours_list2 = [tuple(elem) for elem in neighbours_list]

    # add imaginary outside hexes
    if type(coord) == tuple:
        
        if coord[1] == size - 1:
            neighbours_list2.append(OUTSIDE_RIGHT_HEX_POSITION)
        if coord[1] == 0:
            neighbours_list2.append(OUTSIDE_LEFT_HEX_POSITION)

    return neighbours_list2

# print(list_neighbours((4,0), 5))

def add_edge(start_vertex, end_vertex, weight, edges):
    edges[(start_vertex, end_vertex)] = weight

# search for djikstra shortest path from every cell on the red border to every other cell on the other red border
def search_dijkstra_red(size, board):

    start = OUTSIDE_BOTTOM_HEX_POSITION
    result = dijkstra_red(size, start, board)
    return result[OUTSIDE_TOP_HEX_POSITION]


# djikstra shortest path for RED player
def dijkstra_red(size, start, board):
    start_vertex = start
    edges = {}
    D = {}
    friendly = set()
    obstacles = set()
    visited = set()

    for i in range(size):
        for j in range(size):
            D[(i, j)] = float('inf')
            if board[i][j] == 1: #if hex is a blue piece
                obstacles.add((i, j))
            elif board[i][j] == -1: #if hex is a red piece
                friendly.add((i, j))

    # Add imaginary hexes
    D[OUTSIDE_TOP_HEX_POSITION] = float('inf')
    D[OUTSIDE_BOTTOM_HEX_POSITION] = float('inf')
    
    if start in friendly:
        D[start_vertex] = 0
    elif start in obstacles:
        D[start_vertex] = 100000
    else:
        D[start_vertex] = 1

    # print(f"D: {D}")
    # print(f"Friendly: {friendly}")
    # print(f"Obstacles: {obstacles}")
    
    pq = PriorityQueue()
    pq.put((0, start_vertex))

    while not pq.empty():
        
        (dist, current_vertex) = pq.get()
        # print(f"next in priority queue: {(dist, current_vertex)}")
        visited.add(current_vertex)

        if current_vertex == OUTSIDE_TOP_HEX_POSITION:
            for i in range(size - 1):
                add_edge(current_vertex, (size - 1, i), 0, edges)
        
        if current_vertex == OUTSIDE_BOTTOM_HEX_POSITION:
            for i in range(size - 1):
                add_edge(current_vertex, (0, i), 0, edges)

        # print(f"current_vertex[0]: {current_vertex[0]}")
        if current_vertex[0] == size - 1: # (4, 0), (4, 1) etc.
            add_edge(current_vertex, OUTSIDE_TOP_HEX_POSITION, 0, edges)
        
        if current_vertex[0] == 0: # (4, 0), (4, 1) etc.
            add_edge(current_vertex, OUTSIDE_BOTTOM_HEX_POSITION, 0, edges)
        
        # print(f"edges: {edges}")

        # print(f"neighbours: {list_neighbours(current_vertex, size)}")
        for neighbour in list_neighbours_red(current_vertex, size):
            if neighbour in obstacles:
                add_edge(current_vertex, neighbour, 1000000, edges)
            elif neighbour in friendly:
                add_edge(current_vertex, neighbour, 0, edges)
            else:
                add_edge(current_vertex, neighbour, 1, edges)
        
            # print(f"edges1: {edges}")     # ((4, 3), 'T'): 0

        # for neighbour in range(size):
            distance = edges[current_vertex, neighbour]
            # print(f"current vertex: {current_vertex}, neighbour: {neighbour}, distance: {distance}")
            # print(f"D: {D}")
            if neighbour not in visited:
                old_cost = D[neighbour]
                new_cost = D[current_vertex] + distance
                if new_cost < old_cost:
                    pq.put((new_cost, neighbour))
                    D[neighbour] = new_cost

        # print(f"D: {D}")

    return D

# search for djikstra shortest path from every cell on the blue border to every other cell on the other blue border
def search_dijkstra_blue(size, board):

    start = OUTSIDE_LEFT_HEX_POSITION
    result = dijkstra_blue(size, start, board)
    return result[OUTSIDE_RIGHT_HEX_POSITION]

# djikstra shortest path for BLUE player
def dijkstra_blue(size, start, board):
    start_vertex = start
    edges = {}
    D = {}
    friendly = set()
    obstacles = set()
    visited = set()

    for i in range (size):
        for j in range(size):
            D[(i, j)] = float('inf')
            if board[i][j] == -1: #if hex is a red piece
                obstacles.add((i, j))
            elif board[i][j] == 1: #if hex is a blue piece
                friendly.add((i, j))

    # Add imaginary hexes
    D[OUTSIDE_RIGHT_HEX_POSITION] = float('inf')
    D[OUTSIDE_LEFT_HEX_POSITION] = float('inf')

    if start in friendly:
        D[start_vertex] = 0
    elif start in obstacles:
        D[start_vertex] = 100000
    else:
        D[start_vertex] = 1
    
    pq = PriorityQueue()
    pq.put((0, start_vertex))

    while not pq.empty():
        (dist, current_vertex) = pq.get()
        visited.add(current_vertex)

        if current_vertex == OUTSIDE_RIGHT_HEX_POSITION:
            for i in range(size - 1):
                add_edge(current_vertex, (i, size - 1), 0, edges)
        
        if current_vertex == OUTSIDE_LEFT_HEX_POSITION:
            for i in range(size - 1):
                add_edge(current_vertex, (i, 0), 0, edges)
        
        if current_vertex[1] == size - 1:
            add_edge(current_vertex, OUTSIDE_RIGHT_HEX_POSITION, 0, edges)
        
        if current_vertex[1] == 0:
            add_edge(current_vertex, OUTSIDE_LEFT_HEX_POSITION, 0, edges)

        for neighbour in list_neighbours_blue(current_vertex, size):
            if neighbour in obstacles:
                add_edge(current_vertex, neighbour, 1000000, edges)
            elif neighbour in friendly:
                add_edge(current_vertex, neighbour, 0, edges)
            else:
                add_edge(current_vertex, neighbour, 1, edges)
        
            distance = edges[current_vertex, neighbour]
            if neighbour not in visited:
                old_cost = D[neighbour]
                new_cost = D[current_vertex] + distance
                if new_cost < old_cost:
                    pq.put((new_cost, neighbour))
                    D[neighbour] = new_cost
    return D


print(search_dijkstra_red(size, board))
print(search_dijkstra_blue(size, board))