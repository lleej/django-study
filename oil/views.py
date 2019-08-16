from django.shortcuts import render

# Create your views here.

from . import models

def id_place(request, id):
    a_list = models.Place.objects.filter(pk=id)
    context = {'id': id, 'place_list': a_list}
    return render(request, 'oil/id_place.html', context)

