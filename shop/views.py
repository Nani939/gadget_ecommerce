from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Category, Product
from .forms import OrderCreateForm


# ---- Utility Functions ----

def _get_cart(session):
    return session.setdefault('cart', {})  # {product_id: qty}


# ---- Product Views ----

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


# ---- Cart Views ----

def add_to_cart(request, product_id):
    if request.method != 'POST':
        return redirect('shop:product_list')

    product = get_object_or_404(Product, pk=product_id, available=True)
    qty = int(request.POST.get('qty', 1))
    cart = _get_cart(request.session)
    cart[str(product.id)] = cart.get(str(product.id), 0) + max(qty, 1)
    request.session.modified = True

    messages.success(request, f'Added {product.name} to cart.')
    nxt = request.POST.get('next') or request.GET.get('next')
    return redirect('shop:checkout' if nxt == 'checkout' else 'shop:cart')


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


def cart(request):
    cart = _get_cart(request.session)
    items, total = [], 0
    for pid, qty in cart.items():
        product = get_object_or_404(Product, pk=int(pid))
        subtotal = product.price * qty
        total += subtotal
        items.append({'product': product, 'qty': qty, 'subtotal': subtotal})
    return render(request, 'shop/cart.html', {'items': items, 'total': total})


# ---- Checkout & Order Views ----

def checkout(request):
    cart = _get_cart(request.session)
    items, total = [], 0
    for pid, qty in cart.items():
        product = get_object_or_404(Product, pk=int(pid))
        subtotal = product.price * qty
        total += subtotal
        items.append({'product': product, 'qty': qty, 'subtotal': subtotal})

    if request.method == 'POST':
        # In real app: Save order, payment, email user, etc.
        request.session['cart'] = {}
        request.session.modified = True
        messages.success(request, 'Order placed! (demo flow)')
        return render(request, 'shop/order_success.html', {'total': total})

    return render(request, 'shop/checkout.html', {'items': items, 'total': total})


@login_required
def order_create(request):
    cart = _get_cart(request.session)
    items, total = [], 0
    for pid, qty in cart.items():
        product = get_object_or_404(Product, pk=int(pid))
        subtotal = product.price * qty
        total += subtotal
        items.append({'product': product, 'qty': qty, 'subtotal': subtotal})

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.save()
            request.session['cart'] = {}
            request.session.modified = True
            return render(request, 'shop/order/created.html', {'order': order})
    else:
        form = OrderCreateForm()

    return render(request, 'shop/order/create.html', {
        'cart_items': items,
        'total': total,
        'form': form
    })


# ---- Static Pages ----

def home(request):
    latest_products = Product.objects.filter(available=True).order_by('-id')[:6]
    return render(request, 'shop/home.html', {'latest_products': latest_products})


def about(request):
    return render(request, 'shop/about.html')
from django.shortcuts import redirect, get_object_or_404
from shop.models import Product

def add_to_cart(request, product_id):
    # Your logic to add the product to the cart here
    product = get_object_or_404(Product, id=product_id)
    # Add product to session or cart model
    # ...
    return redirect('shop:cart')  # or redirect wherever needed
