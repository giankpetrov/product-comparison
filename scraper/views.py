from django.shortcuts import render
from django.db.models import Min
from .models import Product, Store

def index(request):
    stores = Store.objects.all()
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')

    products = Product.objects.all()
    if query:
        products = products.filter(name__icontains=query)
    if category:
        products = products.filter(category__icontains=category)

    cheapest = Product.objects.values('name', 'weight').annotate(min_price=Min('price')).order_by('name')

    context = {
        'stores': stores,
        'products': products,
        'cheapest': cheapest,
        'query': query,
        'category': category,
    }
    return render(request, 'scraper/index.html', context)

def comparison(request):
    cheapest = Product.objects.values('name', 'weight').annotate(min_price=Min('price')).order_by('name')
    context = {'cheapest': cheapest}
    return render(request, 'scraper/comparison.html', context)