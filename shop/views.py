from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Category, Product, Order, OrderItem


# -------------------------------
# Home & About
# -------------------------------
def home(request):
    return render(request, "shop/home.html")


def about(request):
    return render(request, "shop/about.html")


# -------------------------------
# Product Views
# -------------------------------
def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    return render(request, "products/product_list.html", {
        "category": category,
        "categories": categories,
        "products": products,
    })


def product_detail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug, available=True)
    return render(request, "products/product_detail.html", {"product": product})


# -------------------------------
# Cart (session-based)
# -------------------------------
def view_cart(request):
    cart = request.session.get("cart", {})
    cart_items, total_price, total_qty = [], 0, 0
    updated_cart = cart.copy()  # To safely remove invalid items

    for product_id, item in cart.items():
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            updated_cart.pop(product_id, None)  # Remove missing product
            continue

        qty = int(item.get("quantity", 1))
        line_total = product.price * qty
        cart_items.append({
            "product": product,
            "quantity": qty,
            "total": line_total,
        })
        total_price += line_total
        total_qty += qty

    request.session["cart"] = updated_cart  # Save cleaned cart

    return render(request, "shop/cart.html", {
        "cart_items": cart_items,
        "total_price": total_price,
        "total_qty": total_qty,
    })


def _parse_qty(request, default=1):
    raw = request.POST.get("quantity") or request.POST.get("qty") or request.GET.get("quantity")
    try:
        q = int(raw) if raw is not None else default
        return max(1, q)
    except (TypeError, ValueError):
        return default


def add_to_cart(request, product_id):
    qty = _parse_qty(request, default=1)
    get_object_or_404(Product, id=product_id)  # 404 if not found

    cart = request.session.get("cart", {})
    current = int(cart.get(str(product_id), {}).get("quantity", 0))
    cart[str(product_id)] = {"quantity": current + qty}
    request.session["cart"] = cart

    if request.GET.get("next") == "checkout":
        return redirect("shop:checkout")
    return redirect("shop:view_cart")


def remove_from_cart(request, item_id):
    cart = request.session.get("cart", {})
    if str(item_id) in cart:
        del cart[str(item_id)]
        request.session["cart"] = cart
    return redirect("shop:view_cart")


def update_quantity(request, item_id):
    if request.method != "POST":
        return redirect("shop:view_cart")
    cart = request.session.get("cart", {})
    if str(item_id) in cart:
        cart[str(item_id)]["quantity"] = _parse_qty(request, default=1)
        request.session["cart"] = cart
    return redirect("shop:view_cart")


def buy_now(request, product_id):
    get_object_or_404(Product, id=product_id)
    cart = request.session.get("cart", {})
    current = int(cart.get(str(product_id), {}).get("quantity", 0))
    cart[str(product_id)] = {"quantity": current + 1}
    request.session["cart"] = cart
    return redirect("shop:checkout")


# -------------------------------
# Checkout & Order Success
# -------------------------------
@login_required
def checkout(request):
    cart = request.session.get("cart", {})
    if not cart:
        return redirect("shop:view_cart")

    cart_items, total_price = [], 0
    for product_id, item in cart.items():
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            continue  # skip missing items

        qty = int(item.get("quantity", 1))
        line_total = product.price * qty
        cart_items.append({"product": product, "quantity": qty, "total": line_total})
        total_price += line_total

    if request.method == "POST":
        order = Order.objects.create(
            customer_name=request.user.username,
            customer_email=request.user.email,
            paid=True,
            address=request.POST.get("address", ""),
            city=request.POST.get("city", ""),
            postal_code=request.POST.get("postal_code", ""),
        )
        for ci in cart_items:
            OrderItem.objects.create(
                order=order,
                product=ci["product"],
                price=ci["product"].price,
                quantity=ci["quantity"],
            )
        request.session["cart"] = {}  # clear cart
        return redirect("shop:order_success", order_id=order.id)

    return render(request, "shop/checkout.html", {
        "cart_items": cart_items,
        "total_price": total_price,
    })


@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer_email=request.user.email)
    return render(request, "shop/order_success.html", {"order": order})
