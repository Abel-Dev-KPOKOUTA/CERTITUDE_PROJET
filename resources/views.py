from django.shortcuts import render

def astuces(request):
    return render(request, 'resources/astuces.html')

def cours(request):
    return render(request, 'resources/cours.html')