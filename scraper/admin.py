from django.contrib import admin
from .models import Store, Product

@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'url')
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'weight', 'price', 'store', 'category', 'scraped_date')
    list_filter = ('store', 'category', 'scraped_date')
    search_fields = ('name', 'category')