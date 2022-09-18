from django.shortcuts import render
from django.http import HttpResponse

from .models import Location

# Create your views here.
def index(request):

    locations = Location.objects.all()

    return render(request, "db.html", {"locations": locations})
