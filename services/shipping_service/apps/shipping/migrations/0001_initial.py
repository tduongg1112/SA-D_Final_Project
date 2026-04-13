from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Shipment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("order_id", models.PositiveBigIntegerField(unique=True)),
                ("recipient_name", models.CharField(max_length=120)),
                ("phone", models.CharField(max_length=20)),
                ("address", models.TextField()),
                ("method", models.CharField(default="Standard delivery", max_length=40)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("preparing", "Preparing"),
                            ("in_transit", "In transit"),
                            ("delivered", "Delivered"),
                        ],
                        default="pending",
                        max_length=20,
                    ),
                ),
                ("tracking_code", models.CharField(max_length=64, unique=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
