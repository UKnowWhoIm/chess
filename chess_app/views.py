from django.http import HttpResponse
from . import engine
from copy import copy
import json
from . import minimax


def serialize_data(success, board=None, castle=None, player=None, is_check=False, pawn_promote=False, game_over=False,
                   winner=None):
    data = '{"success":'
    data += json.dumps(success)
    data += ','
    if success:
        data += '\"board\":\"' + board + '\",'
        data += '\"castle\":' + json.dumps(castle) + ','
        data += '\"player\":\"' + player + '\",'
        data += '\"is_check\":\"' + json.dumps(is_check) + '\",'
        data += '\"pawn_promote\":\"' + json.dumps(pawn_promote) + '\",'
        data += '\"game_over\":\"' + json.dumps(game_over) + '\",'
        data += '\"winner\":\"' + json.dumps(winner) + '\",'
    data += '}'
    return data


def move_validate(request):
    board = request.POST['board']
    current = int(request.POST['current'])
    target = int(request.POST['target'])
    castle = json.load(request.POST['castle'])
    player = request.POST['player']
    is_check = json.load(request.POST['check'])
    if engine.interface(board, player, current, target, castle, is_check):
        [board, castle] = engine.post_move_prcoess(board, copy(castle), current, target, player)
        if board[target].lower() == 'p' and engine.is_pawn_promote(target, player):
            return HttpResponse(serialize_data(True, board, castle, engine.reverse_player(player), False, True))
        check_pieces = engine.is_check(board, engine.reverse_player(player))
        game_over = False
        winner = None
        if check_pieces:
            is_check = True
            if engine.is_checkmate(board, engine.reverse_player(player), check_pieces):
                game_over = True
                winner = player
        return HttpResponse(serialize_data(True, board, castle, engine.reverse_player(player), is_check, False,
                                           game_over, winner))
    return HttpResponse(serialize_data(False))


def ai_handler(request):
    ai = int(request.POST['ai'])
    board = request.POST['board']
    castle = json.load(request.POST['castle'])
    player = request.POST['player']
    if ai == 1:
        # mini_max
        depth = int(request.POST['depth'])
        move = minimax.make_move(board, player, castle, depth)

    [board, castle] = engine.post_move_prcoess(board, copy(castle), move[0], move[1], player)
    if board[move[1]].lower() == 'p' and engine.is_pawn_promote(move[1], player):
        if player == engine.WHITE:
            piece = 'Q'
        else:
            piece = 'q'
        engine.promote_pawn(board, move[1], piece)
    check_pieces = engine.is_check(board, engine.reverse_player(player))
    game_over = False
    is_check = False
    winner = None
    if check_pieces:
        is_check = True
        if engine.is_checkmate(board, engine.reverse_player(player), check_pieces):
            game_over = True
            winner = player
    return HttpResponse(serialize_data(True, board, castle, engine.reverse_player(player), is_check, False,
                                       game_over, winner))
