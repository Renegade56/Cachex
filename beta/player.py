from pydoc import doc
from collections import Counter
import numpy
from queue import Queue
import time

class Player:

    PLAYER_REPRESENTATIONS = {
        "red": 1,
        "blue": 2
    }

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
        self.turn_number = 1 # Start from turn 1
        self.last_placement = tuple()
        
        # Represent board as 2d array
        self.board = numpy.zeros((n, n), dtype=int)
        self.history = Counter({self.board.tobytes(): 1})
        
        

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

        def game_end(lp, lx, ly): # game_end(last_player='blue', last_x=i, last_y=j)  
            
            print("last player: ", lp) #--------------------TEST-----------------------
            print("x: ", lx, "y: ", ly) #--------------------TEST-----------------------

            PLAYER_AXIS = {
                "red": 0, # Red aims to form path in r/0 axis
                "blue": 1 # Blue aims to form path in q/1 axis
            }

            MAX_REPEAT_STATES = 7
            MAX_TURNS = 343

            # Continuous path formed by either player
            #if self.turn_number >= (self.board_size * 2) - 1:  
            reachable = connected_coords((lx, ly))
            print (f"***(reachable) from {lx}, {ly}: {reachable}") #--------------------TEST-----------------------
            
            axis_vals = [coord[PLAYER_AXIS[lp]] for coord in reachable]
            print(f"axis vals: {axis_vals}") #--------------------TEST-----------------------
             
            print(f"board:\n {self.board[::-1]}") #--------------------TEST-----------------------
            print("\n------------------------------------------------\n") #--------------------TEST-----------------------
            

            # time.sleep(0.5)

            if min(axis_vals) == 0 and max(axis_vals) == self.board_size - 1:
                print("HYPOTHETICAL WINNER: ", lp) #--------------------TEST-----------------------
                print("\n------------------------------------------------\n") #--------------------TEST-----------------------
                return lp

            # Draw due to repetition
            if self.history[self.board.tobytes()] >= MAX_REPEAT_STATES:
                return 'draw'

            # Draw due to too many turns
            if self.turn_number >= MAX_TURNS:
                return 'draw'

            return False

        # if self.colour == 'red' and self.turn_number == 1:
        #     return ('PLACE', 3, 2)
        #     # return ('PLACE', (self.board_size // 2) + 1, (self.board_size // 2))

        def AIMove():
            bestScore = -1.0e40
            bestMove = 0

            scoreslol = []

            for i in range(0, self.board_size):
                for j in range(0, self.board_size):
                    if self.board[i][j] == 0:
                        self.board[i][j] = Player.PLAYER_REPRESENTATIONS['blue']
                        score = alphaBetaMinimax('blue', i, j, False, -1.0e40, 1.0e40)
                        scoreslol.append((score, i, j)) # ---------TEST------------
                        self.board[i][j] = 0
                        if (score > bestScore):
                            bestScore = score      
                            bestMove = (i, j)

            
            for elem in scoreslol: # ---------TEST------------
                print(f"for ({elem[1]}, {elem[2]}), score = {elem[0]}") 

            return ('PLACE', bestMove[0], bestMove[1])
        
        def alphaBetaMinimax(last_player, last_x, last_y, isMaxPlayer, alpha, beta):
            nv = -1.0e40 # negative infinity
            pv = 1.0e40 # positive infinity

            alpha = alpha
            beta = beta

            # EVALUATION FUNCTION
            result = game_end(last_player, last_x, last_y)
            
            # If end of game   
            if result == 'red':
                return -1
            elif result == 'blue':
                return 1
            elif result == 'draw':
                return 0

            if isMaxPlayer:

                bestScore = nv
                for i in range(0, self.board_size):
                    for j in range(0, self.board_size):
                        if self.board[i][j] == 0:
                            self.board[i][j] = Player.PLAYER_REPRESENTATIONS['blue']
                            score = alphaBetaMinimax('blue', i, j, False, alpha, beta)

                            if (score > bestScore):
                                bestScore = score

                            # Alpha-beta pruning
                            alpha = max(alpha, bestScore)
                            if beta <= alpha:
                                break      

                            self.board[i][j] = 0
            
                return bestScore

            else:
                
                bestScore = pv
                for i in range(0, self.board_size):
                    for j in range(0, self.board_size):
                        if self.board[i][j] == 0:
                            self.board[i][j] = Player.PLAYER_REPRESENTATIONS['red']
                            score = alphaBetaMinimax('red', i, j, True, alpha, beta)

                            if (score < bestScore):
                                bestScore = score

                            # Alpha-beta pruning
                            beta = min(beta, bestScore)
                            if beta <= alpha:
                                break

                            self.board[i][j] = 0
                            # print('score: ', score, "bestscore: ", bestScore)
                                         
            
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

        # print(self.board) # CHECK ----------------------------------------
        self.turn_number += 1 # Increment turn count
        self.history[self.board.tobytes()] += 1 # Add board state to history



        

