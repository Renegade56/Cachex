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

    MAX_DEPTH = 2



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

        def list_neighbours_search(coord, tokens, n):
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
            
            neighbours_list2 = [tuple(elem) for elem in neighbours_list if tuple(elem) not in tokens]

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
        
        def good_half_neighbour(which_player, pos):
            # i is letter and j is number
            (i, j) = pos
            neighbour_list = []
            if which_player == Player.PLAYER_REPRESENTATIONS['blue']:
                possible_pos_list = [ (i-1, j+1), (i, j+1), (i+1, j) ] # left to right
            elif which_player == Player.PLAYER_REPRESENTATIONS['red']:
                possible_pos_list = [ (i+1, j-1), (i+1, j), (i, j+1) ] # up to down
            for possible_pos in possible_pos_list:
                if (check_pos(possible_pos, self.board_size)):
                    neighbour_list.append(possible_pos)
            return neighbour_list

        def track_path_len(which_player, pos):
            path_len = 1
            i = pos[0]
            j = pos[1]
            next_i = i
            next_j = j

            while(check_pos((next_i,next_j), self.board_size)):
                
                found = False
                for good_neighbour in good_half_neighbour(which_player, (next_i, next_j), self.board_size):
                    
                    if self.board[good_neighbour[0]][good_neighbour[1]] == which_player:
                        next_i = good_neighbour[0]
                        next_j = good_neighbour[1]
                        found = True

                        path_len += 1
                        break
                if found == False:
                    break

            return path_len

        def good_half_neighbour_opposite_direction(which_player, pos):
            # i is letter and j is number
            (i, j) = pos
            neighbour_list = []
            if which_player == Player.PLAYER_REPRESENTATIONS['blue']:
                possible_pos_list = [ (i-1, j), (i, j-1), (i+1, j-1) ] # red, right to left
            elif which_player == Player.PLAYER_REPRESENTATIONS['red']:
                possible_pos_list = [ (i-1, j), (i-1, j+1), (i, j-1) ] # blue, down to up
            for possible_pos in possible_pos_list:
                if (check_pos(possible_pos, self.board_size)):
                    neighbour_list.append(possible_pos)
            return neighbour_list

        def track_path_len_opposite_direction(which_player, pos):
            path_len = 1
            i = pos[0]
            j = pos[1]
            next_i = i
            next_j = j

            while(check_pos((next_i,next_j), self.board_size)):
                found = False
                for good_neighbour in good_half_neighbour_opposite_direction(which_player, (next_i, next_j)):
                    
                    if self.board[good_neighbour[0]][good_neighbour[1]] == which_player:
                        next_i = good_neighbour[0]
                        next_j = good_neighbour[1]
                        found = True
                        path_len += 1
                        break
                
                if found == False:
                    break

            return path_len

        def connect_degree(which_player):
            score = 0
            path_length_1 = 0
            path_length_2 = 0
            if which_player == Player.PLAYER_REPRESENTATIONS['red']:
                if self.board[self.board_size - 1][self.board_size // 2] == Player.PLAYER_REPRESENTATIONS['red']:
                    score -= 50
                for i in range(self.board_size):
                    if self.board[i][0] == Player.PLAYER_REPRESENTATIONS['red']:
                        path_length_1 = track_path_len(self.board, which_player, (i, 0), self.board_size)
                    if self.board[i][self.board_size-1] == Player.PLAYER_REPRESENTATIONS['red']:
                        path_length_2 = track_path_len_opposite_direction(self.board, which_player, (i, self.board_size-1), self.board_size)
                    score -= 10 * max(path_length_1, path_length_2)
            if which_player == Player.PLAYER_REPRESENTATIONS['blue']:
                if self.board[self.board_size // 2][0] == Player.PLAYER_REPRESENTATIONS['blue']:
                    score += 50
                if self.board[self.board_size // 2][self.board_size - 1] == Player.PLAYER_REPRESENTATIONS['blue']:
                    score += 50
                for i in range(self.board_size):
                    if self.board[0][i] == Player.PLAYER_REPRESENTATIONS['blue']:
                        path_length_1 = track_path_len(self.board, which_player, (0, i), self.board_size)
                    if self.board[self.board_size-1][i] == Player.PLAYER_REPRESENTATIONS['blue']:
                        path_length_2 = track_path_len_opposite_direction(self.board, which_player, (self.board_size-1, i), self.board_size)
                    score += 10 * max(path_length_1, path_length_2)
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
                if count >= 4:
                    score -= 20 # unnecessarily too many blues
                elif count <= -4:
                    score += 20 # unnecessarily too many reds
            return score

        def defend():
            # If opponent seeks to destroy bridge, defend the bridge by playing the second available connecting route
            


            return

        def aStarHeuristic(goal, current):
            # Manhattan distance on a hex grid
            if (goal[1] == current[1]) & (goal[0] == current[0]):
                return 0
            if goal[0] == current[0]: # same row
                return abs(goal[1] - current[1])
            if goal[1] == current[1]: # same column
                return abs(goal[0] - current[0])
            else: # column mismatch
                if goal[1] > current[1]: # if column 2 > column 1
                    if goal[0] > current[0]: # if row 2 > row 1
                        return abs(goal[0] - current[0]) + abs(goal[1] - current[1])
                    else: # if row 1 > row 2
                        return max(abs(goal[0] - current[0]), abs(goal[1] - current[1]))
                else: # if column 1 > column 2
                    if goal[0] > current[0]: # if row 2 > row 1
                        return max(abs(goal[0] - current[0]), abs(goal[1] - current[1]))
                    else: # if row 1 > row 2
                        return abs(goal[0] - current[0]) + abs(goal[1] - current[1])

        def aStarSearch(start, goal):

            start_coordinates = start
            goal_coordinates = goal
            
            token_coordinates = []
            for i in range(self.board_size):
                for j in range(self.board_size):
                    if self.board[i][j] != 0:
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
                
                for next in list_neighbours_search(current, token_coordinates, self.board_size):
                    new_cost = cost_so_far[tuple(current)] + 1

                    if next not in cost_so_far or new_cost < cost_so_far[next]:
                        cost_so_far[next] = new_cost
                        priority = new_cost + aStarHeuristic(goal_coordinates, next)
                        frontier.put(next, priority)
                        came_from[next] = current
    
            if tuple(goal_coordinates) not in cost_so_far:
                return 0
            else:
                return cost_so_far[tuple(goal_coordinates)] + 1

        def heuristic_aStarSearch():
            # Using A Star as the heuristic to determine state of board
            score = 0

            TOP_BORDER_HEXES = [(self.board_size - 1, i) for i in range(self.board_size)]
            BOTTOM_BORDER_HEXES = [(0, i) for i in range(self.board_size)]
            LEFT_BORDER_HEXES = [(i, 0) for i in range(self.board_size)]
            RIGHT_BORDER_HEXES = [(self.board_size - 1, 0) for i in range(self.board_size)]
           
            # For each hex
            for i in range(self.board_size):
                for j in range(self.board_size):
                    
                    # for each player
                    if self.board[i][j] == Player.PLAYER_REPRESENTATIONS['blue']:
                        for hex in LEFT_BORDER_HEXES:
                            score -= aStarSearch((i,j), hex)

                        for hex in RIGHT_BORDER_HEXES:
                            score -= aStarSearch((i, j), hex)
                    
                    elif self.board[i][j] == Player.PLAYER_REPRESENTATIONS['red']:
                        for hex in LEFT_BORDER_HEXES:
                            score += aStarSearch((i, j), hex)

                        for hex in RIGHT_BORDER_HEXES:
                            score += aStarSearch((i, j), hex)
            
            return score

        def heuristic_dijkstra():
            
            # def findShortestPathsUsingDijkstra(_from, perspective)

            # def getShortestPathFrom(_from, to, perspective):
            #     findShortestPathsUsingDijkstra(_from, perspective)

            # # For each hex
            # for i in range(self.board_size):
            #     for j in range(self.board_size):
            #         getShortestPathFrom(self.board[i][j], 'red') # change perspective later

            

            # # Shortest path using Dijkstra
            # AIPath = 
            # playerPath = 
            # def getScoreForPath(path, value):

            #     return
            
            # AIScore = getScoreForPath(AIPath, )
            # playerScore = getScoreForPath(playerPath, )

            # return AIScore - playerScore
            return

        def heuristic(which_player):

            heuristic_score = 5 * connect_degree(which_player) #+ 1.5 * centred()

            # print(f"heuristic score: {heuristic_score}")
            # print(self.board[::-1])
            # print("----------------")


            # time.sleep(0.2271)

            return heuristic_score
        
        def alphaBetaMinimax(depth, last_player, last_x, last_y, isMaxPlayer, alpha, beta):

            self.iterations += 1
            
            nv = -1.0e39 # negative infinity
            pv = 1.0e39 # positive infinity

            # print(f"current depth: {depth}") # ---------TEST------------

            # HEURISTIC FUNCTION
            if (depth >= Player.MAX_DEPTH):
                # if last_player == 'blue':
                #     return heuristic('red')
                # else:
                #     return heuristic('blue')
                return heuristic(last_player)

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



        

