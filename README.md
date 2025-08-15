## 📘 README.md for Gadget Shop (`ss` Project)

````markdown
# 🛒 Gadget Shop - Django E-commerce Website

**Gadget Shop** is an e-commerce web application built using the Django framework. It supports product listings, user authentication, shopping cart functionality, and basic order processing.

---

## 🚀 Features

- User registration and login with custom user model
- Product listing and detail views
- Add to cart / remove from cart
- Checkout flow (basic)
- Category-based product filtering
- Admin panel for managing products and users

---

## 🧠 Project Structure

```bash
kk/                    # Project root
├── gadget_ecommerce/  # Django project directory
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── products/          # App for products
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── templates/products/
│
├── shop/              # App for cart and checkout
│   ├── views.py
│   ├── urls.py
│   └── templates/shop/
│
├── users/             # App for authentication
│   ├── models.py      # CustomUser model
│   ├── views.py
│   ├── forms.py
│   └── urls.py
│
├── templates/         # Base HTML templates
│   └── base.html
│
├── static/            # CSS, JS, images
│
├── manage.py
└── requirements.txt
````

---

## ⚙️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/kk.git
cd kk
```

### 2. Create Virtual Environment

```bash
python -m venv env
source env/bin/activate  # Windows: env\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Superuser (for admin access)

```bash
python manage.py createsuperuser
```

### 6. Run the Development Server

```bash
python manage.py runserver
```

Then visit: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## 📌 Important Notes

### 🔒 Custom User Model

Ensure `AUTH_USER_MODEL = 'users.CustomUser'` is defined in `settings.py` **before** running migrations.

### 🧩 URL Namespaces

This project uses **namespaces** (`shop`, `products`, `users`) for routing. Ensure all `app_name` declarations and URL includes match:

Example:

```python
# gadget_ecommerce/urls.py
urlpatterns = [
    path('admin/', admin.site.urls),
    path('products/', include('products.urls', namespace='products')),
    path('accounts/', include('users.urls', namespace='users')),
    path('', include('shop.urls', namespace='shop')),
]
```

Each app's `urls.py` must have:

```python
app_name = 'shop'  # or 'products', 'users'
```

---

## 🛠️ Technologies Used

* Python 3.13
* Django 5.1.7
* SQLite (default)
* Bootstrap 5 (for styling)
* HTML/CSS

---

## 🙋 Common Errors & Fixes

### 🔁 `'shop' is not a registered namespace`

**Fix:** Add `app_name = 'shop'` in `shop/urls.py` and ensure it's included properly in the root `urls.py`.

---

### ❌ `Reverse for 'add_to_cart' not found`

**Fix:** Add this path in `shop/urls.py`:

```python
path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart')
```

---

## 📷 Screenshots

*(You can insert screenshots of the homepage, product page, cart, etc.)*

---

## 👨‍💻 Author

*    SWAMY MUDHIRAJ
* GitHub: [https://github.com/Nani939](https://github.com/Nani939)

---

## 📝 License

This project is open-source and free to use under the [MIT License](LICENSE).


