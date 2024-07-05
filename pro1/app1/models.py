from django.db import models

class Product(models.Model):
    title = models.CharField(max_length=100)


class DefaultPermission(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    permissions = models.JSONField(default=dict)
