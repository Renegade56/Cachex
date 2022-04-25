import numpy
from referee.board import Board
from collections import Counter

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
        # put your code here

        row = int(input("Enter row coordinate: "))
        column = int(input("Enter column coordinate: "))

        return ('PLACE', row, column)


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



        