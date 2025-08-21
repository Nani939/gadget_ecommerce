from django.core.management.base import BaseCommand
from shop.models import Category, Product

class Command(BaseCommand):
    help = 'Create sample products for testing'

    def handle(self, *args, **options):
        # Create categories
        electronics, created = Category.objects.get_or_create(
            name="Electronics",
            defaults={'slug': 'electronics'}
        )
        
        accessories, created = Category.objects.get_or_create(
            name="Accessories", 
            defaults={'slug': 'accessories'}
        )

        # Sample products
        products_data = [
            {
                'name': 'iPhone 15 Pro',
                'slug': 'iphone-15-pro',
                'category': electronics,
                'price': 99999.00,
                'stock': 50,
                'description': 'Latest iPhone with advanced features and powerful performance.',
                'available': True,
            },
            {
                'name': 'Samsung Galaxy S24',
                'slug': 'samsung-galaxy-s24',
                'category': electronics,
                'price': 79999.00,
                'stock': 30,
                'description': 'Premium Android smartphone with excellent camera and display.',
                'available': True,
            },
            {
                'name': 'OnePlus 12R',
                'slug': 'oneplus-12r',
                'category': electronics,
                'price': 45999.00,
                'stock': 25,
                'description': 'Fast charging smartphone with flagship performance.',
                'available': True,
            },
            {
                'name': 'AirPods Pro',
                'slug': 'airpods-pro',
                'category': accessories,
                'price': 24999.00,
                'stock': 100,
                'description': 'Wireless earbuds with active noise cancellation.',
                'available': True,
            },
            {
                'name': 'Wireless Charging Pad',
                'slug': 'wireless-charging-pad',
                'category': accessories,
                'price': 2999.00,
                'stock': 75,
                'description': 'Fast wireless charging pad compatible with all Qi devices.',
                'available': True,
            },
        ]

        for product_data in products_data:
            product, created = Product.objects.get_or_create(
                slug=product_data['slug'],
                defaults=product_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully created product: {product.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Product already exists: {product.name}')
                )

        self.stdout.write(
            self.style.SUCCESS('Sample products creation completed!')
        )