# Generated by Django 5.1.4 on 2025-01-12 21:47

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rest_auth", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="emailconfirmation",
            name="is_expired",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="emailconfirmation",
            name="token",
            field=models.CharField(default=uuid.uuid4, max_length=100),
        ),
    ]
