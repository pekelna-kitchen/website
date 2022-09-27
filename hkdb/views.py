from django.shortcuts import render
from django.http import HttpResponse

from .models import Locations, Products, Instances, Containers

import logging

# Create your views here.
def index(request):

    return render(request, "index.html", {"instances": Instances.objects.all()})
