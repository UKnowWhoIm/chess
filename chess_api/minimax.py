if __name__ == "__main__":
    import engine

else:
    from . import engine
from time import time
from copy import deepcopy as copy


class Game:
    def __init__(self, board, castle=None, neighbourhood=None):
        self.board = board
        self.castle = castle
        self.neighbourhood = neighbourhood
    
    def make_move(self, current, target, player, castle):
        self.neighbourhood = {
                            engine.WHITE: get_king_neighbourhood(self.board, engine.WHITE),
                            engine.BLACK: get_king_neighbourhood(self.board, engine.BLACK)
                            }
        [self.board, self.castle] = engine.post_move_prcoess(self.board, copy(castle), current, target, player)
        if self.board[target].lower() == 'p':
            promote_pawn = None
            if 0 <= target <= 7 and player == engine.WHITE:
                promote_pawn = 'Q'
            elif 56 <= target <= 63 and player == engine.BLACK:
                promote_pawn = 'q'
            if promote_pawn:
                self.board = self.board[:target] + promote_pawn + self.board[target + 1:]


def heuristic(game_state, maximiser, is_max):
    # TODO Heuristic
    if maximiser == engine.WHITE:
        multiplier = -1
    else:
        multiplier = 1
    piece_vals = {
        'f': 0,
        'p': 10,
        'n': 40,
        'b': 40,
        'r': 100,
        'q': 500,
        'k': 10**7,
        'P': -10,
        'N': -40,
        'B': -40,
        'R': -100,
        'Q': -500,
        'K': -10 ** 7
    }
    score = 0
    for i in range(64):
        score += multiplier * piece_vals[game_state.board[i]]
    return score


def mini_max(game_state, player, maximiser, is_max, depth, alpha, beta=10**5):
    if depth == 0:
        return heuristic(game_state, maximiser, is_max)
    if is_max:
        for current, target in get_all_legal_moves(game_state.board, player, game_state.castle,
                                                   game_state.neighbourhood[player]):
            new_game_state = Game(game_state.board)
            new_game_state.make_move(current, target, player, game_state.castle)
            alpha = max(alpha, mini_max(new_game_state, engine.reverse_player(player), maximiser,False, depth - 1,
                                        alpha, beta))
            if beta <= alpha:
                break
        return alpha
    else:
        for current, target in get_all_legal_moves(game_state.board, player, game_state.castle,
                                                   game_state.neighbourhood[player]):
            new_game_state = Game(game_state.board)
            new_game_state.make_move(current, target, player, game_state.castle)
            beta = min(beta, mini_max(new_game_state, engine.reverse_player(player), maximiser, True, depth - 1, alpha, beta))
            if beta <= alpha:
                break
        return beta


def get_all_legal_moves(board, player, castle, king_neighbourhood):
    moves = []
    if king_neighbourhood is None:
        king_neighbourhood = get_king_neighbourhood(board, player)
    for i in range(64):
        if engine.get_player(board[i]) == player:
            for move in engine.get_valid_moves(board, board[i], i, player, castle):
                if king_neighbourhood and move in king_neighbourhood:
                    if engine.interface(board, player, i, move, castle):
                        moves.append([i, move])
                else:
                    moves.append([i, move])
    return moves


def get_king_neighbourhood(board, player, king_pos=None):
    # returns the position of pieces which can expose the king
    # check for check is done only if piece is in neighbourhood
    if king_pos is None:
        king_pos = engine.find_king(board, player)
        if king_pos is None:
            return None
    neighbourhood = [king_pos]
    updations = [-8, 8]
    if engine.can_go_left(king_pos):
        updations += [-9, 7, -1]
    if engine.can_go_right(king_pos):
        updations += [9, -7, 1]

    for u in updations:
        i = king_pos
        i += u
        while 0 <= i <= 63:
            if engine.get_player(board[i]) != '':
                neighbourhood.append(i)
                break
            i += u
    return neighbourhood


def make_move(board, player, castle, depth=3):
    current_game = Game(board, castle)
    current_game.neighbourhood = {
                            engine.WHITE: get_king_neighbourhood(board, engine.WHITE),
                            engine.BLACK: get_king_neighbourhood(board, engine.BLACK)
                            }

    alpha = -10 ** 5
    m_current, m_target = None, None
    if depth == 1:
        # For depth = 1, to avoid illegal movement when checked, force generate assured legal moves
        current_game.neighbourhood[player] = [i for i in range(64) if board[i]]
    for current, target in get_all_legal_moves(board, player, castle, current_game.neighbourhood[player]):
        new_game_state = Game(current_game.board)
        new_game_state.make_move(current, target, player, current_game.castle)
        val = mini_max(new_game_state, engine.reverse_player(player), player, False, depth - 1, alpha)
        if val > alpha:
            alpha = val
            m_current = current
            m_target = target

    return [m_current, m_target]


if __name__ == "__main__":
    bo_ = "rnbqkbnrppppppppffffffffffffffffffffffffffffffffPPPPPPPPRNBQKBNR"
    engine.disp_board(bo_)
    bo_ = engine.move(bo_, 52, 36)
    bo_ = engine.move(bo_, 12, 28)
    bo_ = engine.move(bo_, 59, 31)
    bo_ = engine.move(bo_, 61, 34)
    bo_ = engine.move(bo_, 8, 24)
    a = time()
    move = make_move(bo_, engine.BLACK, None)
    bo_ = engine.move(bo_, move[0], move[1])
    move2 = make_move(bo_, engine.WHITE, None)
    bo_ = engine.move(bo_, move2[0], move2[1])
    move3 = make_move(bo_, engine.BLACK, None)
    bo_ = engine.move(bo_, move3[0], move3[1])
    move4 = make_move(bo_, engine.WHITE, None)
    bo_ = engine.move(bo_, move4[0], move4[1])
    move4 = make_move(bo_, engine.WHITE, None)
    bo_ = engine.move(bo_, move4[0], move4[1])
    print(time() - a)
    engine.disp_board(bo_)
