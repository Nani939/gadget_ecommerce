
# Generated migration for product model and discount fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0009_order_country_order_notes_order_payment_method_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='model',
            field=models.CharField(blank=True, help_text='Product model/variant', max_length=100),
        ),
        migrations.AddField(
            model_name='product',
            name='discount_amount',
            field=models.DecimalField(decimal_places=2, default=0, help_text='Discount amount in rupees', max_digits=10),
        ),
        migrations.AddField(
            model_name='product',
            name='discount_percentage',
            field=models.DecimalField(decimal_places=2, default=0, help_text='Discount percentage (0-100)', max_digits=5),
        ),
    ]
