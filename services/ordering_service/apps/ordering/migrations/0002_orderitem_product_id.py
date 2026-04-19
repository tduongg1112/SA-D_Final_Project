from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ordering", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="orderitem",
            name="product_id",
            field=models.PositiveBigIntegerField(blank=True, null=True),
        ),
    ]
