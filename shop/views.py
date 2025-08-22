import requests
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Category, Product, Order, OrderItem
from users.models import UserProfile  # Make sure this import matches your app structure

# -------------------------------
# Home & About
# -------------------------------
def home(request):
    return render(request, "shop/home.html")

def about(request):
    return render(request, "shop/about.html")

# -------------------------------
# Cart Count API
# -------------------------------
def cart_count(request):
    """Return cart item count as JSON"""
    cart = request.session.get("cart", {})
    total_qty = sum(int(item.get("quantity", 0)) for item in cart.values())
    return JsonResponse({"count": total_qty})

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
    updated_cart = cart.copy()

    for product_id, item in cart.items():
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            updated_cart.pop(product_id, None)
            continue

        qty = int(item.get("quantity", 1))
        line_total = product.price * qty
        cart_items.append({"product": product, "quantity": qty, "total": line_total})
        total_price += line_total
        total_qty += qty

    request.session["cart"] = updated_cart
    return render(request, "shop/cart.html", {"cart_items": cart_items, "total_price": total_price, "total_qty": total_qty})

def _parse_qty(request, default=1):
    raw = request.POST.get("quantity") or request.POST.get("qty") or request.GET.get("quantity")
    try:
        q = int(raw) if raw is not None else default
        return max(1, q)
    except (TypeError, ValueError):
        return default

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id, available=True)
    qty = _parse_qty(request, default=1)
    
    # Check stock availability
    if product.stock < qty:
        messages.error(request, f"Sorry, only {product.stock} items available in stock.")
        return redirect("products:product_detail", pk=product.id)
    
    cart = request.session.get("cart", {})
    current = int(cart.get(str(product_id), {}).get("quantity", 0))
    new_quantity = current + qty
    
    # Check if total quantity exceeds stock
    if new_quantity > product.stock:
        messages.error(request, f"Cannot add {qty} items. Only {product.stock - current} more items available.")
        return redirect("products:product_detail", pk=product.id)
    
    cart[str(product_id)] = {"quantity": new_quantity}
    request.session["cart"] = cart
    messages.success(request, f"Added {qty} {product.name}(s) to your cart.")
    
    if request.GET.get("next") == "checkout":
        return redirect("shop:checkout")
    return redirect("shop:view_cart")

def remove_from_cart(request, product_id):
    cart = request.session.get("cart", {})
    if str(product_id) in cart:
        del cart[str(product_id)]
        request.session["cart"] = cart
        messages.success(request, "Item removed from cart.")
    return redirect("shop:view_cart")

def update_quantity(request, product_id):
    if request.method != "POST":
        return redirect("shop:view_cart")
    
    product = get_object_or_404(Product, id=product_id)
    new_qty = _parse_qty(request, default=1)
    
    # Check stock availability
    if new_qty > product.stock:
        messages.error(request, f"Sorry, only {product.stock} items available in stock.")
        return redirect("shop:view_cart")
    
    cart = request.session.get("cart", {})
    if str(product_id) in cart:
        cart[str(product_id)]["quantity"] = new_qty
        request.session["cart"] = cart
        messages.success(request, "Cart updated successfully.")
    return redirect("shop:view_cart")

def buy_now(request, product_id):
    product = get_object_or_404(Product, id=product_id, available=True)
    qty = _parse_qty(request, default=1)
    
    # Check stock availability
    if product.stock < qty:
        messages.error(request, f"Sorry, only {product.stock} items available in stock.")
        return redirect("products:product_detail", pk=product.id)
    
    cart = request.session.get("cart", {})
    cart[str(product_id)] = {"quantity": qty}  # Replace existing quantity for buy now
    request.session["cart"] = cart
    return redirect("shop:checkout")

# -------------------------------
# Checkout & Order Success with Profile Integration
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
            continue
        qty = int(item.get("quantity", 1))
        line_total = product.price * qty
        cart_items.append({"product": product, "quantity": qty, "total": line_total})
        total_price += line_total

    error = None

    # Try to load user's saved profile if available
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        profile = None

    if request.method == "POST":
        latitude = request.POST.get("latitude")
        longitude = request.POST.get("longitude")
        try:
            latitude = float(latitude) if latitude else None
            longitude = float(longitude) if longitude else None
        except ValueError:
            latitude = None
            longitude = None

        # Grab submitted or profile-backed values
        address = request.POST.get("address", (profile.address if profile else "")).strip()
        city = request.POST.get("city", (profile.city if profile else "")).strip()
        postal_code = request.POST.get("postal_code", (profile.postal_code if profile else "")).strip()
        phone_number = request.POST.get("phone_number", "").strip()
        state = request.POST.get("state", "").strip()

        if latitude and longitude:
            try:
                response = requests.get(
                    "https://nominatim.openstreetmap.org/reverse",
                    params={"format":"json", "lat":latitude, "lon":longitude, "zoom":18, "addressdetails":1},
                    headers={'User-Agent':'gadget-shop'}
                )
                if response.status_code == 200:
                    data = response.json().get("address", {})
                    if not address:
                        address = ", ".join(filter(None, [data.get("road"), data.get("suburb")]))
                    if not city:
                        city = data.get("city") or data.get("town") or data.get("village") or ""
                    if not postal_code:
                        postal_code = data.get("postcode", "")
                else:
                    error = "Could not validate location."
            except Exception:
                error = "Reverse geocoding failed."

        if not address or not city or not postal_code or not phone_number:
            error = error or "Complete address including phone number is required."

        if error:
            return render(request, "shop/checkout.html", {
                "cart_items": cart_items,
                "total_price": total_price,
                "error": error,
                "address": address,
                "city": city,
                "state": state,
                "postal_code": postal_code,
                "phone_number": phone_number,
                "latitude": latitude,
                "longitude": longitude,
            })

        # Calculate total amount
        total_amount = sum(item["total"] for item in cart_items)

        order = Order.objects.create(
            user=request.user,
            customer_name=request.user.username,
            customer_email=request.user.email,
            phone_number=phone_number,
            paid=True,
            address=address,
            city=city,
            state=state,
            postal_code=postal_code,
            total_amount=total_amount,
            payment_method="COD",
            delivery_latitude=latitude,
            delivery_longitude=longitude,
        )
        
        for ci in cart_items:
            OrderItem.objects.create(
                order=order,
                product=ci["product"],
                price=ci["product"].price,
                quantity=ci["quantity"],
            )
            # Reduce stock
            product = ci["product"]
            product.stock -= ci["quantity"]
            product.save()

        # Optionally update user's profile address
        if profile:
            profile.address = address
            profile.city = city
            profile.postal_code = postal_code
            profile.save()

        request.session["cart"] = {}
        return redirect("shop:order_success", order_id=order.id)

    return render(request, "shop/checkout.html", {
        "cart_items": cart_items,
        "total_price": total_price,
        "address": profile.address if profile else "",
        "city": profile.city if profile else "",
        "postal_code": profile.postal_code if profile else "",
        "phone_number": "",
        "state": "",
    })

from datetime import timedelta

@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    estimated_delivery = order.created_at + timedelta(days=3)

    return render(request, "shop/order_success.html", {
        "order": order,
        "estimated_delivery": estimated_delivery,
    })


@login_required
def track_order(request, pk):
    order = get_object_or_404(Order, id=pk)

    status_list = ["PLACED", "PACKED", "SHIPPED", "OUT_FOR_DELIVERY", "DELIVERED"]

    # compute the index of the current status
    try:
        current_status_index = status_list.index(order.status)
    except ValueError:
        current_status_index = -1  # fallback if status not in list

    return render(request, "shop/track_order.html", {
        "order": order,
        "status_list": status_list,
        "current_status_index": current_status_index,
    })
