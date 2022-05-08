from pydoc import doc
from collections import Counter
import numpy
from queue import Queue
from queue import PriorityQueue
import time
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

        # HOW TO REPRESENT THE BETA PLAYER'S BOARD?
        self.colour = player # red or blue, in this case blue
        self.board_size = n # 5
        self.minimax_turn_number = 1
        self.turn_number = 1 # Start from turn 1
        self.last_placement = tuple()
        self.iterations = 0
        self.c=0
        
        # Represent board as 2d array
        self.board = numpy.zeros((n, n), dtype=int)
        self.minimax_history = Counter({self.board.tobytes(): 1})
        self.history = Counter({self.board.tobytes(): 1})
    
    def capturing(self, coord):

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
            return r >= 0 and r < 3 and q >= 0 and q < 3
        
        _SWAP_PLAYER = { 0: 0, Player.PLAYER_REPRESENTATIONS['blue']: Player.PLAYER_REPRESENTATIONS['red'], Player.PLAYER_REPRESENTATIONS['red']: Player.PLAYER_REPRESENTATIONS['blue'] }
        opp_type = self.board[coord]

        mid_type = _SWAP_PLAYER[opp_type]
        captured = set()

        for pattern in _CAPTURE_PATTERNS:

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

    def action(self):

        OUTSIDE_LEFT_HEX_POSITION = (123, 123)
        OUTSIDE_RIGHT_HEX_POSITION = (234, 234)
        OUTSIDE_TOP_HEX_POSITION = (345, 345)
        OUTSIDE_BOTTOM_HEX_POSITION = (456, 456)

        """
        Called at the beginning of your turn. Based on the current state
        of the game, select an action to play.
        """
        
        # From board.py
        def connected_coords(start_coord):
            """
            Find connected coordinates from start_coord. This uses the token 
            value of the start_coord cell to determine which other cells are
            connected (e.g., all will be the same value).
            """
            # Get search token type
            token_type = self.board[start_coord]
            # print("board: ", self.board) ------------DELETE-------------
            # print(f"Token type: {token_type}")  ------------DELETE-------------

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

        # lists out all neighbours of a particular hex (excluding occupied neighbour hexes)
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

        # print out the immediate neighbours of a cell (if they are within the game boundaries)
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

        def game_end(lp, lx, ly): # game_end(last_player='blue', last_x=i, last_y=j)  
            
            # print("last player: ", lp) #--------------------TEST-----------------------
            # print("x: ", lx, "y: ", ly) #--------------------TEST-----------------------

            PLAYER_AXIS = {
                "red": 0, # Red aims to form path in r/0 axis
                "blue": 1 # Blue aims to form path in q/1 axis
            }

            MAX_REPEAT_STATES = 7
            MAX_TURNS = 343

            # Continuous path formed by either player
            #if self.turn_number >= (self.board_size * 2) - 1:  
            reachable = connected_coords((lx, ly))
            # print (f"***(reachable) from {lx}, {ly}: {reachable}") #--------------------TEST-----------------------
            
            axis_vals = [coord[PLAYER_AXIS[lp]] for coord in reachable]
            # print(f"axis vals: {axis_vals}") #--------------------TEST-----------------------
             
            # print(f"board:\n {self.board[::-1]}") #--------------------TEST-----------------------
            # print("\n------------------------------------------------\n") #--------------------TEST-----------------------
            

            if min(axis_vals) == 0 and max(axis_vals) == self.board_size - 1:
                # print("HYPOTHETICAL WINNER: ", lp) #--------------------TEST-----------------------
                # print("\n------------------------------------------------\n") #--------------------TEST-----------------------
                return lp

            # Draw due to repetition
            if self.minimax_history[self.board.tobytes()] >= MAX_REPEAT_STATES:
                print("DRAW DUE TO REPEATED STATES")
                return 'draw'

            # Draw due to too many turns
            if self.minimax_turn_number >= MAX_TURNS:
                print("DRAW DUE TO MAX TURNS")
                return 'draw'

            return False

        def AIMove():
            bestScore = -1.0e40
            bestMove = 0
            depth = 0

            alpha = -1.0e39
            beta = 1.0e39

            scoreslol = []

            breakOutOfNestedLoop = False
            for i in range(0, self.board_size):
                for j in range(0, self.board_size):
                    if self.board[i][j] == 0:
                        self.board[i][j] = Player.PLAYER_REPRESENTATIONS['blue']

                        # ------ Implement capturing mechanism -------
                        
                        # if self.turn_number >= 4:
                        #     hexes_to_capture = self.capturing((i, j))
                        #     if hexes_to_capture: # [(0, 1), (2, 0)]
                        #         for elem in hexes_to_capture:
                        #             # self.c += 1
                        #             # print("capturing iteration: ", self.c)
                        #             self.board[elem] = 0

                        # ------ End capturing mechanism -------

                        # self.minimax_turn_number += 1
                        # self.minimax_history[self.board.tobytes()] += 1

                        score = alphaBetaMinimax(depth, 'blue', i, j, False, alpha, beta)
                        scoreslol.append((score, i, j)) # ---------TEST------------

                        # reset
                        # self.minimax_turn_number -= 1
                        # self.minimax_history[self.board.tobytes()] -= 1

                        self.board[i][j] = 0

                        if (score > bestScore):
                            bestScore = score      
                            bestMove = (i, j)

                        # Alpha-beta pruning
                        alpha = max(alpha, bestScore)

                        if beta <= alpha:
                            
                            # print("*********** PRUNED ********** inside maximising") # -------------- TEST ---------------
                            breakOutOfNestedLoop = True
                            break
                
                if breakOutOfNestedLoop:
                    break
            
            self.iterations = 0

            # for elem in scoreslol: # ---------TEST------------
            #     print(f"for ({elem[1]}, {elem[2]}), score = {elem[0]}") 
            
            print(f"bestmove: {bestMove} ")

            return ('PLACE', bestMove[0], bestMove[1])

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

        def bridge_ends(pos, size):
            # i is letter and j is number
            (i, j) = pos
            ends_list = []
            possible_ends_list = [(i+2, j-1), (i+1, j-2), (i+1, j+1), (i-1, j-1), (i-1, j+2), (i-2, j+1)]
            for possible_pos in possible_ends_list:
                if (check_pos(possible_pos, size)):
                    ends_list.append(possible_pos)
            return ends_list

        def bridging_factor():
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

                        # For all bridges leading from this hex
                        for n in bridge_ends_list:
                            val = self.board[n[0]][n[1]]
                            if val == current_player: # If bridge leads to another one of our pieces
                                score += 3 * current_player
                            elif val == -1 * current_player: # If bridge leads to an opponent piece
                                score += -5 * current_player 
                        
                        # print(f"heuristic score is: {score}")
            return score

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

        def heuristic(last_move):

            score = 0

            # if self.capturing(last_move): # [(0, 1), (2, 0)]
            #     score += 100000

            # print(f"score after possible capturing: {score}")
            
            # time.sleep(0.2271)

            # Opening
            if self.turn_number < self.board_size // 2:
                bridging_score = bridging_factor()
                centred_score = centred()

                # print(f"bridging score: {bridging_score}")
                # print(f"centred score: {centred_score}")
                # print(f"piece diff score: {piece_difference_score}")

                score += 2 * bridging_score + 2 * centred_score

            # Midgame
            else:
                red_score = search_dijkstra_red(self.board_size, self.board)
                blue_score = search_dijkstra_blue(self.board_size, self.board)
                # print(f"red_score: {red_score}")
                # print(f"blue_score: {blue_score}")
                # print(f"dijkstra score: {red_score - blue_score}")
                dijkstra_score = red_score - blue_score
                bridging_score = bridging_factor()

                print(f"bridging score: {bridging_score}")
                print(f"dijkstra score: {dijkstra_score}")
                
                score = bridging_score + 30 * dijkstra_score
                
                # print(f"bridging_score: {bridging_score}")
                # print(f"dijkstra score: {red_score - blue_score}")
                # print("---------------------")




            # print(f"heuristic score: {heuristic_score}")
            # print(self.board[::-1])
            # print("----------------")

            
            # print(f"total score: {score}")
            # print("===============")

            return score
        
        def alphaBetaMinimax(depth, last_player, last_x, last_y, isMaxPlayer, alpha, beta):

            self.iterations += 1
            
            nv = -1.0e39 # negative infinity
            pv = 1.0e39 # positive infinity

            # print(f"current depth: {depth}") # ---------TEST------------

            # HEURISTIC FUNCTION
            # print(f"last player: {last_player}, last move: {last_x}, {last_y}")
            if (depth >= Player.MAX_DEPTH):
                # return heuristic(last_player)
                return heuristic((last_x, last_y))

            # if (depth >= Player.MAX_DEPTH):
            #     return heuristic_aStarSearch()

            # EVALUATION FUNCTION
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
                            self.board[i][j] = Player.PLAYER_REPRESENTATIONS['blue']

                            # ------ Implement capturing mechanism -------
                            
                            # if self.turn_number >= 4:
                            #     hexes_to_capture = self.capturing((i, j))
                            #     if hexes_to_capture: # [(0, 1), (2, 0)]
                            #         for elem in hexes_to_capture:
                            #             # self.c += 1
                            #             # print("capturing iteration: ", self.c)
                            #             self.board[elem] = 0

                            # ------ End capturing mechanism -------

                            # self.minimax_turn_number += 1
                            # self.minimax_history[self.board.tobytes()] += 1

                            score = alphaBetaMinimax(depth + 1, 'blue', i, j, False, alpha, beta)

                            # # reset
                            self.board[i][j] = 0
                            # self.minimax_turn_number -= 1
                            # self.minimax_history[self.board.tobytes()] -= 1

                            # print(f"score: {score}") # -------------- TEST ---------------

                            if (score > bestScore):
                                bestScore = score

                            # print(f"best score: {bestScore}") # -------------- TEST ---------------
                            
                            # print(f'alpha before: {alpha}')
                            # print(f'beta before: {beta}\n')

                            # Alpha-beta pruning
                            alpha = max(alpha, bestScore)

                            # print(f'alpha after: {alpha}')
                            # print(f'beta after: {beta}\n')

                            if beta <= alpha:
                                # print("*********** PRUNED ********** inside maximising") # -------------- TEST ---------------
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
                            self.board[i][j] = Player.PLAYER_REPRESENTATIONS['red']

                            # ------ Implement capturing mechanism -------
                            
                            # if self.turn_number >= 4:
                            #     hexes_to_capture = self.capturing((i, j))
                            #     if hexes_to_capture: # [(0, 1), (2, 0)]
                            #         for elem in hexes_to_capture:
                            #             # self.c += 1
                            #             # print("capturing iteration: ", self.c)
                            #             self.board[elem] = 0
                            # ------ End capturing mechanism -------

                            # self.minimax_turn_number += 1
                            # self.minimax_history[self.board.tobytes()] += 1

                            score = alphaBetaMinimax(depth + 1,'red', i, j, True, alpha, beta)

                            # reset
                            self.board[i][j] = 0
                            # self.minimax_turn_number -= 1
                            # self.minimax_history[self.board.tobytes()] -= 1

                            if (score < bestScore):
                                bestScore = score
                            
                            # print(f'alpha before: {alpha}')
                            # print(f'beta before: {beta}')

                            # Alpha-beta pruning
                            beta = min(beta, bestScore)

                            # print(f'alpha after: {alpha}')
                            # print(f'beta after: {beta}')

                            if beta <= alpha:
                                # print("*********** PRUNED ********** inside minimising") # -------------- TEST ---------------
                                breakOutOfNestedLoop = True
                                break

                            
                            # print('score: ', score, "bestscore: ", bestScore)
                    
                    if breakOutOfNestedLoop:
                        break
                                         
            
                return bestScore
        
        # Main code
        if self.colour == 'blue':

            # Decide whether to steal
            if self.turn_number == 2:
                
                # Hexes not to steal
                safe_hexes = []
                for i in range(self.board_size):
                    for j in range(self.board_size):
                        # Change this later possibly
                        if i == 0 or i == self.board_size - 1 or j == 0 or j == self.board_size - 1:
                            safe_hexes.append((i, j))

                if (self.last_placement[1], self.last_placement[2]) not in safe_hexes:
                    return ('STEAL', )
                
                else:
                    # AI's turn
                    return AIMove()
            
            # ONLY PLACE ACTIONS FROM TURN 3 ONWARDS
            else:
                # AI's turn
                return AIMove()


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
        # put your code here

        if action[0].upper() == 'PLACE': # 'PLACE'
            self.board[action[1]][action[2]] = Player.PLAYER_REPRESENTATIONS[player]

            # Capturing
            if self.capturing((action[1], action[2])): # [(0, 1), (2, 0)]
                for elem in self.capturing((action[1], action[2])):
                    self.board[elem] = 0
            
        else: # 'STEAL'
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

        # print(self.board[::-1])



        

