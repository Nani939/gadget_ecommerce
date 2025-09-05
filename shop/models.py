from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

# -------------------------
# Category Model
# -------------------------
class Category(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "category"
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("shop:product_list_by_category", args=[self.slug])


# -------------------------
# Product Model
# -------------------------
class Product(models.Model):
    category = models.ForeignKey(Category, related_name="products", on_delete=models.CASCADE)
    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, db_index=True)
    image = models.ImageField(upload_to="products/%Y/%m/%d", blank=True, null=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    model = models.CharField(max_length=100, blank=True, help_text="Product model/variant")
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Discount amount in rupees")
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Discount percentage (0-100)")
    available = models.BooleanField(default=True)
    stock = models.PositiveIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    updated = models.DateTimeField(auto_now=True)

    # Extra details (like Amazon page)
    brand = models.CharField(max_length=100, blank=True, null=True)
    model_number = models.CharField(max_length=100, blank=True, null=True)
    weight = models.CharField(max_length=50, blank=True, null=True)
    dimensions = models.CharField(max_length=100, blank=True, null=True)
    warranty = models.CharField(max_length=100, blank=True, null=True)
    shipping = models.CharField(max_length=100, blank=True, null=True)

    # Image
    image = models.ImageField(upload_to="products/", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["name"]
        indexes = [models.Index(fields=["id", "slug"])]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("products:product_detail", args=[self.id])
    
    def get_discounted_price(self):
        if self.discount:
            return self.price - (self.price * (self.discount / 100))
        return self.price
    get_discounted_price.short_description = "Discounted Price"

    def get_savings(self):
        if self.discount:
            return self.price * (self.discount / 100)
        return 0
    get_savings.short_description = "You Save"


def has_discount(self):
    """Check if product has any discount."""
    return self.discount_amount > 0 or self.discount_percentage > 0

# -------------------------
# Order Status Choices
# -------------------------
ORDER_STATUS = [
    ('PLACED', 'Placed'),
    ('PACKED', 'Packed'),
    ('SHIPPED', 'Shipped'),
    ('OUT_FOR_DELIVERY', 'Out for Delivery'),
    ('DELIVERED', 'Delivered'),
    ('PAYMENT_FAILED', 'Payment Failed'),
    ('CANCELLED', 'Cancelled'),
    ('RETURNED', 'Returned'),
]


# -------------------------
# Order Model
# -------------------------
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    customer_name = models.CharField(max_length=200)
    customer_email = models.EmailField()
    phone_number = models.CharField(max_length=15, blank=True)

    # Address fields
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, default="India")

    # Order info
    status = models.CharField(
        max_length=20,
        choices=ORDER_STATUS,
        default="PLACED"
    )
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    delivery_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    delivery_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    delivery_status = models.CharField(max_length=20, default="Pending")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # 🔹 Payment info (ONLY Razorpay)
    payment_method = models.CharField(
        max_length=10,
        choices=[("RZP", "Razorpay")],
        default="RZP"
    )
    paid = models.BooleanField(default=False)

    # 🔹 Razorpay fields
    razorpay_order_id = models.CharField(max_length=255, blank=True, null=True)
    payment_id = models.CharField(max_length=255, blank=True, null=True)
    payment_status = models.CharField(
        max_length=20,
        choices=[("Pending", "Pending"), ("Paid", "Paid"), ("Failed", "Failed")],
        default="Pending"
    )

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.id} - {self.customer_name}"

    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())

# -------------------------
# Order Item Model
# -------------------------
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name="order_items", on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.product.name}"
    
    def get_cost(self):
        return self.price * self.quantity

PAYMENT_METHODS = (
    ('RZP', 'Razorpay'),
)

payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS, default='RZP')

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"
