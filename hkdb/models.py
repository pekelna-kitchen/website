
from django.db import models
import django.utils.timezone

class Сontainer(models.Model):
    symbol = models.CharField(max_length=1, verbose_name='Container symbol')
    description = models.TextField('Container description')

class Location(models.Model):
    name = models.TextField('Location')

class Product(models.Model):
    name = models.TextField('ProductName')

class Instance(models.Model):
    amount = models.TextField('Amount')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    date = models.DateTimeField("Date modified", auto_now=True)
    editor = models.TextField("Last editor")

class Limit(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    amount = models.IntegerField(editable=True, verbose_name="Number of containers limit")
    container = models.ForeignKey(Сontainer, on_delete=models.CASCADE)
