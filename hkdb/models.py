
from django.db import models
import django.utils.timezone


class Location(models.Model):
    name = models.TextField('Location')

class Product(models.Model):
    name = models.TextField('ProductName')
    limit = models.TextField(editable=True, verbose_name=b'Limit to notify', null=True)

class Instance(models.Model):
    amount = models.TextField('Amount')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    date = models.DateTimeField("Date modified", auto_now=True)
    editor = models.TextField("Last editor")
