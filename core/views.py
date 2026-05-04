from django.shortcuts import render
from django.http import HttpResponse

def accueil(request):
    return render(request, 'core/index.html')

def formations(request):
    return render(request,'core/formations.html')

def galerie(request):
    return render(request,'core/galerie.html')

def contact(request):
    return render(request,'core/contact.html')

def apropos(request):
    return render(request,'core/index.html')


def contact(request):
    return render(request,'core/index.html')