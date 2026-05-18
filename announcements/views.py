from django.shortcuts import render

# Create your views here.

def annonces(request):
    return render(request, 'announcements/annonces.html')
