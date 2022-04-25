from pydoc import doc
from collections import Counter
import numpy
from queue import Queue

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
        
        def Min(): # Human player
            pv = 1.0e40 # positive infinity
            qx = None
            qy = None

            result = game_end()
            print("*************** this is min: ", result) # TEST ------------------------------------------------------------

            if result == 'red':
                return (-1, 0, 0)
            elif result == 'blue':
                return (1, 0, 0)
            elif result == 'draw':
                return (0, 0, 0)

            for i in range(0, self.board_size):
                for j in range(0, self.board_size):
                    if self.board[i][j] == 0:
                        # AI makes a move and calls Min()
                        self.board[i][j] = Player.PLAYER_REPRESENTATIONS['red']
                        (m, max_i, max_j) = Max()

                        if m < pv:
                            pv = m
                            qx = i
                            qy = j
                        
                        # Set field back to empty
                        self.board[i][j] = 0
            
            return (pv, qx, qy)
        
        def Max(): # AI player
            nv = -1.0e40 # negative infinity
            px = None
            py = None

            result = game_end()
            print("this is min: ", result) # TEST ------------------------------------------------------------

            if result == 'red':
                return (-1, 0, 0)
            elif result == 'blue':
                return (1, 0, 0)
            elif result == 'draw':
                return (0, 0, 0)

            for i in range(0, self.board_size):
                for j in range(0, self.board_size):
                    if self.board[i][j] == 0:
                        # AI makes a move and calls Min()
                        self.board[i][j] = Player.PLAYER_REPRESENTATIONS['blue']
                        (m, min_i, min_j) = Min()

                        if m > nv:
                            nv = m
                            px = i
                            py = j
                        
                        # Set field back to empty
                        self.board[i][j] = 0
            
            return (nv, px, py)
        
        # From board.py
        def connected_coords(self, start_coord):
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

        def game_end():
            
            PLAYER_AXIS = {
                "red": 0, # Red aims to form path in r/0 axis
                "blue": 1 # Blue aims to form path in q/1 axis
            }

            MAX_REPEAT_STATES = 7
            MAX_TURNS = 343

            # Continuous path formed by either player
            #if self.turn_number >= (self.board_size * 2) - 1:  
            reachable = connected_coords(self, (self.last_placement[1], self.last_placement[2]))
            print ("************************(reachable): ", reachable)
            axis_vals = [coord[PLAYER_AXIS[self.last_placement[0]]] for coord in reachable]
            print ("************************(axis_vals: ", axis_vals)
            if min(axis_vals) == 0 and max(axis_vals) == self.board_size - 1:
                print ("************************(self.last_placement): ", self.last_placement[0])
                return self.last_placement[0]

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
                    (m, px, py) = Max()
                    print ("************************(m, px, py): ", m, px, py)
                    return ('PLACE', px, py)
            
            # ONLY PLACE ACTIONS FROM TURN 3 ONWARDS
            else:
                # AI's turn
                (m, px, py) = Max()
                print ("************************(m, px, py): ", m, px, py)
                return ('PLACE', px, py)
        
        # def minimax(node, depth, isMaxPlayer):
        #     nv = -1.0e40 # negative infinity
        #     pv = 1.0e40 # positive infinity

        #     if depth == 0 or game_end(node):
        #         return heuristic value of node
        #     if isMaxPlayer:
        #         value = nv
        #         for each child of node:
        #             value = max(value, minimax(child, depth - 1, False))
        #         return value

        #     else:
        #         value = pv
        #         for each child of node:
        #             value = min(value, minimax(child, depth - 1, True))
        #         return value 


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



        

