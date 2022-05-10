from pydoc import doc
from collections import Counter
import numpy
from queue import Queue
from queue import PriorityQueue
import random

class Player:

    PLAYER_REPRESENTATIONS = {
        "red": -1,
        "blue": 1
    }

    MAX_DEPTH = 1

    def __init__(self, player, n):
        """
        Called once at the beginning of a game to initialise this player.
        Set up an internal representation of the game state.

        The parameter player is the string "red" if your player will
        play as Red, or the string "blue" if your player will play
        as Blue.
        """

        self.colour = player
        self.board_size = n
        self.minimax_turn_number = 1
        self.turn_number = 1
        self.last_placement = tuple()
        self.iterations = 0
        self.c = 0
        
        # Represent board as 2d array
        self.board = numpy.zeros((n, n), dtype=int)
        self.minimax_history = Counter({self.board.tobytes(): 1})
        self.history = Counter({self.board.tobytes(): 1})

    def action(self):

        # Imaginary hexes used for Dijkstra's algorithm
        OUTSIDE_LEFT_HEX_POSITION = (123, 123)
        OUTSIDE_RIGHT_HEX_POSITION = (234, 234)
        OUTSIDE_TOP_HEX_POSITION = (345, 345)
        OUTSIDE_BOTTOM_HEX_POSITION = (456, 456)

        """
        Called at the beginning of your turn. Based on the current state
        of the game, select an action to play.
        """
        
        # Adapted from board.py in Referee
        def connected_coords(start_coord):
            """
            Find connected coordinates from start_coord. This uses the token 
            value of the start_coord cell to determine which other cells are
            connected (e.g., all will be the same value).
            """
            # Get search token type
            token_type = self.board[start_coord]

            # Use bfs from start coordinate
            reachable = set()
            queue = Queue(0)
            
            queue.put(start_coord)

            while not queue.empty():
                curr_coord = queue.get()
                reachable.add(curr_coord)
                for coord in list_neighbours(curr_coord, self.board_size):
                    if coord not in reachable and self.board[coord] == token_type:
                        queue.put(coord)

            return list(reachable)

        # lists out all neighbours of a particular hex - brought over from Project Part A
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

        # print out the immediate neighbours of a cell for red (if they are within the game boundaries)
        def list_neighbours_red(coord, n):
            neighbours_list = []

            if coord == OUTSIDE_TOP_HEX_POSITION:
                neighbours_list = [(self.board_size - 1, self.board_size - i - 1) for i in range(self.board_size)]
            elif coord == OUTSIDE_BOTTOM_HEX_POSITION:
                neighbours_list = [(0, i) for i in range(self.board_size)]

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
                if coord[0] == self.board_size - 1:
                    neighbours_list2.append(OUTSIDE_TOP_HEX_POSITION)

            return neighbours_list2

        # print out the immediate neighbours of a cell for blue (if they are within the game boundaries)
        def list_neighbours_blue(coord, n):
            neighbours_list = []

            if coord == OUTSIDE_LEFT_HEX_POSITION:
                neighbours_list = [(i, 0) for i in range(self.board_size)]
            elif coord == OUTSIDE_RIGHT_HEX_POSITION:
                neighbours_list = [(self.board_size - i - 1, self.board_size - 1) for i in range(self.board_size)]

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
                
                if coord[1] == self.board_size - 1:
                    neighbours_list2.append(OUTSIDE_RIGHT_HEX_POSITION)
                if coord[1] == 0:
                    neighbours_list2.append(OUTSIDE_LEFT_HEX_POSITION)

            return neighbours_list2

        # Game ending conditions
        def game_end(last_player, lx, ly):
            
            PLAYER_AXIS = {
                "red": 0, # Red aims to form path in r/0 axis
                "blue": 1 # Blue aims to form path in q/1 axis
            }

            MAX_REPEAT_STATES = 7
            MAX_TURNS = 343

            reachable = connected_coords((lx, ly))

            axis_vals = [coord[PLAYER_AXIS[last_player]] for coord in reachable]

            if min(axis_vals) == 0 and max(axis_vals) == self.board_size - 1:
                return last_player

            # Draw due to repetition
            if self.minimax_history[self.board.tobytes()] >= MAX_REPEAT_STATES:
                return 'draw'

            # Draw due to too many turns
            if self.minimax_turn_number >= MAX_TURNS:
                return 'draw'

            return False

        # Calculates move if AI is blue
        def AIMoveBlue(unfavourable_moves):
            bestScore = -1.0e40
            bestMove = 0
            depth = 0

            alpha = -1.0e39
            beta = 1.0e39

            breakOutOfNestedLoop = False
            for i in range(0, self.board_size):
                for j in range(0, self.board_size):

                    if self.board[i][j] == 0 and (i, j) not in unfavourable_moves:

                        self.board[i][j] = Player.PLAYER_REPRESENTATIONS['blue']
                        score = alphaBetaMinimax(depth, 'blue', i, j, False, alpha, beta)
                        self.board[i][j] = 0

                        if (score > bestScore):
                            bestScore = score      
                            bestMove = (i, j)

                        # Alpha-beta pruning
                        alpha = max(alpha, bestScore)

                        if beta <= alpha:
                            breakOutOfNestedLoop = True
                            break
                
                if breakOutOfNestedLoop:
                    break
            
            self.iterations = 0

            # If unable to make a best move, return a random available move
            if bestMove == 0:
                possible_moves = [(i, j) for i in range(self.board_size) for j in range(self.board_size) if self.board[i, j] == 0]
                bestMove = random.choice(possible_moves)

            return ("PLACE", bestMove[0], bestMove[1])
        
        # Calculates move if AI is red
        def AIMoveRed(unfavourable_moves):
            bestScore = 1.0e40
            bestMove = 0
            depth = 0

            alpha = -1.0e39
            beta = 1.0e39

            breakOutOfNestedLoop = False
            for i in range(0, self.board_size):
                for j in range(0, self.board_size):
                    
                    if self.board[i][j] == 0 and (i, j) not in unfavourable_moves:
                        
                        self.board[i][j] = Player.PLAYER_REPRESENTATIONS['red']
                        score = alphaBetaMinimax(depth, 'red', i, j, True, alpha, beta)

                        self.board[i][j] = 0

                        if (score < bestScore):
                            bestScore = score      
                            bestMove = (i, j)

                        # Alpha-beta pruning
                        beta = min(beta, bestScore)

                        if beta <= alpha:
                            breakOutOfNestedLoop = True
                            break
                
                if breakOutOfNestedLoop:
                    break
            
            self.iterations = 0

            # If unable to make a best move, return a random available move
            if bestMove == 0:
                possible_moves = [(i, j) for i in range(self.board_size) for j in range(self.board_size) if self.board[i, j] == 0]
                bestMove = random.choice(possible_moves)

            return ("PLACE", bestMove[0], bestMove[1])

        # Capturing function - from Referee
        def capturing(coord):

            _ADD = lambda a, b: (a[0] + b[0], a[1] + b[1])

            _HEX_STEPS = numpy.array([(1, -1), (1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1)], 
                dtype="i,i")

            _CAPTURE_PATTERNS = [[_ADD(n1, n2), n1, n2] 
                for n1, n2 in 
                    list(zip(_HEX_STEPS, numpy.roll(_HEX_STEPS, 1))) + 
                    list(zip(_HEX_STEPS, numpy.roll(_HEX_STEPS, 2)))]

            def inside_bounds(coord):
                """
                True iff coord inside board bounds.
                """
                r, q = coord
                return r >= 0 and r < self.board_size and q >= 0 and q < self.board_size
            
            _SWAP_PLAYER = { 0: 0, Player.PLAYER_REPRESENTATIONS['blue']: Player.PLAYER_REPRESENTATIONS['red'], Player.PLAYER_REPRESENTATIONS['red']: Player.PLAYER_REPRESENTATIONS['blue'] }
            opp_type = self.board[coord]

            mid_type = _SWAP_PLAYER[opp_type]

            captured = set()

            for pattern in _CAPTURE_PATTERNS:
                # [(1, -2), (1, -1), (0, -1)]  ,   [(2, -1), (1, 0), (1, -1)] etc

                coords = [_ADD(coord, s) for s in pattern]

                # No point checking if any coord is outside the board!

                # if all coords are legal
                if all(map(inside_bounds, coords)):

                    tokens = [self.board[coord] for coord in coords]
                    if tokens == [opp_type, mid_type, mid_type]:
                        # Capturing has to be deferred in case of overlaps
                        # Both mid cell tokens should be captured
                        captured.update(coords[1:])
            
            return list(captured)           

        # Adapted from github user nuankw
        # Source: https://github.com/nuankw/hex-game/blob/master/HexPlayer.py
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

        # Adapted from github user nuankw
        # Source: https://github.com/nuankw/hex-game/blob/master/HexPlayer.py
        # Returns the 'ends' of bridges that can be made from a given hex
        def bridge_ends(pos, size):
            # i is letter and j is number
            (i, j) = pos
            ends_list = []
            possible_ends_list = [(i+2, j-1), (i+1, j-2), (i+1, j+1), (i-1, j-1), (i-1, j+2), (i-2, j+1)]
            for possible_pos in possible_ends_list:
                if (check_pos(possible_pos, size)):
                    ends_list.append(possible_pos)
            return ends_list

        # Adapted from github user nuankw
        # Source: https://github.com/nuankw/hex-game/blob/master/HexPlayer.py
        # Returns an arbitrary score calculated based on the 'appeal' of creating bridges
        def bridging_factor(last_player): # "red" or "blue"
            score = 0
            for i in range(self.board_size):
                for j in range(self.board_size):

                    # For each hex

                    current_player = self.board[i][j]

                    # print(f"({i}, {j})")
                    # print(f"current player: {current_player}")

                    # If hex belongs to a player
                    if current_player != 0:

                        bridge_ends_list = bridge_ends((i,j), self.board_size)

                        if last_player == 'red':
                            for n in bridge_ends_list:
                                val = self.board[n[0]][n[1]]
                                if val == current_player: # If bridge leads to another one of our pieces
                                    score += -3 * current_player
                                elif val == -1 * current_player: # If bridge leads to an opponent piece
                                    score += 5 * current_player 
                        
                        elif last_player == 'blue':
                            for n in bridge_ends_list:
                                val = self.board[n[0]][n[1]]
                                if val == current_player: # If bridge leads to another one of our pieces
                                    score += 3 * current_player
                                elif val == -1 * current_player: # If bridge leads to an opponent piece
                                    score += -5 * current_player 
                        
                        # print(f"heuristic score is: {score}")
            return score

        # Adapted from github user nuankw
        # Source: https://github.com/nuankw/hex-game/blob/master/HexPlayer.py
        # Weights heuristic score based on how 'centred' a particular move causes the player to be
        def centred():
            score = 0
            center = (self.board_size // 2, self.board_size // 2)
            center_val = self.board[self.board_size // 2][self.board_size // 2]
            if center_val != 0:
                score += 50 * center_val
                c_neighbours = list_neighbours(center, self.board_size)
                count = 0 # num_red - num_blue
                for (pos_i, pos_j) in c_neighbours:
                    value = self.board[pos_i][pos_j]
                    score += 3 * value
                    if (value == Player.PLAYER_REPRESENTATIONS['red']):
                        count -= 1
                    elif (value == Player.PLAYER_REPRESENTATIONS['blue']):
                        count += 1

            return score

        # Adapted from Stackabuse
        # Source: https://stackabuse.com/dijkstras-algorithm-in-python/
        def add_edge(start_vertex, end_vertex, weight, edges):
            edges[(start_vertex, end_vertex)] = weight

        # Search for djikstra shortest path from every cell on the red border to every other cell on the other red border
        def search_dijkstra_red(size, board):

            start = OUTSIDE_BOTTOM_HEX_POSITION
            result = dijkstra_red(size, start, board)
            return result[OUTSIDE_TOP_HEX_POSITION]

        # Adapted from Stackabuse
        # Source: https://stackabuse.com/dijkstras-algorithm-in-python/
        # Djikstra shortest path for RED player
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
                D[start_vertex] = 1000000
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
                        add_edge(current_vertex, neighbour, 100, edges)
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

        # Search for djikstra shortest path from every cell on the blue border to every other cell on the other blue border
        def search_dijkstra_blue(size, board):

            start = OUTSIDE_LEFT_HEX_POSITION
            result = dijkstra_blue(size, start, board)
            return result[OUTSIDE_RIGHT_HEX_POSITION]

        # Adapted from Stackabuse
        # Source: https://stackabuse.com/dijkstras-algorithm-in-python/
        # Djikstra shortest path for BLUE player
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
                        add_edge(current_vertex, neighbour, 100, edges)
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

        # Calculates the heuristic score
        def heuristic(last_player):

            score = 0

            # Opening
            if self.turn_number < self.board_size:
                bridging_score = bridging_factor(last_player)
                centred_score = centred()
                red_score = search_dijkstra_red(self.board_size, self.board)
                blue_score = search_dijkstra_blue(self.board_size, self.board)
                dijkstra_score = red_score - blue_score

                score += 20 * dijkstra_score + 2 * bridging_score + 1 * centred_score

            # Midgame
            else:
                red_score = search_dijkstra_red(self.board_size, self.board)
                blue_score = search_dijkstra_blue(self.board_size, self.board)
                dijkstra_score = red_score - blue_score
                bridging_score = bridging_factor(last_player)
                
                score = 25 * dijkstra_score + bridging_score
            
            return score
        
        # Returns the minimax value utilising alpha-beta pruning technique
        def alphaBetaMinimax(depth, last_player, last_x, last_y, isMaxPlayer, alpha, beta):

            self.iterations += 1
            
            nv = -1.0e39 # negative infinity
            pv = 1.0e39 # positive infinity

            # EVALUATION FUNCTION
            if self.board_size > 3:
                if self.board_size < 5:
                    if (depth >= 4):
                        # return heuristic(last_player)
                        return heuristic(last_player)
                
                elif self.board_size < 6:
                    if (depth >= 2):
                        # return heuristic(last_player)
                        return heuristic(last_player)
                        
                elif self.board_size < 10:
                    if (depth >= 1):
                        # return heuristic(last_player)
                        return heuristic(last_player)
                else:
                    if (depth >= 0):
                        # return heuristic(last_player)
                        return heuristic(last_player)

            # GAME END CONDITIONS
            result = game_end(last_player, last_x, last_y)
            
            # If end of game   
            if result == 'red':
                return -1.0e39
            elif result == 'blue':
                return 1.0e39
            elif result == 'draw':
                return 0

            if isMaxPlayer:

                bestScore = nv

                breakOutOfNestedLoop = False
                for i in range(0, self.board_size):
                    for j in range(0, self.board_size):
                        if self.board[i][j] == 0:

                            if last_player == 'red':
                                self.board[i][j] = Player.PLAYER_REPRESENTATIONS['blue']
                                score = alphaBetaMinimax(depth + 1, 'blue', i, j, False, alpha, beta)
                            
                            elif last_player == 'blue':
                                self.board[i][j] = Player.PLAYER_REPRESENTATIONS['red']
                                score = alphaBetaMinimax(depth + 1, 'red', i, j, True, alpha, beta)

                            # # reset
                            self.board[i][j] = 0

                            if (score > bestScore):
                                bestScore = score

                            # Alpha-beta pruning
                            alpha = max(alpha, bestScore)

                            if beta <= alpha:
                                breakOutOfNestedLoop = True
                                break 

                    if breakOutOfNestedLoop:
                        break
            
                return bestScore

            else:
                
                bestScore = pv
                
                breakOutOfNestedLoop = False
                for i in range(0, self.board_size):
                    for j in range(0, self.board_size):
                        if self.board[i][j] == 0:
                            if last_player == 'red':
                                self.board[i][j] = Player.PLAYER_REPRESENTATIONS['blue']
                                score = alphaBetaMinimax(depth + 1, 'blue', i, j, False, alpha, beta)
                            
                            elif last_player == 'blue':
                                self.board[i][j] = Player.PLAYER_REPRESENTATIONS['red']
                                score = alphaBetaMinimax(depth + 1, 'red', i, j, True, alpha, beta)

                            # reset
                            self.board[i][j] = 0

                            if (score < bestScore):
                                bestScore = score

                            # Alpha-beta pruning
                            beta = min(beta, bestScore)

                            if beta <= alpha:
                                breakOutOfNestedLoop = True
                                break
                    
                    if breakOutOfNestedLoop:
                        break
                                         
            
                return bestScore

        # ------------------------------------ MAIN CODE -----------------------------------------

        # If there is an immediate capture to be made, make it straight away
        unfavourable_moves = []
        if self.turn_number > 3:
            for i in range(self.board_size):
                for j in range(self.board_size):

                    if self.board[i][j] == 0:
                    
                        if self.colour == 'blue':
                            self.board[i][j] = Player.PLAYER_REPRESENTATIONS['blue']
                        else:
                            self.board[i][j] = Player.PLAYER_REPRESENTATIONS['red']

                        # Can this particular move capture opponent pieces?
                        captured = capturing((i, j))
                        self.board[i][j] = 0
                        if captured:
                            return ("PLACE", i, j)
                        
                        # By playing here, am I allowing myself to be captured by opponent?
                        if self.colour == 'blue':
                            self.board[i][j] = Player.PLAYER_REPRESENTATIONS['blue']
                        else:
                            self.board[i][j] = Player.PLAYER_REPRESENTATIONS['red']
                        
                        
                        for neighbour in list_neighbours((i, j), self.board_size):
                            if self.board[neighbour] == 0:

                                if self.colour == 'blue':
                                    self.board[neighbour] = Player.PLAYER_REPRESENTATIONS['red']
                                else:
                                    self.board[neighbour] = Player.PLAYER_REPRESENTATIONS['blue']
                                
                                captured = capturing(neighbour)
                                self.board[neighbour] = 0
                                if captured:
                                    unfavourable_moves.append((i, j))
                        
                        self.board[i][j] = 0
                                
                        # print(f"don't play in these hexes: {unfavourable_moves}")
        
        # If there is an opportunity to win immediately, play that move.
        if self.turn_number >= 2 * self.board_size:

            for i in range(self.board_size):
                for j in range(self.board_size):
                    if self.board[i][j] == 0:
                        
                        if self.colour == 'blue':
                            self.board[i][j] = Player.PLAYER_REPRESENTATIONS['blue']
                        else:
                            self.board[i][j] = Player.PLAYER_REPRESENTATIONS['red']
                        
                        if game_end(self.colour, i, j) == self.colour:
                            return ("PLACE", i, j)

                        self.board[i][j] = 0       

        # Decide whether to steal
        # As blue, if red plays on border, don't steal and then play in centre
        # As red, play (size - 2, size - 3) or (size - 3, size - 1)
        
        if self.colour == 'blue':
            if self.turn_number == 2:
                
                # Hexes not to steal
                safe_hexes = []
                for i in range(self.board_size):
                    for j in range(self.board_size):
                        # Change this later possibly
                        if i == 0 or i == self.board_size - 1 or j == 0 or j == self.board_size - 1:
                            safe_hexes.append((i, j))

                if (self.last_placement[1], self.last_placement[2]) not in safe_hexes:
                    return ("STEAL", )
                
                else:
                    return ("PLACE", self.board_size // 2, self.board_size // 2)
            
            # ONLY PLACE ACTIONS FROM TURN 3 ONWARDS
            else:
                return AIMoveBlue(unfavourable_moves)
        
        else:
            if self.turn_number == 1:
                return random.choice([
                    ("PLACE", self.board_size - 2, self.board_size - 3), 
                    ("PLACE", self.board_size - 3, 0)])
            elif self.turn_number == 3:
                if self.board[self.board_size // 2, self.board_size // 2] == 0:
                    return ("PLACE", self.board_size // 2, self.board_size // 2)
                else:
                    return AIMoveRed(unfavourable_moves)
            else:
                return AIMoveRed(unfavourable_moves)

    def turn(self, player, action):
        """
        Called at the end of each player's turn to inform this player of 
        their chosen action. Update your internal representation of the 
        game state based on this. The parameter action is the chosen 
        action itself. 
        
        Note: At the end of your player's turn, the action parameter is
        the same as what your player returned from the action method
        above. However, the referee has validated it at this point.
        """

        # From referee
        def capturing(coord):

            _ADD = lambda a, b: (a[0] + b[0], a[1] + b[1])

            _HEX_STEPS = numpy.array([(1, -1), (1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1)], 
                dtype="i,i")

            _CAPTURE_PATTERNS = [[_ADD(n1, n2), n1, n2] 
                for n1, n2 in 
                    list(zip(_HEX_STEPS, numpy.roll(_HEX_STEPS, 1))) + 
                    list(zip(_HEX_STEPS, numpy.roll(_HEX_STEPS, 2)))]

            def inside_bounds(coord):
                """
                True iff coord inside board bounds.
                """
                r, q = coord
                return r >= 0 and r < self.board_size and q >= 0 and q < self.board_size
            
            _SWAP_PLAYER = { 0: 0, Player.PLAYER_REPRESENTATIONS['blue']: Player.PLAYER_REPRESENTATIONS['red'], Player.PLAYER_REPRESENTATIONS['red']: Player.PLAYER_REPRESENTATIONS['blue'] }
            opp_type = self.board[coord]

            mid_type = _SWAP_PLAYER[opp_type]

            captured = set()

            for pattern in _CAPTURE_PATTERNS:
                # [(1, -2), (1, -1), (0, -1)]  ,   [(2, -1), (1, 0), (1, -1)] etc

                coords = [_ADD(coord, s) for s in pattern]

                # No point checking if any coord is outside the board!

                # if all coords are legal
                if all(map(inside_bounds, coords)):

                    tokens = [self.board[coord] for coord in coords]
                    if tokens == [opp_type, mid_type, mid_type]:
                        # Capturing has to be deferred in case of overlaps
                        # Both mid cell tokens should be captured
                        captured.update(coords[1:])
            
            return list(captured)

        if action[0].upper() == 'PLACE': # 'PLACE' action
            self.board[action[1]][action[2]] = Player.PLAYER_REPRESENTATIONS[player]

            # Capturing
            captured = capturing((action[1], action[2]))
            if captured:
                for elem in captured:
                    self.board[elem] = 0
            
        else: # 'STEAL' action
            is_looping = True
            for i in range(self.board_size):
                for j in range(self.board_size):
                    if self.board[i][j] != 0:
                        self.board[j][i] = Player.PLAYER_REPRESENTATIONS[player]
                        self.board[i][j] = 0
                        is_looping = False
                
                if not is_looping:
                    break

        if action[0].upper() != "STEAL":
            self.last_placement = (player, action[1], action[2])

        self.turn_number += 1 # Increment turn count
        self.history[self.board.tobytes()] += 1 # Add board state to history