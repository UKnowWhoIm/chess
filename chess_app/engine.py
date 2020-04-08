
BLACK = 'black'
WHITE = 'white'


def get_player(piece):
    if piece == 'f':
        return ''
    if ord(piece) > 96:
        return BLACK
    return WHITE


def get_color(pos):
    [x, y] = get_coods(pos)
    if (x + y) % 2 == 1:
        return WHITE
    return BLACK


def get_coods(n):
    x = n // 8
    y = n % 8
    return [x, y]


def get_pos(x, y):
    pos = x * 8
    pos += y
    return pos


def can_go_left(pos):
    return pos % 8 != 0


def can_go_right(pos):
    return pos % 8 != 7


def reverse_player(player):
    if player == WHITE:
        return BLACK
    return WHITE


def generate_moves(board, pos, updation):
    moves = []
    for u in updation:
        i = pos
        i += u[0]
        while 0 <= i <= 63:
            if u[1] and not u[1](i):
                # Next move Out of bounds
                moves.append(i)
                break
            if get_player(board[i]) == get_player(board[pos]):
                # Own Piece
                break
            if board[i] != 'f':
                # Capture
                moves.append(i)
                break
            # Blank Space
            moves.append(i)
            i += u[0]
    return moves


def get_valid_moves(board, piece, pos, player, castle):
    moves = []
    coods = get_coods(pos)
    if piece.lower() == 'p':
        if player == BLACK:
            # Black
            dirn = 1
            initial_row = 1
        else:
            # White
            dirn = -1
            initial_row = 6
        if board[pos + dirn * 8] == 'f':
            # Single Step(normal)
            moves.append(pos + dirn * 8)
        if coods[0] == initial_row and board[pos + dirn * 16] == 'f' and board[pos + dirn * 8] == 'f':
            # Double Step(initial)
            moves.append(pos + dirn * 16)
        if board[pos + dirn * 8 - 1] != 'f' and get_player(board[pos + dirn * 8 - 1]) != player and can_go_left(pos):
            # left side capture
            moves.append(pos + dirn * 8 - 1)
        if board[pos + dirn * 8 + 1] != 'f' and get_player(board[pos + dirn * 8 + 1]) != player and can_go_right(pos):
            # right side capture
            moves.append(pos + dirn * 8 + 1)
    elif piece.lower() == 'n':
        posns = []
        if can_go_right(pos):
            # Case 1
            # . . x
            # . . .
            # . K .
            # . . .
            # . . x
            posns += [17, -15]
            if can_go_right(pos + 1):
                # Case 2
                # . . . . x
                # . . N . .
                # . . . . x
                posns += [-6, 10]
        if can_go_left(pos):
            # Case 1 to left
            posns += [-17, 15]
            if can_go_left(pos - 1):
                # Case 2 to left
                posns += [6, -10]
        for target in [i + pos for i in posns if 0 <= i + pos <= 63]:
            if get_player(board[target]) != player:
                moves.append(target)
    elif piece.lower() == 'k':
        posns = [-8, 8]
        if can_go_right(pos):
            if castle and castle[player][1]:
                if board[pos + 1] == 'f' and board[pos + 2] == 'f' and not is_check(board, player, True, pos + 1):
                    posns += [2]
            posns += [9, 7, 1]
        if can_go_left(pos):
            if castle and castle[player][0]:
                if board[pos - 1] == 'f' and board[pos - 2] == 'f' and not is_check(board, player, True, pos - 1):
                    posns += [-2]
            posns += [-9, -7, -1]
        for target in [i + pos for i in posns if 0 <= i + pos <= 63]:
            if get_player(board[target]) != player:
                moves.append(target)
    else:
        # Queen, Rook, Bishop
        rook_updation = [[-8, None], [8, None]]
        bishop_updation = []
        if can_go_left(pos):
            rook_updation.append([-1, can_go_left])
            bishop_updation += [[-9, can_go_left], [7, can_go_left]]
        if can_go_right(pos):
            rook_updation.append([1, can_go_right])
            bishop_updation += [[9, can_go_left], [-7, can_go_left]]
        if piece.lower() == 'q':
            moves += generate_moves(board, pos, bishop_updation + rook_updation)
        elif piece.lower() == 'b':
            moves += generate_moves(board, pos, bishop_updation)
        elif piece.lower() == 'r':
            moves += generate_moves(board, pos, rook_updation)
    return moves


def find_king(board, player):
    if player == WHITE:
        # White King would mostly be on the bottom half of the board
        target = 'K'
        start = 63
        stop = 0
        step = -1
    else:
        # Black King would mostly be on the top half of the board
        target = 'k'
        start = 0
        stop = 63
        step = 1
    for i in range(start, stop, step):
        if board[i] == target:
            return i


def move(board, current, target):
    # Make the actual move
    piece = board[current]
    board = board[:current] + 'f' + board[current + 1:]
    board = board[:target] + piece + board[target + 1:]
    return board


def get_all_moves_player(board, player, castle):
    moves = []
    for i in range(64):
        if get_player(board[i]) == player:
            moves += get_valid_moves(board, board[i], i, player, castle)
    return moves


def is_check(board, player, skip_pieces=False, king_pos=None):
    if king_pos is None:
        king_pos = find_king(board, player)

    pieces = []
    for i in range(64):
        if board[i].lower() != 'k' and get_player(board[i]) == reverse_player(player):
            if board[i].lower() == 'b' and get_color(i) != get_color(king_pos):
                # Bishops can only move in same color
                continue
            if board[i].lower() == 'n' and get_color(i) == get_color(king_pos):
                # Knights move in alternate colors
                continue
            if king_pos in get_valid_moves(board, board[i], i, reverse_player(player), None):
                if skip_pieces:
                    return True
                pieces.append(i)
    return pieces


def is_checkmate(board, player, responsible_pieces):
    # Player is currently in check
    king_pos = find_king(board, player)
    king_moves = get_valid_moves(board, board[king_pos], king_pos, player, None)
    for king_move in king_moves:
        # King can move
        temp_board = move(board, king_pos, king_move)
        if not is_check(temp_board, player, True, king_move):
            return False
    if len(responsible_pieces) > 1:
        # Check involving multiple pieces cant be blocked or captured
        return True
    target = responsible_pieces[0]
    for i in range(len(board)):
        if board[i].lower() != 'k' and get_player(board[i]) == player:
            if board[i].lower() == 'b' and get_color(i) != get_color(target):
                # bishop can only move through same color
                continue
            if board[i].lower() == 'n' and get_color(i) == get_color(target):
                # Knights move in alternate colors
                continue
            if target in get_valid_moves(board, board[i], i, player, None):
                # Some piece can capture
                return False
    if board[target].lower == 'n' or board[target].lower() == 'p':
        # Pawn and Knight Checks can't be blocked
        return True
    # TODO Block Check
    return True


def interface(board, player, current, target, castle, checked=False):
    if checked:
        # If in check, king can't castle
        castle_ = None
    else:
        castle_ = castle
    if get_player(board[current]) != player:
        # Not  their piece
        return False
    if get_player(board[target]) == player:
        # Trying to capture own piece?
        return False
    if target in get_valid_moves(board, board[current], current, player, castle_):
        temp_board = move(board, current, target)
        if is_check(temp_board, player, True):
            # Move results in check
            return False
        return True
    return False


bo_ = "rnbqkbnrppppppppffffffffffffffffffffffffffffffffPPPPPPPPRNBQKBNR"

print(bo_)
for z in range(64):
    if z % 8 == 0:
        print()
    print(bo_[z], end=' ')
print()
