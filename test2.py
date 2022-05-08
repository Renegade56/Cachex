from queue import PriorityQueue

RED_PLAYER = -1
BLUE_PLAYER = 1

board = [
        [0, 0, 0, 0, 0],
        [0, 0, 1, 1, 1],
        [0, -1, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, -1, 0, 0, 0]]

size = 5


# print out the immediate neighbours of a cell (if they are within the game boundaries)
def list_neighbours(coord, n):
    neighbours_list = []

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

    return neighbours_list2



# add edge to a graph
def add_edge(start_vertex, end_vertex, weight, edges):
    edges[(start_vertex, end_vertex)] = weight

# search for djikstra shortest path from every cell on the red border to every other cell on the other red border
def search_dijkstra_red(size, board):
    min_path = 1000000
    for i in range(size):
        start = (0, i)


        # print(f"start: {start}")

        result = dijkstra_red(size, start, board)
        for j in range(size):
            # print(f"dijkstra result: {result}")
            curr_path = result[size - 1, j]
            if curr_path < min_path:
                min_path = curr_path
            
    #         print(f"curr path: {curr_path}\n-----------\n")
    
    # print(f"min_path: {min_path}")
    return min_path

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

        # print(f"neighbours: {list_neighbours(current_vertex, size)}")
        for neighbour in list_neighbours(current_vertex, size):
            if neighbour in obstacles:
                add_edge(current_vertex, neighbour, 1000000, edges)
            elif neighbour in friendly:
                add_edge(current_vertex, neighbour, 0, edges)
            else:
                add_edge(current_vertex, neighbour, 1, edges)
        
        # print(f"edges: {edges}")

        # for neighbour in range(size):
            distance = edges[current_vertex, neighbour]
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
    min_path = 1000000
    for i in range(size):
        start = (i, 0)
        result = dijkstra_blue(size, start, board)
        for j in range(size):
            curr_path = result[j, size - 1]
            if curr_path < min_path:
                min_path = curr_path
    return min_path

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

        for neighbour in list_neighbours(current_vertex, size):
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