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


def is_endgame(white_score, black_score, maximiser):
    if maximiser == engine.WHITE:
        diff = black_score - white_score
    else:
        diff = white_score - black_score
    if diff > 1400:
        return True
    if white_score < (2000 + 10**7) and black_score < (2000 + 10**7):
        return True


def advanced_heuristic(game_state, maximiser, is_max):
    piece_vals = {
        'f': 0,
        'p': 50,
        'n': 200,
        'b': 300,
        'r': 500,
        'q': 1000,
        'k': 10 ** 7,
        'P': -50,
        'N': -200,
        'B': -300,
        'R': -500,
        'Q': -1000,
        'K': -10 ** 7
    }
    if maximiser == engine.WHITE:
        multiplier = -1
    else:
        multiplier = 1
    score = 0
    pawn_structure_factor = 0.5 * multiplier
    pawn_promotion_factor = 0.5 * multiplier
    position_factor = 1 * multiplier
    white_material_score = 0
    black_material_score = 0
    king_pos = {engine.WHITE: None, engine.BLACK: None}
    pawn_positions = []
    knight_piece_score = [0, 0, 1, 3, 5, 3, 1, 0, 0]
    offensive_piece_posns = []
    for i in range(64):
        score += multiplier * piece_vals[game_state.board[i]]
        white_material_score += abs(piece_vals[game_state.board[i]])
        black_material_score += abs(piece_vals[game_state.board[i]])
        cood = engine.get_coods(i)
        if game_state.board[i].lower() == 'p':
            pawn_positions.append(i)
        elif game_state.board[i].lower() == 'k':
            king_pos[engine.get_player(game_state.board[i])] = i
        else:
            offensive_piece_posns.append(i)

    if is_endgame(white_material_score, black_material_score, maximiser):
        for pos in pawn_positions:
            cood = engine.get_coods(pos)
            if engine.get_player(game_state.board[pos]) == engine.WHITE:
                score += pawn_promotion_factor * (3 - cood[0]) * -1
            if engine.get_player(game_state.board[pos]) == engine.BLACK:
                score += pawn_promotion_factor * (cood[0] - 4)
    else:
        for pos in pawn_positions:
            if engine.get_player(game_state.board[pos]) == engine.WHITE:
                if engine.can_go_left(pos) and game_state.board[pos + 7].lower() == 'p':
                    score += 5 * pawn_structure_factor * -1
                if engine.can_go_right(pos) and game_state.board[pos + 9].lower() == 'p':
                    score += 5 * pawn_structure_factor * -1
            else:
                if engine.can_go_left(pos) and game_state.board[pos - 9].lower() == 'p':
                    score += 5 * pawn_structure_factor
                if engine.can_go_right(pos) and game_state.board[pos - 7].lower() == 'p':
                    score += 5 * pawn_structure_factor
    diff = white_material_score - black_material_score
    if maximiser == engine.WHITE:
        diff = -diff
    # Adjust position_factor according to game state
    if diff > 1500:
        position_factor *= 10
    elif diff > 1000:
        position_factor *= 4
    elif diff < 0:
        position_factor /= 2
    for pos in offensive_piece_posns:
        cood = engine.get_coods(pos)
        if game_state.board[pos].lower() == 'n':
            if engine.get_player(game_state.board[pos]) == engine.WHITE:
                score += position_factor * knight_piece_score[cood[1]] * -1
            else:
                score += position_factor * knight_piece_score[cood[1]]

            if engine.get_player(game_state.board[pos]) == engine.WHITE:
                score += position_factor * knight_piece_score[cood[0]]
            else:
                score += position_factor * knight_piece_score[cood[0]] * -1
        else:
            if game_state.board[pos] == engine.WHITE and cood[0] <= 4:
                score += (cood[0] - 3) * position_factor
            if game_state.board[pos] == engine.BLACK and cood[0] >= 3:
                score += (cood[0] - 3) * position_factor * -1

    return score


def is_disadvantaged(board, player):
    piece_vals = {
        'f': 0,
        'p': 10,
        'n': 40,
        'b': 40,
        'r': 100,
        'q': 500,
        'k': 10 ** 7,
        'P': -10,
        'N': -40,
        'B': -40,
        'R': -100,
        'Q': -500,
        'K': -10 ** 7
    }
    white_score = 0
    black_score = 0
    for i in range(64):
        if engine.get_player(board[i]) == engine.WHITE:
            white_score += abs(white_score)
        else:
            black_score += abs(black_score)
    diff = black_score - white_score
    if player == engine.BLACK:
        diff = -diff

    if diff > 1500:
        return True
    return False


def heuristic(game_state, maximiser, is_max):
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
        'k': 10 ** 7,
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


def mini_max(game_state, player, maximiser, is_max, depth, alpha, beta=10 ** 5):
    if depth == 0:
        return advanced_heuristic(game_state, maximiser, is_max)
    if is_max:
        can_move = False
        for current, target in get_all_legal_moves(game_state.board, player, game_state.castle,
                                                   game_state.neighbourhood[player]):
            can_move = True
            new_game_state = Game(game_state.board)
            new_game_state.make_move(current, target, player, game_state.castle)
            alpha = max(alpha, mini_max(new_game_state, engine.reverse_player(player), maximiser, False, depth - 1,
                                        alpha, beta))
            if beta <= alpha:
                # print('alpha prune')
                break
        if not can_move:
            # Either check_mate or stalemate
            if engine.is_check(game_state.board, player, True):
                # CheckMate, fucking play this move
                pass
            else:
                # Stalemate, if disadvantaged play this move
                # Else Dont you fucking dare
                if not is_disadvantaged(game_state.board, player):
                    return -10**5
        return alpha
    else:
        can_move = False
        for current, target in get_all_legal_moves(game_state.board, player, game_state.castle,
                                                   game_state.neighbourhood[player]):
            can_move = True
            new_game_state = Game(game_state.board)
            new_game_state.make_move(current, target, player, game_state.castle)
            beta = min(beta,
                       mini_max(new_game_state, engine.reverse_player(player), maximiser, True, depth - 1, alpha, beta))
            if beta <= alpha:
                # print('beta prune')
                break
        if not can_move:
            # Either check_mate or stalemate
            if engine.is_check(game_state.board, player, True):
                # CheckMate, fucking play this move
                pass
            else:
                # Stalemate, if disadvantaged play this move
                # Else Dont you fucking dare
                if not is_disadvantaged(game_state.board, player):
                    return 10**5
        return beta


def get_all_legal_moves(board, player, castle, king_neighbourhood):
    moves = []
    if king_neighbourhood is None:
        king_neighbourhood = get_king_neighbourhood(board, player)
    for i in range(64):
        if engine.get_player(board[i]) == player:
            for move in engine.get_valid_moves(board, board[i], i, player, castle):
                if king_neighbourhood and move in king_neighbourhood or king_neighbourhood is False:
                    if engine.interface(board, player, i, move, castle, False, True):
                        # print('checked for check')
                        moves.append([i, move])
                else:
                    # print('pruned check')
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
    a = time()
    current_game = Game(board, castle)
    current_game.neighbourhood = {
        engine.WHITE: get_king_neighbourhood(board, engine.WHITE),
        engine.BLACK: get_king_neighbourhood(board, engine.BLACK)
    }

    alpha = -10 ** 5
    m_current, m_target = None, None
    if depth == 1:
        # For depth = 1, to avoid illegal movement when checked, force generate assured legal moves
        current_game.neighbourhood[player] = False
    possible_games = []
    for current, target in get_all_legal_moves(board, player, castle, current_game.neighbourhood[player]):
        new_game_state = Game(current_game.board)
        new_game_state.make_move(current, target, player, current_game.castle)
        possible_games.append([new_game_state, [current, target]])
    possible_games = sorted(possible_games, key=lambda x: advanced_heuristic(x[0], player, True), reverse=True)
    for game, move in possible_games:
        val = mini_max(game, engine.reverse_player(player), player, False, depth - 1, alpha)
        if val > alpha:
            alpha = val
            m_current = move[0]
            m_target = move[1]
    print(time()- a, "Original")
    return [m_current, m_target]


if __name__ == "__main__":
    bo_ = "rnbqkbnrpfppppppfpffffffffffffffffffffffffffPfffPPPPfPPPRNBQKBNR"
    engine.disp_board(bo_)
    """
    bo_ = engine.move(bo_, 52, 36)
    bo_ = engine.move(bo_, 12, 28)
    bo_ = engine.move(bo_, 59, 31)
    bo_ = engine.move(bo_, 61, 34)
    bo_ = engine.move(bo_, 8, 24)
    """
    a = time()
    move = make_move(bo_, engine.BLACK, None, 4)
    bo_ = engine.move(bo_, move[0], move[1])
    """
    move2 = make_move(bo_, engine.WHITE, None)
    bo_ = engine.move(bo_, move2[0], move2[1])
    move3 = make_move(bo_, engine.BLACK, None)
    bo_ = engine.move(bo_, move3[0], move3[1])
    move4 = make_move(bo_, engine.WHITE, None)
    bo_ = engine.move(bo_, move4[0], move4[1])
    move4 = make_move(bo_, engine.WHITE, None)
    bo_ = engine.move(bo_, move4[0], move4[1])
    """
    print(time() - a)
    engine.disp_board(bo_)
