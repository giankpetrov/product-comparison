from django.db import models

class Store(models.Model):
    name = models.CharField(max_length=100)
    url = models.URLField()

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255)
    weight = models.CharField(max_length=50, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    category = models.CharField(max_length=100, blank=True)
    scraped_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.weight}) - {self.store.name}"