from django.shortcuts import render

def product_list(request):
    # You can fetch products from the database here if needed
    return render(request, 'shop/product_list.html')

from django.shortcuts import render, get_object_or_404
from .models import Product  # make sure you have a Product model

def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    return render(request, 'shop/product_detail.html', {'product': product})

from django.shortcuts import render

def cart(request):
    return render(request, 'shop/cart.html')

from django.shortcuts import render

def checkout(request):
    return render(request, 'shop/checkout.html')

from django.shortcuts import render, get_object_or_404, redirect
from .models import Product

def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + int(request.POST.get('quantity', 1))
    request.session['cart'] = cart
    return redirect('cart')

def cart_view(request):
    cart = request.session.get('cart', {})
    products = Product.objects.filter(id__in=cart.keys())
    cart_items = []
    total = 0
    for product in products:
        quantity = cart[str(product.id)]
        total += product.price * quantity
        cart_items.append({'product': product, 'quantity': quantity, 'subtotal': product.price * quantity})
    return render(request, 'shop/cart.html', {'cart_items': cart_items, 'total': total})

from django.shortcuts import render
from .models import Product

def product_list(request):
    products = Product.objects.all()
    return render(request, 'shop/product_list.html', {'products': products})

from django.shortcuts import render, get_object_or_404
from .models import Product

def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    return render(request, 'shop/product_detail.html', {'product': product})
from django.shortcuts import render

def checkout_view(request):
    # You can fetch cart data here if needed
    return render(request, 'shop/checkout.html')
