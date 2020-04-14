from django.http import HttpResponse
from . import engine
from copy import deepcopy as copy
import json
from . import minimax
import random


def serialize_data(success, board=None, castle=None, player=None, is_check=False, pawn_promote=None, game_over=False,
                   winner=None, additional_data=None):
    data = {'success': success}
    if success:
        data['board'] = board
        data['castle'] = castle
        data['player'] = player
        data['is_check'] = is_check
        data['pawn_promote'] = pawn_promote
        data['game_over'] = game_over
        data['winner'] = winner
    if additional_data:
        data.update(additional_data)
    return json.dumps(data)


def return_data(board, player, castle, additional_data=None):
    is_check = False
    check_pieces = engine.is_check(board, engine.reverse_player(player))
    game_over = False
    winner = None
    if check_pieces:
        is_check = True
        if engine.is_checkmate(board, engine.reverse_player(player), check_pieces):
            game_over = True
            winner = player
    else:
        if engine.is_stalemate(board, player, castle):
            game_over = True
            winner = None
    return HttpResponse(serialize_data(True, board, castle, engine.reverse_player(player), is_check, None,
                                       game_over, winner, additional_data))


def move_validate(request):
    # Data is served in json
    data = json.loads(request.body.decode('utf-8'))
    board = data['board']
    current = int(data['current'])
    target = int(data['target'])
    castle = data['castle']
    player = data['player']
    is_check = data['is_check']
    if engine.interface(board, player, current, target, copy(castle), is_check):
        [board, castle] = engine.post_move_prcoess(board, copy(castle), current, target, player)
        if board[target].lower() == 'p' and engine.is_pawn_promote(target, player):
            return HttpResponse(serialize_data(True, board, castle, player, False, target))
        return return_data(board, player, castle)
    return HttpResponse(serialize_data(False))


def ai_handler(request):
    # Data is served in json
    data = json.loads(request.body.decode('utf-8'))
    ai = int(data['ai'])
    board = data['board']
    castle = data['castle']
    player = data['player']

    if ai not in [1, 2]:
        # Tampering
        return HttpResponse(serialize_data(False))
    if ai == 1:
        # mini_max and greedy(mini_max with depth 1)
        depth = int(data['depth'])
        move = minimax.make_move(board, player, copy(castle), depth)
    elif ai == 2:
        # Random Move
        move = random.choice(minimax.get_all_legal_moves(board, player, copy(castle), False))
    if move == [None, None]:
        # No available moves
        return HttpResponse(serialize_data(False))
    [board, castle] = engine.post_move_prcoess(board, copy(castle), move[0], move[1], player)
    if board[move[1]].lower() == 'p' and engine.is_pawn_promote(move[1], player):
        # Promote Pawn To Queen
        if player == engine.BLACK:
            piece = "q"
        else:
            piece = "Q"
        board = engine.promote_pawn(board, move[1], piece)
    if board[move[1]].lower() == 'p' and engine.is_pawn_promote(move[1], player):
        if player == engine.WHITE:
            piece = 'Q'
        else:
            piece = 'q'
        engine.promote_pawn(board, move[1], piece)
    return return_data(board, player, castle, {'move': move})


def promote_pawn(request):
    data = json.loads(request.body.decode('utf-8'))
    pawn_current = data['current']
    promoted_piece = data['promoted_piece']
    board = data['board']
    castle = data['castle']
    player = data['player']
    if promoted_piece.lower() not in ['q', 'b', 'n', 'r']:
        return HttpResponse(serialize_data(False))
    if engine.get_player(board[pawn_current]) == engine.get_player(promoted_piece) and \
            engine.get_player(board[pawn_current]) == player:
        if engine.is_pawn_promote(pawn_current, player):
            board = engine.promote_pawn(board, pawn_current, promoted_piece)
            return return_data(board, player, castle)
    return HttpResponse(serialize_data(False))


def initialize(request):
    board = "rnbqkbnrppppppppffffffffffffffffffffffffffffffffPPPPPPPPRNBQKBNR"
    castle = {engine.WHITE: [True, True], engine.BLACK: [True, True]}
    return HttpResponse(serialize_data(True, board, castle, engine.WHITE))


def get_all_moves(request):
    data = json.loads(request.body.decode('utf-8'))
    board = data['board']
    castle = data['castle']
    player = data['player']
    move_dic = {}
    moves = minimax.get_all_legal_moves(board, player, castle, False)
    for move in moves:
        try:
            move_dic[move[0]].append(move[1])
        except KeyError:
            move_dic[move[0]] = [move[1]]
    return HttpResponse(json.dumps(move_dic))

