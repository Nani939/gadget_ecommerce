from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Category, Product
from django.contrib.auth.decorators import login_required

# --- Utility to get or create cart in session ---
def _get_cart(session):
    return session.setdefault('cart', {})  # {product_id: qty}


# --- Product List and Detail Views ---

def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    return render(request, 'shop/product/list.html', {
        'category': category,
        'categories': categories,
        'products': products
    })


def product_detail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug, available=True)
    return render(request, 'shop/product/detail.html', {'product': product})


# --- Cart Views ---

def add_to_cart(request, product_id):
    if request.method != 'POST':
        return redirect('shop:product_list')

    product = get_object_or_404(Product, pk=product_id, available=True)
    qty = int(request.POST.get('qty', 1))
    cart = _get_cart(request.session)
    cart[str(product.id)] = cart.get(str(product.id), 0) + max(qty, 1)
    request.session.modified = True

    messages.success(request, f'Added {product.name} to cart.')
    next_page = request.POST.get('next') or 'shop:cart'
    return redirect(next_page)


def buy_now(request, product_id):
    product = get_object_or_404(Product, pk=product_id, available=True)
    cart = _get_cart(request.session)
    cart[str(product.id)] = 1  # Set quantity to 1
    request.session.modified = True
    return redirect('shop:checkout')


def cart(request):
    cart = _get_cart(request.session)
    items = []
    total = 0

    for pid in list(cart.keys()):
        try:
            product = Product.objects.get(pk=int(pid))
        except Product.DoesNotExist:
            del cart[pid]
            request.session.modified = True
            continue

        qty = cart[pid]
        subtotal = product.price * qty
        total += subtotal
        items.append({'product': product, 'qty': qty, 'subtotal': subtotal})

    return render(request, 'shop/cart.html', {'items': items, 'total': total})


def remove_from_cart(request, product_id):
    cart = _get_cart(request.session)
    cart.pop(str(product_id), None)
    request.session.modified = True
    messages.info(request, 'Item removed from cart.')
    return redirect('shop:cart')


def clear_cart(request):
    request.session['cart'] = {}
    request.session.modified = True
    messages.info(request, 'Cart cleared.')
    return redirect('shop:cart')


# --- Checkout View ---

def checkout(request):
    cart = _get_cart(request.session)
    items = []
    total = 0

    for pid in list(cart.keys()):
        try:
            product = Product.objects.get(pk=int(pid))
        except Product.DoesNotExist:
            del cart[pid]
            request.session.modified = True
            continue

        qty = cart[pid]
        subtotal = product.price * qty
        total += subtotal
        items.append({'product': product, 'qty': qty, 'subtotal': subtotal})

    if request.method == 'POST':
        # In real app, process order/payment here
        request.session['cart'] = {}
        request.session.modified = True
        messages.success(request, 'Order placed! (demo)')
        return render(request, 'shop/order_success.html', {'total': total})

    return render(request, 'shop/checkout.html', {'items': items, 'total': total})


# --- Static Pages ---

def home(request):
    latest_products = Product.objects.filter(available=True).order_by('-id')[:6]
    return render(request, 'shop/home.html', {'latest_products': latest_products})


def about(request):
    return render(request, 'shop/about.html')
