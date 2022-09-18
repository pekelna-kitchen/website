from django.db import models

class Location(models.Model):
    name = models.TextField('Location')

class Product(models.Model):
    name = models.TextField('ProductName')
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    