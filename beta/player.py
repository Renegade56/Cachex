from referee.board import Board
from collections import Counter

class Player:
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
        self.history = Counter({self.board.tobytes(): 1})

        # Represent board as 2d array
        self.board = [ [0] * n for i in range(n) ]
        
        

    def action(self):
        """
        Called at the beginning of your turn. Based on the current state
        of the game, select an action to play.
        """
        # put your code here

        if self.colour == 'red' and self.turn_number == 1:
            return ('PLACE', 3, 2)
            # return ('PLACE', (self.board_size // 2) + 1, (self.board_size // 2))
        
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
                    pass # CONTINUE ON WITH MINIMAX ETC.
            
            # ONLY PLACE ACTIONS FROM TURN 3 ONWARDS
            else:
                pass
        
        def game_end():
            
            PLAYER_AXIS = {
                "red": 0, # Red aims to form path in r/0 axis
                "blue": 1 # Blue aims to form path in q/1 axis
            }

            MAX_REPEAT_STATES = 7
            MAX_TURNS = 343

            # Continuous path formed by either player
            if self.turn_number >= (self.board_size * 2) - 1:
                reachable = Board.connected_coords((self.last_placement[1], self.last_placement[2]))
                axis_vals = [coord[PLAYER_AXIS[self.last_placement[0]]] for coord in reachable]
                if min(axis_vals) == 0 and max(axis_vals) == self.board_size - 1:
                    return True

            # Draw due to repetition
            if self.history[self.board.tobytes()] >= MAX_REPEAT_STATES:
                return True

            # Draw due to too many turns
            if self.turn_number >= MAX_TURNS:
                return True

            return False


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
            self.board[action[1]][action[2]] = player[0]
            
        else: # 'STEAL'
            is_looping = True
            for i in range(self.board_size):
                for j in range(self.board_size):
                    if self.board[i][j] != 0:
                        self.board[j][i] = player[0]
                        self.board[i][j] = 0
                        is_looping = False
                
                if not is_looping:
                    break
        
        if action[0].upper() != "STEAL":
            self.last_placement = (player, action[1], action[2])

        print(self.board) # CHECK ----------------------------------------
        self.turn_number += 1 # Increment turn count
        self.history[self.board.tobytes()] += 1 # Add board state to history



        

