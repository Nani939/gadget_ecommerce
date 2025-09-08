import requests
from datetime import timedelta
from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.mail import send_mail
import json, hmac, hashlib
from .models import Category, Product, Order, OrderItem
from users.models import UserProfile
from shop.models import Wishlist  # 👈 import your model here

import razorpay

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
# Payment Success (Razorpay callback)
# -------------------------------
@csrf_exempt
def payment_success(request):
    if request.method == "POST":
        import json, hmac, hashlib
        from django.contrib.auth import get_user_model
        data = json.loads(request.body)
        # Extract payment and address info
        razorpay_payment_id = data.get("razorpay_payment_id")
        razorpay_order_id = data.get("razorpay_order_id")
        razorpay_signature = data.get("razorpay_signature")
        name = data.get("name", "").strip()
        address = data.get("address", "").strip()
        phone_number = data.get("phone", "").strip()
        user = request.user if request.user.is_authenticated else None
        # Razorpay signature verification
        key_secret = getattr(settings, 'RAZORPAY_KEY_SECRET', None)
        if not (razorpay_payment_id and razorpay_order_id and razorpay_signature and key_secret):
            return JsonResponse({"status": "error", "error": "Missing payment data."}, status=400)
        msg = f"{razorpay_order_id}|{razorpay_payment_id}"
        generated_signature = hmac.new(
            key_secret.encode(),
            msg.encode(),
            hashlib.sha256
        ).hexdigest()
        if generated_signature != razorpay_signature:
            return JsonResponse({"status": "error", "error": "Payment signature verification failed."}, status=400)
        # Get cart from session
        cart = request.session.get("cart", {})
        if not cart or not name or not address or not phone_number:
            return JsonResponse({"status": "error", "error": "Missing data or cart empty."}, status=400)
        # Calculate total and create order
        cart_items, total_price = [], 0
        from .models import Product, Order, OrderItem
        for product_id, item in cart.items():
            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                continue
            qty = int(item.get("quantity", 1))
            line_total = product.get_discounted_price() * qty
            cart_items.append({"product": product, "quantity": qty, "total": line_total})
            total_price += line_total
        order = Order.objects.create(
            user=user,
            customer_name=name,
            customer_email=user.email if user else "",
            phone_number=phone_number,
            paid=True,
            address=address,
            city="",
            state="",
            postal_code="",
            total_amount=total_price,
            payment_method="razorpay",
            payment_id=razorpay_payment_id,
            payment_signature=razorpay_signature,
            payment_order_id=razorpay_order_id,
        )
        # Send order confirmation email (plain text)
        if order.customer_email:
            subject = f"Order Confirmation - Gadget Shop (Order #{order.id})"
            message = (
                f"Dear {order.customer_name},\n\n"
                f"Thank you for your order! Your payment was successful.\n\n"
                f"Order Number: {order.id}\n"
                f"Total Amount: ₹{order.total_amount}\n"
                f"Status: {order.get_status_display()}\n\n"
                f"We'll notify you when your order is shipped.\n\n"
                f"Thank you for shopping with us!\nGadget Shop Team"
            )
            send_mail(subject, message, None, [order.customer_email], fail_silently=True)
        for ci in cart_items:
            OrderItem.objects.create(
                order=order,
                product=ci["product"],
                price=ci["product"].get_discounted_price(),
                quantity=ci["quantity"],
            )
            ci["product"].stock -= ci["quantity"]
            ci["product"].save()
        # Optionally update user's profile address
        if user:
            try:
                profile = user.userprofile
                profile.address = address
                profile.save()
            except Exception:
                pass
        request.session["cart"] = {}
        return JsonResponse({"status": "success", "order_id": order.id})
    return JsonResponse({"error": "Invalid request"}, status=400)

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
        line_total = product.get_discounted_price() * qty
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
# Checkout & Order Success with Razorpay Integration
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
        line_total = product.get_discounted_price() * qty
        cart_items.append({"product": product, "quantity": qty, "total": line_total})
        total_price += line_total

    # Load or create user's profile using the correct related_name
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        import json
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            payment_method = data.get("payment_method", "COD").lower()
            address = data.get("address", "").strip()
            phone_number = data.get("phone", "").strip()
            name = data.get("name", "").strip()
            city = data.get("city", "").strip()
            state = data.get("state", "").strip()
            postal_code = data.get("postal_code", "").strip()
            latitude = data.get("latitude")
            longitude = data.get("longitude")

            if not address or not phone_number or not name:
                return JsonResponse({"status": "error", "error": "All address fields required."}, status=400)

            # Save/update user's profile info
            profile.address = address
            profile.city = city
            profile.postal_code = postal_code
            profile.save()

            # Razorpay integration
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            razorpay_order = client.order.create({
                "amount": int(total_price * 100),  # in paise
                "currency": "INR",
                "payment_capture": "1"
            })

            return JsonResponse({
                "razorpay_order_id": razorpay_order["id"],
                "razorpay_key": settings.RAZORPAY_KEY_ID,
                "razorpay_amount": int(total_price * 100)
            })

        # fallback for non-JSON POST (form submit)
        # ... your existing form handling code ...

    return render(request, "shop/checkout.html", {
        "cart_items": cart_items,
        "total_price": total_price,
        "address": profile.address,
        "city": profile.city,
        "postal_code": profile.postal_code,
        "phone_number": "",
        "state": "",
    })


@csrf_exempt
@login_required
def payment_success(request):
    if request.method == "POST":
        data = json.loads(request.body)

        razorpay_order_id = data.get("razorpay_order_id")
        razorpay_payment_id = data.get("razorpay_payment_id")
        razorpay_signature = data.get("razorpay_signature")

        # ✅ Verify signature
        generated_signature = hmac.new(
            settings.RAZORPAY_SECRET.encode(),
            f"{razorpay_order_id}|{razorpay_payment_id}".encode(),
            hashlib.sha256
        ).hexdigest()

        if generated_signature != razorpay_signature:
            return JsonResponse({"status": "failed", "message": "Signature mismatch"})

        # ✅ Find order
        try:
            order = Order.objects.get(razorpay_order_id=razorpay_order_id, user=request.user)
        except Order.DoesNotExist:
            return JsonResponse({"status": "failed", "message": "Order not found"})

        # ✅ Update order as paid
        order.payment_status = "Paid"
        order.payment_id = razorpay_payment_id
        order.save()

        return JsonResponse({
            "status": "success",
            "redirect_url": f"/orders/success/{order.id}/"
        })

    return JsonResponse({"status": "failed", "message": "Invalid request"}, status=400)
# -------------------------------
# Order Success
# -------------------------------
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
    order = get_object_or_404(Order, id=pk, user=request.user)
    status_list = ["PLACED", "PACKED", "SHIPPED", "OUT_FOR_DELIVERY", "DELIVERED"]
    try:
        current_status_index = status_list.index(order.status)
    except ValueError:
        current_status_index = -1
    return render(request, "shop/track_order.html", {
        "order": order,
        "status_list": status_list,
        "current_status_index": current_status_index,
    })

# -------------------------------
# Print and Delivery Management
# -------------------------------
@login_required
def print_order_details(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if not request.user.is_staff and order.user != request.user:
        messages.error(request, "You don't have permission to view this order.")
        return redirect('shop:home')
    context = {
        'order': order,
        'print_date': timezone.now(),
        'company_info': {
            'name': 'Gadget Shop',
            'address': '123 Tech Street, Digital City, 560001',
            'phone': '+91 98765 43210',
            'email': 'orders@gadgetshop.com',
            'website': 'www.gadgetshop.com',
            'gst': 'GST123456789'
        }
    }
    return render(request, 'shop/print_order_details.html', context)

@login_required
def delivery_slip(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if not request.user.is_staff and order.user != request.user:
        messages.error(request, "You don't have permission to view this order.")
        return redirect('shop:home')
    context = {
        'order': order,
        'delivery_date': timezone.now(),
        'courier_instructions': [
            'Handle with care - Electronic items',
            'Verify customer identity before delivery',
            'Collect payment if COD',
            'Get delivery confirmation signature',
            'Take photo proof of delivery'
        ]
    }
    return render(request, 'shop/delivery_slip.html', context)

# -------------------------------
# Unique Features
# -------------------------------
@login_required
def wishlist(request):
    wishlist_items = request.session.get('wishlist', [])
    products = Product.objects.filter(id__in=wishlist_items, available=True)
    return render(request, 'shop/wishlist.html', {
        'products': products,
        'wishlist_count': len(wishlist_items)
    })

@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id, available=True)
    wishlist = request.session.get('wishlist', [])
    if product_id not in wishlist:
        wishlist.append(product_id)
        request.session['wishlist'] = wishlist
        messages.success(request, f"{product.name} added to your wishlist!")
    else:
        messages.info(request, f"{product.name} is already in your wishlist.")
    return redirect('products:product_detail', pk=product.id)

def compare_products(request):
    compare_list = request.session.get('compare', [])
    products = Product.objects.filter(id__in=compare_list, available=True)
    return render(request, 'shop/compare_products.html', {
        'products': products,
        'compare_count': len(compare_list)
    })

def add_to_compare(request, product_id):
    product = get_object_or_404(Product, id=product_id, available=True)
    compare_list = request.session.get('compare', [])
    if len(compare_list) >= 4:
        messages.warning(request, "You can compare maximum 4 products at a time.")
        return redirect('shop:compare_products')
    if product_id not in compare_list:
        compare_list.append(product_id)
        request.session['compare'] = compare_list
        messages.success(request, f"{product.name} added to comparison!")
    else:
        messages.info(request, f"{product.name} is already in comparison.")
    return redirect('products:product_detail', pk=product.id)

@login_required
def quick_order(request):
    if request.method == 'POST':
        product_codes = request.POST.get('product_codes', '').strip()
        if not product_codes:
            messages.error(request, "Please enter product codes.")
            return render(request, 'shop/quick_order.html')
        cart = request.session.get("cart", {})
        added_count = 0
        for line in product_codes.split('\n'):
            line = line.strip()
            if ':' in line:
                try:
                    code, qty = line.split(':')
                    product_id = int(code.strip())
                    quantity = int(qty.strip())
                    product = Product.objects.get(id=product_id, available=True)
                    if product.stock >= quantity:
                        cart[str(product_id)] = {"quantity": quantity}
                        added_count += 1
                    else:
                        messages.warning(request, f"Product {product.name} has insufficient stock.")
                except (ValueError, Product.DoesNotExist):
                    messages.warning(request, f"Invalid product code: {line}")
        if added_count > 0:
            request.session["cart"] = cart
            messages.success(request, f"{added_count} products added to cart.")
            return redirect('shop:view_cart')
        else:
            messages.error(request, "No valid products were added.")
    return render(request, 'shop/quick_order.html')

@login_required
def bulk_order(request):
    if request.method == 'POST':
        csv_file = request.FILES.get('bulk_file')
        if csv_file:
            try:
                import csv
                import io
                file_data = csv_file.read().decode('utf-8')
                csv_data = csv.reader(io.StringIO(file_data))
                cart = request.session.get("cart", {})
                added_count = 0
                for row in csv_data:
                    if len(row) >= 2:
                        try:
                            product_id = int(row[0])
                            quantity = int(row[1])
                            product = Product.objects.get(id=product_id, available=True)
                            if product.stock >= quantity:
                                cart[str(product_id)] = {"quantity": quantity}
                                added_count += 1
                        except (ValueError, Product.DoesNotExist):
                            continue
                if added_count > 0:
                    request.session["cart"] = cart
                    messages.success(request, f"{added_count} products added from bulk order.")
                    return redirect('shop:view_cart')
                else:
                    messages.error(request, "No valid products found in the file.")
            except Exception:
                messages.error(request, "Error processing file. Please check the format.")
    return render(request, 'shop/bulk_order.html')

@login_required(login_url="users:login")
def orders_list(request):
    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "shop/orders.html", {"orders": orders})

def order_details_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    estimated_delivery = order.created_at + timedelta(days=3)
    context = {
        "order": order,
        "estimated_delivery": estimated_delivery,
    }
    return render(request, "admin/shop/order_details.html", context)




@login_required
def remove_from_wishlist(request, product_id):
    wishlist = request.session.get('wishlist', [])
    if product_id in wishlist:
        wishlist.remove(product_id)
        request.session['wishlist'] = wishlist
    return JsonResponse({"success": True, "wishlist_count": len(wishlist)})

# Admin helper views for CSV downloads
def download_addresses_admin(request):
    """Admin view to download all addresses"""
    if not request.user.is_staff:
        return redirect('shop:home')
    
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="all_customer_addresses.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        "Order ID", "Customer Name", "Email", "Phone", "Address", 
        "City", "State", "Postal Code", "Country", "Order Date"
    ])
    
    orders = Order.objects.all().order_by("-created_at")
    for order in orders:
        writer.writerow([
            order.id, order.customer_name, order.customer_email,
            order.phone_number or "N/A", order.address or "N/A",
            order.city or "N/A", order.state or "N/A", 
            order.postal_code or "N/A", order.country,
            order.created_at.strftime("%Y-%m-%d")
        ])
    
    return response

def download_single_address_admin(request, order_id):
    """Admin view to download single order address"""
    if not request.user.is_staff:
        return redirect('shop:home')
    
    import csv
    from django.http import HttpResponse
    
    order = get_object_or_404(Order, id=order_id)
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="order_{order.id}_address.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        "Order ID", "Customer Name", "Email", "Phone", "Address", 
        "City", "State", "Postal Code", "Country", "Order Date"
    ])
    writer.writerow([
        order.id, order.customer_name, order.customer_email,
        order.phone_number or "N/A", order.address or "N/A",
        order.city or "N/A", order.state or "N/A", 
        order.postal_code or "N/A", order.country,
        order.created_at.strftime("%Y-%m-%d")
    ])
    
    return response