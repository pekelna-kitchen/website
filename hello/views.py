from django.shortcuts import render
from django.http import HttpResponse

from .models import Location, Product

import logging

# Create your views here.
def index(request):

    productList = []
    locations = Location.objects.all()

    for location in locations:
        productList.append( (location, Product.objects.filter(location=location.id)) )

    return render(request, "db.html", {"productList": productList})
