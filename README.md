
# Gadget Ecommerce

This is a Django-based e-commerce web application for managing and selling products online.  
Developed by **Swamy Mudhiraj**.

## 📂 Project Structure

```
gadget_ecommerce_extracted/
    gadget_ecommerce-master/
        .gitignore
        README.md
        db.sqlite3
        manage.py
        gadget_ecommerce/
            __init__.py
            asgi.py
            settings.py
            urls.py
            wsgi.py
            __pycache__/
                __init__.cpython-313.pyc
                settings.cpython-313.pyc
                urls.cpython-313.pyc
                views.cpython-313.pyc
                wsgi.cpython-313.pyc
        media/
            products/
                2025/
                    08/
                        18/
                            EARBUDS.jpg
                            ONE_PLUS_2R.webp
                        21/
                            BOAT.webp
                        24/
                            240_F_498259499_l8CkRusvH5pjU47qtvfxV8QgqGCje6O5.jpg
                            Hangman_29_001.webp
                        26/
                            EARBUDS.jpg
                            EARBUDS_dVdIsp2.jpg
                            EARBUDS_qMG1WU7.jpg
        products/
            __init__.py
            apps.py
            tests.py
            urls.py
            views.py
            2025/
                08/
                    13/
                        EARBUDS.jpg
            __pycache__/
                __init__.cpython-313.pyc
                admin.cpython-313.pyc
                apps.cpython-313.pyc
                models.cpython-313.pyc
                urls.cpython-313.pyc
                views.cpython-313.pyc
            migrations/
                0001_initial.py
                0002_product_available_alter_product_image_url_and_more.py
                0003_product_created.py
                0004_remove_product_category_delete_category_and_more.py
                __init__.py
                __pycache__/
                    0001_initial.cpython-313.pyc
                    0002_product_available_alter_product_image_url_and_more.cpython-313.pyc
                    0003_product_created.cpython-313.pyc
                    0004_remove_product_category_delete_category_and_more.cpython-313.pyc
                    __init__.cpython-313.pyc
            templates/
                products/
                    product_detail.html
                    product_list.html
        shop/
            __init__.py
            admin.py
            apps.py
            cart.py
            forms.py
            models.py
            tests.py
            urls.py
            views.py
            __pycache__/
                __init__.cpython-313.pyc
                admin.cpython-313.pyc
                apps.cpython-313.pyc
                cart.cpython-313.pyc
                forms.cpython-313.pyc
                models.cpython-313.pyc
                urls.cpython-313.pyc
                views.cpython-313.pyc
            management/
                __init__.py
                __pycache__/
                    __init__.cpython-313.pyc
                commands/
                    __init__.py
                    create_sample_products.py
            migrations/
                0001_initial.py
                0002_rename_created_at_product_created_product_image_and_more.py
                0003_cart_cartitem.py
                0004_orderitem_remove_cart_user_remove_cartitem_cart_and_more.py
                0005_product_image_product_stock.py
                0006_alter_category_options_alter_order_options_and_more.py
                0007_order_status_order_tracking_number.py
                0008_order_delivery_latitude_order_delivery_longitude_and_more.py
                0009_order_country_order_notes_order_payment_method_and_more.py
                0010_add_product_model_discount.py
                0011_product_discount.py
                0012_product_brand_product_created_at_product_dimensions_and_more.py
                __init__.py
                __pycache__/
                    0001_initial.cpython-313.pyc
                    0002_initial.cpython-313.pyc
                    0002_rename_created_at_product_created_product_image_and_more.cpython-313.pyc
                    0003_cart_cartitem.cpython-313.pyc
                    0004_orderitem_remove_cart_user_remove_cartitem_cart_and_more.cpython-313.pyc
                    0005_product_image_product_stock.cpython-313.pyc
                    0006_alter_category_options_alter_order_options_and_more.cpython-313.pyc
                    0007_order_status_order_tracking_number.cpython-313.pyc
                    0008_order_delivery_latitude_order_delivery_longitude_and_more.cpython-313.pyc
                    0009_order_country_order_notes_order_payment_method_and_more.cpython-313.pyc
                    0010_add_product_model_discount.cpython-313.pyc
                    0011_product_discount.cpython-313.pyc
                    0012_product_brand_product_created_at_product_dimensions_and_more.cpython-313.pyc
                    __init__.cpython-313.pyc
            templates/
                shop/
                    about.html
                    bulk_order.html
                    cart.html
                    checkout.html
                    checkout_success.html
                    compare_products.html
                    home.html
                    order_success.html
                    orders.html
                    payment_success.html
                    print_order_details.html
                    quick_order.html
                    track_order.html
                    wishlist.html
            templatetags/
                __init__.py
                admin_extras.py
                order_extras.py
                shop_extras.py
                __pycache__/
                    __init__.cpython-313.pyc
                    admin_extras.cpython-313.pyc
                    order_extras.cpython-313.pyc
                    shop_extras.cpython-313.pyc
        static/
            css/
                amazon-style.css
            js/
                main.js
        templates/
            base.html
            admin/
                shop/
                    change_list.html
                    delivery_slip.html
                    order_details.html
                    order_stats.html
        users/
            __init__.py
            admin.py
            apps.py
            forms.py
            models.py
            signals.py
            tests.py
            urls.py
            views.py
            __pycache__/
                __init__.cpython-313.pyc
                admin.cpython-313.pyc
                apps.cpython-313.pyc
                forms.cpython-313.pyc
                models.cpython-313.pyc
                urls.cpython-313.pyc
                views.cpython-313.pyc
            migrations/
                0001_initial.py
                0002_address.py
                0003_userprofile.py
                __init__.py
                __pycache__/
                    0001_initial.cpython-313.pyc
                    0002_address.cpython-313.pyc
                    0003_userprofile.cpython-313.pyc
                    __init__.cpython-313.pyc
            templates/
                users/
                    login.html
                    logout.html
                    profile.html
                    signup.html
```

### 🔑 Key Files & Folders

- **manage.py** → Django project management script.
- **db.sqlite3** → Default SQLite database file.
- **gadget_ecommerce/** → Main Django project folder containing settings and configuration.
  - `settings.py` → Project settings.
  - `urls.py` → URL routing for the project.
  - `wsgi.py` / `asgi.py` → Deployment entry points.
- **products/** → Django app for product-related logic.
  - `models.py` → Database models for products.
  - `views.py` → Logic for displaying products.
  - `urls.py` → Routes for product pages.
  - `templates/products/` → HTML templates for product list and detail pages.
  - `migrations/` → Database schema migrations.
- **shop/** → Handles cart, checkout, and order logic.
  - `cart.py` → Shopping cart logic.
  - `models.py` → Order and cart models.
  - `views.py` → Business logic for shop features.
  - `urls.py` → Routes for shop pages.
  - `templates/` (if present) → HTML pages related to cart/checkout.
- **media/** → Uploaded product images and media files.
- **templates/** → Base HTML templates for frontend (if available).
- **.gitignore** → Git ignore rules.
- **README.md** → Documentation file.

## 🚀 Getting Started

### 1️⃣ Clone the repository
```bash
git clone https://github.com/Nani939/gadget_ecommerce.git
cd gadget_ecommerce
```

### 2️⃣ Create & activate virtual environment
```bash
python -m venv venv
source venv/bin/activate   # On Linux/Mac
venv\Scripts\activate    # On Windows
```

### 3️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Run migrations
```bash
python manage.py migrate
```

### 5️⃣ Create a superuser (for admin access)
```bash
python manage.py createsuperuser
```

### 6️⃣ Run the development server
```bash
python manage.py runserver
```

Visit 👉 http://127.0.0.1:8000 in your browser.

## 🛠 Features

- ✅ User authentication (login/signup)
- ✅ Product listing & details
- ✅ Shopping cart functionality
- ✅ Media handling for product images
- ✅ Admin dashboard for managing products & orders

## 📌 Notes

- Default database is SQLite (`db.sqlite3`), but you can switch to PostgreSQL/MySQL in `settings.py`.
- Product images are stored in the `media/` folder.
- Templates for products are located under `products/templates/products/`.

---

💡 *This project is still in development. Contributions are welcome!*
