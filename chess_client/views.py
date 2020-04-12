from django.shortcuts import render


# Create your views here.
def index_view(request):
    return render(request, "chess_client/index.html")


def custom_match(request):
    return render(request, "chess_client/custom_match.html")


def ai_vs_ai(request):
    return render(request, "chess_client/custom_match.html")


def game(request):
    return render(request, "chess_client/custom_match.html")

