from django.shortcuts import render
from django.http import HttpResponse

from .models import Locations, Products, Instances, Containers

import humanize
import logging

# Create your views here.
def index(request):

    result = []
    instances = Instances.objects.all()
    for i in instances:
        result.append((i, humanize.naturalday(i.date)))

    return render(request, "index.html", {"instances": result })
