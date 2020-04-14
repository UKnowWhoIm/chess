from django import template
import json

register = template.Library()


def get_color(pos):
    x = pos // 8
    y = pos % 8
    if (x + y) % 2 == 0:
        return "white"
    return "black"


@register.filter
def print_board(board):
    print(board)
    data = '<tr>'
    for i in range(64):
        if i % 8 == 0 and i != 0:
            data += '</tr>'
            data += '<tr>'
        data += "<td id=\'"+str(i)+"\' class=\'cell "+get_color(i)+"\'>"+board[i]+'</td>'
    data += '</tr>'
    return data


@register.filter
def last_moves(board):
    move = board[-1][1]
    return "["+str(move[0])+", "+str(move[1])+"]"


@register.filter
def to_json(table):
    return json.dumps(table)