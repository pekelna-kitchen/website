
from django.db import models
import django.utils.timezone

class Containers(models.Model):
    symbol = models.CharField(max_length=1, verbose_name='Container symbol')
    description = models.TextField('Container description')

class Locations(models.Model):
    name = models.TextField('Location')

class Products(models.Model):
    name = models.TextField('ProductName')

class Instances(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    location = models.ForeignKey(Locations, on_delete=models.CASCADE)
    container = models.ForeignKey(Containers, on_delete=models.CASCADE)
    amount = models.TextField('Amount')
    date = models.DateTimeField("Date modified", auto_now=True)
    editor = models.TextField("Last editor")

class Limits(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    amount = models.IntegerField(editable=True, verbose_name="Number of containers limit")
    container = models.ForeignKey(Containers, on_delete=models.CASCADE)
