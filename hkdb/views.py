from django.shortcuts import render
from django.http import HttpResponse

from .models import Location, Product, Instance

import logging

# Create your views here.
def index(request):

    instanceList = []
    locations = Location.objects.all()

    for location in locations:
        instanceList.append( (location, Instance.objects.filter(location=location.id)) )

    return render(request, "db.html", {"instanceList": instanceList})
