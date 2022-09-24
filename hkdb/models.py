from django.db import models

class Location(models.Model):
    name = models.TextField('Location')

class Product(models.Model):
    name = models.TextField('ProductName')

class Instance(models.Model):
    amount = models.TextField('Amount')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    lastModifyDate = models.DateTimeField(auto_now=True)
    lastModifyAuthor = models.TextField("Last editor")
