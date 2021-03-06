from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
import requests
import os
from time import time

BLACK = 'black'
WHITE = 'white'
server = os.environ.get("DJANGO_API_SERVER", 'http://127.0.0.1:8000')
FAIL = '300'
SUCCESS = '200'


def dump_data(request, response, move=None):
    if move:
        request.session['history'].append([request.session['board'], move])
        key_val = request.session['player'] + '_captured'
        if request.session['history'][-1][0][move[1]] != 'f':
            request.session[key_val].append(request.session['history'][-1][0][move[1]])
    keys = ['board', 'player', 'castle', 'is_check', 'pawn_promote', 'game_over', 'winner']
    for key in keys:
        request.session[key] = response[key]


def pack_data(request, additional_data):
    keys = ['board', 'player', 'castle', 'is_check', 'pawn_promote', 'game_over', 'winner']
    data = {}
    for key in keys:
        data[key] = request.session[key]
    data.update(additional_data)
    return data


def index_view(request):
    return render(request, "chess_client/index.html")


def custom_match(request):
    return render(request, "chess_client/custom_match.html")


def ai_vs_ai(request):
    return render(request, "chess_client/ai_vs_ai.html")


def game(request):
    if request.session.get('board', None) is None:
        request.session['history'] = []
        request.session['white_captured'] = []
        request.session['black_captured'] = []
        initial_data = requests.get(server + '/api/initialize').json()
        dump_data(request, initial_data)
    data = pack_data(request, {})
    request.session['legal_moves'] = requests.post(server + '/api/get_all_moves', json=data).json()
    return render(request, "chess_client/game.html")


def player_validate(request):
    current = int(request.POST['current'])
    target = int(request.POST['target'])
    if not (0 <= current <= 63 or 0 <= target <= 63):
        return HttpResponse(FAIL)
    data = pack_data(request, {'current': current, 'target': target})
    response = requests.post(server + '/api/validate_move', json=data).json()
    if response['success']:
        dump_data(request, response, [current, target])
        return HttpResponse(SUCCESS)
    return HttpResponse(FAIL)


def call_ai(request):
    if request.session.get('ai_disabled', False):
        # AI is disabled
        return HttpResponse(FAIL)
    if not request.session.get('player_disabled', False) and request.session['player'] != BLACK:
        # Not AI's turn
        return HttpResponse(FAIL)
    ai_key_val = request.session['player'] + '_ai'
    depth_key_val = request.session['player'] + '_depth'
    data = pack_data(request, {'ai': request.session[ai_key_val], 'depth': request.session[depth_key_val]})
    # a = time()
    response = requests.post(server + '/api/ai_move', json=data).json()
    # print(time() - a)
    if response['success']:
        dump_data(request, response, response['move'])
        return HttpResponse(SUCCESS)
    return HttpResponse(FAIL)


def pawn_promote(request):
    if request.session['pawn_promote'] is None:
        return HttpResponse(FAIL)
    data = pack_data(request, {'current': request.session['pawn_promote'], 'promoted_piece': request.POST['piece']})
    response = requests.post(server + '/api/pawn_promotion', json=data).json()
    if response['success']:
        dump_data(request, response)
        return HttpResponse(SUCCESS)
    return HttpResponse(FAIL)


def new_game(request):
    type_ = int(request.GET.get('type', 1))
    request.session.flush()
    if type_ == 2:
        # Multi player
        request.session['ai_disabled'] = True
    elif type_ == 3:
        # AI vs AI
        request.session['player_disabled'] = True
        white_ai = float(request.GET.get('white_ai', 1))
        black_ai = float(request.GET.get('black_ai', 1))
        white_depth = int(request.GET.get('white_depth', 3))
        black_depth = int(request.GET.get('black_depth', 3))

        if white_ai == 1.5:
            white_ai = 1
            white_depth = 1
        if black_ai == 1.5:
            black_ai = 1
            black_depth = 1
        if not (1 <= white_depth <= 6):
            white_depth = 3
        if not (1 <= black_depth <= 6):
            black_depth = 3

        request.session['white_ai'] = int(white_ai)
        request.session['black_ai'] = int(black_ai)
        request.session['black_depth'] = black_depth
        request.session['white_depth'] = white_depth
    elif type_ == 1:
        # Single Player
        ai = float(request.GET.get('ai', 1))
        depth = int(request.GET.get('depth', 3))

        if ai == 1.5:
            depth = 1
        if not (1 <= depth <= 5):
            depth = 3
        if ai not in [1, 2]:
            ai = 1

        request.session['black_ai'] = int(ai)
        request.session['black_depth'] = depth
    return HttpResponseRedirect('/game')
