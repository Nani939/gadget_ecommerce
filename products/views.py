from django.shortcuts import render, get_object_or_404
from shop.models import Product

def product_list(request):
    products = Product.objects.filter(available=True).order_by('name')
    return render(request, 'products/product_list.html', {'products': products})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk, available=True)
    return render(request, 'products/product_detail.html', {'product': product})
