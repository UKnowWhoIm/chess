
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


"""
The following functions are used for optimizing the engine
These are constant time functions which checks if the move can ever be legal using the basic 
move conditions for each piece
Similar to alpha beta optimization in minimax, these functions will never affect the final outcome, it will just 'prune'
the unnecessary 'nodes'
"""


def check_bishop(current_pos, target_pos):
    current_cood = get_coods(current_pos)
    target_cood = get_coods(target_pos)
    diff = [current_cood[0] - target_cood[0], current_cood[1] - target_cood[1]]
    if abs(diff[0]) != abs(diff[1]):
        # Bishop can only move diagonally
        # Therefore absolute value of x diff and y diff should be same
        return False
    return True


def check_rook(current_pos, target_pos):
    current_cood = get_coods(current_pos)
    target_cood = get_coods(target_pos)
    diff = [current_cood[0] - target_cood[0], current_cood[1] - target_cood[1]]
    if diff[0] != 0 and diff[1] != 0:
        # Rook can move only vertically or horizontally
        # Therefore either x diff or y diff should be 0
        return False
    return True


def check_pawn(current_pos, target_pos, player, is_capture):
    if player == WHITE:
        dirn = -1
        capture_diff = [-9, -7]
    else:
        dirn = 1
        capture_diff = [7, 9]
    if is_capture:
        # Capture move
        for x in capture_diff:
            if current_pos + x == target_pos:
                return True
        return False
    if dirn * (target_pos - current_pos) == 8 or dirn * (target_pos - current_pos) == 16:
        # Normal move
        return True
    return False


def check_knight(current_pos, target_pos):
    # All of knights moves have absolute diff of [2, 1] or [1, 2]
    current_cood = get_coods(current_pos)
    target_cood = get_coods(target_pos)
    abs_diff = [abs(current_cood[0] - target_cood[0]), abs(current_cood[1] - target_cood[1])]
    if abs_diff == [1, 2] or abs_diff == [2, 1]:
        return True
    return False


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


def get_valid_moves(board, piece, pos, player, castle, queen_bishop_check=True, queen_rook_check=True):
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
        if can_go_left(pos) and board[pos + dirn * 8 - 1] != 'f' and get_player(board[pos + dirn * 8 - 1]) != player:
            # left side capture
            moves.append(pos + dirn * 8 - 1)
        if can_go_right(pos) and board[pos + dirn * 8 + 1] != 'f' and get_player(board[pos + dirn * 8 + 1]) != player:
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
            posns += [9, -7, 1]
        if can_go_left(pos):
            if castle and castle[player][0]:
                if board[pos - 1] == 'f' and board[pos - 2] == 'f' and board[pos - 3] == 'f' and \
                        not is_check(board, player, True, pos - 1):
                    posns += [-2]
            posns += [-9, 7, -1]
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
            bishop_updation += [[9, can_go_right], [-7, can_go_right]]
        if piece.lower() == 'q':
            if queen_bishop_check:
                moves += generate_moves(board, pos, bishop_updation)
            if queen_rook_check:
                moves += generate_moves(board, pos, rook_updation)
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
        if king_pos is None:
            # Sometimes mini_max enemy captures the king
            # Therefore king_pos would be None
            # return True to quickly terminate the execution of that branch
            return True
    pieces = []
    queen_bishop_check = True
    queen_rook_check = True
    for i in range(64):
        if get_player(board[i]) == reverse_player(player):
            if board[i].lower() == 'b' and not check_bishop(i, king_pos):
                continue
            elif board[i].lower() == 'r' and not check_rook(i, king_pos):
                continue
            elif board[i].lower() == 'p' and not check_pawn(i, king_pos, reverse_player(player), True):
                continue
            elif board[i].lower() == 'q':
                if check_bishop(i, king_pos):
                    queen_bishop_check = True
                else:
                    queen_bishop_check = False
                if check_rook(i, king_pos):
                    queen_rook_check = True
                else:
                    queen_rook_check = False
            elif board[i].lower() == 'n' and not check_knight(i, king_pos):
                # Knights move in alternate colors
                continue
            if king_pos in get_valid_moves(board, board[i], i, reverse_player(player), None, queen_bishop_check,
                                           queen_rook_check):
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
    target_ = responsible_pieces[0]
    targets = []
    target_cood = get_coods(target_)
    king_cood = get_coods(king_pos)
    diff_cood = [king_cood[i] - target_cood[i] for i in range(2)]
    dirn_cood = [0, 0]
    if diff_cood[0] != 0:
        dirn_cood[0] = diff_cood[0]/abs(diff_cood[0])
    if diff_cood[1] != 0:
        dirn_cood[1] = diff_cood[1]/abs(diff_cood[1])
    [x_temp, y_temp] = target_cood
    i = target_
    while i != king_pos:
        # Get the path b/w piece and king to try to capture the piece or block the way
        targets.append(i)
        x_temp += dirn_cood[0]
        y_temp += dirn_cood[1]
        i = get_pos(x_temp, y_temp)
    queen_bishop_check = True
    queen_rook_check = True
    # The first iteration checks for capture
    # The rest checks if check can be blocked
    for target in targets:
        # capture only when col is occupied by enemy
        is_capture = get_player(board[int(target)]) == reverse_player(player)
        for i in range(len(board)):
            if board[i].lower() != 'k' and get_player(board[i]) == player:
                if board[i].lower() == 'b' and not check_bishop(i, target):
                    continue
                elif board[i].lower() == 'r' and not check_rook(i, target):
                    continue
                elif board[i].lower() == 'p' and not check_pawn(i, target, player, is_capture):
                    continue
                elif board[i].lower() == 'n' and not check_knight(i, target):
                    continue
                elif board[i].lower() == 'q':
                    if check_bishop(i, target):
                        queen_bishop_check = True
                    else:
                        queen_bishop_check = False
                    if check_rook(i, target):
                        queen_rook_check = True
                    else:
                        queen_rook_check = False
                if target in get_valid_moves(board, board[i], i, player, None, queen_bishop_check, queen_rook_check):
                    # Some piece can capture
                    return False
        if board[target_].lower == 'n' or board[target_].lower() == 'p':
            # Pawn and Knight Checks can't be blocked
            # Since the piece can't be captured, it is checkmate
            return True
    return True


def is_pawn_promote(pos, player):

    if 0 <= pos <= 7 and player == WHITE:
        return True
    if 56 <= pos <= 63 and player == BLACK:
        return True
    return False


def promote_pawn(board, pos, piece):
    board = board[:pos] + piece + board[pos + 1:]
    return board


def interface(board, player, current, target, castle, checked=False, ai=False):
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
    move_is_valid = ai
    if not move_is_valid:
        move_is_valid = target in get_valid_moves(board, board[current], current, player, castle_)
    if move_is_valid:
        temp_board = move(board, current, target)
        return not is_check(temp_board, player, True)
    return False


def disp_board(board):
    for z in range(64):
        if z % 8 == 0:
            print()
        print(board[z], end=' ')
    print()


def post_move_prcoess(board, castle, current, target, player):
    board = move(board, current, target)
    if board[target].lower() == 'k':
        if castle:
            castle[player] = [False, False]
        if abs(current - target) == 2:
            # Castle
            if current - target == 2:
                # Queen Side
                if player == BLACK:
                    rook_pos = 0
                    rook_target = 3
                else:
                    rook_pos = 56
                    rook_target = 59
            else:
                # King side
                if player == BLACK:
                    rook_pos = 7
                    rook_target = 5
                else:
                    rook_pos = 63
                    rook_target = 61
            board = move(board, rook_pos, rook_target)
    if board[target].lower() == 'r' and castle and castle[player] != [False, False]:
        # If rook moves, that side castle is not possible
        if current == 0 and player == BLACK:
            castle[player][0] = False
        if current == 7 and player == BLACK:
            castle[player][1] = False
        if current == 56 and player == WHITE:
            castle[player][0] = False
        if current == 63 and player == WHITE:
            castle[player][1] = False
    return [board, castle]

