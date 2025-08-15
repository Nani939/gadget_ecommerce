from django.test import TestCase
from .models import Category, Product

class ProductModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Electronics", slug="electronics")
        self.product = Product.objects.create(
            category=self.category,
            name="Laptop",
            price=1000,
            stock=10,
            available=True
        )

    def test_product_str(self):
        self.assertEqual(str(self.product), "Laptop")

    def test_category_str(self):
        self.assertEqual(str(self.category), "Electronics")
