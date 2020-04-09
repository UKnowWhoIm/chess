if __name__ == "__main__":
    import engine
    from time import time
else:
    from . import engine


class Game:
    def __init__(self, board, castle=None, neighbourhood=None):
        self.board = board
        self.castle = castle
        self.neighbourhood = neighbourhood
    
    def make_move(self, current, target, player, castle):
        self.board = engine.move(self.board, current, target)
        self.neighbourhood = {
                            engine.WHITE: get_king_neighbourhood(self.board, engine.WHITE),
                            engine.BLACK: get_king_neighbourhood(self.board, engine.BLACK)
                            }
        self.castle = castle
        if self.board[target].lower() == 'k':
            if self.castle:
                self.castle[player] = [False, False]
            if abs(current - target) == 2:
                # Castle
                if current - target == 2:
                    # Queen Side
                    if player == engine.BLACK:
                        rook_pos = 0
                        rook_target = 3
                    else:
                        rook_pos = 56
                        rook_target = 59
                else:
                    # King side
                    if player == engine.BLACK:
                        rook_pos = 7
                        rook_target = 5
                    else:
                        rook_pos = 63
                        rook_target = 61
                self.board = engine.move(self.board, rook_pos, rook_target)
        if self.board[target].lower() == 'r' and self.castle and self.castle[player] != [False, False]:
            # If rook moves, that side castle is not possible
            if current == 0 and player == engine.BLACK:
                self.castle[player][0] = False
            if current == 7 and player == engine.BLACK:
                self.castle[player][1] = False
            if current == 56 and player == engine.WHITE:
                self.castle[player][0] = False
            if current == 63 and player == engine.WHITE:
                self.castle[player][1] = False


def minimax(game_state, player, is_max, depth, alpha, beta=10**5):
    if depth == 0:
        # TODO Heuristic
        return 0
    if is_max:
        for current, target in get_all_legal_moves(game_state.board, player, game_state.castle,
                                                   game_state.neighbourhood[player]):
            new_game_state = Game(game_state.board)
            new_game_state.make_move(current, target, player, game_state.castle)
            alpha = max(alpha, minimax(new_game_state, engine.reverse_player(player), False, depth - 1,alpha, beta))
            if beta <= alpha:
                break
        return alpha
    else:
        for current, target in get_all_legal_moves(game_state.board, player, game_state.castle,
                                                   game_state.neighbourhood[player]):
            new_game_state = Game(game_state.board)
            new_game_state.make_move(current, target, player, game_state.castle)
            beta = min(beta, minimax(new_game_state, engine.reverse_player(player), True, depth - 1, alpha, beta))
            if beta <= alpha:
                break
        return beta


def get_all_legal_moves(board, player, castle, king_neighbourhood):
    moves = []
    for i in range(64):
        if engine.get_player(board[i]) == player:
            for move in engine.get_valid_moves(board, board[i], i, player, castle):
                if move in king_neighbourhood:
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
    neighbourhood = [king_pos]
    updations = [-8, 8]
    if engine.can_go_left(king_pos):
        updations += [-9, 7, -1]
    if engine.can_go_right(king_pos):
        updations += [9, -7, 1]

    for u in updations:
        i = king_pos
        i += u
        while 0 <= i <= 64:
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
    for current, target in get_all_legal_moves(board, player, castle, current_game.neighbourhood[player]):
        new_game_state = Game(current_game.board)
        new_game_state.make_move(current, target, player, current_game.castle)
        val = minimax(new_game_state, engine.reverse_player(player), False, depth - 1, alpha)
        if val > alpha:
            alpha = val
            m_current = current
            m_target = target

    return [m_current, m_target]


if __name__ == "__main__":
    bo_ = "rnbqkbnrppppppppffffffffffffffffffffffffffffffffPPPPPPPPRNBQKBNR"
    engine.disp_board(bo_)
    move = make_move(bo_, engine.BLACK, None)
    bo_ = engine.move(bo_, move[0], move[1])
    engine.disp_board(bo_)
