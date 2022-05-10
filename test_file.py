from queue import PriorityQueue
import numpy

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
        [0, 1, 0, 0, 0],
        [0, 0, 0, 0, 0]]

size = 5

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
        return r >= 0 and r < 3 and q >= 0 and q < 3
    
    _SWAP_PLAYER = { 0: 0, 1:-1, -1:1 }
    opp_type = board[coord]

    mid_type = _SWAP_PLAYER[opp_type]
    captured = set()

    for pattern in _CAPTURE_PATTERNS:

        coords = [_ADD(coord, s) for s in pattern]
        # No point checking if any coord is outside the board!

        # if all coords are legal
        if all(map(inside_bounds, coords)):

            tokens = [board[coord] for coord in coords]
            if tokens == [opp_type, mid_type, mid_type]:
                # Capturing has to be deferred in case of overlaps
                # Both mid cell tokens should be captured
                captured.update(coords[1:])
    
    return list(captured)

# print(capturing([1,2]))
coord = (1, 2)
print(board[coord])